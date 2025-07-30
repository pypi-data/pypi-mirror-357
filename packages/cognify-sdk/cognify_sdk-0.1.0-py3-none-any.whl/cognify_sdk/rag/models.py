"""
RAG and Agents models for the Cognify SDK.

This module contains all the data models and types related to RAG
(Retrieval-Augmented Generation) and AI agent operations.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, AsyncIterator

from pydantic import BaseModel, Field, validator


class ResponseFormat(str, Enum):
    """Response format options for RAG queries."""

    SIMPLE = "simple"
    STRUCTURED = "structured"
    DETAILED = "detailed"
    MARKDOWN = "markdown"


class CitationStyle(str, Enum):
    """Citation style options."""

    INLINE = "inline"
    FOOTNOTE = "footnote"
    BIBLIOGRAPHY = "bibliography"


class AgentStatus(str, Enum):
    """Agent status options."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    OVERLOADED = "overloaded"


class Citation(BaseModel):
    """
    Citation model for source attribution.
    """

    id: str = Field(description="Unique citation identifier")
    document_id: str = Field(description="Source document ID")
    chunk_id: Optional[str] = Field(default=None, description="Source chunk ID")
    filename: str = Field(description="Source filename")
    title: Optional[str] = Field(default=None, description="Document title")
    line_start: Optional[int] = Field(default=None, description="Starting line number")
    line_end: Optional[int] = Field(default=None, description="Ending line number")
    relevance_score: float = Field(description="Relevance score (0.0-1.0)")
    content_preview: str = Field(description="Preview of cited content")
    url: Optional[str] = Field(default=None, description="Source URL if available")

    @validator("relevance_score")
    def validate_relevance_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")
        return v


class RAGQueryRequest(BaseModel):
    """
    Request model for RAG queries.
    """

    query: str = Field(description="Natural language question")
    collection_id: Optional[str] = Field(default=None, description="Collection to query")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to query")
    response_format: ResponseFormat = Field(default=ResponseFormat.SIMPLE, description="Response format")
    citation_style: CitationStyle = Field(default=CitationStyle.INLINE, description="Citation style")
    max_context_length: int = Field(default=4000, description="Maximum context length")
    include_sources: bool = Field(default=True, description="Include source citations")
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

    @validator("max_context_length")
    def validate_max_context_length(cls, v):
        if v < 100:
            raise ValueError("max_context_length must be at least 100")
        if v > 16000:
            raise ValueError("max_context_length cannot exceed 16000")
        return v

    @validator("temperature")
    def validate_temperature(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class RAGResponse(BaseModel):
    """
    Response model for RAG queries.
    """

    query_id: str = Field(description="Unique query identifier")
    query: str = Field(description="Original query")
    answer: str = Field(description="Generated answer")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    confidence_score: float = Field(description="Answer confidence (0.0-1.0)")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    ai_model_used: str = Field(description="AI model used for generation")
    tokens_used: int = Field(description="Number of tokens used")
    context_length: int = Field(description="Context length used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(description="Response timestamp")

    @validator("confidence_score")
    def validate_confidence_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v

    @property
    def has_citations(self) -> bool:
        """Check if response has citations."""
        return len(self.citations) > 0

    @property
    def top_citation(self) -> Optional[Citation]:
        """Get the highest-scoring citation."""
        if not self.citations:
            return None
        return max(self.citations, key=lambda c: c.relevance_score)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StructuredSection(BaseModel):
    """
    Section in a structured response.
    """

    title: str = Field(description="Section title")
    content: str = Field(description="Section content")
    section_type: str = Field(description="Type of section (overview, details, etc.)")
    citations: List[Citation] = Field(default_factory=list, description="Section-specific citations")
    confidence: float = Field(description="Section confidence score")


class CodeExample(BaseModel):
    """
    Code example in a structured response.
    """

    title: str = Field(description="Code example title")
    language: str = Field(description="Programming language")
    code: str = Field(description="Code content")
    explanation: str = Field(description="Code explanation")
    citations: List[Citation] = Field(default_factory=list, description="Code-specific citations")


class StructuredResponse(BaseModel):
    """
    Structured response model for complex RAG queries.
    """

    query_id: str = Field(description="Unique query identifier")
    query: str = Field(description="Original query")
    summary: str = Field(description="Response summary")
    sections: List[StructuredSection] = Field(default_factory=list, description="Response sections")
    code_examples: List[CodeExample] = Field(default_factory=list, description="Code examples")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    warnings: List[str] = Field(default_factory=list, description="Warnings or caveats")
    citations: List[Citation] = Field(default_factory=list, description="All citations")
    confidence_score: float = Field(description="Overall confidence score")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    ai_model_used: str = Field(description="AI model used")
    tokens_used: int = Field(description="Number of tokens used")
    created_at: datetime = Field(description="Response timestamp")

    @validator("confidence_score")
    def validate_confidence_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentInfo(BaseModel):
    """
    Information about an AI agent.
    """

    id: str = Field(description="Unique agent identifier")
    name: str = Field(description="Agent name")
    description: str = Field(description="Agent description")
    capabilities: List[str] = Field(description="Agent capabilities")
    specialization: str = Field(description="Agent specialization area")
    status: AgentStatus = Field(description="Current agent status")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    version: str = Field(description="Agent version")
    created_at: datetime = Field(description="Agent creation time")
    updated_at: datetime = Field(description="Last update time")

    @property
    def is_available(self) -> bool:
        """Check if agent is available for queries."""
        return self.status == AgentStatus.ACTIVE

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentQueryRequest(BaseModel):
    """
    Request model for agent queries.
    """

    query: str = Field(description="Query for the agent")
    agent_id: Optional[str] = Field(default=None, description="Specific agent ID (auto-select if None)")
    collection_id: Optional[str] = Field(default=None, description="Collection to query")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to query")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    stream: bool = Field(default=False, description="Stream response")
    temperature: float = Field(default=0.7, description="Response creativity")
    max_tokens: int = Field(default=1000, description="Maximum response tokens")

    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        if len(v) > 3000:
            raise ValueError("Query cannot exceed 3000 characters")
        return v.strip()

    @validator("temperature")
    def validate_temperature(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class AgentResponse(BaseModel):
    """
    Response model for agent queries.
    """

    query_id: str = Field(description="Unique query identifier")
    agent_id: str = Field(description="Agent that processed the query")
    agent_name: str = Field(description="Agent name")
    query: str = Field(description="Original query")
    response: str = Field(description="Agent response")
    confidence: float = Field(description="Response confidence")
    reasoning: Optional[str] = Field(default=None, description="Agent reasoning process")
    citations: List[Citation] = Field(default_factory=list, description="Source citations")
    processing_time_ms: float = Field(description="Processing time")
    tokens_used: int = Field(description="Tokens used")
    created_at: datetime = Field(description="Response timestamp")

    @validator("confidence")
    def validate_confidence(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StreamingChunk(BaseModel):
    """
    Individual chunk in a streaming response.
    """

    chunk_id: str = Field(description="Chunk identifier")
    content: str = Field(description="Chunk content")
    is_final: bool = Field(default=False, description="Whether this is the final chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Chunk metadata")


class RAGStats(BaseModel):
    """
    RAG service statistics.
    """

    total_queries: int = Field(description="Total number of queries processed")
    avg_response_time_ms: float = Field(description="Average response time")
    avg_confidence_score: float = Field(description="Average confidence score")
    total_tokens_used: int = Field(description="Total tokens used")
    queries_by_format: Dict[str, int] = Field(description="Queries by response format")
    popular_collections: List[Dict[str, Any]] = Field(description="Most queried collections")
    error_rate: float = Field(description="Error rate percentage")
    uptime_percentage: float = Field(description="Service uptime percentage")
    last_updated: datetime = Field(description="Last statistics update")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AgentStats(BaseModel):
    """
    Agent service statistics.
    """

    total_agents: int = Field(description="Total number of agents")
    active_agents: int = Field(description="Number of active agents")
    total_queries: int = Field(description="Total queries processed by all agents")
    avg_response_time_ms: float = Field(description="Average response time across agents")
    queries_by_agent: Dict[str, int] = Field(description="Queries processed by each agent")
    agent_performance: Dict[str, Dict[str, float]] = Field(description="Performance metrics by agent")
    specialization_usage: Dict[str, int] = Field(description="Usage by specialization")
    last_updated: datetime = Field(description="Last statistics update")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
