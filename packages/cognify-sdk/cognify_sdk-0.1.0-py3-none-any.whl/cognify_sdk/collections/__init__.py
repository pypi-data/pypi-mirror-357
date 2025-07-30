"""
Collections and organizations module for the Cognify SDK.

This module provides functionality for managing collections, organizations,
workspaces, and collaboration features in the Cognify platform.
"""

from .models import (
    Collection,
    CollectionVisibility,
    CollaboratorRole,
    Collaborator,
    CollectionStats,
    CollectionCreateRequest,
    CollectionUpdateRequest,
    CollectionListRequest,
    CollectionSearchRequest,
    CollaboratorAddRequest,
    CollaboratorUpdateRequest,
    Organization,
    Workspace,
)

from .collections_module import CollectionsModule
from .collaboration import CollaborationModule
from .analytics import CollectionAnalytics

__all__ = [
    # Models and types
    "Collection",
    "CollectionVisibility",
    "CollaboratorRole",
    "Collaborator",
    "CollectionStats",
    "CollectionCreateRequest",
    "CollectionUpdateRequest",
    "CollectionListRequest",
    "CollectionSearchRequest",
    "CollaboratorAddRequest",
    "CollaboratorUpdateRequest",
    "Organization",
    "Workspace",
    # Modules
    "CollectionsModule",
    "CollaborationModule",
    "CollectionAnalytics",
]
