"""
Collections and organizations data models for the Cognify SDK.

This module defines all data models, enums, and request/response types
for collections, organizations, workspaces, and collaboration features.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from ..types import BaseResponse


class CollectionVisibility(str, Enum):
    """Collection visibility levels."""
    PRIVATE = "private"
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    PUBLIC = "public"


class CollaboratorRole(str, Enum):
    """Collaborator role levels."""
    VIEWER = "viewer"
    CONTRIBUTOR = "contributor"
    EDITOR = "editor"
    ADMIN = "admin"


class ProcessingStatus(str, Enum):
    """Collection processing status."""
    UNKNOWN = "unknown"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class EmbeddingStatus(str, Enum):
    """Collection embedding status."""
    UNKNOWN = "unknown"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


# Core Models
class Collection(BaseModel):
    """Collection data model."""
    id: str = Field(..., description="Collection ID", alias="collection_id")
    name: str = Field(..., description="Collection name")
    description: Optional[str] = Field(None, description="Collection description")
    visibility: CollectionVisibility = Field(..., description="Collection visibility")
    owner_id: str = Field(..., description="Owner user ID")
    owner_name: Optional[str] = Field(None, description="Owner display name")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    workspace_id: Optional[str] = Field(None, description="Workspace ID")

    # Statistics
    document_count: int = Field(0, description="Number of documents")
    total_size: int = Field(0, description="Total size in bytes")
    collaborators_count: int = Field(0, description="Number of collaborators")

    # Status
    processing_status: ProcessingStatus = Field(ProcessingStatus.UNKNOWN, description="Processing status")
    embedding_status: EmbeddingStatus = Field(EmbeddingStatus.UNKNOWN, description="Embedding status")
    is_public: bool = Field(False, description="Whether collection is public")
    access_level: Optional[str] = Field(None, description="Current user's access level")

    # Metadata
    tags: Optional[List[str]] = Field(None, description="Collection tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Collection metadata")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")

    class Config:
        populate_by_name = True


class Collaborator(BaseModel):
    """Collaborator data model."""
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    name: str = Field(..., description="User display name")
    role: CollaboratorRole = Field(..., description="Collaborator role")
    permissions: List[str] = Field(default_factory=list, description="Specific permissions")

    # Timestamps
    added_at: datetime = Field(..., description="When collaborator was added")
    added_by: str = Field(..., description="Who added the collaborator")
    last_accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")

    # Activity
    access_count: int = Field(0, description="Number of times accessed")


class CollectionStats(BaseModel):
    """Collection statistics and analytics."""
    collection_id: str = Field(..., description="Collection ID")

    # Document statistics
    document_count: int = Field(0, description="Total number of documents")
    total_size_bytes: int = Field(0, description="Total size in bytes")
    processing_status: Dict[str, int] = Field(default_factory=dict, description="Processing status breakdown")

    # Activity statistics
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    query_count_30d: int = Field(0, description="Query count in last 30 days")
    view_count_30d: int = Field(0, description="View count in last 30 days")

    # Top contributors and documents
    top_contributors: List[Dict[str, Any]] = Field(default_factory=list, description="Top contributors")
    popular_documents: List[Dict[str, Any]] = Field(default_factory=list, description="Popular documents")
    recent_activity: List[Dict[str, Any]] = Field(default_factory=list, description="Recent activity")


class Organization(BaseModel):
    """Organization data model."""
    id: str = Field(..., description="Organization ID")
    name: str = Field(..., description="Organization name")
    slug: str = Field(..., description="Organization slug")
    description: Optional[str] = Field(None, description="Organization description")

    # Plan and status
    plan_type: str = Field("free", description="Organization plan type")
    status: str = Field("active", description="Organization status")

    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict, description="Organization settings")
    billing_email: Optional[str] = Field(None, description="Billing email")

    # Resource limits
    max_workspaces: int = Field(1, description="Maximum workspaces allowed")
    max_users: int = Field(5, description="Maximum users allowed")
    max_documents: int = Field(100, description="Maximum documents allowed")
    max_storage_gb: int = Field(1, description="Maximum storage in GB")

    # Owner information
    owner_id: Optional[str] = Field(None, description="Owner user ID")
    owner_name: Optional[str] = Field(None, description="Owner display name")
    owner_email: Optional[str] = Field(None, description="Owner email")

    # Statistics
    member_count: Optional[int] = Field(None, description="Number of members")
    user_role: Optional[str] = Field(None, description="Current user's role")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class Workspace(BaseModel):
    """Workspace data model."""
    id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Workspace name")
    slug: str = Field(..., description="Workspace slug")
    description: Optional[str] = Field(None, description="Workspace description")
    organization_id: str = Field(..., description="Organization ID")

    # Visibility and settings
    visibility: str = Field("private", description="Workspace visibility")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Workspace settings")

    # Resource limits
    max_collections: int = Field(10, description="Maximum collections allowed")
    max_documents_per_collection: int = Field(1000, description="Maximum documents per collection")

    # Timestamps
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


# Request Models
class CollectionCreateRequest(BaseModel):
    """Request model for creating a collection."""
    name: str = Field(..., min_length=1, max_length=255, description="Collection name")
    description: Optional[str] = Field(None, max_length=1000, description="Collection description")
    visibility: CollectionVisibility = Field(CollectionVisibility.PRIVATE, description="Collection visibility")
    organization_id: Optional[str] = Field(None, description="Organization ID")
    workspace_id: Optional[str] = Field(None, description="Workspace ID")
    tags: Optional[List[str]] = Field(None, description="Collection tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Collection metadata")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Collection name cannot be empty")
        return v.strip()


class CollectionUpdateRequest(BaseModel):
    """Request model for updating a collection."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Collection name")
    description: Optional[str] = Field(None, max_length=1000, description="Collection description")
    visibility: Optional[CollectionVisibility] = Field(None, description="Collection visibility")
    tags: Optional[List[str]] = Field(None, description="Collection tags")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Collection metadata")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Collection name cannot be empty")
        return v.strip() if v else v


class CollectionListRequest(BaseModel):
    """Request model for listing collections."""
    workspace_id: Optional[str] = Field(None, description="Filter by workspace ID")
    organization_id: Optional[str] = Field(None, description="Filter by organization ID")
    visibility: Optional[CollectionVisibility] = Field(None, description="Filter by visibility")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        if v < 1 or v > 100:
            raise ValueError("Limit must be between 1 and 100")
        return v

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v


class CollectionSearchRequest(BaseModel):
    """Request model for searching collections."""
    query: str = Field(..., min_length=1, description="Search query")
    workspace_id: Optional[str] = Field(None, description="Filter by workspace ID")
    organization_id: Optional[str] = Field(None, description="Filter by organization ID")
    visibility: Optional[CollectionVisibility] = Field(None, description="Filter by visibility")
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Number of results to skip")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Search query cannot be empty")
        return v.strip()


class CollaboratorAddRequest(BaseModel):
    """Request model for adding a collaborator."""
    email: str = Field(..., description="Collaborator email")
    role: CollaboratorRole = Field(CollaboratorRole.VIEWER, description="Collaborator role")
    permissions: Optional[List[str]] = Field(None, description="Specific permissions")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        # Basic email validation
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v.strip().lower()


class CollaboratorUpdateRequest(BaseModel):
    """Request model for updating a collaborator."""
    role: Optional[CollaboratorRole] = Field(None, description="New collaborator role")
    permissions: Optional[List[str]] = Field(None, description="New permissions")


# Response Models
class CollectionListResponse(BaseResponse):
    """Response model for collection list."""
    collections: List[Collection] = Field(..., description="List of collections")
    total: int = Field(..., description="Total number of collections")
    limit: int = Field(..., description="Limit used")
    offset: int = Field(..., description="Offset used")


class CollaboratorListResponse(BaseResponse):
    """Response model for collaborator list."""
    collaborators: List[Collaborator] = Field(..., description="List of collaborators")
    total: int = Field(..., description="Total number of collaborators")


class CollectionStatsResponse(BaseResponse):
    """Response model for collection statistics."""
    stats: CollectionStats = Field(..., description="Collection statistics")


class CollectionStatusResponse(BaseResponse):
    """Response model for collection status."""
    collection_id: str = Field(..., description="Collection ID")
    processing_status: ProcessingStatus = Field(..., description="Processing status")
    embedding_status: EmbeddingStatus = Field(..., description="Embedding status")
    document_count: int = Field(..., description="Number of documents")
    processed_documents: int = Field(..., description="Number of processed documents")
    failed_documents: int = Field(..., description="Number of failed documents")
    last_updated: datetime = Field(..., description="Last status update")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional status details")
