"""
Configuration management for the Cognify SDK.

This module handles all configuration options, environment variables,
and settings for the SDK client.
"""

import os
from typing import Optional, Dict, Any
from urllib.parse import urlparse

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import CognifyConfigurationError


class CognifyConfig(BaseSettings):
    """
    Configuration settings for the Cognify SDK.

    This class manages all configuration options for the SDK, including
    API credentials, endpoints, timeouts, and other client settings.

    Configuration can be provided through:
    1. Direct instantiation parameters
    2. Environment variables (prefixed with COGNIFY_)
    3. .env file
    4. Default values

    Example:
        ```python
        # Direct configuration
        config = CognifyConfig(
            api_key="cog_xxx",
            base_url="https://api.cognify.ai",
            timeout=60
        )

        # Environment-based configuration
        # Set COGNIFY_API_KEY=cog_xxx
        config = CognifyConfig()
        ```
    """

    # Authentication
    api_key: Optional[str] = Field(
        default=None,
        description="Cognify API key for authentication"
    )

    # API Configuration
    base_url: str = Field(
        default="https://api.cognify.ai",
        description="Base URL for the Cognify API"
    )

    api_version: str = Field(
        default="v1",
        description="API version to use"
    )

    # Request Configuration
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds",
        gt=0
    )

    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts",
        ge=0
    )

    retry_delay: float = Field(
        default=1.0,
        description="Base delay between retries in seconds",
        ge=0
    )

    # Connection Configuration
    max_connections: int = Field(
        default=100,
        description="Maximum number of HTTP connections",
        gt=0
    )

    max_keepalive_connections: int = Field(
        default=20,
        description="Maximum number of keep-alive connections",
        gt=0
    )

    keepalive_expiry: float = Field(
        default=5.0,
        description="Keep-alive connection expiry time in seconds",
        gt=0
    )

    # Debugging and Logging
    debug: bool = Field(
        default=False,
        description="Enable debug mode with verbose logging"
    )

    log_requests: bool = Field(
        default=False,
        description="Log all HTTP requests and responses"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    # User Agent
    user_agent: Optional[str] = Field(
        default=None,
        description="Custom User-Agent header"
    )

    # Additional Headers
    extra_headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional headers to include in all requests"
    )

    # Proxy Configuration
    proxy: Optional[str] = Field(
        default=None,
        description="HTTP proxy URL"
    )

    proxy_auth: Optional[str] = Field(
        default=None,
        description="Proxy authentication credentials"
    )

    # SSL Configuration
    verify_ssl: bool = Field(
        default=True,
        description="Verify SSL certificates"
    )

    ssl_cert_file: Optional[str] = Field(
        default=None,
        description="Path to SSL certificate file"
    )

    ssl_key_file: Optional[str] = Field(
        default=None,
        description="Path to SSL key file"
    )

    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable client-side rate limiting"
    )

    rate_limit_requests: int = Field(
        default=100,
        description="Maximum requests per rate limit window",
        gt=0
    )

    rate_limit_window: int = Field(
        default=60,
        description="Rate limit window in seconds",
        gt=0
    )

    model_config = SettingsConfigDict(
        env_prefix="COGNIFY_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @validator("base_url")
    def validate_base_url(cls, v: str) -> str:
        """Validate and normalize the base URL."""
        if not v:
            raise CognifyConfigurationError("base_url cannot be empty")

        # Parse URL to validate format
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise CognifyConfigurationError(
                f"Invalid base_url format: {v}. Must include scheme and host."
            )

        # Ensure HTTPS in production
        if parsed.scheme not in ("http", "https"):
            raise CognifyConfigurationError(
                f"Invalid URL scheme: {parsed.scheme}. Must be http or https."
            )

        # Remove trailing slash
        return v.rstrip("/")

    @validator("api_key")
    def validate_api_key(cls, v: Optional[str]) -> Optional[str]:
        """Validate API key format."""
        if v is None:
            return v

        v = v.strip()  # Strip whitespace first

        if not v:
            raise CognifyConfigurationError("api_key cannot be empty")

        # Basic format validation (adjust based on actual Cognify API key format)
        if not v.startswith("cog_"):
            raise CognifyConfigurationError(
                "Invalid API key format. Must start with 'cog_'"
            )

        return v

    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise CognifyConfigurationError(
                f"Invalid log_level: {v}. Must be one of {valid_levels}"
            )
        return v_upper

    @validator("proxy")
    def validate_proxy(cls, v: Optional[str]) -> Optional[str]:
        """Validate proxy URL format."""
        if v is None:
            return v

        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise CognifyConfigurationError(
                f"Invalid proxy URL format: {v}"
            )

        return v

    def get_full_url(self, path: str) -> str:
        """
        Construct full URL for API endpoint.

        Args:
            path: API endpoint path

        Returns:
            Complete URL for the endpoint
        """
        path = path.lstrip("/")

        # Special endpoints that don't need API version prefix
        special_endpoints = {"health", "metrics", "docs", "redoc", "openapi.json"}

        # If path is empty (root) or is a special endpoint, don't add API version
        if not path or path in special_endpoints:
            return f"{self.base_url}/{path}" if path else self.base_url

        # For API endpoints, add the version prefix if not already present
        if not path.startswith("api/"):
            return f"{self.base_url}/api/{self.api_version}/{path}"
        else:
            return f"{self.base_url}/{path}"

    def get_headers(self) -> Dict[str, str]:
        """
        Get default headers for requests.

        Returns:
            Dictionary of headers to include in requests
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Add API key if available
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Add user agent
        if self.user_agent:
            headers["User-Agent"] = self.user_agent
        else:
            headers["User-Agent"] = "cognify-sdk-python/0.1.0"

        # Add extra headers
        headers.update(self.extra_headers)

        return headers

    def is_configured(self) -> bool:
        """
        Check if the configuration has minimum required settings.

        Returns:
            True if configuration is valid for making API requests
        """
        return self.api_key is not None and bool(self.base_url)

    def validate_configuration(self) -> None:
        """
        Validate that the configuration is complete and valid.

        Raises:
            CognifyConfigurationError: If configuration is invalid
        """
        if not self.api_key:
            raise CognifyConfigurationError(
                "API key is required. Set COGNIFY_API_KEY environment variable "
                "or provide api_key parameter."
            )

        if not self.base_url:
            raise CognifyConfigurationError("base_url is required")

        # Validate SSL configuration
        if self.ssl_cert_file and not os.path.exists(self.ssl_cert_file):
            raise CognifyConfigurationError(
                f"SSL certificate file not found: {self.ssl_cert_file}"
            )

        if self.ssl_key_file and not os.path.exists(self.ssl_key_file):
            raise CognifyConfigurationError(
                f"SSL key file not found: {self.ssl_key_file}"
            )

    def __repr__(self) -> str:
        """String representation with sensitive data masked."""
        return (
            f"CognifyConfig("
            f"api_key={'***' if self.api_key else None}, "
            f"base_url='{self.base_url}', "
            f"timeout={self.timeout}, "
            f"debug={self.debug}"
            f")"
        )
