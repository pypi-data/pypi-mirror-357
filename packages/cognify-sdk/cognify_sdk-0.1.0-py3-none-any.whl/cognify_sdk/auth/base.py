"""
Base authentication classes for the Cognify SDK.

This module defines the abstract base classes and concrete implementations
for different authentication methods supported by the Cognify API.
"""

try:
    import jwt
except ImportError:
    jwt = None
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any

from ..exceptions import CognifyAuthenticationError, CognifyValidationError


class AuthProvider(ABC):
    """
    Abstract base class for authentication providers.

    This class defines the interface that all authentication providers
    must implement to work with the Cognify SDK.
    """

    @abstractmethod
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for HTTP requests.

        Returns:
            Dictionary of headers to include in requests
        """
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """
        Check if the current authentication is valid.

        Returns:
            True if authentication is valid, False otherwise
        """
        pass

    @abstractmethod
    async def refresh_if_needed(self) -> bool:
        """
        Refresh authentication credentials if needed.

        Returns:
            True if refresh was performed, False if not needed

        Raises:
            CognifyAuthenticationError: If refresh fails
        """
        pass

    @abstractmethod
    def get_user_id(self) -> Optional[str]:
        """
        Get the user ID from the authentication credentials.

        Returns:
            User ID if available, None otherwise
        """
        pass


class APIKeyAuthProvider(AuthProvider):
    """
    Authentication provider for API key-based authentication.

    This provider handles Cognify API keys in the format 'cog_*'.
    """

    def __init__(self, api_key: str) -> None:
        """
        Initialize API key authentication provider.

        Args:
            api_key: Cognify API key starting with 'cog_'

        Raises:
            CognifyValidationError: If API key format is invalid
        """
        if not api_key or not isinstance(api_key, str):
            raise CognifyValidationError("API key must be a non-empty string")

        if not api_key.startswith("cog_"):
            raise CognifyValidationError("API key must start with 'cog_'")

        self.api_key = api_key

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API key."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
        }

    def is_valid(self) -> bool:
        """API keys don't expire, so always valid if present."""
        return bool(self.api_key)

    async def refresh_if_needed(self) -> bool:
        """API keys don't need refresh."""
        return False

    def get_user_id(self) -> Optional[str]:
        """API keys don't contain user information."""
        return None

    def __repr__(self) -> str:
        """String representation with masked API key."""
        masked_key = f"{self.api_key[:8]}***" if len(self.api_key) > 8 else "***"
        return f"APIKeyAuthProvider(api_key={masked_key})"


class JWTAuthProvider(AuthProvider):
    """
    Authentication provider for JWT token-based authentication.

    This provider handles JWT access tokens and refresh tokens,
    including automatic token refresh when needed.
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """
        Initialize JWT authentication provider.

        Args:
            access_token: JWT access token
            refresh_token: JWT refresh token (optional)
            expires_at: Token expiration time (optional, will be parsed from token)

        Raises:
            CognifyValidationError: If token format is invalid
        """
        if not access_token or not isinstance(access_token, str):
            raise CognifyValidationError("Access token must be a non-empty string")

        self.access_token = access_token
        self.refresh_token = refresh_token
        self._expires_at = expires_at
        self._user_id: Optional[str] = None

        # Parse token to extract expiration and user info
        self._parse_token()

    def _parse_token(self) -> None:
        """Parse JWT token to extract expiration and user information."""
        if jwt is None:
            # PyJWT not available, skip parsing
            return

        try:
            # Decode without verification to extract claims
            payload = jwt.decode(
                self.access_token,
                options={"verify_signature": False, "verify_exp": False}
            )

            # Extract expiration time
            if "exp" in payload:
                self._expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)

            # Extract user ID
            self._user_id = payload.get("sub") or payload.get("user_id")

        except (jwt.InvalidTokenError, ValueError, TypeError):
            # If token parsing fails, don't set expiration (assume valid for testing)
            # In production, this might be more strict
            pass

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for JWT token."""
        return {
            "Authorization": f"Bearer {self.access_token}",
        }

    def is_valid(self) -> bool:
        """Check if JWT token is valid and not expired."""
        if not self.access_token:
            return False

        if self._expires_at is None:
            return True  # No expiration info, assume valid

        return datetime.now(timezone.utc) < self._expires_at

    def is_expired(self) -> bool:
        """Check if JWT token is expired."""
        return not self.is_valid()

    def needs_refresh(self, buffer_minutes: int = 5) -> bool:
        """
        Check if token needs refresh (expires within buffer time).

        Args:
            buffer_minutes: Minutes before expiration to trigger refresh

        Returns:
            True if token should be refreshed
        """
        if not self._expires_at:
            return False

        buffer_time = datetime.now(timezone.utc) + timedelta(minutes=buffer_minutes)
        return buffer_time >= self._expires_at

    async def refresh_if_needed(self) -> bool:
        """
        Refresh JWT token if needed.

        Note: This is a placeholder. Actual refresh logic should be
        implemented by the AuthModule that has access to the HTTP client.

        Returns:
            True if refresh was attempted, False if not needed
        """
        if self.needs_refresh() and self.refresh_token:
            # This will be implemented by AuthModule
            raise NotImplementedError(
                "Token refresh must be handled by AuthModule with HTTP client access"
            )
        return False

    def get_user_id(self) -> Optional[str]:
        """Get user ID from JWT token."""
        return self._user_id

    def update_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> None:
        """
        Update JWT tokens.

        Args:
            access_token: New access token
            refresh_token: New refresh token (optional)
            expires_at: New expiration time (optional)
        """
        self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token
        self._expires_at = expires_at
        self._parse_token()

    def get_expires_at(self) -> Optional[datetime]:
        """Get token expiration time."""
        return self._expires_at

    def get_time_until_expiry(self) -> Optional[timedelta]:
        """Get time remaining until token expires."""
        if not self._expires_at:
            return None

        now = datetime.now(timezone.utc)
        if now >= self._expires_at:
            return timedelta(0)

        return self._expires_at - now

    def __repr__(self) -> str:
        """String representation with masked tokens."""
        access_preview = f"{self.access_token[:20]}..." if len(self.access_token) > 20 else "***"
        refresh_preview = "***" if self.refresh_token else None

        return (
            f"JWTAuthProvider("
            f"access_token={access_preview}, "
            f"refresh_token={refresh_preview}, "
            f"expires_at={self._expires_at}, "
            f"user_id={self._user_id}"
            f")"
        )


class NoAuthProvider(AuthProvider):
    """
    No-authentication provider for public endpoints.

    This provider is used when no authentication is required
    or when authentication hasn't been configured yet.
    """

    def __init__(self, allow_unauthenticated: bool = False) -> None:
        """
        Initialize no-auth provider.

        Args:
            allow_unauthenticated: Whether to consider this as valid authentication
        """
        self.allow_unauthenticated = allow_unauthenticated

    def get_auth_headers(self) -> Dict[str, str]:
        """Return empty headers for no authentication."""
        return {}

    def is_valid(self) -> bool:
        """Check if no auth is considered valid."""
        return self.allow_unauthenticated

    async def refresh_if_needed(self) -> bool:
        """No refresh needed for no auth."""
        return False

    def get_user_id(self) -> Optional[str]:
        """No user ID for no auth."""
        return None

    def __repr__(self) -> str:
        """String representation."""
        return f"NoAuthProvider(allow_unauthenticated={self.allow_unauthenticated})"
