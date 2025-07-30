"""
Authentication middleware for the Cognify SDK.

This module provides middleware for automatically adding authentication
headers to HTTP requests and handling authentication errors.
"""

import logging
from typing import Optional, Dict, Any

import httpx

from .base import AuthProvider, NoAuthProvider
from ..exceptions import (
    CognifyAuthenticationError,
    CognifyRateLimitError,
    CognifyNotFoundError,
    CognifyAPIError,
)


logger = logging.getLogger(__name__)


class AuthMiddleware:
    """
    Authentication middleware for HTTP requests.

    This middleware automatically adds authentication headers to requests
    and handles authentication-related errors in responses.
    """

    def __init__(self, auth_provider: Optional[AuthProvider] = None) -> None:
        """
        Initialize authentication middleware.

        Args:
            auth_provider: Authentication provider to use (optional)
        """
        self.auth_provider = auth_provider or NoAuthProvider(allow_unauthenticated=False)

    def set_auth_provider(self, auth_provider: AuthProvider) -> None:
        """
        Set or update the authentication provider.

        Args:
            auth_provider: New authentication provider
        """
        self.auth_provider = auth_provider
        logger.debug(f"Auth provider updated: {type(auth_provider).__name__}")

    def get_auth_provider(self) -> AuthProvider:
        """Get the current authentication provider."""
        return self.auth_provider

    async def prepare_request(self, request: httpx.Request) -> httpx.Request:
        """
        Prepare HTTP request by adding authentication headers.

        Args:
            request: HTTP request to prepare

        Returns:
            Modified request with authentication headers

        Raises:
            CognifyAuthenticationError: If authentication fails
        """
        try:
            # Refresh authentication if needed
            await self.auth_provider.refresh_if_needed()

            # Get authentication headers
            auth_headers = self.auth_provider.get_auth_headers()

            # Add headers to request
            for key, value in auth_headers.items():
                request.headers[key] = value

            logger.debug(f"Added auth headers to {request.method} {request.url}")
            return request

        except NotImplementedError:
            # Handle case where refresh_if_needed is not implemented
            # (e.g., for JWTAuthProvider without HTTP client access)
            auth_headers = self.auth_provider.get_auth_headers()
            for key, value in auth_headers.items():
                request.headers[key] = value
            return request

        except Exception as e:
            logger.error(f"Failed to prepare authentication: {e}")
            raise CognifyAuthenticationError(f"Authentication preparation failed: {e}")

    def handle_response(self, response: httpx.Response) -> None:
        """
        Handle HTTP response and check for authentication errors.

        Args:
            response: HTTP response to check

        Raises:
            CognifyAuthenticationError: For 401 Unauthorized
            CognifyAuthenticationError: For 403 Forbidden
            CognifyRateLimitError: For 429 Too Many Requests
            CognifyNotFoundError: For 404 Not Found
            CognifyAPIError: For other HTTP errors
        """
        if 200 <= response.status_code < 300:
            return  # Success, no error handling needed

        # Extract error information
        request_id = response.headers.get("x-request-id")

        try:
            error_data = response.json()
            error_message = error_data.get("message", "Unknown error")
            error_code = error_data.get("code")
        except ValueError:
            error_message = response.text or f"HTTP {response.status_code}"
            error_data = {}
            error_code = None

        # Handle specific error types
        if response.status_code == 401:
            # Unauthorized - invalid or expired credentials
            self._handle_unauthorized_error(error_message, error_data, request_id)

        elif response.status_code == 403:
            # Forbidden - insufficient permissions
            self._handle_forbidden_error(error_message, error_data, request_id)

        elif response.status_code == 404:
            # Not Found
            raise CognifyNotFoundError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
            )

        elif response.status_code == 429:
            # Rate Limited
            retry_after = response.headers.get("retry-after")
            raise CognifyRateLimitError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
                retry_after=int(retry_after) if retry_after else None,
            )

        else:
            # Other API errors
            raise CognifyAPIError(
                message=error_message,
                status_code=response.status_code,
                response=error_data,
                request_id=request_id,
            )

    def _handle_unauthorized_error(
        self,
        message: str,
        error_data: Dict[str, Any],
        request_id: Optional[str],
    ) -> None:
        """
        Handle 401 Unauthorized errors.

        Args:
            message: Error message
            error_data: Error response data
            request_id: Request ID for debugging

        Raises:
            CognifyAuthenticationError: Always raised for 401 errors
        """
        # Check if this is a token expiration error
        error_code = error_data.get("code", "").lower()

        if "expired" in error_code or "expired" in message.lower():
            raise CognifyAuthenticationError(
                "Access token has expired. Please refresh your token or re-authenticate.",
                status_code=401,
                response=error_data,
                request_id=request_id,
            )

        elif "invalid" in error_code or "invalid" in message.lower():
            raise CognifyAuthenticationError(
                "Invalid authentication credentials. Please check your API key or token.",
                status_code=401,
                response=error_data,
                request_id=request_id,
            )

        else:
            raise CognifyAuthenticationError(
                f"Authentication failed: {message}",
                status_code=401,
                response=error_data,
                request_id=request_id,
            )

    def _handle_forbidden_error(
        self,
        message: str,
        error_data: Dict[str, Any],
        request_id: Optional[str],
    ) -> None:
        """
        Handle 403 Forbidden errors.

        Args:
            message: Error message
            error_data: Error response data
            request_id: Request ID for debugging

        Raises:
            CognifyAuthenticationError: Always raised for 403 errors
        """
        raise CognifyAuthenticationError(
            f"Insufficient permissions: {message}",
            status_code=403,
            response=error_data,
            request_id=request_id,
        )

    def is_authenticated(self) -> bool:
        """
        Check if current authentication is valid.

        Returns:
            True if authenticated, False otherwise
        """
        return self.auth_provider.is_valid()

    def get_user_id(self) -> Optional[str]:
        """
        Get user ID from current authentication.

        Returns:
            User ID if available, None otherwise
        """
        return self.auth_provider.get_user_id()

    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get information about current authentication.

        Returns:
            Dictionary with authentication information
        """
        return {
            "provider_type": type(self.auth_provider).__name__,
            "is_authenticated": self.is_authenticated(),
            "user_id": self.get_user_id(),
            "provider_info": str(self.auth_provider),
        }

    def __repr__(self) -> str:
        """String representation of middleware."""
        return f"AuthMiddleware(provider={type(self.auth_provider).__name__})"
