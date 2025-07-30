"""
Type definitions for the Cognify SDK.

This module contains all the type definitions, data models, and type aliases
used throughout the SDK for type safety and documentation.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from typing_extensions import TypedDict, Literal

from pydantic import BaseModel, Field


# Basic type aliases
JSONValue = Union[str, int, float, bool, None, Dict[str, Any], List[Any]]
Headers = Dict[str, str]
QueryParams = Dict[str, Union[str, int, float, bool]]


class BaseResponse(BaseModel):
    """
    Base response model for all API responses.
    """

    success: bool = Field(description="Whether the request was successful")
    message: Optional[str] = Field(default=None, description="Response message")
    request_id: Optional[str] = Field(default=None, description="Unique request identifier")
    timestamp: Optional[datetime] = Field(default=None, description="Response timestamp")


class APIResponse(BaseResponse):
    """
    Standard API response wrapper.

    All Cognify API responses follow this structure for consistency.
    """

    data: Optional[Any] = Field(default=None, description="Response data")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class PaginatedResponse(BaseModel):
    """
    Paginated response wrapper for list endpoints.
    """

    items: List[Any] = Field(description="List of items in current page")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    per_page: int = Field(description="Items per page")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_prev: bool = Field(description="Whether there are previous pages")


class DocumentStatus(str, Enum):
    """Document processing status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class DocumentType(str, Enum):
    """Supported document types."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    HTML = "html"
    CSV = "csv"
    JSON = "json"


class Document(BaseModel):
    """
    Document model representing a document in the Cognify system.
    """

    id: str = Field(description="Unique document identifier")
    name: str = Field(description="Document name")
    type: DocumentType = Field(description="Document type")
    status: DocumentStatus = Field(description="Processing status")
    size: int = Field(description="Document size in bytes")
    content: Optional[str] = Field(default=None, description="Document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    processed_at: Optional[datetime] = Field(default=None, description="Processing completion timestamp")
    collection_id: Optional[str] = Field(default=None, description="Collection ID if part of collection")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChunkingStrategy(str, Enum):
    """Document chunking strategies."""

    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"


class DocumentChunk(BaseModel):
    """
    Document chunk model for processed document segments.
    """

    id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Parent document ID")
    content: str = Field(description="Chunk content")
    position: int = Field(description="Position in document")
    size: int = Field(description="Chunk size in characters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding")


class QueryType(str, Enum):
    """Query types for search operations."""

    SEMANTIC = "semantic"
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    SIMILARITY = "similarity"


class SearchResult(BaseModel):
    """
    Search result model.
    """

    id: str = Field(description="Result identifier")
    document_id: str = Field(description="Source document ID")
    chunk_id: Optional[str] = Field(default=None, description="Source chunk ID")
    content: str = Field(description="Matching content")
    score: float = Field(description="Relevance score")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Result metadata")
    highlights: List[str] = Field(default_factory=list, description="Highlighted text snippets")


class QueryResult(BaseModel):
    """
    Query result wrapper containing search results and metadata.
    """

    query: str = Field(description="Original query")
    results: List[SearchResult] = Field(description="Search results")
    total: int = Field(description="Total number of results")
    took: float = Field(description="Query execution time in seconds")
    query_type: QueryType = Field(description="Type of query performed")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Applied filters")


class MessageRole(str, Enum):
    """Message roles in conversations."""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Message(BaseModel):
    """
    Conversation message model.
    """

    id: str = Field(description="Unique message identifier")
    role: MessageRole = Field(description="Message role")
    content: str = Field(description="Message content")
    timestamp: datetime = Field(description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationStatus(str, Enum):
    """Conversation status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class Conversation(BaseModel):
    """
    Conversation model for chat interactions.
    """

    id: str = Field(description="Unique conversation identifier")
    title: Optional[str] = Field(default=None, description="Conversation title")
    status: ConversationStatus = Field(description="Conversation status")
    messages: List[Message] = Field(default_factory=list, description="Conversation messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Conversation metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Collection(BaseModel):
    """
    Document collection model.
    """

    id: str = Field(description="Unique collection identifier")
    name: str = Field(description="Collection name")
    description: Optional[str] = Field(default=None, description="Collection description")
    document_count: int = Field(default=0, description="Number of documents in collection")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Collection metadata")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Organization(BaseModel):
    """
    Organization model for multi-tenant support.
    """

    id: str = Field(description="Unique organization identifier")
    name: str = Field(description="Organization name")
    description: Optional[str] = Field(default=None, description="Organization description")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Organization settings")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Request/Response type definitions
class UploadDocumentRequest(TypedDict, total=False):
    """Request model for document upload."""

    name: str
    content: Optional[str]
    file: Optional[bytes]
    metadata: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    collection_id: Optional[str]
    chunking_strategy: Optional[ChunkingStrategy]


class SearchRequest(TypedDict, total=False):
    """Request model for search operations."""

    query: str
    query_type: Optional[QueryType]
    limit: Optional[int]
    offset: Optional[int]
    filters: Optional[Dict[str, Any]]
    include_content: Optional[bool]
    include_metadata: Optional[bool]


class CreateConversationRequest(TypedDict, total=False):
    """Request model for creating conversations."""

    title: Optional[str]
    initial_message: Optional[str]
    metadata: Optional[Dict[str, Any]]


class SendMessageRequest(TypedDict, total=False):
    """Request model for sending messages."""

    content: str
    role: Optional[MessageRole]
    metadata: Optional[Dict[str, Any]]
