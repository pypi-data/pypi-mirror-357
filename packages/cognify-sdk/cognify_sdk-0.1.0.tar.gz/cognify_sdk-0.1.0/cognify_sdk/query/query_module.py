"""
Main query module for the Cognify SDK.

This module provides the primary interface for query and search operations
including RAG queries, semantic search, and advanced search capabilities.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .models import (
    QueryRequest,
    RAGQueryRequest,
    QueryResponse,
    RAGResponse,
    SearchResult,
    SearchMode,
    QueryType,
    AdvancedSearchRequest,
    QueryHistoryEntry,
    BatchQueryResponse,
    SortOrder,
)

if TYPE_CHECKING:
    from ..client import CognifyClient


logger = logging.getLogger(__name__)


class QueryModule:
    """
    Main query module for the Cognify SDK.

    This class provides methods for RAG queries, search operations,
    suggestions, and analytics.
    """

    def __init__(self, client: "CognifyClient") -> None:
        """
        Initialize query module.

        Args:
            client: Cognify client instance
        """
        self.client = client

    # RAG Queries

    async def ask(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context_limit: int = 5,
        include_sources: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500,
        stream: bool = False
    ) -> RAGResponse:
        """
        Submit a RAG query for natural language Q&A.

        Args:
            query: Natural language question
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            context_limit: Maximum context chunks (default: 5)
            include_sources: Include source references (default: True)
            temperature: Response creativity 0.0-1.0 (default: 0.7)
            max_tokens: Maximum response tokens (default: 500)
            stream: Stream response (default: False)

        Returns:
            RAGResponse with generated answer and sources

        Raises:
            CognifyValidationError: If query is invalid
            CognifyAPIError: If query fails
        """
        request = RAGQueryRequest(
            query=query,
            collection_id=collection_id,
            workspace_id=workspace_id,
            context_limit=context_limit,
            include_sources=include_sources,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )

        logger.info(f"Submitting RAG query: {query[:50]}...")

        response = await self.client.http.arequest(
            'POST',
            '/query',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        # Create RAG response
        rag_response = RAGResponse(
            query_id=data.get('query_id', f"rag_{int(datetime.now().timestamp())}"),
            query=query,
            answer=data.get('answer', ''),
            sources=[SearchResult(**source) for source in data.get('sources', [])],
            confidence=data.get('confidence', 0.0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            tokens_used=data.get('tokens_used', 0),
            model_metadata=data.get('model_info', {}),
            created_at=datetime.now()
        )

        logger.info(f"RAG query completed: {rag_response.query_id}")
        return rag_response

    def ask_sync(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context_limit: int = 5,
        include_sources: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> RAGResponse:
        """
        Submit a RAG query synchronously.

        Args:
            query: Natural language question
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            context_limit: Maximum context chunks (default: 5)
            include_sources: Include source references (default: True)
            temperature: Response creativity 0.0-1.0 (default: 0.7)
            max_tokens: Maximum response tokens (default: 500)

        Returns:
            RAGResponse with generated answer and sources
        """
        request = RAGQueryRequest(
            query=query,
            collection_id=collection_id,
            workspace_id=workspace_id,
            context_limit=context_limit,
            include_sources=include_sources,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        response = self.client.http.request(
            'POST',
            '/query',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        return RAGResponse(
            query_id=data.get('query_id', f"rag_{int(datetime.now().timestamp())}"),
            query=query,
            answer=data.get('answer', ''),
            sources=[SearchResult(**source) for source in data.get('sources', [])],
            confidence=data.get('confidence', 0.0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            tokens_used=data.get('tokens_used', 0),
            model_metadata=data.get('model_info', {}),
            created_at=datetime.now()
        )

    # Search Operations

    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_highlights: bool = True
    ) -> QueryResponse:
        """
        Perform search with specified mode.

        Args:
            query: Search query text
            mode: Search mode (default: HYBRID)
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Maximum results (default: 10)
            offset: Results offset (default: 0)
            filters: Additional filters (optional)
            include_metadata: Include metadata (default: True)
            include_highlights: Include highlights (default: True)

        Returns:
            QueryResponse with search results
        """
        request = QueryRequest(
            query=query,
            collection_id=collection_id,
            workspace_id=workspace_id,
            mode=mode,
            limit=limit,
            offset=offset,
            filters=filters,
            include_metadata=include_metadata,
            include_highlights=include_highlights
        )

        logger.info(f"Performing {mode.value} search: {query[:50]}...")

        response = await self.client.http.arequest(
            'POST',
            '/query/search',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        return QueryResponse(
            query_id=data.get('query_id', f"search_{int(datetime.now().timestamp())}"),
            query=query,
            query_type=QueryType.SEARCH,
            results=[SearchResult(**result) for result in data.get('results', [])],
            total_results=data.get('total_results', 0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            suggestions=data.get('suggestions', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.now()
        )

    def search_sync(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None,
        include_metadata: bool = True,
        include_highlights: bool = True
    ) -> QueryResponse:
        """
        Perform search synchronously.

        Args:
            query: Search query text
            mode: Search mode (default: HYBRID)
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Maximum results (default: 10)
            offset: Results offset (default: 0)
            filters: Additional filters (optional)
            include_metadata: Include metadata (default: True)
            include_highlights: Include highlights (default: True)

        Returns:
            QueryResponse with search results
        """
        request = QueryRequest(
            query=query,
            collection_id=collection_id,
            workspace_id=workspace_id,
            mode=mode,
            limit=limit,
            offset=offset,
            filters=filters,
            include_metadata=include_metadata,
            include_highlights=include_highlights
        )

        response = self.client.http.request(
            'POST',
            '/query/search',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        return QueryResponse(
            query_id=data.get('query_id', f"search_{int(datetime.now().timestamp())}"),
            query=query,
            query_type=QueryType.SEARCH,
            results=[SearchResult(**result) for result in data.get('results', [])],
            total_results=data.get('total_results', 0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            suggestions=data.get('suggestions', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.now()
        )

    async def semantic_search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10
    ) -> QueryResponse:
        """
        Perform semantic vector search.

        Args:
            query: Search query
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Maximum results (default: 10)

        Returns:
            QueryResponse with semantic search results
        """
        return await self.search(
            query=query,
            mode=SearchMode.SEMANTIC,
            collection_id=collection_id,
            workspace_id=workspace_id,
            limit=limit
        )

    def semantic_search_sync(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10
    ) -> QueryResponse:
        """
        Perform semantic vector search synchronously.

        Args:
            query: Search query
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Maximum results (default: 10)

        Returns:
            QueryResponse with semantic search results
        """
        return self.search_sync(
            query=query,
            mode=SearchMode.SEMANTIC,
            collection_id=collection_id,
            workspace_id=workspace_id,
            limit=limit
        )

    async def hybrid_search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        semantic_weight: float = 0.7
    ) -> QueryResponse:
        """
        Perform hybrid semantic + keyword search.

        Args:
            query: Search query
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Maximum results (default: 10)
            semantic_weight: Weight for semantic vs keyword (default: 0.7)

        Returns:
            QueryResponse with hybrid search results
        """
        filters = {"semantic_weight": semantic_weight} if semantic_weight != 0.7 else None

        return await self.search(
            query=query,
            mode=SearchMode.HYBRID,
            collection_id=collection_id,
            workspace_id=workspace_id,
            limit=limit,
            filters=filters
        )

    def hybrid_search_sync(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        semantic_weight: float = 0.7
    ) -> QueryResponse:
        """
        Perform hybrid search synchronously.

        Args:
            query: Search query
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Maximum results (default: 10)
            semantic_weight: Weight for semantic vs keyword (default: 0.7)

        Returns:
            QueryResponse with hybrid search results
        """
        filters = {"semantic_weight": semantic_weight} if semantic_weight != 0.7 else None

        return self.search_sync(
            query=query,
            mode=SearchMode.HYBRID,
            collection_id=collection_id,
            workspace_id=workspace_id,
            limit=limit,
            filters=filters
        )

    # Advanced Search

    async def advanced_search(
        self,
        query: str,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: SortOrder = SortOrder.DESC,
        facets: Optional[List[str]] = None,
        highlight_fields: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> QueryResponse:
        """
        Perform advanced search with complex filters.

        Args:
            query: Search query
            filters: Search filters
            sort_by: Sort field (optional)
            sort_order: Sort order (default: DESC)
            facets: Facet fields (optional)
            highlight_fields: Fields to highlight (optional)
            limit: Maximum results (default: 10)
            offset: Results offset (default: 0)

        Returns:
            QueryResponse with advanced search results
        """
        request = AdvancedSearchRequest(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            facets=facets,
            highlight_fields=highlight_fields,
            limit=limit,
            offset=offset
        )

        logger.info(f"Performing advanced search: {query[:50]}...")

        response = await self.client.http.arequest(
            'POST',
            '/query/advanced',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        return QueryResponse(
            query_id=data.get('query_id', f"advanced_{int(datetime.now().timestamp())}"),
            query=query,
            query_type=QueryType.SEARCH,
            results=[SearchResult(**result) for result in data.get('results', [])],
            total_results=data.get('total_results', 0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            suggestions=data.get('suggestions', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.now()
        )

    def advanced_search_sync(
        self,
        query: str,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: SortOrder = SortOrder.DESC,
        facets: Optional[List[str]] = None,
        highlight_fields: Optional[List[str]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> QueryResponse:
        """
        Perform advanced search synchronously.

        Args:
            query: Search query
            filters: Search filters
            sort_by: Sort field (optional)
            sort_order: Sort order (default: DESC)
            facets: Facet fields (optional)
            highlight_fields: Fields to highlight (optional)
            limit: Maximum results (default: 10)
            offset: Results offset (default: 0)

        Returns:
            QueryResponse with advanced search results
        """
        request = AdvancedSearchRequest(
            query=query,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            facets=facets,
            highlight_fields=highlight_fields,
            limit=limit,
            offset=offset
        )

        response = self.client.http.request(
            'POST',
            '/query/advanced',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        return QueryResponse(
            query_id=data.get('query_id', f"advanced_{int(datetime.now().timestamp())}"),
            query=query,
            query_type=QueryType.SEARCH,
            results=[SearchResult(**result) for result in data.get('results', [])],
            total_results=data.get('total_results', 0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            suggestions=data.get('suggestions', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.now()
        )

    # Sub-module properties

    @property
    def suggestions(self):
        """Access suggestions sub-module."""
        if not hasattr(self, '_suggestions'):
            from .suggestions import SuggestionsModule
            self._suggestions = SuggestionsModule(self)
        return self._suggestions

    @property
    def history(self):
        """Access history sub-module."""
        if not hasattr(self, '_history'):
            from .history import QueryHistory
            self._history = QueryHistory(self)
        return self._history

    @property
    def batch(self):
        """Access batch processing sub-module."""
        if not hasattr(self, '_batch'):
            from .batch import BatchQueryProcessor
            self._batch = BatchQueryProcessor(self)
        return self._batch

    # Convenience methods for sub-modules

    async def get_suggestions(
        self,
        query_prefix: str,
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> List[str]:
        """Get search suggestions (convenience method)."""
        return await self.suggestions.get_suggestions(
            query_prefix=query_prefix,
            collection_id=collection_id,
            limit=limit
        )

    def get_suggestions_sync(
        self,
        query_prefix: str,
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> List[str]:
        """Get search suggestions synchronously (convenience method)."""
        return self.suggestions.get_suggestions_sync(
            query_prefix=query_prefix,
            collection_id=collection_id,
            limit=limit
        )

    async def get_history(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[QueryHistoryEntry]:
        """Get query history (convenience method)."""
        return await self.history.get_history(limit=limit, offset=offset)

    def get_history_sync(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> List[QueryHistoryEntry]:
        """Get query history synchronously (convenience method)."""
        return self.history.get_history_sync(limit=limit, offset=offset)

    async def batch_search(
        self,
        queries: List[str],
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> BatchQueryResponse:
        """Batch search queries (convenience method)."""
        return await self.batch.batch_search(
            queries=queries,
            mode=mode,
            collection_id=collection_id,
            limit=limit
        )

    def batch_search_sync(
        self,
        queries: List[str],
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> BatchQueryResponse:
        """Batch search queries synchronously (convenience method)."""
        return self.batch.batch_search_sync(
            queries=queries,
            mode=mode,
            collection_id=collection_id,
            limit=limit
        )