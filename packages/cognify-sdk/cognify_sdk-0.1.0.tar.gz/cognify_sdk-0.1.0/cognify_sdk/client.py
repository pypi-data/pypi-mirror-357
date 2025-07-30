"""
Core client class for the Cognify SDK.

This module contains the main CognifyClient class that serves as the
entry point for all SDK functionality.
"""

import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

from .config import CognifyConfig
from .http_client import HTTPClient
from .exceptions import CognifyConfigurationError

if TYPE_CHECKING:
    from .auth import AuthModule
    from .documents import DocumentsModule
    from .query import QueryModule
    from .rag import RAGModule
    from .conversations import ConversationsModule
    from .collections import CollectionsModule


logger = logging.getLogger(__name__)


class CognifyClient:
    """
    Main client class for the Cognify SDK.

    This class provides the primary interface for interacting with the Cognify API,
    including document management, search, RAG, and conversation capabilities.

    The client supports both synchronous and asynchronous operations, and can be
    used as a context manager for automatic resource cleanup.

    Example:
        Basic usage:

        ```python
        client = CognifyClient(api_key="your_api_key")
        documents = client.documents.list()
        ```

        With custom configuration:

        ```python
        client = CognifyClient(
            api_key="your_api_key",
            base_url="https://custom.cognify.ai",
            timeout=60,
            debug=True
        )
        ```

        As a context manager:

        ```python
        with CognifyClient(api_key="your_api_key") as client:
            documents = client.documents.list()
        ```

        Async usage:

        ```python
        async with CognifyClient(api_key="your_api_key") as client:
            documents = await client.documents.alist()
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_retries: Optional[int] = None,
        debug: Optional[bool] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the Cognify client.

        Args:
            api_key: Cognify API key. If not provided, will look for COGNIFY_API_KEY
                    environment variable.
            base_url: Base URL for the Cognify API. Defaults to https://api.cognify.ai
            timeout: Request timeout in seconds. Defaults to 30.
            max_retries: Maximum number of retry attempts. Defaults to 3.
            debug: Enable debug mode with verbose logging. Defaults to False.
            **kwargs: Additional configuration options passed to CognifyConfig.

        Raises:
            CognifyConfigurationError: If configuration is invalid or incomplete.
        """
        # Build configuration
        config_kwargs = kwargs.copy()
        if api_key is not None:
            config_kwargs["api_key"] = api_key
        if base_url is not None:
            config_kwargs["base_url"] = base_url
        if timeout is not None:
            config_kwargs["timeout"] = timeout
        if max_retries is not None:
            config_kwargs["max_retries"] = max_retries
        if debug is not None:
            config_kwargs["debug"] = debug

        self.config = CognifyConfig(**config_kwargs)

        # Validate configuration
        try:
            self.config.validate_configuration()
        except Exception as e:
            raise CognifyConfigurationError(f"Invalid configuration: {e}")

        # Initialize HTTP client
        self.http = HTTPClient(self.config)
        self.http_client = self.http  # Alias for modules that expect http_client

        # Initialize authentication module
        from .auth import AuthModule
        self._auth = AuthModule(self)

        # Connect auth middleware to HTTP client
        self.http.set_auth_middleware(self._auth.middleware)

        # Initialize documents module
        from .documents import DocumentsModule
        self._documents = DocumentsModule(self)

        # Initialize query module
        from .query import QueryModule
        self._query = QueryModule(self)

        # Initialize RAG module
        from .rag import RAGModule
        self._rag = RAGModule(self)

        # Initialize conversations module
        from .conversations import ConversationsModule
        self._conversations = ConversationsModule(self)

        # Initialize collections module
        from .collections import CollectionsModule
        self._collections = CollectionsModule(self)

        # Initialize other module placeholders (will be implemented in subsequent plans)
        self._organizations = None

        logger.info(f"Initialized Cognify client for {self.config.base_url}")

    @property
    def auth(self) -> "AuthModule":
        """Access authentication module."""
        return self._auth

    @property
    def documents(self) -> "DocumentsModule":
        """Access documents module."""
        return self._documents

    @property
    def query(self) -> "QueryModule":
        """Access query/search module."""
        return self._query

    @property
    def rag(self) -> "RAGModule":
        """Access RAG and agents module."""
        return self._rag

    @property
    def conversations(self) -> "ConversationsModule":
        """Access conversations module."""
        return self._conversations

    @property
    def collections(self) -> "CollectionsModule":
        """Access collections module."""
        return self._collections

    @property
    def organizations(self) -> Any:
        """Access organizations module."""
        if self._organizations is None:
            # Will be implemented in Plan 08: Organizations Module
            raise NotImplementedError("Organizations module not yet implemented")
        return self._organizations

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check against the Cognify API.

        Returns:
            Health check response data

        Raises:
            CognifyAPIError: If health check fails
        """
        return self.http.get("/health")

    async def ahealth_check(self) -> Dict[str, Any]:
        """
        Perform an asynchronous health check against the Cognify API.

        Returns:
            Health check response data

        Raises:
            CognifyAPIError: If health check fails
        """
        return await self.http.aget("/health")

    def get_api_info(self) -> Dict[str, Any]:
        """
        Get API information and version details.

        Returns:
            API information response
        """
        return self.http.get("/")

    async def aget_api_info(self) -> Dict[str, Any]:
        """
        Get API information and version details asynchronously.

        Returns:
            API information response
        """
        return await self.http.aget("/")

    def close(self) -> None:
        """
        Close the client and clean up resources.

        This method should be called when you're done using the client
        to ensure proper cleanup of HTTP connections.
        """
        self.http.close()
        logger.debug("Cognify client closed")

    async def aclose(self) -> None:
        """
        Asynchronously close the client and clean up resources.

        This method should be called when you're done using the client
        to ensure proper cleanup of HTTP connections.
        """
        await self.http.aclose()
        logger.debug("Cognify client closed (async)")

    def __enter__(self) -> "CognifyClient":
        """
        Context manager entry.

        Returns:
            The client instance
        """
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit with automatic cleanup.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        self.close()

    async def __aenter__(self) -> "CognifyClient":
        """
        Async context manager entry.

        Returns:
            The client instance
        """
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Async context manager exit with automatic cleanup.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self.aclose()

    def __repr__(self) -> str:
        """
        String representation of the client.

        Returns:
            Client representation with masked sensitive data
        """
        return (
            f"CognifyClient("
            f"base_url='{self.config.base_url}', "
            f"api_key={'***' if self.config.api_key else None}, "
            f"timeout={self.config.timeout}"
            f")"
        )
