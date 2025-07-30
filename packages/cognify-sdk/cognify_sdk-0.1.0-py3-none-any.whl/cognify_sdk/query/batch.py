"""
Batch query processing functionality for the Cognify SDK.

This module handles batch processing of multiple queries with
parallel execution and result aggregation.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .models import (
    BatchQueryRequest,
    BatchQueryResponse,
    QueryResponse,
    RAGResponse,
    SearchMode,
    QueryType,
)
from ..exceptions import CognifyValidationError, CognifyAPIError

if TYPE_CHECKING:
    from .query_module import QueryModule


logger = logging.getLogger(__name__)


class BatchQueryProcessor:
    """
    Handles batch processing of multiple queries.
    """
    
    def __init__(self, query_module: "QueryModule") -> None:
        """
        Initialize batch query processor.
        
        Args:
            query_module: Parent query module instance
        """
        self.query = query_module
        self.client = query_module.client
        self._max_concurrent = 10  # Maximum concurrent queries
    
    async def batch_search(
        self,
        queries: List[str],
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        parallel: bool = True,
        max_concurrent: int = 5
    ) -> BatchQueryResponse:
        """
        Process multiple search queries in batch.
        
        Args:
            queries: List of search queries
            mode: Search mode for all queries (default: HYBRID)
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Results per query (default: 10)
            parallel: Process queries in parallel (default: True)
            max_concurrent: Maximum concurrent queries (default: 5)
            
        Returns:
            BatchQueryResponse with all results
            
        Raises:
            CognifyValidationError: If queries are invalid
            CognifyAPIError: If batch processing fails
        """
        if not queries:
            raise CognifyValidationError("At least one query is required")
        
        if len(queries) > 50:
            raise CognifyValidationError("Cannot process more than 50 queries at once")
        
        if max_concurrent > self._max_concurrent:
            max_concurrent = self._max_concurrent
        
        batch_id = f"batch_search_{int(time.time())}"
        start_time = time.time()
        
        logger.info(f"Starting batch search: {len(queries)} queries (parallel: {parallel})")
        
        results = []
        successful_queries = 0
        failed_queries = 0
        
        if parallel:
            # Process queries in parallel with semaphore for concurrency control
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_single_query(query: str) -> Optional[QueryResponse]:
                async with semaphore:
                    try:
                        result = await self.query.search(
                            query=query,
                            mode=mode,
                            collection_id=collection_id,
                            workspace_id=workspace_id,
                            limit=limit
                        )
                        return result
                    except Exception as e:
                        logger.error(f"Failed to process query '{query}': {e}")
                        return None
            
            # Execute all queries concurrently
            tasks = [process_single_query(query) for query in queries]
            query_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(query_results):
                if isinstance(result, Exception):
                    logger.error(f"Query {i} failed: {result}")
                    failed_queries += 1
                elif result is None:
                    failed_queries += 1
                else:
                    results.append(result)
                    successful_queries += 1
        
        else:
            # Process queries sequentially
            for query in queries:
                try:
                    result = await self.query.search(
                        query=query,
                        mode=mode,
                        collection_id=collection_id,
                        workspace_id=workspace_id,
                        limit=limit
                    )
                    results.append(result)
                    successful_queries += 1
                except Exception as e:
                    logger.error(f"Failed to process query '{query}': {e}")
                    failed_queries += 1
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        batch_response = BatchQueryResponse(
            batch_id=batch_id,
            total_queries=len(queries),
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            results=results,
            processing_time_ms=processing_time_ms,
            created_at=datetime.now()
        )
        
        logger.info(
            f"Batch search completed: {successful_queries}/{len(queries)} successful "
            f"({processing_time_ms:.1f}ms)"
        )
        
        return batch_response
    
    def batch_search_sync(
        self,
        queries: List[str],
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10
    ) -> BatchQueryResponse:
        """
        Process multiple search queries synchronously.
        
        Args:
            queries: List of search queries
            mode: Search mode for all queries (default: HYBRID)
            collection_id: Collection to search (optional)
            workspace_id: Workspace to search (optional)
            limit: Results per query (default: 10)
            
        Returns:
            BatchQueryResponse with all results
        """
        if not queries:
            raise CognifyValidationError("At least one query is required")
        
        if len(queries) > 50:
            raise CognifyValidationError("Cannot process more than 50 queries at once")
        
        batch_id = f"batch_search_sync_{int(time.time())}"
        start_time = time.time()
        
        results = []
        successful_queries = 0
        failed_queries = 0
        
        for query in queries:
            try:
                result = self.query.search_sync(
                    query=query,
                    mode=mode,
                    collection_id=collection_id,
                    workspace_id=workspace_id,
                    limit=limit
                )
                results.append(result)
                successful_queries += 1
            except Exception as e:
                logger.error(f"Failed to process query '{query}': {e}")
                failed_queries += 1
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return BatchQueryResponse(
            batch_id=batch_id,
            total_queries=len(queries),
            successful_queries=successful_queries,
            failed_queries=failed_queries,
            results=results,
            processing_time_ms=processing_time_ms,
            created_at=datetime.now()
        )
    
    async def batch_rag_queries(
        self,
        queries: List[str],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context_limit: int = 5,
        parallel: bool = True,
        max_concurrent: int = 3
    ) -> List[RAGResponse]:
        """
        Process multiple RAG queries in batch.
        
        Args:
            queries: List of RAG queries
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            context_limit: Context limit per query (default: 5)
            parallel: Process queries in parallel (default: True)
            max_concurrent: Maximum concurrent queries (default: 3)
            
        Returns:
            List of RAGResponse objects
            
        Raises:
            CognifyValidationError: If queries are invalid
        """
        if not queries:
            raise CognifyValidationError("At least one query is required")
        
        if len(queries) > 20:
            raise CognifyValidationError("Cannot process more than 20 RAG queries at once")
        
        if max_concurrent > 5:  # RAG queries are more resource intensive
            max_concurrent = 5
        
        logger.info(f"Starting batch RAG queries: {len(queries)} queries (parallel: {parallel})")
        
        results = []
        
        if parallel:
            # Process RAG queries in parallel with lower concurrency
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_single_rag_query(query: str) -> Optional[RAGResponse]:
                async with semaphore:
                    try:
                        result = await self.query.ask(
                            query=query,
                            collection_id=collection_id,
                            workspace_id=workspace_id,
                            context_limit=context_limit
                        )
                        return result
                    except Exception as e:
                        logger.error(f"Failed to process RAG query '{query}': {e}")
                        return None
            
            # Execute all RAG queries concurrently
            tasks = [process_single_rag_query(query) for query in queries]
            rag_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for i, result in enumerate(rag_results):
                if isinstance(result, Exception):
                    logger.error(f"RAG query {i} failed: {result}")
                elif result is not None:
                    results.append(result)
        
        else:
            # Process RAG queries sequentially
            for query in queries:
                try:
                    result = await self.query.ask(
                        query=query,
                        collection_id=collection_id,
                        workspace_id=workspace_id,
                        context_limit=context_limit
                    )
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to process RAG query '{query}': {e}")
        
        logger.info(f"Batch RAG queries completed: {len(results)}/{len(queries)} successful")
        return results
    
    def batch_rag_queries_sync(
        self,
        queries: List[str],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context_limit: int = 5
    ) -> List[RAGResponse]:
        """
        Process multiple RAG queries synchronously.
        
        Args:
            queries: List of RAG queries
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            context_limit: Context limit per query (default: 5)
            
        Returns:
            List of RAGResponse objects
        """
        if not queries:
            raise CognifyValidationError("At least one query is required")
        
        if len(queries) > 20:
            raise CognifyValidationError("Cannot process more than 20 RAG queries at once")
        
        results = []
        
        for query in queries:
            try:
                result = self.query.ask_sync(
                    query=query,
                    collection_id=collection_id,
                    workspace_id=workspace_id,
                    context_limit=context_limit
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process RAG query '{query}': {e}")
        
        return results
    
    async def batch_mixed_queries(
        self,
        search_queries: List[str],
        rag_queries: List[str],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        search_mode: SearchMode = SearchMode.HYBRID,
        search_limit: int = 10,
        context_limit: int = 5
    ) -> Dict[str, Any]:
        """
        Process mixed batch of search and RAG queries.
        
        Args:
            search_queries: List of search queries
            rag_queries: List of RAG queries
            collection_id: Collection to query (optional)
            workspace_id: Workspace to query (optional)
            search_mode: Search mode (default: HYBRID)
            search_limit: Search results limit (default: 10)
            context_limit: RAG context limit (default: 5)
            
        Returns:
            Dictionary with search and RAG results
        """
        logger.info(
            f"Processing mixed batch: {len(search_queries)} search, "
            f"{len(rag_queries)} RAG queries"
        )
        
        # Process both types concurrently
        search_task = None
        rag_task = None
        
        if search_queries:
            search_task = self.batch_search(
                queries=search_queries,
                mode=search_mode,
                collection_id=collection_id,
                workspace_id=workspace_id,
                limit=search_limit
            )
        
        if rag_queries:
            rag_task = self.batch_rag_queries(
                queries=rag_queries,
                collection_id=collection_id,
                workspace_id=workspace_id,
                context_limit=context_limit
            )
        
        # Wait for both to complete
        search_results = None
        rag_results = None
        
        if search_task and rag_task:
            search_results, rag_results = await asyncio.gather(search_task, rag_task)
        elif search_task:
            search_results = await search_task
        elif rag_task:
            rag_results = await rag_task
        
        return {
            'search_results': search_results,
            'rag_results': rag_results,
            'total_search_queries': len(search_queries),
            'total_rag_queries': len(rag_queries)
        }
