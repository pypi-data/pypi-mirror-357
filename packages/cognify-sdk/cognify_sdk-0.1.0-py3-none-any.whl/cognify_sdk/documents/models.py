"""
Document models for the Cognify SDK.

This module contains all the data models and types related to document
management, including documents, chunks, and processing status.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class DocumentStatus(str, Enum):
    """Document processing status."""

    QUEUED = "queued"
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
    PYTHON = "py"
    JAVASCRIPT = "js"
    TYPESCRIPT = "ts"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    GO = "go"
    RUST = "rs"
    OTHER = "other"


class ChunkingStrategy(str, Enum):
    """Document chunking strategies."""

    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    PARAGRAPH = "paragraph"
    SENTENCE = "sentence"
    AST_FALLBACK = "ast_fallback"
    HYBRID = "hybrid"
    AGENTIC = "agentic"


class Document(BaseModel):
    """
    Document model representing a document in the Cognify system.
    """

    id: str = Field(description="Unique document identifier", alias="document_id")
    title: str = Field(description="Document title")
    filename: str = Field(description="Original filename", alias="file_name")
    file_size: int = Field(description="File size in bytes")
    document_type: str = Field(description="Document type/format")
    status: DocumentStatus = Field(description="Processing status")
    collection_id: Optional[str] = Field(default=None, description="Collection ID")
    workspace_id: Optional[str] = Field(default=None, description="Workspace ID")
    organization_id: Optional[str] = Field(default=None, description="Organization ID")
    owner_id: Optional[str] = Field(default=None, description="Owner ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    tags: List[str] = Field(default_factory=list, description="Document tags")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    processed_at: Optional[datetime] = Field(default=None, description="Processing completion timestamp")
    processing_info: Optional[Dict[str, Any]] = Field(default=None, description="Processing information")
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DocumentChunk(BaseModel):
    """
    Document chunk model for processed document segments.
    """

    id: str = Field(description="Unique chunk identifier")
    document_id: str = Field(description="Parent document ID")
    content: str = Field(description="Chunk content")
    chunk_index: int = Field(description="Index of chunk in document")
    start_char: int = Field(description="Start character position")
    end_char: int = Field(description="End character position")
    size: int = Field(description="Chunk size in characters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding")
    created_at: datetime = Field(description="Creation timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UploadProgress(BaseModel):
    """
    Upload progress information.
    """

    bytes_uploaded: int = Field(description="Bytes uploaded so far")
    total_bytes: int = Field(description="Total bytes to upload")
    percentage: float = Field(description="Upload percentage (0-100)")
    speed_bps: Optional[float] = Field(default=None, description="Upload speed in bytes per second")
    eta_seconds: Optional[float] = Field(default=None, description="Estimated time to completion")

    @property
    def is_complete(self) -> bool:
        """Check if upload is complete."""
        return self.bytes_uploaded >= self.total_bytes


class BulkUploadSession(BaseModel):
    """
    Bulk upload session information.
    """

    id: str = Field(description="Unique session identifier")
    total_files: int = Field(description="Total number of files to upload")
    completed_files: int = Field(description="Number of files completed")
    failed_files: int = Field(description="Number of files that failed")
    status: str = Field(description="Session status")
    created_at: datetime = Field(description="Session creation time")
    updated_at: datetime = Field(description="Last update time")
    files: List[Dict[str, Any]] = Field(default_factory=list, description="File upload details")

    @property
    def is_complete(self) -> bool:
        """Check if all uploads are complete."""
        return self.completed_files + self.failed_files >= self.total_files

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.completed_files / self.total_files) * 100

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ChunkingRequest(BaseModel):
    """
    Request model for content chunking.
    """

    content: str = Field(description="Content to chunk")
    language: Optional[str] = Field(default=None, description="Programming language (if applicable)")
    strategy: ChunkingStrategy = Field(default=ChunkingStrategy.HYBRID, description="Chunking strategy")
    max_chunk_size: int = Field(default=1000, description="Maximum chunk size in characters")
    overlap: int = Field(default=100, description="Overlap between chunks in characters")
    preserve_structure: bool = Field(default=True, description="Preserve code/document structure")

    @validator("max_chunk_size")
    def validate_max_chunk_size(cls, v):
        if v < 100:
            raise ValueError("max_chunk_size must be at least 100 characters")
        if v > 10000:
            raise ValueError("max_chunk_size cannot exceed 10000 characters")
        return v

    @validator("overlap")
    def validate_overlap(cls, v, values):
        if v < 0:
            raise ValueError("overlap cannot be negative")
        if "max_chunk_size" in values and v >= values["max_chunk_size"]:
            raise ValueError("overlap must be less than max_chunk_size")
        return v


class DocumentFilter(BaseModel):
    """
    Filter options for document listing and searching.
    """

    workspace_id: Optional[str] = Field(default=None, description="Filter by workspace")
    collection_id: Optional[str] = Field(default=None, description="Filter by collection")
    document_type: Optional[str] = Field(default=None, description="Filter by document type")
    status: Optional[DocumentStatus] = Field(default=None, description="Filter by status")
    tags: Optional[List[str]] = Field(default=None, description="Filter by tags")
    created_after: Optional[datetime] = Field(default=None, description="Filter by creation date")
    created_before: Optional[datetime] = Field(default=None, description="Filter by creation date")
    limit: int = Field(default=50, description="Maximum number of results")
    offset: int = Field(default=0, description="Number of results to skip")

    @validator("limit")
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError("limit must be at least 1")
        if v > 1000:
            raise ValueError("limit cannot exceed 1000")
        return v

    @validator("offset")
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError("offset cannot be negative")
        return v


class DocumentSearchRequest(BaseModel):
    """
    Request model for document search.
    """

    query: str = Field(description="Search query")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to search in")
    collection_id: Optional[str] = Field(default=None, description="Collection to search in")
    document_types: Optional[List[str]] = Field(default=None, description="Document types to include")
    tags: Optional[List[str]] = Field(default=None, description="Tags to filter by")
    limit: int = Field(default=50, description="Maximum number of results")
    include_content: bool = Field(default=False, description="Include document content in results")

    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("query cannot be empty")
        if len(v) > 1000:
            raise ValueError("query cannot exceed 1000 characters")
        return v.strip()


class FileUploadRequest(BaseModel):
    """
    Request model for file upload.
    """

    file_path: Union[str, Path] = Field(description="Path to file to upload")
    collection_id: Optional[str] = Field(default=None, description="Collection to upload to")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to upload to")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    tags: Optional[List[str]] = Field(default=None, description="Tags to apply")
    chunking_strategy: Optional[ChunkingStrategy] = Field(default=None, description="Chunking strategy")

    @validator("file_path")
    def validate_file_path(cls, v):
        path = Path(v)
        if not path.exists():
            raise ValueError(f"File does not exist: {v}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {v}")
        return path

    class Config:
        arbitrary_types_allowed = True
