"""
Main RAG module for the Cognify SDK.

This module provides the primary interface for RAG (Retrieval-Augmented Generation)
operations including natural language Q&A, structured responses, and citations.
"""

import logging
from datetime import datetime
from typing import Any, AsyncIterator, Dict, Optional, TYPE_CHECKING

from .models import (
    RAGQueryRequest,
    RAGResponse,
    StructuredResponse,
    Citation,
    ResponseFormat,
    CitationStyle,
    RAGStats,
)
from .streaming import StreamingManager
from ..exceptions import CognifyValidationError, CognifyAPIError

if TYPE_CHECKING:
    from ..client import CognifyClient


logger = logging.getLogger(__name__)


class RAGModule:
    """
    Main RAG module for the Cognify SDK.

    This class provides methods for RAG queries, structured responses,
    and citation management.
    """

    def __init__(self, client: "CognifyClient") -> None:
        """
        Initialize RAG module.

        Args:
            client: Cognify client instance
        """
        self.client = client
        self.streaming_manager = StreamingManager()

    # Basic RAG Operations

    async def ask(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        response_format: ResponseFormat = ResponseFormat.SIMPLE,
        citation_style: CitationStyle = CitationStyle.INLINE,
        max_context_length: int = 4000,
        include_sources: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> RAGResponse:
        """
        Ask a natural language question with RAG.

        Args:
            query: Natural language question
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            response_format: Response format (default: SIMPLE)
            citation_style: Citation style (default: INLINE)
            max_context_length: Maximum context length (default: 4000)
            include_sources: Include source citations (default: True)
            temperature: Response creativity 0.0-1.0 (default: 0.7)
            max_tokens: Maximum response tokens (default: 500)

        Returns:
            RAGResponse with generated answer and citations

        Raises:
            CognifyValidationError: If query is invalid
            CognifyAPIError: If RAG query fails
        """
        request = RAGQueryRequest(
            query=query,
            collection_id=collection_id,
            workspace_id=workspace_id,
            response_format=response_format,
            citation_style=citation_style,
            max_context_length=max_context_length,
            include_sources=include_sources,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        logger.info(f"Submitting RAG query: {query[:50]}...")

        response = await self.client.http.arequest(
            'POST',
            '/rag/ask',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        # Create RAG response
        rag_response = RAGResponse(
            query_id=data.get('query_id', f"rag_{int(datetime.now().timestamp())}"),
            query=query,
            answer=data.get('answer', ''),
            citations=[Citation(**citation) for citation in data.get('citations', [])],
            confidence_score=data.get('confidence_score', 0.0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            ai_model_used=data.get('model_used', 'unknown'),
            tokens_used=data.get('tokens_used', 0),
            context_length=data.get('context_length', 0),
            metadata=data.get('metadata', {}),
            created_at=datetime.now()
        )

        logger.info(f"RAG query completed: {rag_response.query_id}")
        return rag_response

    def ask_sync(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        response_format: ResponseFormat = ResponseFormat.SIMPLE,
        citation_style: CitationStyle = CitationStyle.INLINE,
        max_context_length: int = 4000,
        include_sources: bool = True,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> RAGResponse:
        """
        Ask a natural language question synchronously.

        Args:
            query: Natural language question
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            response_format: Response format (default: SIMPLE)
            citation_style: Citation style (default: INLINE)
            max_context_length: Maximum context length (default: 4000)
            include_sources: Include source citations (default: True)
            temperature: Response creativity 0.0-1.0 (default: 0.7)
            max_tokens: Maximum response tokens (default: 500)

        Returns:
            RAGResponse with generated answer and citations
        """
        request = RAGQueryRequest(
            query=query,
            collection_id=collection_id,
            workspace_id=workspace_id,
            response_format=response_format,
            citation_style=citation_style,
            max_context_length=max_context_length,
            include_sources=include_sources,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        response = self.client.http.request(
            'POST',
            '/rag/ask',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        return RAGResponse(
            query_id=data.get('query_id', f"rag_{int(datetime.now().timestamp())}"),
            query=query,
            answer=data.get('answer', ''),
            citations=[Citation(**citation) for citation in data.get('citations', [])],
            confidence_score=data.get('confidence_score', 0.0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            ai_model_used=data.get('model_used', 'unknown'),
            tokens_used=data.get('tokens_used', 0),
            context_length=data.get('context_length', 0),
            metadata=data.get('metadata', {}),
            created_at=datetime.now()
        )

    async def ask_structured(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        include_code_examples: bool = True,
        include_recommendations: bool = True,
        citation_style: CitationStyle = CitationStyle.INLINE,
        max_context_length: int = 6000,
        temperature: float = 0.7
    ) -> StructuredResponse:
        """
        Ask a question and get a structured response.

        Args:
            query: Natural language question
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            include_code_examples: Include code examples (default: True)
            include_recommendations: Include recommendations (default: True)
            citation_style: Citation style (default: INLINE)
            max_context_length: Maximum context length (default: 6000)
            temperature: Response creativity (default: 0.7)

        Returns:
            StructuredResponse with organized content

        Raises:
            CognifyValidationError: If query is invalid
            CognifyAPIError: If structured query fails
        """
        request_data = {
            'query': query,
            'response_format': ResponseFormat.STRUCTURED.value,
            'citation_style': citation_style.value,
            'max_context_length': max_context_length,
            'temperature': temperature,
            'include_code_examples': include_code_examples,
            'include_recommendations': include_recommendations
        }

        if collection_id:
            request_data['collection_id'] = collection_id
        if workspace_id:
            request_data['workspace_id'] = workspace_id

        logger.info(f"Submitting structured RAG query: {query[:50]}...")

        response = await self.client.http.arequest(
            'POST',
            '/rag/ask-structured',
            json=request_data
        )

        # Parse response
        data = response.get('data', {})

        # Parse sections
        sections = []
        for section_data in data.get('sections', []):
            from .models import StructuredSection
            sections.append(StructuredSection(**section_data))

        # Parse code examples
        code_examples = []
        for code_data in data.get('code_examples', []):
            from .models import CodeExample
            code_examples.append(CodeExample(**code_data))

        structured_response = StructuredResponse(
            query_id=data.get('query_id', f"structured_{int(datetime.now().timestamp())}"),
            query=query,
            summary=data.get('summary', ''),
            sections=sections,
            code_examples=code_examples,
            recommendations=data.get('recommendations', []),
            warnings=data.get('warnings', []),
            citations=[Citation(**citation) for citation in data.get('citations', [])],
            confidence_score=data.get('confidence_score', 0.0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            ai_model_used=data.get('model_used', 'unknown'),
            tokens_used=data.get('tokens_used', 0),
            created_at=datetime.now()
        )

        logger.info(f"Structured RAG query completed: {structured_response.query_id}")
        return structured_response

    def ask_structured_sync(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        include_code_examples: bool = True,
        include_recommendations: bool = True,
        citation_style: CitationStyle = CitationStyle.INLINE,
        max_context_length: int = 6000,
        temperature: float = 0.7
    ) -> StructuredResponse:
        """
        Ask a structured question synchronously.

        Args:
            query: Natural language question
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            include_code_examples: Include code examples (default: True)
            include_recommendations: Include recommendations (default: True)
            citation_style: Citation style (default: INLINE)
            max_context_length: Maximum context length (default: 6000)
            temperature: Response creativity (default: 0.7)

        Returns:
            StructuredResponse with organized content
        """
        request_data = {
            'query': query,
            'response_format': ResponseFormat.STRUCTURED.value,
            'citation_style': citation_style.value,
            'max_context_length': max_context_length,
            'temperature': temperature,
            'include_code_examples': include_code_examples,
            'include_recommendations': include_recommendations
        }

        if collection_id:
            request_data['collection_id'] = collection_id
        if workspace_id:
            request_data['workspace_id'] = workspace_id

        response = self.client.http.request(
            'POST',
            '/rag/ask-structured',
            json=request_data
        )

        # Parse response (same logic as async version)
        data = response.get('data', {})

        # Parse sections
        sections = []
        for section_data in data.get('sections', []):
            from .models import StructuredSection
            sections.append(StructuredSection(**section_data))

        # Parse code examples
        code_examples = []
        for code_data in data.get('code_examples', []):
            from .models import CodeExample
            code_examples.append(CodeExample(**code_data))

        return StructuredResponse(
            query_id=data.get('query_id', f"structured_{int(datetime.now().timestamp())}"),
            query=query,
            summary=data.get('summary', ''),
            sections=sections,
            code_examples=code_examples,
            recommendations=data.get('recommendations', []),
            warnings=data.get('warnings', []),
            citations=[Citation(**citation) for citation in data.get('citations', [])],
            confidence_score=data.get('confidence_score', 0.0),
            processing_time_ms=data.get('processing_time_ms', 0.0),
            ai_model_used=data.get('model_used', 'unknown'),
            tokens_used=data.get('tokens_used', 0),
            created_at=datetime.now()
        )

    # Streaming Operations

    async def ask_stream(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> AsyncIterator[str]:
        """
        Ask a question with streaming response.

        Args:
            query: Natural language question
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            temperature: Response creativity (default: 0.7)
            max_tokens: Maximum response tokens (default: 1000)

        Yields:
            String chunks of the response

        Raises:
            CognifyValidationError: If query is invalid
            CognifyAPIError: If streaming fails
        """
        if not query or not query.strip():
            raise CognifyValidationError("Query cannot be empty")

        request_data = {
            'query': query.strip(),
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': True
        }

        if collection_id:
            request_data['collection_id'] = collection_id
        if workspace_id:
            request_data['workspace_id'] = workspace_id

        logger.info(f"Starting streaming RAG query: {query[:50]}...")

        # Note: This would use a streaming HTTP method in real implementation
        # For now, we'll simulate streaming behavior
        response = await self.client.http.arequest(
            'POST',
            '/rag/ask',
            json=request_data
        )

        # Simulate streaming by yielding chunks
        answer = response.get('data', {}).get('answer', '')
        chunk_size = 10  # Characters per chunk

        for i in range(0, len(answer), chunk_size):
            chunk = answer[i:i + chunk_size]
            yield chunk

    # Statistics and Health

    async def get_stats(self) -> RAGStats:
        """
        Get RAG service statistics.

        Returns:
            RAGStats with service metrics

        Raises:
            CognifyAPIError: If stats request fails
        """
        logger.debug("Getting RAG service statistics")

        response = await self.client.http.arequest(
            'GET',
            '/rag/stats'
        )

        data = response.get('data', {})

        return RAGStats(
            total_queries=data.get('total_queries', 0),
            avg_response_time_ms=data.get('avg_response_time_ms', 0.0),
            avg_confidence_score=data.get('avg_confidence_score', 0.0),
            total_tokens_used=data.get('total_tokens_used', 0),
            queries_by_format=data.get('queries_by_format', {}),
            popular_collections=data.get('popular_collections', []),
            error_rate=data.get('error_rate', 0.0),
            uptime_percentage=data.get('uptime_percentage', 0.0),
            last_updated=datetime.now()
        )

    def get_stats_sync(self) -> RAGStats:
        """
        Get RAG service statistics synchronously.

        Returns:
            RAGStats with service metrics
        """
        response = self.client.http.request(
            'GET',
            '/rag/stats'
        )

        data = response.get('data', {})

        return RAGStats(
            total_queries=data.get('total_queries', 0),
            avg_response_time_ms=data.get('avg_response_time_ms', 0.0),
            avg_confidence_score=data.get('avg_confidence_score', 0.0),
            total_tokens_used=data.get('total_tokens_used', 0),
            queries_by_format=data.get('queries_by_format', {}),
            popular_collections=data.get('popular_collections', []),
            error_rate=data.get('error_rate', 0.0),
            uptime_percentage=data.get('uptime_percentage', 0.0),
            last_updated=datetime.now()
        )

    async def health_check(self) -> Dict[str, Any]:
        """
        Check RAG service health.

        Returns:
            Health status dictionary

        Raises:
            CognifyAPIError: If health check fails
        """
        logger.debug("Performing RAG service health check")

        try:
            response = await self.client.http.arequest(
                'GET',
                '/rag/health'
            )

            health_data = response.get('data', {})

            logger.info(f"RAG service health: {health_data.get('status', 'unknown')}")
            return health_data

        except CognifyAPIError as e:
            logger.error(f"RAG health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def health_check_sync(self) -> Dict[str, Any]:
        """
        Check RAG service health synchronously.

        Returns:
            Health status dictionary
        """
        try:
            response = self.client.http.request(
                'GET',
                '/rag/health'
            )

            return response.get('data', {})

        except CognifyAPIError as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    # Sub-module properties

    @property
    def agents(self):
        """Access agents sub-module."""
        if not hasattr(self, '_agents'):
            from .agents import AgentsModule
            self._agents = AgentsModule(self)
        return self._agents