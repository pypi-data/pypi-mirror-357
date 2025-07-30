"""
Conversation models for the Cognify SDK.

This module contains all the data models and types related to conversation
management, multi-turn dialogue, and context handling.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ConversationStatus(str, Enum):
    """Status of a conversation session."""
    
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"


class ConversationTurn(BaseModel):
    """
    Individual turn in a conversation.
    """
    
    id: str = Field(description="Unique turn identifier")
    session_id: str = Field(description="Session this turn belongs to")
    query: str = Field(description="User query")
    response: str = Field(description="AI response")
    timestamp: datetime = Field(description="Turn timestamp")
    processing_time_ms: float = Field(description="Processing time in milliseconds")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    context_used: Optional[str] = Field(default=None, description="Context used for this turn")
    confidence_score: float = Field(default=0.0, description="Response confidence (0.0-1.0)")
    tokens_used: int = Field(default=0, description="Number of tokens used")
    
    @validator("confidence_score")
    def validate_confidence_score(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        return v
    
    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationSession(BaseModel):
    """
    Conversation session containing multiple turns.
    """
    
    id: str = Field(description="Unique session identifier")
    user_id: str = Field(description="User who owns this session")
    title: Optional[str] = Field(default=None, description="Session title")
    status: ConversationStatus = Field(description="Current session status")
    collection_id: Optional[str] = Field(default=None, description="Associated collection")
    workspace_id: Optional[str] = Field(default=None, description="Associated workspace")
    started_at: datetime = Field(description="Session start time")
    last_activity: datetime = Field(description="Last activity timestamp")
    ended_at: Optional[datetime] = Field(default=None, description="Session end time")
    turn_count: int = Field(default=0, description="Number of turns in session")
    total_tokens: int = Field(default=0, description="Total tokens used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")
    tags: List[str] = Field(default_factory=list, description="Session tags")
    
    @validator("turn_count")
    def validate_turn_count(cls, v):
        if v < 0:
            raise ValueError("Turn count cannot be negative")
        return v
    
    @validator("total_tokens")
    def validate_total_tokens(cls, v):
        if v < 0:
            raise ValueError("Total tokens cannot be negative")
        return v
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == ConversationStatus.ACTIVE
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Get session duration in minutes."""
        if self.ended_at:
            delta = self.ended_at - self.started_at
            return delta.total_seconds() / 60
        else:
            delta = self.last_activity - self.started_at
            return delta.total_seconds() / 60
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationContext(BaseModel):
    """
    Context information for a conversation session.
    """
    
    session_id: str = Field(description="Session identifier")
    recent_turns: List[ConversationTurn] = Field(description="Recent conversation turns")
    user_preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    conversation_summary: str = Field(default="", description="Conversation summary")
    key_topics: List[str] = Field(default_factory=list, description="Key topics discussed")
    relevant_documents: List[str] = Field(default_factory=list, description="Relevant document IDs")
    context_length: int = Field(default=0, description="Total context length in characters")
    last_updated: datetime = Field(description="Last context update")
    
    @property
    def turn_count(self) -> int:
        """Get number of turns in context."""
        return len(self.recent_turns)
    
    @property
    def latest_turn(self) -> Optional[ConversationTurn]:
        """Get the most recent turn."""
        return self.recent_turns[-1] if self.recent_turns else None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationStartRequest(BaseModel):
    """
    Request to start a new conversation session.
    """
    
    title: Optional[str] = Field(default=None, description="Session title")
    collection_id: Optional[str] = Field(default=None, description="Collection to focus on")
    workspace_id: Optional[str] = Field(default=None, description="Workspace to use")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Initial context")
    tags: List[str] = Field(default_factory=list, description="Session tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ConversationQueryRequest(BaseModel):
    """
    Request for a conversation query.
    """
    
    query: str = Field(description="User query")
    session_id: str = Field(description="Session identifier")
    include_context: bool = Field(default=True, description="Include conversation context")
    max_context_turns: int = Field(default=5, description="Maximum turns to include in context")
    temperature: float = Field(default=0.7, description="Response creativity (0.0-1.0)")
    max_tokens: int = Field(default=500, description="Maximum response tokens")
    
    @validator("query")
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        if len(v) > 2000:
            raise ValueError("Query cannot exceed 2000 characters")
        return v.strip()
    
    @validator("max_context_turns")
    def validate_max_context_turns(cls, v):
        if v < 0:
            raise ValueError("max_context_turns cannot be negative")
        if v > 20:
            raise ValueError("max_context_turns cannot exceed 20")
        return v
    
    @validator("temperature")
    def validate_temperature(cls, v):
        if v < 0.0 or v > 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v


class ConversationHistoryRequest(BaseModel):
    """
    Request for conversation history.
    """
    
    limit: int = Field(default=10, description="Maximum number of sessions to return")
    offset: int = Field(default=0, description="Number of sessions to skip")
    status: Optional[ConversationStatus] = Field(default=None, description="Filter by status")
    collection_id: Optional[str] = Field(default=None, description="Filter by collection")
    workspace_id: Optional[str] = Field(default=None, description="Filter by workspace")
    include_context: bool = Field(default=False, description="Include session context")
    date_from: Optional[datetime] = Field(default=None, description="Filter from date")
    date_to: Optional[datetime] = Field(default=None, description="Filter to date")
    
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


class ConversationStats(BaseModel):
    """
    Conversation system statistics.
    """
    
    total_sessions: int = Field(description="Total number of sessions")
    active_sessions: int = Field(description="Number of active sessions")
    total_turns: int = Field(description="Total number of turns")
    avg_turns_per_session: float = Field(description="Average turns per session")
    avg_session_duration_minutes: float = Field(description="Average session duration")
    total_tokens_used: int = Field(description="Total tokens used")
    popular_topics: List[Dict[str, Any]] = Field(description="Most discussed topics")
    user_activity: Dict[str, int] = Field(description="User activity statistics")
    collection_usage: Dict[str, int] = Field(description="Collection usage statistics")
    last_updated: datetime = Field(description="Last statistics update")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserProfile(BaseModel):
    """
    User behavior profile from conversations.
    """
    
    user_id: str = Field(description="User identifier")
    total_conversations: int = Field(description="Total number of conversations")
    total_turns: int = Field(description="Total number of turns")
    avg_turns_per_conversation: float = Field(description="Average turns per conversation")
    total_time_minutes: float = Field(description="Total conversation time")
    favorite_topics: List[str] = Field(description="Most discussed topics")
    preferred_collections: List[str] = Field(description="Most used collections")
    conversation_patterns: Dict[str, Any] = Field(description="Conversation behavior patterns")
    activity_by_hour: Dict[str, int] = Field(description="Activity distribution by hour")
    last_activity: datetime = Field(description="Last conversation activity")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TeamAnalytics(BaseModel):
    """
    Team collaboration analytics.
    """
    
    team_id: str = Field(description="Team identifier")
    total_team_conversations: int = Field(description="Total team conversations")
    active_users: int = Field(description="Number of active users")
    collaboration_score: float = Field(description="Team collaboration score")
    trending_topics: List[str] = Field(description="Trending discussion topics")
    knowledge_sharing_metrics: Dict[str, Any] = Field(description="Knowledge sharing metrics")
    user_contributions: Dict[str, Dict[str, Any]] = Field(description="Individual user contributions")
    peak_activity_hours: List[int] = Field(description="Peak activity hours")
    cross_collection_usage: Dict[str, int] = Field(description="Cross-collection usage patterns")
    last_updated: datetime = Field(description="Last analytics update")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConversationExportRequest(BaseModel):
    """
    Request to export conversations.
    """
    
    session_ids: Optional[List[str]] = Field(default=None, description="Specific sessions to export")
    format: str = Field(default="json", description="Export format (json, markdown, csv)")
    include_context: bool = Field(default=True, description="Include conversation context")
    include_metadata: bool = Field(default=False, description="Include metadata")
    date_from: Optional[datetime] = Field(default=None, description="Export from date")
    date_to: Optional[datetime] = Field(default=None, description="Export to date")
    
    @validator("format")
    def validate_format(cls, v):
        allowed_formats = ["json", "markdown", "csv", "xlsx"]
        if v.lower() not in allowed_formats:
            raise ValueError(f"Format must be one of: {', '.join(allowed_formats)}")
        return v.lower()
