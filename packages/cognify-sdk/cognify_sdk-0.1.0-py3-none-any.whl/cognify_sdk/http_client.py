"""
HTTP client wrapper for the Cognify SDK.

This module provides a unified HTTP client interface with both synchronous
and asynchronous support, built on top of httpx.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional, Union, AsyncGenerator, TYPE_CHECKING
from urllib.parse import urljoin

import httpx
from httpx import Response

from .config import CognifyConfig
from .exceptions import (
    CognifyAPIError,
    CognifyAuthenticationError,
    CognifyConnectionError,
    CognifyNotFoundError,
    CognifyRateLimitError,
    CognifyTimeoutError,
)
from .types import Headers, QueryParams

if TYPE_CHECKING:
    from .auth.middleware import AuthMiddleware


logger = logging.getLogger(__name__)


class HTTPClient:
    """
    HTTP client wrapper providing both sync and async interfaces.

    This class handles all HTTP communication with the Cognify API,
    including authentication, error handling, retries, and response parsing.
    """

    def __init__(self, config: CognifyConfig) -> None:
        """
        Initialize the HTTP client.

        Args:
            config: Cognify configuration object
        """
        self.config = config
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
        self._auth_middleware: Optional["AuthMiddleware"] = None

        # Setup logging
        if config.debug:
            logging.basicConfig(level=logging.DEBUG)
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(getattr(logging, config.log_level))

    def _get_client_kwargs(self) -> Dict[str, Any]:
        """Get common client configuration."""
        kwargs = {
            "base_url": self.config.base_url,
            "timeout": httpx.Timeout(self.config.timeout),
            "limits": httpx.Limits(
                max_connections=self.config.max_connections,
                max_keepalive_connections=self.config.max_keepalive_connections,
                keepalive_expiry=self.config.keepalive_expiry,
            ),
            "verify": self.config.verify_ssl,
        }

        # Add proxy configuration
        if self.config.proxy:
            kwargs["proxies"] = self.config.proxy

        # Add SSL configuration
        if self.config.ssl_cert_file and self.config.ssl_key_file:
            kwargs["cert"] = (self.config.ssl_cert_file, self.config.ssl_key_file)

        return kwargs

    def set_auth_middleware(self, auth_middleware: "AuthMiddleware") -> None:
        """
        Set authentication middleware for requests.

        Args:
            auth_middleware: Authentication middleware instance
        """
        self._auth_middleware = auth_middleware

    @property
    def sync_client(self) -> httpx.Client:
        """Get or create synchronous HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(**self._get_client_kwargs())
        return self._sync_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create asynchronous HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(**self._get_client_kwargs())
        return self._async_client

    def _prepare_headers(self, headers: Optional[Headers] = None) -> Headers:
        """Prepare request headers."""
        default_headers = self.config.get_headers()
        if headers:
            default_headers.update(headers)
        return default_headers

    def _prepare_url(self, url: str) -> str:
        """Prepare request URL."""
        if url.startswith(("http://", "https://")):
            return url
        return self.config.get_full_url(url)

    def _handle_response(self, response: Response) -> Dict[str, Any]:
        """
        Handle HTTP response and extract data.

        Args:
            response: HTTP response object

        Returns:
            Parsed response data

        Raises:
            CognifyAPIError: For API errors
            CognifyAuthenticationError: For auth errors
            CognifyNotFoundError: For 404 errors
            CognifyRateLimitError: For rate limit errors
        """
        request_id = response.headers.get("x-request-id")

        # Log response if debugging
        if self.config.log_requests:
            logger.debug(
                f"Response: {response.status_code} {response.request.method} "
                f"{response.request.url} - {len(response.content)} bytes"
            )

        # Handle successful responses
        if 200 <= response.status_code < 300:
            try:
                return response.json()
            except ValueError:
                # Handle non-JSON responses
                return {"content": response.text}

        # Parse error response
        try:
            error_data = response.json()
            error_message = error_data.get("message", "Unknown error")
        except ValueError:
            error_message = response.text or f"HTTP {response.status_code}"
            error_data = {}

        # Handle specific error types
        if response.status_code == 401:
            raise CognifyAuthenticationError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
            )
        elif response.status_code == 404:
            raise CognifyNotFoundError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("retry-after")
            raise CognifyRateLimitError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
                retry_after=int(retry_after) if retry_after else None,
            )
        else:
            raise CognifyAPIError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
            )

    def _should_retry(self, attempt: int, exception: Exception) -> bool:
        """Determine if request should be retried."""
        if attempt >= self.config.max_retries:
            return False

        # Retry on connection errors and 5xx responses
        if isinstance(exception, (CognifyConnectionError, CognifyTimeoutError)):
            return True

        if isinstance(exception, CognifyAPIError):
            return 500 <= exception.status_code < 600

        return False

    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay before retry with exponential backoff."""
        return self.config.retry_delay * (2 ** attempt)

    def request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Make a synchronous HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            headers: Request headers
            json: JSON data
            data: Raw data
            files: File uploads
            **kwargs: Additional httpx arguments

        Returns:
            Parsed response data
        """
        prepared_url = self._prepare_url(url)
        prepared_headers = self._prepare_headers(headers)

        # Log request if debugging
        if self.config.log_requests:
            logger.debug(f"Request: {method} {prepared_url}")

        for attempt in range(self.config.max_retries + 1):
            try:
                # Create request object for auth middleware
                request = httpx.Request(
                    method=method,
                    url=prepared_url,
                    params=params,
                    headers=prepared_headers,
                    json=json,
                    data=data,
                    files=files,
                    **kwargs,
                )

                # Apply authentication middleware if available
                if self._auth_middleware:
                    # Note: sync version doesn't support async middleware
                    # We'll add auth headers directly from the provider
                    try:
                        auth_headers = self._auth_middleware.get_auth_provider().get_auth_headers()
                        request.headers.update(auth_headers)
                    except Exception as e:
                        logger.warning(f"Failed to add auth headers: {e}")

                response = self.sync_client.send(request)

                # Handle auth errors through middleware
                if self._auth_middleware:
                    self._auth_middleware.handle_response(response)

                return self._handle_response(response)

            except httpx.TimeoutException as e:
                exception = CognifyTimeoutError(
                    f"Request timed out after {self.config.timeout}s",
                    timeout=self.config.timeout,
                )
                if not self._should_retry(attempt, exception):
                    raise exception

            except httpx.ConnectError as e:
                exception = CognifyConnectionError(f"Connection failed: {e}")
                if not self._should_retry(attempt, exception):
                    raise exception

            except CognifyAPIError as e:
                if not self._should_retry(attempt, e):
                    raise
                exception = e

            # Wait before retry
            if attempt < self.config.max_retries:
                delay = self._calculate_retry_delay(attempt)
                logger.debug(f"Retrying in {delay}s (attempt {attempt + 1})")
                time.sleep(delay)

        # This should never be reached, but just in case
        raise exception  # type: ignore

    async def arequest(
        self,
        method: str,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Make an asynchronous HTTP request.

        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            headers: Request headers
            json: JSON data
            data: Raw data
            files: File uploads
            **kwargs: Additional httpx arguments

        Returns:
            Parsed response data
        """
        prepared_url = self._prepare_url(url)
        prepared_headers = self._prepare_headers(headers)

        # Log request if debugging
        if self.config.log_requests:
            logger.debug(f"Async Request: {method} {prepared_url}")

        for attempt in range(self.config.max_retries + 1):
            try:
                # Create request object for auth middleware
                request = httpx.Request(
                    method=method,
                    url=prepared_url,
                    params=params,
                    headers=prepared_headers,
                    json=json,
                    data=data,
                    files=files,
                    **kwargs,
                )

                # Apply authentication middleware if available
                if self._auth_middleware:
                    request = await self._auth_middleware.prepare_request(request)

                response = await self.async_client.send(request)

                # Handle auth errors through middleware
                if self._auth_middleware:
                    self._auth_middleware.handle_response(response)

                return self._handle_response(response)

            except httpx.TimeoutException as e:
                exception = CognifyTimeoutError(
                    f"Request timed out after {self.config.timeout}s",
                    timeout=self.config.timeout,
                )
                if not self._should_retry(attempt, exception):
                    raise exception

            except httpx.ConnectError as e:
                exception = CognifyConnectionError(f"Connection failed: {e}")
                if not self._should_retry(attempt, exception):
                    raise exception

            except CognifyAPIError as e:
                if not self._should_retry(attempt, e):
                    raise
                exception = e

            # Wait before retry
            if attempt < self.config.max_retries:
                delay = self._calculate_retry_delay(attempt)
                logger.debug(f"Retrying in {delay}s (attempt {attempt + 1})")
                await asyncio.sleep(delay)

        # This should never be reached, but just in case
        raise exception  # type: ignore

    # Convenience methods for common HTTP verbs
    def get(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a synchronous GET request."""
        return self.request("GET", url, params=params, headers=headers, **kwargs)

    def post(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a synchronous POST request."""
        return self.request(
            "POST", url, params=params, headers=headers, json=json, data=data, files=files, **kwargs
        )

    def put(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a synchronous PUT request."""
        return self.request("PUT", url, params=params, headers=headers, json=json, data=data, **kwargs)

    def delete(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a synchronous DELETE request."""
        return self.request("DELETE", url, params=params, headers=headers, **kwargs)

    def patch(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make a synchronous PATCH request."""
        return self.request("PATCH", url, params=params, headers=headers, json=json, data=data, **kwargs)

    # Async convenience methods
    async def aget(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an asynchronous GET request."""
        return await self.arequest("GET", url, params=params, headers=headers, **kwargs)

    async def apost(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        files: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an asynchronous POST request."""
        return await self.arequest(
            "POST", url, params=params, headers=headers, json=json, data=data, files=files, **kwargs
        )

    async def aput(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an asynchronous PUT request."""
        return await self.arequest("PUT", url, params=params, headers=headers, json=json, data=data, **kwargs)

    async def adelete(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an asynchronous DELETE request."""
        return await self.arequest("DELETE", url, params=params, headers=headers, **kwargs)

    async def apatch(
        self,
        url: str,
        *,
        params: Optional[QueryParams] = None,
        headers: Optional[Headers] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Union[str, bytes]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Make an asynchronous PATCH request."""
        return await self.arequest("PATCH", url, params=params, headers=headers, json=json, data=data, **kwargs)

    def close(self) -> None:
        """Close synchronous client."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    async def aclose(self) -> None:
        """Close asynchronous client."""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self) -> "HTTPClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "HTTPClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.aclose()
