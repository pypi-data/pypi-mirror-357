"""
Query and search module for the Cognify SDK.

This module provides comprehensive query and search functionality including
RAG queries, semantic search, suggestions, history, and batch processing.
"""

from .query_module import QueryModule
from .models import (
    QueryRequest,
    RAGQueryRequest,
    QueryResponse,
    RAGResponse,
    SearchResult,
    SearchMode,
    QueryType,
    AdvancedSearchRequest,
    SuggestionRequest,
    QueryHistoryEntry,
    QueryAnalytics,
    BatchQueryRequest,
    BatchQueryResponse,
    SortOrder,
)
from .suggestions import SuggestionsModule
from .history import QueryHistory
from .batch import BatchQueryProcessor

__all__ = [
    "QueryModule",
    "QueryRequest",
    "RAGQueryRequest",
    "QueryResponse",
    "RAGResponse",
    "SearchResult",
    "SearchMode",
    "QueryType",
    "AdvancedSearchRequest",
    "SuggestionRequest",
    "QueryHistoryEntry",
    "QueryAnalytics",
    "BatchQueryRequest",
    "BatchQueryResponse",
    "SortOrder",
    "SuggestionsModule",
    "QueryHistory",
    "BatchQueryProcessor",
]
