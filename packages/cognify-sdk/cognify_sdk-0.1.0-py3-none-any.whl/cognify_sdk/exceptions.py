"""
Exception hierarchy for the Cognify SDK.

This module defines all custom exceptions used throughout the SDK,
providing clear error handling and debugging capabilities.
"""

from typing import Any, Dict, Optional


class CognifyError(Exception):
    """
    Base exception for all Cognify SDK errors.

    This is the root exception that all other Cognify-specific
    exceptions inherit from.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class CognifyAPIError(CognifyError):
    """
    Exception raised for API-related errors.

    This exception is raised when the Cognify API returns an error response,
    including HTTP status codes, error messages, and response data.

    Attributes:
        status_code: HTTP status code from the API response
        response: Full response data from the API
        request_id: Unique request ID for debugging (if available)
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        self.status_code = status_code
        self.response = response or {}
        self.request_id = request_id

        details = {
            "status_code": status_code,
            "response": response,
            "request_id": request_id,
        }
        super().__init__(message, details)

    def __str__(self) -> str:
        parts = [f"HTTP {self.status_code}: {self.message}"]
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class CognifyAuthenticationError(CognifyAPIError):
    """
    Exception raised for authentication-related errors.

    This includes invalid API keys, expired tokens, insufficient permissions,
    and other authentication/authorization failures.
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: int = 401,
        response: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> None:
        super().__init__(message, status_code, response, request_id)


class CognifyValidationError(CognifyError):
    """
    Exception raised for input validation errors.

    This exception is raised when the SDK detects invalid input parameters
    before making an API request, helping to catch errors early.

    Attributes:
        field: The field that failed validation (if applicable)
        value: The invalid value that was provided
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ) -> None:
        self.field = field
        self.value = value

        details = {}
        if field is not None:
            details["field"] = field
        if value is not None:
            details["value"] = value

        super().__init__(message, details)


class CognifyRateLimitError(CognifyAPIError):
    """
    Exception raised when API rate limits are exceeded.

    Attributes:
        retry_after: Number of seconds to wait before retrying (if provided)
        limit: The rate limit that was exceeded
        remaining: Number of requests remaining in the current window
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        response: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
    ) -> None:
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining

        super().__init__(message, status_code, response, request_id)


class CognifyPermissionError(CognifyAPIError):
    """
    Exception raised for permission/authorization errors.

    This exception is raised when the user lacks sufficient permissions
    to perform the requested operation.

    Attributes:
        required_permission: The permission that was required
        resource_type: Type of resource being accessed
        resource_id: ID of the resource being accessed
    """

    def __init__(
        self,
        message: str = "Permission denied",
        status_code: int = 403,
        response: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        required_permission: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> None:
        self.required_permission = required_permission
        self.resource_type = resource_type
        self.resource_id = resource_id

        super().__init__(message, status_code, response, request_id)


class CognifyNotFoundError(CognifyAPIError):
    """
    Exception raised when a requested resource is not found.

    Attributes:
        resource_type: Type of resource that was not found
        resource_id: ID of the resource that was not found
    """

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: int = 404,
        response: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
    ) -> None:
        self.resource_type = resource_type
        self.resource_id = resource_id

        super().__init__(message, status_code, response, request_id)


class CognifyTimeoutError(CognifyError):
    """
    Exception raised when a request times out.

    Attributes:
        timeout: The timeout value that was exceeded
    """

    def __init__(
        self,
        message: str = "Request timed out",
        timeout: Optional[float] = None,
    ) -> None:
        self.timeout = timeout
        details = {"timeout": timeout} if timeout is not None else {}
        super().__init__(message, details)


class CognifyConnectionError(CognifyError):
    """
    Exception raised for connection-related errors.

    This includes network connectivity issues, DNS resolution failures,
    and other low-level connection problems.
    """

    def __init__(self, message: str = "Connection error") -> None:
        super().__init__(message)


class CognifyConfigurationError(CognifyError):
    """
    Exception raised for configuration-related errors.

    This includes missing required configuration values, invalid
    configuration formats, and other setup issues.
    """

    def __init__(self, message: str, config_key: Optional[str] = None) -> None:
        self.config_key = config_key
        details = {"config_key": config_key} if config_key else {}
        super().__init__(message, details)
