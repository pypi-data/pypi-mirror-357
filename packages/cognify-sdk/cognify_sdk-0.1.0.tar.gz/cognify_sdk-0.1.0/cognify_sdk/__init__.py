"""
Cognify Python SDK

A comprehensive Python SDK for the Cognify AI platform, providing easy access to
document management, search, RAG, and conversation capabilities.

Example:
    Basic usage:

    ```python
    from cognify_sdk import CognifyClient

    client = CognifyClient(api_key="your_api_key")
    documents = client.documents.list()
    ```

    Async usage:

    ```python
    import asyncio
    from cognify_sdk import CognifyClient

    async def main():
        async with CognifyClient(api_key="your_api_key") as client:
            documents = await client.documents.alist()

    asyncio.run(main())
    ```
"""

from .client import CognifyClient
from .config import CognifyConfig
from .exceptions import (
    CognifyError,
    CognifyAPIError,
    CognifyAuthenticationError,
    CognifyValidationError,
    CognifyRateLimitError,
    CognifyPermissionError,
    CognifyNotFoundError,
)
from .types import (
    BaseResponse,
    APIResponse,
    Document,
    QueryResult,
    SearchResult,
    Conversation,
    Message,
)

# Collections module exports
from .collections import (
    Collection,
    CollectionVisibility,
    CollaboratorRole,
    Collaborator,
    CollectionStats,
    Organization,
    Workspace,
)

__version__ = "0.1.0"
__author__ = "Cognify Team"
__email__ = "support@cognify.ai"

__all__ = [
    # Core client
    "CognifyClient",
    "CognifyConfig",

    # Exceptions
    "CognifyError",
    "CognifyAPIError",
    "CognifyAuthenticationError",
    "CognifyValidationError",
    "CognifyRateLimitError",
    "CognifyPermissionError",
    "CognifyNotFoundError",

    # Types
    "BaseResponse",
    "APIResponse",
    "Document",
    "QueryResult",
    "SearchResult",
    "Conversation",
    "Message",

    # Collections
    "Collection",
    "CollectionVisibility",
    "CollaboratorRole",
    "Collaborator",
    "CollectionStats",
    "Organization",
    "Workspace",

    # Metadata
    "__version__",
    "__author__",
    "__email__",
]
