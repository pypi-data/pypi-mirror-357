"""
Collections module for the Cognify SDK.

This module provides functionality for managing collections including
CRUD operations, search, and basic collection management.
"""

import asyncio
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlencode

from ..exceptions import (
    CognifyAPIError,
    CognifyValidationError,
    CognifyNotFoundError,
    CognifyPermissionError,
)
from ..types import APIResponse
from .models import (
    Collection,
    CollectionVisibility,
    CollectionCreateRequest,
    CollectionUpdateRequest,
    CollectionListRequest,
    CollectionSearchRequest,
    CollectionListResponse,
    CollectionStatusResponse,
)


class CollectionsModule:
    """
    Collections management module.

    Provides functionality for creating, managing, and organizing collections
    in the Cognify platform with support for multi-tenant architecture.
    """

    def __init__(self, client: 'CognifyClient'):
        """Initialize the collections module."""
        self.client = client
        self._base_url = "/api/v1/collections"

    async def create(
        self,
        name: str,
        description: Optional[str] = None,
        visibility: CollectionVisibility = CollectionVisibility.PRIVATE,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Collection:
        """
        Create a new collection.

        Args:
            name: Collection name
            description: Optional collection description
            visibility: Collection visibility level
            organization_id: Organization ID (for organization collections)
            workspace_id: Workspace ID (for workspace collections)
            tags: Optional list of tags
            metadata: Optional metadata dictionary

        Returns:
            Created collection

        Raises:
            CognifyValidationError: If request data is invalid
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            # Create request model
            request = CollectionCreateRequest(
                name=name,
                description=description,
                visibility=visibility,
                organization_id=organization_id,
                workspace_id=workspace_id,
                tags=tags,
                metadata=metadata,
            )

            # Make API request
            response = await self.client.http.arequest(
                'POST',
                '/collections/',
                json=request.dict(exclude_none=True),
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: {response.get('message', 'Cannot create collection')}"
                    )
                raise CognifyAPIError(f"Failed to create collection: {response.get('message', 'Unknown error')}", status_code=400)

            collection_data = response.get("data", {})
            return Collection(**collection_data)

        except CognifyValidationError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error creating collection: {str(e)}", status_code=500)

    async def list(
        self,
        workspace_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        visibility: Optional[CollectionVisibility] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> CollectionListResponse:
        """
        List collections with optional filtering.

        Args:
            workspace_id: Filter by workspace ID
            organization_id: Filter by organization ID
            visibility: Filter by visibility level
            limit: Maximum number of results (1-100)
            offset: Number of results to skip

        Returns:
            Collection list response with pagination

        Raises:
            CognifyValidationError: If request parameters are invalid
            CognifyAPIError: If API request fails
        """
        try:
            # Create request model for validation
            request = CollectionListRequest(
                workspace_id=workspace_id,
                organization_id=organization_id,
                visibility=visibility,
                limit=limit,
                offset=offset,
            )

            # Build query parameters
            params = {}
            if workspace_id:
                params["workspace_id"] = workspace_id
            if organization_id:
                params["organization_id"] = organization_id
            if visibility:
                params["visibility"] = visibility.value
            params["limit"] = limit
            params["offset"] = offset

            # Make API request
            url = f"{self._base_url}/"
            if params:
                url += f"?{urlencode(params)}"

            response = await self.client.http.arequest("GET", url)

            # Parse response
            if not response.get("success", False):
                raise CognifyAPIError(f"Failed to list collections: {response.get('message', 'Unknown error')}", status_code=400)

            data = response.get("data", {})
            collections_data = data.get("collections", [])
            collections = [Collection(**col) for col in collections_data]

            return CollectionListResponse(
                success=True,
                collections=collections,
                total=data.get("total", len(collections)),
                limit=limit,
                offset=offset,
                message="Collections retrieved successfully",
            )

        except CognifyValidationError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error listing collections: {str(e)}", status_code=500)

    async def get(self, collection_id: str) -> Collection:
        """
        Get a collection by ID.

        Args:
            collection_id: Collection ID

        Returns:
            Collection details

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Make API request
            response = await self.client.http.arequest("GET", f"/collections/{collection_id}")

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(f"Permission denied: Cannot access collection {collection_id}")
                raise CognifyAPIError(f"Failed to get collection: {response.get('message', 'Unknown error')}", status_code=400)

            collection_data = response.get("data", {})
            return Collection(**collection_data)

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting collection: {str(e)}", status_code=500)

    async def update(
        self,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        visibility: Optional[CollectionVisibility] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Collection:
        """
        Update a collection.

        Args:
            collection_id: Collection ID
            name: New collection name
            description: New collection description
            visibility: New visibility level
            tags: New tags list
            metadata: New metadata dictionary

        Returns:
            Updated collection

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyValidationError: If request data is invalid
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Create request model
            request = CollectionUpdateRequest(
                name=name,
                description=description,
                visibility=visibility,
                tags=tags,
                metadata=metadata,
            )

            # Only include non-None values
            update_data = request.model_dump(exclude_none=True)
            if not update_data:
                raise CognifyValidationError("At least one field must be provided for update")

            # Make API request
            response = await self.client.http.arequest(
                "PUT",
                f"/collections/{collection_id}",
                json=update_data,
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(f"Permission denied: Cannot update collection {collection_id}")
                raise CognifyAPIError(f"Failed to update collection: {response.get('message', 'Unknown error')}", status_code=400)

            collection_data = response.get("data", {})
            return Collection(**collection_data)

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error updating collection: {str(e)}", status_code=500)

    async def delete(self, collection_id: str) -> bool:
        """
        Delete a collection (soft delete).

        Args:
            collection_id: Collection ID

        Returns:
            True if deletion was successful

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Make API request
            response = await self.client.http.arequest("DELETE", f"/collections/{collection_id}")

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(f"Permission denied: Cannot delete collection {collection_id}")
                raise CognifyAPIError(f"Failed to delete collection: {response.get('message', 'Unknown error')}", status_code=400)

            return True

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error deleting collection: {str(e)}", status_code=500)

    async def search(
        self,
        query: str,
        workspace_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        visibility: Optional[CollectionVisibility] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> CollectionListResponse:
        """
        Search collections by name or description.

        Args:
            query: Search query
            workspace_id: Filter by workspace ID
            organization_id: Filter by organization ID
            visibility: Filter by visibility level
            limit: Maximum number of results (1-100)
            offset: Number of results to skip

        Returns:
            Collection search results with pagination

        Raises:
            CognifyValidationError: If request parameters are invalid
            CognifyAPIError: If API request fails
        """
        try:
            # Create request model for validation
            request = CollectionSearchRequest(
                query=query,
                workspace_id=workspace_id,
                organization_id=organization_id,
                visibility=visibility,
                limit=limit,
                offset=offset,
            )

            # Build query parameters
            params = {
                "query": query,
                "limit": limit,
                "offset": offset,
            }
            if workspace_id:
                params["workspace_id"] = workspace_id
            if organization_id:
                params["organization_id"] = organization_id
            if visibility:
                params["visibility"] = visibility.value

            # Make API request
            url = f"{self._base_url}/search?{urlencode(params)}"
            response = await self.client.http.arequest("GET", url)

            # Parse response
            if not response.get("success", False):
                raise CognifyAPIError(f"Failed to search collections: {response.get('message', 'Unknown error')}", status_code=400)

            data = response.get("data", {})
            collections_data = data.get("collections", [])
            collections = [Collection(**col) for col in collections_data]

            return CollectionListResponse(
                success=True,
                collections=collections,
                total=data.get("total", len(collections)),
                limit=limit,
                offset=offset,
                message="Collection search completed successfully",
            )

        except CognifyValidationError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error searching collections: {str(e)}", status_code=500)

    async def get_status(self, collection_id: str) -> CollectionStatusResponse:
        """
        Get collection processing status and health information.

        Args:
            collection_id: Collection ID

        Returns:
            Collection status information

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Make API request
            response = await self.client.http.arequest("GET", f"/collections/{collection_id}/status")

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(f"Permission denied: Cannot access collection status {collection_id}")
                raise CognifyAPIError(f"Failed to get collection status: {response.get('message', 'Unknown error')}", status_code=400)

            status_data = response.get("data", {})
            return CollectionStatusResponse(
                success=True,
                message="Collection status retrieved successfully",
                **status_data
            )

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting collection status: {str(e)}", status_code=500)

    # Sync versions of async methods
    def create_sync(
        self,
        name: str,
        description: Optional[str] = None,
        visibility: CollectionVisibility = CollectionVisibility.PRIVATE,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Collection:
        """
        Create a new collection synchronously.

        Args:
            name: Collection name
            description: Optional collection description
            visibility: Collection visibility level
            organization_id: Organization ID (for organization collections)
            workspace_id: Workspace ID (for workspace collections)
            tags: Optional list of tags
            metadata: Optional metadata dictionary

        Returns:
            Created collection
        """
        try:
            # Create request model
            request = CollectionCreateRequest(
                name=name,
                description=description,
                visibility=visibility,
                organization_id=organization_id,
                workspace_id=workspace_id,
                tags=tags,
                metadata=metadata,
            )

            # Make API request
            response = self.client.http.post(
                '/collections/',
                json=request.dict(exclude_none=True),
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: {response.get('message', 'Cannot create collection')}"
                    )
                raise CognifyAPIError(f"Failed to create collection: {response.get('message', 'Unknown error')}", status_code=400)

            collection_data = response.get("data", {})
            return Collection(**collection_data)

        except CognifyValidationError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error creating collection: {str(e)}", status_code=500)

    def list_sync(self, *args, **kwargs) -> CollectionListResponse:
        """Synchronous version of list()."""
        return asyncio.run(self.list(*args, **kwargs))

    def get_sync(self, *args, **kwargs) -> Collection:
        """Synchronous version of get()."""
        return asyncio.run(self.get(*args, **kwargs))

    def update_sync(self, *args, **kwargs) -> Collection:
        """Synchronous version of update()."""
        return asyncio.run(self.update(*args, **kwargs))

    def delete_sync(self, *args, **kwargs) -> bool:
        """Synchronous version of delete()."""
        return asyncio.run(self.delete(*args, **kwargs))

    def search_sync(self, *args, **kwargs) -> CollectionListResponse:
        """Synchronous version of search()."""
        return asyncio.run(self.search(*args, **kwargs))

    def get_status_sync(self, *args, **kwargs) -> CollectionStatusResponse:
        """Synchronous version of get_status()."""
        return asyncio.run(self.get_status(*args, **kwargs))
