"""
HTTP client for the MCP-PyPI client.
"""

import json
import logging
import asyncio
import random
from typing import Dict, Any, Optional, cast

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from mcp_pypi.core.models import PyPIClientConfig, ErrorCode, format_error
from mcp_pypi.core.cache import AsyncCacheManager

logger = logging.getLogger("mcp-pypi.http")


class AsyncHTTPClient:
    """Async HTTP client for making requests to PyPI."""

    def __init__(self, config: PyPIClientConfig, cache_manager: AsyncCacheManager):
        self.config = config
        self.cache = cache_manager  # Changed from self.cache_manager to self.cache
        self.rate_limit_delay = 0.1  # Initial delay between requests
        self.last_request_time = 0.0
        self._session: Optional[ClientSession] = None

    async def _get_session(self) -> ClientSession:
        """Get or create an aiohttp ClientSession."""
        if self._session is None or self._session.closed:
            timeout = ClientTimeout(total=self.config.timeout)  # type: ignore[call-arg]
            self._session = ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _apply_rate_limit(self) -> None:
        """Apply rate limiting to avoid overwhelming the server."""
        import time

        current_time = time.time()
        elapsed = current_time - self.last_request_time

        if elapsed < self.rate_limit_delay:
            delay = self.rate_limit_delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {delay:.2f}s")
            await asyncio.sleep(delay)

        self.last_request_time = time.time()

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        data: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Fetch data from URL with caching, rate limiting, and retries.

        Args:
            url: The URL to fetch
            method: The HTTP method to use (default: GET)
            headers: Optional additional headers to send
            data: Optional request body data (for POST requests)

        Returns:
            The parsed response as a dictionary
        """
        # Check cache first (only for GET requests)
        if method == "GET" and data is None:
            cached_data = await self.cache.get(url)
            if cached_data:
                logger.debug(f"Cache hit for {url}")
                return cached_data

        # Get ETag if available for conditional requests
        etag = await self.cache.get_etag(url) if method == "GET" else None

        # Prepare headers
        request_headers = {"User-Agent": self.config.user_agent}
        if etag:
            request_headers["If-None-Match"] = etag

        # Merge with any additional headers provided
        if headers:
            request_headers.update(headers)

        session = await self._get_session()
        retries_left = self.config.max_retries
        retry_delay = self.config.retry_delay
        last_error = None

        while retries_left > 0:
            try:
                # Apply rate limiting
                await self._apply_rate_limit()

                logger.debug(f"Sending {method} request to {url}")
                async with session.request(
                    method, url, headers=request_headers, data=data
                ) as response:
                    logger.debug(
                        f"Received response with status {response.status} and content type {response.headers.get('Content-Type', 'unknown')}"
                    )

                    # Handle HTTP status codes
                    if response.status == 304 and cached_data:  # Not Modified
                        logger.debug(f"Not modified (304) for {url}, using cache")
                        return cached_data
                    elif response.status == 304:
                        logger.warning(
                            f"Received 304 Not Modified but no cached data available for {url}"
                        )
                        # Make a new request without any ETag or cache
                        logger.debug(f"Retrying request without cache headers")
                        retry_headers = {"User-Agent": self.config.user_agent}
                        if headers:
                            retry_headers.update(headers)
                        async with session.request(
                            method, url, headers=retry_headers, data=data
                        ) as retry_response:
                            logger.debug(
                                f"Retry response status: {retry_response.status}"
                            )

                            if retry_response.status >= 400:
                                error_message = f"HTTP error {retry_response.status}: {retry_response.reason}"
                                return cast(
                                    Dict[str, Any],
                                    format_error(
                                        ErrorCode.NETWORK_ERROR, error_message
                                    ),
                                )

                            content_type = retry_response.headers.get(
                                "Content-Type", ""
                            )
                            new_etag = retry_response.headers.get("ETag")

                            if "application/json" in content_type:
                                try:
                                    result = await retry_response.json()
                                    if isinstance(result, dict) and method == "GET":
                                        await self.cache.set(url, result, new_etag)
                                    return result
                                except json.JSONDecodeError as e:
                                    return cast(
                                        Dict[str, Any],
                                        format_error(
                                            ErrorCode.PARSE_ERROR,
                                            f"Invalid JSON response from {url}: {e}",
                                        ),
                                    )
                            else:
                                # For non-JSON responses
                                data = await retry_response.read()
                                if (
                                    "application/xml" in content_type
                                    or "text/xml" in content_type
                                ):
                                    return {
                                        "raw_data": data,
                                        "content_type": content_type,
                                    }

                                try:
                                    text_result = data.decode("utf-8")
                                    return {
                                        "raw_data": text_result,
                                        "content_type": content_type,
                                    }
                                except UnicodeDecodeError:
                                    return {
                                        "raw_data": data,
                                        "content_type": content_type,
                                    }

                    if response.status == 429:  # Too Many Requests
                        retry_after = response.headers.get("Retry-After")
                        if retry_after and retry_after.isdigit():
                            self.rate_limit_delay = float(retry_after)
                        else:
                            # Exponential backoff with jitter
                            self.rate_limit_delay = min(
                                60, self.rate_limit_delay * 2
                            ) + random.uniform(0, 1)

                        logger.warning(
                            f"Rate limited, retrying after {self.rate_limit_delay:.2f}s"
                        )
                        await asyncio.sleep(self.rate_limit_delay)
                        continue

                    if response.status == 404:
                        return cast(
                            Dict[str, Any],
                            format_error(
                                ErrorCode.NOT_FOUND, f"Resource not found: {url}"
                            ),
                        )

                    if response.status >= 400:
                        error_message = (
                            f"HTTP error {response.status}: {response.reason}"
                        )

                        # Try to extract more details from response body
                        try:
                            error_body = await response.text()
                            if error_body:
                                error_message += f" - {error_body[:200]}"
                        except Exception:
                            pass

                        # Decide if we should retry based on status code
                        if response.status >= 500:  # Server errors are retriable
                            retries_left -= 1
                            retry_delay = self._get_next_retry_delay(retry_delay)
                            logger.warning(
                                f"Server error {response.status}, retrying in {retry_delay:.2f}s ({retries_left} retries left)"
                            )
                            await asyncio.sleep(retry_delay)
                            continue
                        else:  # Client errors are not retriable
                            return cast(
                                Dict[str, Any],
                                format_error(ErrorCode.NETWORK_ERROR, error_message),
                            )

                    # Extract content type and response data
                    content_type = response.headers.get("Content-Type", "")
                    new_etag = response.headers.get("ETag")

                    logger.debug(
                        f"Processing response with content type: {content_type}"
                    )

                    if "application/json" in content_type:
                        try:
                            result = await response.json()
                            logger.debug(
                                f"Successfully parsed JSON response with keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
                            )

                            # Cache successful JSON responses (only for GET requests)
                            if isinstance(result, dict) and method == "GET":
                                logger.debug(f"Caching result for {url}")
                                await self.cache.set(url, result, new_etag)

                            return result
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error for {url}: {e}")
                            return cast(
                                Dict[str, Any],
                                format_error(
                                    ErrorCode.PARSE_ERROR,
                                    f"Invalid JSON response from {url}: {e}",
                                ),
                            )
                    else:
                        # Return raw data for non-JSON responses
                        try:
                            data = await response.read()
                            logger.debug(f"Read raw data of length {len(data)} bytes")

                            # For XML responses, keep it as bytes for the XML parser
                            if (
                                "application/xml" in content_type
                                or "text/xml" in content_type
                            ):
                                logger.debug(f"Returning XML data as bytes")
                                return {"raw_data": data, "content_type": content_type}

                            # Convert bytes to UTF-8 string for text responses
                            try:
                                text_result = data.decode("utf-8")
                                logger.debug(
                                    f"Decoded as UTF-8 text of length {len(text_result)} chars"
                                )
                                return {
                                    "raw_data": text_result,
                                    "content_type": content_type,
                                }
                            except UnicodeDecodeError:
                                # If it can't be decoded as UTF-8, return as bytes
                                logger.debug(
                                    f"Could not decode as UTF-8, returning as bytes"
                                )
                                return {"raw_data": data, "content_type": content_type}
                        except Exception as e:
                            logger.error(f"Error reading response data: {e}")
                            return cast(
                                Dict[str, Any],
                                format_error(
                                    ErrorCode.PARSE_ERROR,
                                    f"Error reading response data: {e}",
                                ),
                            )

            except aiohttp.ClientConnectorError as e:
                last_error = str(e)
                logger.warning(f"Connection error for {url}: {e}")
            except aiohttp.ClientError as e:
                last_error = str(e)
                logger.warning(f"Client error for {url}: {e}")
            except asyncio.TimeoutError:
                last_error = "Request timed out"
                logger.warning(f"Timeout for {url}")
            except json.JSONDecodeError as e:
                return cast(
                    Dict[str, Any],
                    format_error(
                        ErrorCode.PARSE_ERROR, f"Invalid JSON response from {url}: {e}"
                    ),
                )
            except Exception as e:
                last_error = str(e)
                logger.exception(f"Unexpected error for {url}: {e}")

            # Apply backoff before retrying
            retries_left -= 1
            if retries_left > 0:
                retry_delay = self._get_next_retry_delay(retry_delay)
                logger.warning(
                    f"Retrying in {retry_delay:.2f}s ({retries_left} retries left)"
                )
                await asyncio.sleep(retry_delay)

        # All retries failed
        return cast(
            Dict[str, Any],
            format_error(
                ErrorCode.NETWORK_ERROR,
                f"Failed to fetch {url} after {self.config.max_retries} retries: {last_error}",
            ),
        )

    def _get_next_retry_delay(self, current_delay: float) -> float:
        """Calculate the next retry delay using exponential backoff with jitter."""
        # Apply full jitter: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
        return min(60.0, current_delay * 2) * random.uniform(0.5, 1.0)
