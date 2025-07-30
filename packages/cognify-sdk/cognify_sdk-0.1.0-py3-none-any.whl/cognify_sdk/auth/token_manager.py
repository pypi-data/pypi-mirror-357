"""
Token management for JWT authentication in the Cognify SDK.

This module handles JWT token storage, validation, and refresh operations.
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from ..exceptions import CognifyAuthenticationError
from ..types import Headers


logger = logging.getLogger(__name__)


class TokenManager:
    """
    Manages JWT tokens including storage, validation, and refresh.
    
    This class handles the lifecycle of JWT tokens, including automatic
    refresh when tokens are about to expire.
    """
    
    def __init__(self) -> None:
        """Initialize token manager."""
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: Optional[datetime] = None
        self._user_id: Optional[str] = None
        self._refresh_lock = asyncio.Lock()
    
    def set_tokens(
        self,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: Optional[int] = None,
        expires_at: Optional[datetime] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """
        Set JWT tokens with expiration information.
        
        Args:
            access_token: JWT access token
            refresh_token: JWT refresh token (optional)
            expires_in: Token lifetime in seconds (optional)
            expires_at: Absolute expiration time (optional)
            user_id: User ID associated with the token (optional)
        """
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._user_id = user_id
        
        # Calculate expiration time
        if expires_at:
            self._expires_at = expires_at
        elif expires_in:
            self._expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        else:
            # Default to 1 hour if no expiration provided
            self._expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        logger.debug(f"Tokens set, expires at: {self._expires_at}")
    
    def clear_tokens(self) -> None:
        """Clear all stored tokens."""
        self._access_token = None
        self._refresh_token = None
        self._expires_at = None
        self._user_id = None
        logger.debug("Tokens cleared")
    
    def has_tokens(self) -> bool:
        """Check if tokens are available."""
        return self._access_token is not None
    
    def get_access_token(self) -> Optional[str]:
        """Get the current access token."""
        return self._access_token
    
    def get_refresh_token(self) -> Optional[str]:
        """Get the current refresh token."""
        return self._refresh_token
    
    def get_user_id(self) -> Optional[str]:
        """Get the user ID associated with the token."""
        return self._user_id
    
    def get_expires_at(self) -> Optional[datetime]:
        """Get token expiration time."""
        return self._expires_at
    
    def is_expired(self) -> bool:
        """
        Check if the access token is expired.
        
        Returns:
            True if token is expired or missing
        """
        if not self._access_token or not self._expires_at:
            return True
        
        return datetime.now(timezone.utc) >= self._expires_at
    
    def needs_refresh(self, buffer_minutes: int = 5) -> bool:
        """
        Check if token needs refresh (expires within buffer time).
        
        Args:
            buffer_minutes: Minutes before expiration to trigger refresh
            
        Returns:
            True if token should be refreshed
        """
        if not self._access_token or not self._expires_at:
            return False
        
        if not self._refresh_token:
            return False  # Can't refresh without refresh token
        
        buffer_time = datetime.now(timezone.utc) + timedelta(minutes=buffer_minutes)
        return buffer_time >= self._expires_at
    
    def get_time_until_expiry(self) -> Optional[timedelta]:
        """
        Get time remaining until token expires.
        
        Returns:
            Time remaining, or None if no expiration set
        """
        if not self._expires_at:
            return None
        
        now = datetime.now(timezone.utc)
        if now >= self._expires_at:
            return timedelta(0)
        
        return self._expires_at - now
    
    async def refresh_token(self, http_client) -> bool:
        """
        Refresh the access token using the refresh token.
        
        Args:
            http_client: HTTP client instance for making refresh request
            
        Returns:
            True if refresh was successful, False otherwise
            
        Raises:
            CognifyAuthenticationError: If refresh fails
        """
        async with self._refresh_lock:
            # Check if we still need refresh (another thread might have done it)
            if not self.needs_refresh():
                return False
            
            if not self._refresh_token:
                raise CognifyAuthenticationError(
                    "Cannot refresh token: no refresh token available"
                )
            
            logger.debug("Attempting to refresh access token")
            
            try:
                # Make refresh request to Cognify API
                response = await http_client.arequest(
                    "POST",
                    "/auth/refresh",
                    json={"refresh_token": self._refresh_token},
                )
                
                # Extract new tokens from response
                data = response.get("data", {})
                new_access_token = data.get("access_token")
                new_refresh_token = data.get("refresh_token")
                expires_in = data.get("expires_in")
                
                if not new_access_token:
                    raise CognifyAuthenticationError(
                        "Token refresh failed: no access token in response"
                    )
                
                # Update tokens
                self.set_tokens(
                    access_token=new_access_token,
                    refresh_token=new_refresh_token or self._refresh_token,
                    expires_in=expires_in,
                    user_id=self._user_id,
                )
                
                logger.info("Access token refreshed successfully")
                return True
                
            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                # Clear tokens on refresh failure
                self.clear_tokens()
                raise CognifyAuthenticationError(f"Token refresh failed: {e}")
    
    def get_auth_headers(self) -> Headers:
        """
        Get authentication headers for HTTP requests.
        
        Returns:
            Dictionary of headers to include in requests
            
        Raises:
            CognifyAuthenticationError: If no valid token available
        """
        if not self._access_token:
            raise CognifyAuthenticationError("No access token available")
        
        if self.is_expired():
            raise CognifyAuthenticationError("Access token has expired")
        
        return {
            "Authorization": f"Bearer {self._access_token}",
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert token manager state to dictionary.
        
        Returns:
            Dictionary representation of token state
        """
        return {
            "has_access_token": bool(self._access_token),
            "has_refresh_token": bool(self._refresh_token),
            "expires_at": self._expires_at.isoformat() if self._expires_at else None,
            "user_id": self._user_id,
            "is_expired": self.is_expired(),
            "needs_refresh": self.needs_refresh(),
            "time_until_expiry": (
                str(self.get_time_until_expiry()) 
                if self.get_time_until_expiry() else None
            ),
        }
    
    def __repr__(self) -> str:
        """String representation with masked sensitive data."""
        access_preview = "***" if self._access_token else None
        refresh_preview = "***" if self._refresh_token else None
        
        return (
            f"TokenManager("
            f"access_token={access_preview}, "
            f"refresh_token={refresh_preview}, "
            f"expires_at={self._expires_at}, "
            f"user_id={self._user_id}"
            f")"
        )
