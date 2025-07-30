"""
Main authentication module for the Cognify SDK.

This module provides the primary interface for authentication operations
including login, logout, token management, and user profile access.
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

from .base import AuthProvider, APIKeyAuthProvider, JWTAuthProvider, NoAuthProvider
from .token_manager import TokenManager
from .middleware import AuthMiddleware
from ..exceptions import CognifyAuthenticationError, CognifyValidationError
from ..types import APIResponse

if TYPE_CHECKING:
    from ..client import CognifyClient


logger = logging.getLogger(__name__)


class AuthModule:
    """
    Main authentication module for the Cognify SDK.

    This class provides methods for authentication, token management,
    and user profile operations.
    """

    def __init__(self, client: "CognifyClient") -> None:
        """
        Initialize authentication module.

        Args:
            client: Cognify client instance
        """
        self.client = client
        self.token_manager = TokenManager()
        self.middleware = AuthMiddleware()

        # Initialize with API key if provided in config
        if client.config.api_key:
            self.set_api_key(client.config.api_key)

    def set_api_key(self, api_key: str) -> None:
        """
        Set API key for authentication.

        Args:
            api_key: Cognify API key starting with 'cog_'

        Raises:
            CognifyValidationError: If API key format is invalid
        """
        try:
            provider = APIKeyAuthProvider(api_key)
            self.middleware.set_auth_provider(provider)
            logger.info("API key authentication configured")
        except Exception as e:
            raise CognifyValidationError(f"Invalid API key: {e}")

    def set_jwt_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Set JWT tokens for authentication.

        Args:
            access_token: JWT access token
            refresh_token: JWT refresh token (optional)
            expires_in: Token lifetime in seconds (optional)
            user_id: User ID associated with the token (optional)

        Raises:
            CognifyValidationError: If token format is invalid
        """
        try:
            # Store tokens in token manager
            self.token_manager.set_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                user_id=user_id,
            )

            # Create JWT auth provider
            provider = JWTAuthProvider(
                access_token=access_token,
                refresh_token=refresh_token,
            )

            self.middleware.set_auth_provider(provider)
            logger.info("JWT authentication configured")

        except Exception as e:
            raise CognifyValidationError(f"Invalid JWT tokens: {e}")

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login with email and password to get JWT tokens.

        Args:
            email: User email address
            password: User password

        Returns:
            Login response with tokens and user information

        Raises:
            CognifyAuthenticationError: If login fails
            CognifyValidationError: If credentials are invalid
        """
        if not email or not password:
            raise CognifyValidationError("Email and password are required")

        try:
            # Make login request
            response = await self.client.http.arequest(
                "POST",
                "/auth/login",
                json={
                    "email": email,
                    "password": password,
                }
            )

            # Extract tokens and user info from response
            data = response.get("data", {})
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            expires_in = data.get("expires_in")
            user_info = data.get("user", {})

            if not access_token:
                raise CognifyAuthenticationError("Login failed: no access token received")

            # Set up JWT authentication
            self.set_jwt_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                user_id=user_info.get("id"),
            )

            logger.info(f"Successfully logged in as {email}")
            return response

        except CognifyAuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login failed: {e}")
            raise CognifyAuthenticationError(f"Login failed: {e}")

    async def logout(self) -> None:
        """
        Logout and invalidate current session.

        This method will attempt to invalidate the refresh token on the server
        and clear all local authentication state.
        """
        try:
            # If we have a refresh token, try to invalidate it on the server
            if self.token_manager.get_refresh_token():
                try:
                    await self.client.http.arequest(
                        "POST",
                        "/auth/logout",
                        json={
                            "refresh_token": self.token_manager.get_refresh_token()
                        }
                    )
                except Exception as e:
                    logger.warning(f"Server logout failed: {e}")

            # Clear local authentication state
            self.token_manager.clear_tokens()
            self.middleware.set_auth_provider(NoAuthProvider(allow_unauthenticated=False))

            logger.info("Successfully logged out")

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            # Still clear local state even if server logout fails
            self.token_manager.clear_tokens()
            self.middleware.set_auth_provider(NoAuthProvider(allow_unauthenticated=False))

    async def refresh_token(self) -> bool:
        """
        Manually refresh the access token.

        Returns:
            True if refresh was successful, False otherwise

        Raises:
            CognifyAuthenticationError: If refresh fails
        """
        try:
            success = await self.token_manager.refresh_token(self.client.http)

            if success:
                # Update the auth provider with new token
                new_access_token = self.token_manager.get_access_token()
                new_refresh_token = self.token_manager.get_refresh_token()

                if new_access_token:
                    provider = JWTAuthProvider(
                        access_token=new_access_token,
                        refresh_token=new_refresh_token,
                    )
                    self.middleware.set_auth_provider(provider)

            return success

        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise CognifyAuthenticationError(f"Token refresh failed: {e}")

    async def get_current_user(self) -> Dict[str, Any]:
        """
        Get current authenticated user information.

        Returns:
            User profile information

        Raises:
            CognifyAuthenticationError: If not authenticated or request fails
        """
        if not self.is_authenticated():
            raise CognifyAuthenticationError("Not authenticated")

        try:
            response = await self.client.http.arequest("GET", "/auth/me")
            return response.get("data", {})

        except Exception as e:
            logger.error(f"Failed to get current user: {e}")
            raise CognifyAuthenticationError(f"Failed to get user info: {e}")

    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.

        Returns:
            True if authenticated with valid credentials
        """
        return self.middleware.is_authenticated()

    def get_user_id(self) -> Optional[str]:
        """
        Get current user ID.

        Returns:
            User ID if available, None otherwise
        """
        return self.middleware.get_user_id()

    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get detailed authentication information.

        Returns:
            Dictionary with authentication details
        """
        auth_info = self.middleware.get_auth_info()

        # Add token manager info if using JWT
        if isinstance(self.middleware.get_auth_provider(), JWTAuthProvider):
            auth_info.update({
                "token_info": self.token_manager.to_dict()
            })

        return auth_info

    def clear_authentication(self) -> None:
        """
        Clear all authentication state.

        This method removes all stored credentials and resets
        the authentication state to unauthenticated.
        """
        self.token_manager.clear_tokens()
        self.middleware.set_auth_provider(NoAuthProvider(allow_unauthenticated=False))
        logger.info("Authentication state cleared")

    def __repr__(self) -> str:
        """String representation of auth module."""
        provider_type = type(self.middleware.get_auth_provider()).__name__
        is_auth = self.is_authenticated()
        user_id = self.get_user_id()

        return (
            f"AuthModule("
            f"provider={provider_type}, "
            f"authenticated={is_auth}, "
            f"user_id={user_id}"
            f")"
        )
