"""
Query history and analytics functionality for the Cognify SDK.

This module handles query history tracking, analytics, and export functionality.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple, TYPE_CHECKING

from .models import QueryHistoryEntry, QueryAnalytics, QueryType
from ..exceptions import CognifyValidationError, CognifyAPIError

if TYPE_CHECKING:
    from .query_module import QueryModule


logger = logging.getLogger(__name__)


class QueryHistory:
    """
    Handles query history tracking and analytics.
    """
    
    def __init__(self, query_module: "QueryModule") -> None:
        """
        Initialize query history module.
        
        Args:
            query_module: Parent query module instance
        """
        self.query = query_module
        self.client = query_module.client
    
    async def get_history(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        query_type: Optional[QueryType] = None,
        limit: int = 50,
        offset: int = 0,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[QueryHistoryEntry]:
        """
        Get user's query history.
        
        Args:
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            query_type: Filter by query type (optional)
            limit: Maximum entries (default: 50)
            offset: Number of entries to skip (default: 0)
            date_from: Start date filter (optional)
            date_to: End date filter (optional)
            
        Returns:
            List of QueryHistoryEntry objects
            
        Raises:
            CognifyValidationError: If parameters are invalid
            CognifyAPIError: If request fails
        """
        if limit < 1 or limit > 1000:
            raise CognifyValidationError("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise CognifyValidationError("Offset cannot be negative")
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        if query_type:
            params['query_type'] = query_type.value
        if date_from:
            params['date_from'] = date_from.isoformat()
        if date_to:
            params['date_to'] = date_to.isoformat()
        
        logger.debug(f"Getting query history (limit: {limit}, offset: {offset})")
        
        response = await self.client.http.arequest(
            'GET',
            '/query/history',
            params=params
        )
        
        history_data = response.get('data', [])
        history_entries = [QueryHistoryEntry(**entry) for entry in history_data]
        
        logger.debug(f"Retrieved {len(history_entries)} history entries")
        return history_entries
    
    def get_history_sync(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        query_type: Optional[QueryType] = None,
        limit: int = 50,
        offset: int = 0,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[QueryHistoryEntry]:
        """
        Get user's query history synchronously.
        
        Args:
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            query_type: Filter by query type (optional)
            limit: Maximum entries (default: 50)
            offset: Number of entries to skip (default: 0)
            date_from: Start date filter (optional)
            date_to: End date filter (optional)
            
        Returns:
            List of QueryHistoryEntry objects
        """
        if limit < 1 or limit > 1000:
            raise CognifyValidationError("Limit must be between 1 and 1000")
        
        if offset < 0:
            raise CognifyValidationError("Offset cannot be negative")
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        if query_type:
            params['query_type'] = query_type.value
        if date_from:
            params['date_from'] = date_from.isoformat()
        if date_to:
            params['date_to'] = date_to.isoformat()
        
        response = self.client.http.request(
            'GET',
            '/query/history',
            params=params
        )
        
        history_data = response.get('data', [])
        return [QueryHistoryEntry(**entry) for entry in history_data]
    
    async def get_analytics(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        days: int = 30
    ) -> QueryAnalytics:
        """
        Get search analytics and statistics.
        
        Args:
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            days: Number of days to analyze (default: 30)
            
        Returns:
            QueryAnalytics object with statistics
            
        Raises:
            CognifyValidationError: If days parameter is invalid
            CognifyAPIError: If request fails
        """
        if days < 1 or days > 365:
            raise CognifyValidationError("Days must be between 1 and 365")
        
        params = {
            'days': days,
            'type': 'analytics'
        }
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        
        logger.debug(f"Getting analytics for {days} days")
        
        response = await self.client.http.arequest(
            'GET',
            '/query/analytics',
            params=params
        )
        
        analytics_data = response.get('data', {})
        analytics = QueryAnalytics(**analytics_data)
        
        logger.debug(f"Analytics: {analytics.total_queries} total queries")
        return analytics
    
    def get_analytics_sync(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        days: int = 30
    ) -> QueryAnalytics:
        """
        Get search analytics synchronously.
        
        Args:
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            days: Number of days to analyze (default: 30)
            
        Returns:
            QueryAnalytics object with statistics
        """
        if days < 1 or days > 365:
            raise CognifyValidationError("Days must be between 1 and 365")
        
        params = {
            'days': days,
            'type': 'analytics'
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
        
        analytics_data = response.get('data', {})
        return QueryAnalytics(**analytics_data)
    
    async def export_history(
        self,
        format: str = "json",
        date_range: Optional[Tuple[datetime, datetime]] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        query_type: Optional[QueryType] = None
    ) -> Union[str, bytes]:
        """
        Export query history in specified format.
        
        Args:
            format: Export format ("json", "csv", "xlsx") (default: "json")
            date_range: Date range tuple (start, end) (optional)
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            query_type: Filter by query type (optional)
            
        Returns:
            Exported data as string (json/csv) or bytes (xlsx)
            
        Raises:
            CognifyValidationError: If format is invalid
            CognifyAPIError: If export fails
        """
        valid_formats = ["json", "csv", "xlsx"]
        if format not in valid_formats:
            raise CognifyValidationError(f"Format must be one of: {valid_formats}")
        
        params = {
            'format': format
        }
        
        if date_range:
            start_date, end_date = date_range
            params['date_from'] = start_date.isoformat()
            params['date_to'] = end_date.isoformat()
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        if query_type:
            params['query_type'] = query_type.value
        
        logger.info(f"Exporting query history in {format} format")
        
        response = await self.client.http.arequest(
            'GET',
            '/query/history/export',
            params=params
        )
        
        if format == "xlsx":
            # For binary formats, return bytes
            return response.get('data', b'')
        else:
            # For text formats, return string
            return response.get('data', '')
    
    def export_history_sync(
        self,
        format: str = "json",
        date_range: Optional[Tuple[datetime, datetime]] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        query_type: Optional[QueryType] = None
    ) -> Union[str, bytes]:
        """
        Export query history synchronously.
        
        Args:
            format: Export format ("json", "csv", "xlsx") (default: "json")
            date_range: Date range tuple (start, end) (optional)
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            query_type: Filter by query type (optional)
            
        Returns:
            Exported data as string (json/csv) or bytes (xlsx)
        """
        valid_formats = ["json", "csv", "xlsx"]
        if format not in valid_formats:
            raise CognifyValidationError(f"Format must be one of: {valid_formats}")
        
        params = {
            'format': format
        }
        
        if date_range:
            start_date, end_date = date_range
            params['date_from'] = start_date.isoformat()
            params['date_to'] = end_date.isoformat()
        
        if collection_id:
            params['collection_id'] = collection_id
        if workspace_id:
            params['workspace_id'] = workspace_id
        if query_type:
            params['query_type'] = query_type.value
        
        response = self.client.http.request(
            'GET',
            '/query/history/export',
            params=params
        )
        
        if format == "xlsx":
            return response.get('data', b'')
        else:
            return response.get('data', '')
    
    async def clear_history(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        date_before: Optional[datetime] = None,
        confirm: bool = False
    ) -> bool:
        """
        Clear query history.
        
        Args:
            collection_id: Clear only for collection (optional)
            workspace_id: Clear only for workspace (optional)
            date_before: Clear entries before this date (optional)
            confirm: Confirmation flag (required)
            
        Returns:
            True if history was cleared
            
        Raises:
            CognifyValidationError: If confirmation is missing
            CognifyAPIError: If clearing fails
        """
        if not confirm:
            raise CognifyValidationError("Must confirm history clearing with confirm=True")
        
        data = {
            'confirm': True
        }
        
        if collection_id:
            data['collection_id'] = collection_id
        if workspace_id:
            data['workspace_id'] = workspace_id
        if date_before:
            data['date_before'] = date_before.isoformat()
        
        logger.warning("Clearing query history")
        
        await self.client.http.arequest(
            'DELETE',
            '/query/history',
            json=data
        )
        
        logger.info("Query history cleared successfully")
        return True
    
    def clear_history_sync(
        self,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        date_before: Optional[datetime] = None,
        confirm: bool = False
    ) -> bool:
        """
        Clear query history synchronously.
        
        Args:
            collection_id: Clear only for collection (optional)
            workspace_id: Clear only for workspace (optional)
            date_before: Clear entries before this date (optional)
            confirm: Confirmation flag (required)
            
        Returns:
            True if history was cleared
        """
        if not confirm:
            raise CognifyValidationError("Must confirm history clearing with confirm=True")
        
        data = {
            'confirm': True
        }
        
        if collection_id:
            data['collection_id'] = collection_id
        if workspace_id:
            data['workspace_id'] = workspace_id
        if date_before:
            data['date_before'] = date_before.isoformat()
        
        self.client.http.request(
            'DELETE',
            '/query/history',
            json=data
        )
        
        return True
