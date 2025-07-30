"""
Query and search models for the Cognify SDK.

This module contains all the data models and types related to query
and search operations, including RAG queries, search results, and analytics.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class SearchMode(str, Enum):
    """Search mode options."""

    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    VECTOR = "vector"
    KEYWORD = "keyword"
    FUZZY = "fuzzy"


class QueryType(str, Enum):
    """Query type classification."""

    RAG = "rag"
    SEARCH = "search"
    SUGGESTION = "suggestion"
    ANALYTICS = "analytics"


class SortOrder(str, Enum):
    """Sort order options."""

    ASC = "asc"
    DESC = "desc"


class QueryRequest(BaseModel):
    """
    Base query request model.
    """

    query: str = Field(description="Search query text")
    collection_id: Optional[str] = Field(default=None, description="Collection to search in")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to search in")
    mode: SearchMode = Field(default=SearchMode.HYBRID, description="Search mode")
    limit: int = Field(default=10, description="Maximum number of results")
    offset: int = Field(default=0, description="Number of results to skip")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Additional filters")
    include_metadata: bool = Field(default=True, description="Include result metadata")
    include_highlights: bool = Field(default=True, description="Include text highlights")

    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        if len(v) > 1000:
            raise ValueError("Query cannot exceed 1000 characters")
        return v.strip()

    @validator("limit")
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError("Limit must be at least 1")
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v

    @validator("offset")
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError("Offset cannot be negative")
        return v


class RAGQueryRequest(BaseModel):
    """
    RAG (Retrieval-Augmented Generation) query request.
    """

    query: str = Field(description="Natural language question")
    collection_id: Optional[str] = Field(default=None, description="Collection to query")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to query")
    context_limit: int = Field(default=5, description="Maximum context chunks")
    include_sources: bool = Field(default=True, description="Include source references")
    temperature: float = Field(default=0.7, description="Response creativity (0.0-1.0)")
    max_tokens: int = Field(default=500, description="Maximum response tokens")
    stream: bool = Field(default=False, description="Stream response")

    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        if len(v) > 2000:
            raise ValueError("Query cannot exceed 2000 characters")
        return v.strip()

    @validator("context_limit")
    def validate_context_limit(cls, v):
        if v < 1:
            raise ValueError("Context limit must be at least 1")
        if v > 20:
            raise ValueError("Context limit cannot exceed 20")
        return v

    @validator("temperature")
    def validate_temperature(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class SearchResult(BaseModel):
    """
    Individual search result.
    """

    id: str = Field(description="Unique result identifier")
    content: str = Field(description="Result content/text")
    score: float = Field(description="Relevance score (0.0-1.0)")
    document_id: str = Field(description="Source document ID")
    chunk_id: Optional[str] = Field(default=None, description="Source chunk ID")
    title: Optional[str] = Field(default=None, description="Result title")
    filename: Optional[str] = Field(default=None, description="Source filename")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    highlights: List[str] = Field(default_factory=list, description="Text highlights")
    position: Optional[Dict[str, int]] = Field(default=None, description="Position in document")

    @validator("score")
    def validate_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")
        return v


class QueryResponse(BaseModel):
    """
    Query response with results and metadata.
    """

    query_id: str = Field(description="Unique query identifier")
    query: str = Field(description="Original query text")
    query_type: QueryType = Field(description="Type of query")
    results: List[SearchResult] = Field(description="Search results")
    total_results: int = Field(description="Total number of results")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    suggestions: List[str] = Field(default_factory=list, description="Query suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    created_at: datetime = Field(description="Query timestamp")

    @property
    def has_results(self) -> bool:
        """Check if query has results."""
        return len(self.results) > 0

    @property
    def top_result(self) -> Optional[SearchResult]:
        """Get the top-scoring result."""
        return self.results[0] if self.results else None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RAGResponse(BaseModel):
    """
    RAG query response with generated answer.
    """

    query_id: str = Field(description="Unique query identifier")
    query: str = Field(description="Original question")
    answer: str = Field(description="Generated answer")
    sources: List[SearchResult] = Field(description="Source documents/chunks")
    confidence: float = Field(description="Answer confidence (0.0-1.0)")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    tokens_used: int = Field(description="Number of tokens used")
    model_metadata: Dict[str, Any] = Field(default_factory=dict, description="Model information")
    created_at: datetime = Field(description="Query timestamp")

    @validator("confidence")
    def validate_confidence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AdvancedSearchRequest(BaseModel):
    """
    Advanced search request with complex filtering.
    """

    query: str = Field(description="Search query")
    filters: Dict[str, Any] = Field(description="Search filters")
    sort_by: Optional[str] = Field(default=None, description="Sort field")
    sort_order: SortOrder = Field(default=SortOrder.DESC, description="Sort order")
    facets: Optional[List[str]] = Field(default=None, description="Facet fields")
    highlight_fields: Optional[List[str]] = Field(default=None, description="Fields to highlight")
    limit: int = Field(default=10, description="Maximum results")
    offset: int = Field(default=0, description="Results offset")

    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SuggestionRequest(BaseModel):
    """
    Search suggestion request.
    """

    query_prefix: str = Field(description="Query prefix for suggestions")
    collection_id: Optional[str] = Field(default=None, description="Collection context")
    workspace_id: Optional[str] = Field(default=None, description="Workspace context")
    limit: int = Field(default=10, description="Maximum suggestions")
    include_popular: bool = Field(default=True, description="Include popular queries")

    @validator("query_prefix")
    def validate_query_prefix(cls, v):
        if len(v) > 100:
            raise ValueError("Query prefix cannot exceed 100 characters")
        return v.strip()

    @validator("limit")
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError("Limit must be at least 1")
        if v > 50:
            raise ValueError("Limit cannot exceed 50")
        return v


class QueryHistoryEntry(BaseModel):
    """
    Query history entry.
    """

    id: str = Field(description="Query history ID")
    query: str = Field(description="Query text")
    query_type: QueryType = Field(description="Type of query")
    collection_id: Optional[str] = Field(default=None, description="Collection queried")
    workspace_id: Optional[str] = Field(default=None, description="Workspace queried")
    results_count: int = Field(description="Number of results returned")
    processing_time_ms: float = Field(description="Processing time")
    created_at: datetime = Field(description="Query timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class QueryAnalytics(BaseModel):
    """
    Query analytics and statistics.
    """

    total_queries: int = Field(description="Total number of queries")
    unique_queries: int = Field(description="Number of unique queries")
    avg_processing_time_ms: float = Field(description="Average processing time")
    popular_queries: List[Dict[str, Any]] = Field(description="Most popular queries")
    query_trends: Dict[str, Any] = Field(description="Query trends over time")
    search_modes: Dict[str, int] = Field(description="Usage by search mode")
    collections: Dict[str, int] = Field(description="Usage by collection")
    date_range: Dict[str, str] = Field(description="Analytics date range")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BatchQueryRequest(BaseModel):
    """
    Batch query request for processing multiple queries.
    """

    queries: List[str] = Field(description="List of queries to process")
    mode: SearchMode = Field(default=SearchMode.HYBRID, description="Search mode for all queries")
    collection_id: Optional[str] = Field(default=None, description="Collection to search")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to search")
    limit: int = Field(default=10, description="Results per query")
    parallel: bool = Field(default=True, description="Process queries in parallel")

    @validator("queries")
    def validate_queries(cls, v):
        if not v:
            raise ValueError("At least one query is required")
        if len(v) > 50:
            raise ValueError("Cannot process more than 50 queries at once")
        for query in v:
            if not query or not query.strip():
                raise ValueError("All queries must be non-empty")
        return v


class BatchQueryResponse(BaseModel):
    """
    Batch query response.
    """

    batch_id: str = Field(description="Batch processing ID")
    total_queries: int = Field(description="Total number of queries")
    successful_queries: int = Field(description="Successfully processed queries")
    failed_queries: int = Field(description="Failed queries")
    results: List[QueryResponse] = Field(description="Individual query results")
    processing_time_ms: float = Field(description="Total processing time")
    created_at: datetime = Field(description="Batch processing timestamp")

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_queries == 0:
            return 0.0
        return (self.successful_queries / self.total_queries) * 100

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
