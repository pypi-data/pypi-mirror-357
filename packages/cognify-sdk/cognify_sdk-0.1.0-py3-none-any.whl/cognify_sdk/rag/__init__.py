"""
RAG and Agents module for the Cognify SDK.

This module provides comprehensive RAG (Retrieval-Augmented Generation)
and AI agent functionality including natural language Q&A, structured responses,
citations, and agent orchestration.
"""

from .rag_module import RAGModule
from .agents import AgentsModule
from .models import (
    RAGQueryRequest,
    RAGResponse,
    StructuredResponse,
    Citation,
    ResponseFormat,
    CitationStyle,
    AgentInfo,
    AgentQueryRequest,
    AgentResponse,
    AgentStatus,
    StructuredSection,
    CodeExample,
    RAGStats,
    AgentStats,
    StreamingChunk,
)
from .streaming import StreamingResponse, StreamingManager, StreamingBuffer

__all__ = [
    "RAGModule",
    "AgentsModule",
    "RAGQueryRequest",
    "RAGResponse",
    "StructuredResponse",
    "Citation",
    "ResponseFormat",
    "CitationStyle",
    "AgentInfo",
    "AgentQueryRequest",
    "AgentResponse",
    "AgentStatus",
    "StructuredSection",
    "CodeExample",
    "RAGStats",
    "AgentStats",
    "StreamingChunk",
    "StreamingResponse",
    "StreamingManager",
    "StreamingBuffer",
]
