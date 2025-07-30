"""
Analytics functionality for conversations.

This module handles conversation analytics, user behavior insights,
and team collaboration metrics.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING

from .models import (
    ConversationStats,
    UserProfile,
    TeamAnalytics,
    ConversationExportRequest,
)
from ..exceptions import CognifyAPIError, CognifyValidationError

if TYPE_CHECKING:
    from .conversations_module import ConversationsModule


logger = logging.getLogger(__name__)


class ConversationAnalytics:
    """
    Handles conversation analytics and insights.
    """
    
    def __init__(self, conversations_module: "ConversationsModule") -> None:
        """
        Initialize analytics module.
        
        Args:
            conversations_module: Parent conversations module instance
        """
        self.conversations = conversations_module
        self.client = conversations_module.client
    
    # User Analytics
    
    async def get_user_profile(
        self,
        user_id: Optional[str] = None,
        days_back: int = 30
    ) -> UserProfile:
        """
        Get comprehensive user behavior profile.
        
        Args:
            user_id: User identifier (optional, defaults to current user)
            days_back: Number of days to analyze (default: 30)
            
        Returns:
            UserProfile with behavior insights
            
        Raises:
            CognifyAPIError: If profile request fails
        """
        if days_back < 1 or days_back > 365:
            raise CognifyValidationError("days_back must be between 1 and 365")
        
        params = {'days_back': days_back}
        if user_id:
            params['user_id'] = user_id
        
        logger.debug(f"Getting user profile for {days_back} days")
        
        response = await self.client.http.arequest(
            'GET',
            '/conversations/analytics/profile',
            params=params
        )
        
        data = response.get('data', {})
        
        return UserProfile(
            user_id=data.get('user_id', 'current_user'),
            total_conversations=data.get('total_conversations', 0),
            total_turns=data.get('total_turns', 0),
            avg_turns_per_conversation=data.get('avg_turns_per_conversation', 0.0),
            total_time_minutes=data.get('total_time_minutes', 0.0),
            favorite_topics=data.get('favorite_topics', []),
            preferred_collections=data.get('preferred_collections', []),
            conversation_patterns=data.get('conversation_patterns', {}),
            activity_by_hour=data.get('activity_by_hour', {}),
            last_activity=datetime.now()
        )
    
    def get_user_profile_sync(
        self,
        user_id: Optional[str] = None,
        days_back: int = 30
    ) -> UserProfile:
        """
        Get user profile synchronously.
        
        Args:
            user_id: User identifier (optional)
            days_back: Number of days to analyze (default: 30)
            
        Returns:
            UserProfile with behavior insights
        """
        if days_back < 1 or days_back > 365:
            raise CognifyValidationError("days_back must be between 1 and 365")
        
        params = {'days_back': days_back}
        if user_id:
            params['user_id'] = user_id
        
        response = self.client.http.request(
            'GET',
            '/conversations/analytics/profile',
            params=params
        )
        
        data = response.get('data', {})
        
        return UserProfile(
            user_id=data.get('user_id', 'current_user'),
            total_conversations=data.get('total_conversations', 0),
            total_turns=data.get('total_turns', 0),
            avg_turns_per_conversation=data.get('avg_turns_per_conversation', 0.0),
            total_time_minutes=data.get('total_time_minutes', 0.0),
            favorite_topics=data.get('favorite_topics', []),
            preferred_collections=data.get('preferred_collections', []),
            conversation_patterns=data.get('conversation_patterns', {}),
            activity_by_hour=data.get('activity_by_hour', {}),
            last_activity=datetime.now()
        )
    
    # Team Analytics
    
    async def get_team_analytics(
        self,
        team_id: Optional[str] = None,
        days_back: int = 30
    ) -> TeamAnalytics:
        """
        Get team analytics and collaboration insights.
        
        Args:
            team_id: Team identifier (optional)
            days_back: Number of days to analyze (default: 30)
            
        Returns:
            TeamAnalytics with collaboration metrics
            
        Raises:
            CognifyAPIError: If analytics request fails
        """
        if days_back < 1 or days_back > 365:
            raise CognifyValidationError("days_back must be between 1 and 365")
        
        params = {'days_back': days_back}
        if team_id:
            params['team_id'] = team_id
        
        logger.debug(f"Getting team analytics for {days_back} days")
        
        response = await self.client.http.arequest(
            'GET',
            '/conversations/analytics/team',
            params=params
        )
        
        data = response.get('data', {})
        
        return TeamAnalytics(
            team_id=data.get('team_id', 'current_team'),
            total_team_conversations=data.get('total_team_conversations', 0),
            active_users=data.get('active_users', 0),
            collaboration_score=data.get('collaboration_score', 0.0),
            trending_topics=data.get('trending_topics', []),
            knowledge_sharing_metrics=data.get('knowledge_sharing_metrics', {}),
            user_contributions=data.get('user_contributions', {}),
            peak_activity_hours=data.get('peak_activity_hours', []),
            cross_collection_usage=data.get('cross_collection_usage', {}),
            last_updated=datetime.now()
        )
    
    def get_team_analytics_sync(
        self,
        team_id: Optional[str] = None,
        days_back: int = 30
    ) -> TeamAnalytics:
        """
        Get team analytics synchronously.
        
        Args:
            team_id: Team identifier (optional)
            days_back: Number of days to analyze (default: 30)
            
        Returns:
            TeamAnalytics with collaboration metrics
        """
        if days_back < 1 or days_back > 365:
            raise CognifyValidationError("days_back must be between 1 and 365")
        
        params = {'days_back': days_back}
        if team_id:
            params['team_id'] = team_id
        
        response = self.client.http.request(
            'GET',
            '/conversations/analytics/team',
            params=params
        )
        
        data = response.get('data', {})
        
        return TeamAnalytics(
            team_id=data.get('team_id', 'current_team'),
            total_team_conversations=data.get('total_team_conversations', 0),
            active_users=data.get('active_users', 0),
            collaboration_score=data.get('collaboration_score', 0.0),
            trending_topics=data.get('trending_topics', []),
            knowledge_sharing_metrics=data.get('knowledge_sharing_metrics', {}),
            user_contributions=data.get('user_contributions', {}),
            peak_activity_hours=data.get('peak_activity_hours', []),
            cross_collection_usage=data.get('cross_collection_usage', {}),
            last_updated=datetime.now()
        )
    
    # System Statistics
    
    async def get_conversation_stats(self) -> ConversationStats:
        """
        Get conversation system statistics.
        
        Returns:
            ConversationStats with system metrics
            
        Raises:
            CognifyAPIError: If stats request fails
        """
        logger.debug("Getting conversation system statistics")
        
        response = await self.client.http.arequest(
            'GET',
            '/conversations/stats'
        )
        
        data = response.get('data', {})
        
        return ConversationStats(
            total_sessions=data.get('total_sessions', 0),
            active_sessions=data.get('active_sessions', 0),
            total_turns=data.get('total_turns', 0),
            avg_turns_per_session=data.get('avg_turns_per_session', 0.0),
            avg_session_duration_minutes=data.get('avg_session_duration_minutes', 0.0),
            total_tokens_used=data.get('total_tokens_used', 0),
            popular_topics=data.get('popular_topics', []),
            user_activity=data.get('user_activity', {}),
            collection_usage=data.get('collection_usage', {}),
            last_updated=datetime.now()
        )
    
    def get_conversation_stats_sync(self) -> ConversationStats:
        """
        Get conversation statistics synchronously.
        
        Returns:
            ConversationStats with system metrics
        """
        response = self.client.http.request(
            'GET',
            '/conversations/stats'
        )
        
        data = response.get('data', {})
        
        return ConversationStats(
            total_sessions=data.get('total_sessions', 0),
            active_sessions=data.get('active_sessions', 0),
            total_turns=data.get('total_turns', 0),
            avg_turns_per_session=data.get('avg_turns_per_session', 0.0),
            avg_session_duration_minutes=data.get('avg_session_duration_minutes', 0.0),
            total_tokens_used=data.get('total_tokens_used', 0),
            popular_topics=data.get('popular_topics', []),
            user_activity=data.get('user_activity', {}),
            collection_usage=data.get('collection_usage', {}),
            last_updated=datetime.now()
        )
    
    # Export Functionality
    
    async def export_conversations(
        self,
        session_ids: Optional[List[str]] = None,
        format: str = "json",
        include_context: bool = True,
        include_metadata: bool = False,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Union[str, bytes]:
        """
        Export conversations in specified format.
        
        Args:
            session_ids: Specific sessions to export (optional)
            format: Export format (json, markdown, csv, xlsx)
            include_context: Include conversation context (default: True)
            include_metadata: Include metadata (default: False)
            date_from: Export from date (optional)
            date_to: Export to date (optional)
            
        Returns:
            Exported data as string or bytes
            
        Raises:
            CognifyValidationError: If export parameters are invalid
            CognifyAPIError: If export fails
        """
        request = ConversationExportRequest(
            session_ids=session_ids,
            format=format,
            include_context=include_context,
            include_metadata=include_metadata,
            date_from=date_from,
            date_to=date_to
        )
        
        logger.info(f"Exporting conversations in {format} format")
        
        response = await self.client.http.arequest(
            'POST',
            '/conversations/export',
            json=request.dict(exclude_none=True)
        )
        
        # Handle different response types
        if format.lower() in ['xlsx']:
            return response.get('data', b'')  # Binary data
        else:
            return response.get('data', '')  # Text data
    
    def export_conversations_sync(
        self,
        session_ids: Optional[List[str]] = None,
        format: str = "json",
        include_context: bool = True,
        include_metadata: bool = False,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Union[str, bytes]:
        """
        Export conversations synchronously.
        
        Args:
            session_ids: Specific sessions to export (optional)
            format: Export format (json, markdown, csv, xlsx)
            include_context: Include conversation context (default: True)
            include_metadata: Include metadata (default: False)
            date_from: Export from date (optional)
            date_to: Export to date (optional)
            
        Returns:
            Exported data as string or bytes
        """
        request = ConversationExportRequest(
            session_ids=session_ids,
            format=format,
            include_context=include_context,
            include_metadata=include_metadata,
            date_from=date_from,
            date_to=date_to
        )
        
        response = self.client.http.request(
            'POST',
            '/conversations/export',
            json=request.dict(exclude_none=True)
        )
        
        # Handle different response types
        if format.lower() in ['xlsx']:
            return response.get('data', b'')  # Binary data
        else:
            return response.get('data', '')  # Text data
