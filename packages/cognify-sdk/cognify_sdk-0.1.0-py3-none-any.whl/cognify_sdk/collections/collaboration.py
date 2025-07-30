"""
Collaboration module for the Cognify SDK.

This module provides functionality for managing collaborators and permissions
in collections, including adding, updating, and removing team members.
"""

import asyncio
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode

from ..exceptions import (
    CognifyAPIError,
    CognifyValidationError,
    CognifyNotFoundError,
    CognifyPermissionError,
)
from .models import (
    Collaborator,
    CollaboratorRole,
    CollaboratorAddRequest,
    CollaboratorUpdateRequest,
    CollaboratorListResponse,
)


class CollaborationModule:
    """
    Collaboration management module.

    Provides functionality for managing collaborators and permissions
    in collections within the Cognify platform.
    """

    def __init__(self, collections_module: 'CollectionsModule'):
        """Initialize the collaboration module."""
        self.collections = collections_module
        self.client = collections_module.client
        self._base_url = "/api/v1/collections"

    async def get_collaborators(self, collection_id: str) -> List[Collaborator]:
        """
        Get list of collaborators for a collection.

        Args:
            collection_id: Collection ID

        Returns:
            List of collaborators

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Make API request
            response = await self.client.http.arequest(
                "GET", f"/collections/{collection_id}/collaborators"
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot access collaborators for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to get collaborators: {response.get('message', 'Unknown error')}", status_code=400
                )

            data = response.get("data", {})
            collaborators_data = data.get("collaborators", [])
            return [Collaborator(**collab) for collab in collaborators_data]

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting collaborators: {str(e)}", status_code=500)

    async def add_collaborator(
        self,
        collection_id: str,
        email: str,
        role: CollaboratorRole = CollaboratorRole.VIEWER,
        permissions: Optional[List[str]] = None,
    ) -> Collaborator:
        """
        Add a collaborator to a collection.

        Args:
            collection_id: Collection ID
            email: Collaborator email address
            role: Collaborator role (default: VIEWER)
            permissions: Optional specific permissions

        Returns:
            Added collaborator information

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
            request = CollaboratorAddRequest(
                email=email,
                role=role,
                permissions=permissions,
            )

            # Make API request
            response = await self.client.http.arequest(
                "POST",
                f"/collections/{collection_id}/collaborators",
                json=request.model_dump(exclude_none=True),
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot add collaborator to collection {collection_id}"
                    )
                elif error.get("code") == "VALIDATION_ERROR":
                    raise CognifyValidationError(
                        f"Invalid collaborator data: {response.get('message', 'Unknown validation error')}"
                    )
                raise CognifyAPIError(
                    f"Failed to add collaborator: {response.get('message', 'Unknown error')}", status_code=400
                )

            collaborator_data = response.get("data", {})
            return Collaborator(**collaborator_data)

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error adding collaborator: {str(e)}", status_code=500)

    async def update_collaborator(
        self,
        collection_id: str,
        user_id: str,
        role: Optional[CollaboratorRole] = None,
        permissions: Optional[List[str]] = None,
    ) -> Collaborator:
        """
        Update collaborator role and permissions.

        Args:
            collection_id: Collection ID
            user_id: User ID of the collaborator
            role: New collaborator role
            permissions: New specific permissions

        Returns:
            Updated collaborator information

        Raises:
            CognifyNotFoundError: If collection or collaborator not found
            CognifyPermissionError: If user lacks permission
            CognifyValidationError: If request data is invalid
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")
            if not user_id or not user_id.strip():
                raise CognifyValidationError("User ID cannot be empty")

            # Create request model
            request = CollaboratorUpdateRequest(
                role=role,
                permissions=permissions,
            )

            # Only include non-None values
            update_data = request.model_dump(exclude_none=True)
            if not update_data:
                raise CognifyValidationError("At least one field must be provided for update")

            # Make API request
            response = await self.client.http.arequest(
                "PUT",
                f"/collections/{collection_id}/collaborators/{user_id}",
                json=update_data,
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(
                        f"Collection or collaborator not found: {collection_id}/{user_id}"
                    )
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot update collaborator in collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to update collaborator: {response.get('message', 'Unknown error')}", status_code=400
                )

            collaborator_data = response.get("data", {})
            return Collaborator(**collaborator_data)

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error updating collaborator: {str(e)}", status_code=500)

    async def remove_collaborator(self, collection_id: str, user_id: str) -> bool:
        """
        Remove a collaborator from a collection.

        Args:
            collection_id: Collection ID
            user_id: User ID of the collaborator to remove

        Returns:
            True if removal was successful

        Raises:
            CognifyNotFoundError: If collection or collaborator not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")
            if not user_id or not user_id.strip():
                raise CognifyValidationError("User ID cannot be empty")

            # Make API request
            response = await self.client.http.arequest(
                "DELETE", f"/collections/{collection_id}/collaborators/{user_id}"
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(
                        f"Collection or collaborator not found: {collection_id}/{user_id}"
                    )
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot remove collaborator from collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to remove collaborator: {response.get('message', 'Unknown error')}", status_code=400
                )

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
            raise CognifyAPIError(f"Unexpected error removing collaborator: {str(e)}", status_code=500)

    async def get_user_permissions(
        self,
        collection_id: str,
        user_id: Optional[str] = None,
    ) -> List[str]:
        """
        Get user permissions for a collection.

        Args:
            collection_id: Collection ID
            user_id: User ID (if None, uses current user)

        Returns:
            List of permissions for the user

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Build URL
            url = f"/collections/{collection_id}/permissions"
            if user_id:
                url += f"?user_id={user_id}"

            # Make API request
            response = await self.client.http.arequest("GET", url)

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot access permissions for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to get user permissions: {response.get('message', 'Unknown error')}", status_code=400
                )

            data = response.get("data", {})
            return data.get("permissions", [])

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting user permissions: {str(e)}", status_code=500)

    async def check_user_access(
        self,
        collection_id: str,
        required_permission: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Check if user has specific permission for a collection.

        Args:
            collection_id: Collection ID
            required_permission: Permission to check
            user_id: User ID (if None, uses current user)

        Returns:
            True if user has the permission

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyAPIError: If API request fails
        """
        try:
            permissions = await self.get_user_permissions(collection_id, user_id)
            return required_permission in permissions or "admin" in permissions

        except CognifyNotFoundError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error checking user access: {str(e)}", status_code=500)

    # Sync versions of async methods
    def get_collaborators_sync(self, *args, **kwargs) -> List[Collaborator]:
        """Synchronous version of get_collaborators()."""
        return asyncio.run(self.get_collaborators(*args, **kwargs))

    def add_collaborator_sync(self, *args, **kwargs) -> Collaborator:
        """Synchronous version of add_collaborator()."""
        return asyncio.run(self.add_collaborator(*args, **kwargs))

    def update_collaborator_sync(self, *args, **kwargs) -> Collaborator:
        """Synchronous version of update_collaborator()."""
        return asyncio.run(self.update_collaborator(*args, **kwargs))

    def remove_collaborator_sync(self, *args, **kwargs) -> bool:
        """Synchronous version of remove_collaborator()."""
        return asyncio.run(self.remove_collaborator(*args, **kwargs))

    def get_user_permissions_sync(self, *args, **kwargs) -> List[str]:
        """Synchronous version of get_user_permissions()."""
        return asyncio.run(self.get_user_permissions(*args, **kwargs))

    def check_user_access_sync(self, *args, **kwargs) -> bool:
        """Synchronous version of check_user_access()."""
        return asyncio.run(self.check_user_access(*args, **kwargs))
