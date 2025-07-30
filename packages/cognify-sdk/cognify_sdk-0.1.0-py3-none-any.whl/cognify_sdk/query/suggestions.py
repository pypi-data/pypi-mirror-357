"""
Search suggestions functionality for the Cognify SDK.

This module handles search suggestions, autocomplete, and query recommendations.
"""

import logging
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .models import SuggestionRequest, QueryType
from ..exceptions import CognifyValidationError, CognifyAPIError

if TYPE_CHECKING:
    from .query_module import QueryModule


logger = logging.getLogger(__name__)


class SuggestionsModule:
    """
    Handles search suggestions and query recommendations.
    """
    
    def __init__(self, query_module: "QueryModule") -> None:
        """
        Initialize suggestions module.
        
        Args:
            query_module: Parent query module instance
        """
        self.query = query_module
        self.client = query_module.client
    
    async def get_suggestions(
        self,
        query_prefix: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        include_popular: bool = True
    ) -> List[str]:
        """
        Get search suggestions based on query prefix.
        
        Args:
            query_prefix: Query prefix for suggestions
            collection_id: Collection context (optional)
            workspace_id: Workspace context (optional)
            limit: Maximum suggestions (default: 10)
            include_popular: Include popular queries (default: True)
            
        Returns:
            List of suggested query strings
            
        Raises:
            CognifyValidationError: If prefix is invalid
            CognifyAPIError: If request fails
        """
        if not query_prefix or len(query_prefix.strip()) < 2:
            raise CognifyValidationError("Query prefix must be at least 2 characters")
        
        request = SuggestionRequest(
            query_prefix=query_prefix,
            collection_id=collection_id,
            workspace_id=workspace_id,
            limit=limit,
            include_popular=include_popular
        )
        
        logger.debug(f"Getting suggestions for: {query_prefix}")
        
        params = request.dict(exclude_none=True)
        
        response = await self.client.http.arequest(
            'GET',
            '/query/suggestions',
            params=params
        )
        
        suggestions = response.get('data', {}).get('suggestions', [])
        logger.debug(f"Found {len(suggestions)} suggestions")
        
        return suggestions
    
    def get_suggestions_sync(
        self,
        query_prefix: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        include_popular: bool = True
    ) -> List[str]:
        """
        Get search suggestions synchronously.
        
        Args:
            query_prefix: Query prefix for suggestions
            collection_id: Collection context (optional)
            workspace_id: Workspace context (optional)
            limit: Maximum suggestions (default: 10)
            include_popular: Include popular queries (default: True)
            
        Returns:
            List of suggested query strings
        """
        if not query_prefix or len(query_prefix.strip()) < 2:
            raise CognifyValidationError("Query prefix must be at least 2 characters")
        
        request = SuggestionRequest(
            query_prefix=query_prefix,
            collection_id=collection_id,
            workspace_id=workspace_id,
            limit=limit,
            include_popular=include_popular
        )
        
        params = request.dict(exclude_none=True)
        
        response = self.client.http.request(
            'GET',
            '/query/suggestions',
            params=params
        )
        
        return response.get('data', {}).get('suggestions', [])
    
    async def get_popular_queries(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get popular queries for collection.
        
        Args:
            collection_id: Collection to analyze (optional)
            workspace_id: Workspace to analyze (optional)
            days: Number of days to analyze (default: 30)
            limit: Maximum queries (default: 10)
            
        Returns:
            List of popular query dictionaries with counts
        """
        params = {
            'days': days,
            'limit': limit,
            'type': 'popular'
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        logger.debug(f"Getting popular queries for {days} days")
        
        response = await self.client.http.arequest(
            'GET',
            '/query/analytics',
            params=params
        )
        
        popular_queries = response.get('data', {}).get('popular_queries', [])
        logger.debug(f"Found {len(popular_queries)} popular queries")
        
        return popular_queries
    
    def get_popular_queries_sync(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get popular queries synchronously.
        
        Args:
            collection_id: Collection to analyze (optional)
            workspace_id: Workspace to analyze (optional)
            days: Number of days to analyze (default: 30)
            limit: Maximum queries (default: 10)
            
        Returns:
            List of popular query dictionaries with counts
        """
        params = {
            'days': days,
            'limit': limit,
            'type': 'popular'
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        response = self.client.http.request(
            'GET',
            '/query/analytics',
            params=params
        )
        
        return response.get('data', {}).get('popular_queries', [])
    
    async def get_related_queries(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 5
    ) -> List[str]:
        """
        Get queries related to the given query.
        
        Args:
            query: Base query for finding related queries
            collection_id: Collection context (optional)
            workspace_id: Workspace context (optional)
            limit: Maximum related queries (default: 5)
            
        Returns:
            List of related query strings
        """
        if not query or not query.strip():
            raise CognifyValidationError("Query cannot be empty")
        
        params = {
            'query': query.strip(),
            'limit': limit,
            'type': 'related'
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        logger.debug(f"Getting related queries for: {query[:50]}...")
        
        response = await self.client.http.arequest(
            'GET',
            '/query/suggestions',
            params=params
        )
        
        related_queries = response.get('data', {}).get('related_queries', [])
        logger.debug(f"Found {len(related_queries)} related queries")
        
        return related_queries
    
    def get_related_queries_sync(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 5
    ) -> List[str]:
        """
        Get related queries synchronously.
        
        Args:
            query: Base query for finding related queries
            collection_id: Collection context (optional)
            workspace_id: Workspace context (optional)
            limit: Maximum related queries (default: 5)
            
        Returns:
            List of related query strings
        """
        if not query or not query.strip():
            raise CognifyValidationError("Query cannot be empty")
        
        params = {
            'query': query.strip(),
            'limit': limit,
            'type': 'related'
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        response = self.client.http.request(
            'GET',
            '/query/suggestions',
            params=params
        )
        
        return response.get('data', {}).get('related_queries', [])
    
    async def get_trending_queries(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        hours: int = 24,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending queries in the specified time period.
        
        Args:
            collection_id: Collection to analyze (optional)
            workspace_id: Workspace to analyze (optional)
            hours: Number of hours to analyze (default: 24)
            limit: Maximum queries (default: 10)
            
        Returns:
            List of trending query dictionaries
        """
        params = {
            'hours': hours,
            'limit': limit,
            'type': 'trending'
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        logger.debug(f"Getting trending queries for {hours} hours")
        
        response = await self.client.http.arequest(
            'GET',
            '/query/analytics',
            params=params
        )
        
        trending_queries = response.get('data', {}).get('trending_queries', [])
        logger.debug(f"Found {len(trending_queries)} trending queries")
        
        return trending_queries
    
    def get_trending_queries_sync(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        hours: int = 24,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get trending queries synchronously.
        
        Args:
            collection_id: Collection to analyze (optional)
            workspace_id: Workspace to analyze (optional)
            hours: Number of hours to analyze (default: 24)
            limit: Maximum queries (default: 10)
            
        Returns:
            List of trending query dictionaries
        """
        params = {
            'hours': hours,
            'limit': limit,
            'type': 'trending'
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        response = self.client.http.request(
            'GET',
            '/query/analytics',
            params=params
        )
        
        return response.get('data', {}).get('trending_queries', [])
