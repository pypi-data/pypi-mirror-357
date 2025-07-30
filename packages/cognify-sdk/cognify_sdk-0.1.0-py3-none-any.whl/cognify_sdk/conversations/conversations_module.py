"""
Main conversations module for the Cognify SDK.

This module provides the primary interface for conversation management,
multi-turn dialogue, and context-aware interactions.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from .models import (
    ConversationSession,
    ConversationTurn,
    ConversationContext,
    ConversationStatus,
    ConversationStartRequest,
    ConversationQueryRequest,
    ConversationHistoryRequest,
    ConversationStats,
)
from .context_manager import ConversationContextManager
from ..exceptions import CognifyValidationError, CognifyAPIError, CognifyNotFoundError

if TYPE_CHECKING:
    from ..client import CognifyClient


logger = logging.getLogger(__name__)


class ConversationsModule:
    """
    Main conversations module for the Cognify SDK.

    This class provides methods for conversation session management,
    context-aware queries, and conversation history.
    """

    def __init__(self, client: "CognifyClient") -> None:
        """
        Initialize conversations module.

        Args:
            client: Cognify client instance
        """
        self.client = client
        self.context_manager = ConversationContextManager()

    # Session Management

    async def start_session(
        self,
        title: Optional[str] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationSession:
        """
        Start a new conversation session.

        Args:
            title: Session title (optional)
            collection_id: Collection to focus on (optional)
            workspace_id: Workspace to use (optional)
            context: Initial context (optional)
            tags: Session tags (optional)
            metadata: Additional metadata (optional)

        Returns:
            ConversationSession object

        Raises:
            CognifyAPIError: If session creation fails
        """
        request = ConversationStartRequest(
            title=title,
            collection_id=collection_id,
            workspace_id=workspace_id,
            context=context,
            tags=tags or [],
            metadata=metadata or {}
        )

        logger.info(f"Starting new conversation session: {title or 'Untitled'}")

        response = await self.client.http.arequest(
            'POST',
            '/conversations/start',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        session = ConversationSession(
            id=data.get('id', f"session_{uuid.uuid4().hex[:8]}"),
            user_id=data.get('user_id', 'default_user'),
            title=title,
            status=ConversationStatus.ACTIVE,
            collection_id=collection_id,
            workspace_id=workspace_id,
            started_at=datetime.now(),
            last_activity=datetime.now(),
            turn_count=0,
            total_tokens=0,
            metadata=metadata or {},
            tags=tags or []
        )

        logger.info(f"Started conversation session: {session.id}")
        return session

    def start_session_sync(
        self,
        title: Optional[str] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationSession:
        """
        Start a new conversation session synchronously.

        Args:
            title: Session title (optional)
            collection_id: Collection to focus on (optional)
            workspace_id: Workspace to use (optional)
            context: Initial context (optional)
            tags: Session tags (optional)
            metadata: Additional metadata (optional)

        Returns:
            ConversationSession object
        """
        request = ConversationStartRequest(
            title=title,
            collection_id=collection_id,
            workspace_id=workspace_id,
            context=context,
            tags=tags or [],
            metadata=metadata or {}
        )

        response = self.client.http.request(
            'POST',
            '/conversations/start',
            json=request.model_dump(exclude_none=True)
        )

        # Parse response
        data = response.get('data', {})

        return ConversationSession(
            id=data.get('id', f"session_{uuid.uuid4().hex[:8]}"),
            user_id=data.get('user_id', 'default_user'),
            title=title,
            status=ConversationStatus.ACTIVE,
            collection_id=collection_id,
            workspace_id=workspace_id,
            started_at=datetime.now(),
            last_activity=datetime.now(),
            turn_count=0,
            total_tokens=0,
            metadata=metadata or {},
            tags=tags or []
        )

    async def end_session(self, session_id: str) -> bool:
        """
        End a conversation session.

        Args:
            session_id: Session identifier

        Returns:
            True if session was ended successfully

        Raises:
            CognifyNotFoundError: If session not found
            CognifyAPIError: If ending session fails
        """
        logger.info(f"Ending conversation session: {session_id}")

        try:
            response = await self.client.http.arequest(
                'POST',
                f'/conversations/end/{session_id}'
            )

            # Clean up local context
            if session_id in self.context_manager.active_sessions:
                del self.context_manager.active_sessions[session_id]

            logger.info(f"Successfully ended session: {session_id}")
            return response.get('data', {}).get('success', True)

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    def end_session_sync(self, session_id: str) -> bool:
        """
        End a conversation session synchronously.

        Args:
            session_id: Session identifier

        Returns:
            True if session was ended successfully
        """
        try:
            response = self.client.http.request(
                'POST',
                f'/conversations/end/{session_id}'
            )

            # Clean up local context
            if session_id in self.context_manager.active_sessions:
                del self.context_manager.active_sessions[session_id]

            return response.get('data', {}).get('success', True)

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    async def get_session_context(
        self,
        session_id: str,
        max_turns: int = 10
    ) -> ConversationContext:
        """
        Get detailed context for a conversation session.

        Args:
            session_id: Session identifier
            max_turns: Maximum number of turns to include

        Returns:
            ConversationContext object

        Raises:
            CognifyNotFoundError: If session not found
            CognifyAPIError: If context retrieval fails
        """
        logger.debug(f"Getting context for session: {session_id}")

        # Check local context first
        local_context = self.context_manager.get_session_context(session_id)
        if local_context:
            return local_context

        # Fetch from API
        try:
            response = await self.client.http.arequest(
                'GET',
                f'/conversations/context/{session_id}',
                params={'max_turns': max_turns}
            )

            data = response.get('data', {})

            # Parse turns
            turns = []
            for turn_data in data.get('recent_turns', []):
                turns.append(ConversationTurn(**turn_data))

            context = ConversationContext(
                session_id=session_id,
                recent_turns=turns,
                user_preferences=data.get('user_preferences', {}),
                conversation_summary=data.get('conversation_summary', ''),
                key_topics=data.get('key_topics', []),
                relevant_documents=data.get('relevant_documents', []),
                context_length=data.get('context_length', 0),
                last_updated=datetime.now()
            )

            # Store in local context manager
            self.context_manager.active_sessions[session_id] = context

            logger.debug(f"Retrieved context for session {session_id}: {len(turns)} turns")
            return context

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    def get_session_context_sync(
        self,
        session_id: str,
        max_turns: int = 10
    ) -> ConversationContext:
        """
        Get session context synchronously.

        Args:
            session_id: Session identifier
            max_turns: Maximum number of turns to include

        Returns:
            ConversationContext object
        """
        # Check local context first
        local_context = self.context_manager.get_session_context(session_id)
        if local_context:
            return local_context

        # Fetch from API
        try:
            response = self.client.http.request(
                'GET',
                f'/conversations/context/{session_id}',
                params={'max_turns': max_turns}
            )

            data = response.get('data', {})

            # Parse turns
            turns = []
            for turn_data in data.get('recent_turns', []):
                turns.append(ConversationTurn(**turn_data))

            context = ConversationContext(
                session_id=session_id,
                recent_turns=turns,
                user_preferences=data.get('user_preferences', {}),
                conversation_summary=data.get('conversation_summary', ''),
                key_topics=data.get('key_topics', []),
                relevant_documents=data.get('relevant_documents', []),
                context_length=data.get('context_length', 0),
                last_updated=datetime.now()
            )

            # Store in local context manager
            self.context_manager.active_sessions[session_id] = context

            return context

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    # Context-Aware Queries

    async def ask(
        self,
        query: str,
        session_id: str,
        include_context: bool = True,
        max_context_turns: int = 5,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> ConversationTurn:
        """
        Ask a question with conversation context.

        Args:
            query: User query
            session_id: Session identifier
            include_context: Include conversation context (default: True)
            max_context_turns: Maximum turns to include in context (default: 5)
            temperature: Response creativity (default: 0.7)
            max_tokens: Maximum response tokens (default: 500)

        Returns:
            ConversationTurn with response

        Raises:
            CognifyValidationError: If query is invalid
            CognifyNotFoundError: If session not found
            CognifyAPIError: If query fails
        """
        request = ConversationQueryRequest(
            query=query,
            session_id=session_id,
            include_context=include_context,
            max_context_turns=max_context_turns,
            temperature=temperature,
            max_tokens=max_tokens
        )

        logger.info(f"Asking question in session {session_id}: {query[:50]}...")

        # Get context if requested
        context_str = ""
        if include_context:
            context_str = self.context_manager.get_context_for_query(
                session_id, max_context_turns
            )

        # Prepare request data
        request_data = request.model_dump(exclude_none=True)
        if context_str:
            request_data['context'] = context_str

        try:
            response = await self.client.http.arequest(
                'POST',
                '/conversations/ask',
                json=request_data
            )

            # Parse response
            data = response.get('data', {})

            turn = ConversationTurn(
                id=data.get('id', f"turn_{uuid.uuid4().hex[:8]}"),
                session_id=session_id,
                query=query,
                response=data.get('response', ''),
                timestamp=datetime.now(),
                processing_time_ms=data.get('processing_time_ms', 0.0),
                sources=data.get('sources', []),
                metadata=data.get('metadata', {}),
                context_used=context_str if include_context else None,
                confidence_score=data.get('confidence_score', 0.0),
                tokens_used=data.get('tokens_used', 0)
            )

            # Add turn to context manager
            self.context_manager.add_turn(session_id, turn)

            logger.info(f"Question answered in session {session_id}: {turn.id}")
            return turn

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    def ask_sync(
        self,
        query: str,
        session_id: str,
        include_context: bool = True,
        max_context_turns: int = 5,
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> ConversationTurn:
        """
        Ask a question synchronously.

        Args:
            query: User query
            session_id: Session identifier
            include_context: Include conversation context (default: True)
            max_context_turns: Maximum turns to include in context (default: 5)
            temperature: Response creativity (default: 0.7)
            max_tokens: Maximum response tokens (default: 500)

        Returns:
            ConversationTurn with response
        """
        request = ConversationQueryRequest(
            query=query,
            session_id=session_id,
            include_context=include_context,
            max_context_turns=max_context_turns,
            temperature=temperature,
            max_tokens=max_tokens
        )

        # Get context if requested
        context_str = ""
        if include_context:
            context_str = self.context_manager.get_context_for_query(
                session_id, max_context_turns
            )

        # Prepare request data
        request_data = request.dict(exclude_none=True)
        if context_str:
            request_data['context'] = context_str

        try:
            response = self.client.http.request(
                'POST',
                '/conversations/ask',
                json=request_data
            )

            # Parse response
            data = response.get('data', {})

            turn = ConversationTurn(
                id=data.get('id', f"turn_{uuid.uuid4().hex[:8]}"),
                session_id=session_id,
                query=query,
                response=data.get('response', ''),
                timestamp=datetime.now(),
                processing_time_ms=data.get('processing_time_ms', 0.0),
                sources=data.get('sources', []),
                metadata=data.get('metadata', {}),
                context_used=context_str if include_context else None,
                confidence_score=data.get('confidence_score', 0.0),
                tokens_used=data.get('tokens_used', 0)
            )

            # Add turn to context manager
            self.context_manager.add_turn(session_id, turn)

            return turn

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    async def continue_conversation(
        self,
        query: str,
        session_id: Optional[str] = None,
        auto_create_session: bool = True,
        **kwargs
    ) -> ConversationTurn:
        """
        Continue an existing conversation or start new one.

        Args:
            query: User query
            session_id: Session identifier (optional)
            auto_create_session: Create new session if none provided (default: True)
            **kwargs: Additional arguments for ask() method

        Returns:
            ConversationTurn with response

        Raises:
            CognifyValidationError: If no session and auto_create_session is False
        """
        if not session_id:
            if not auto_create_session:
                raise CognifyValidationError(
                    "No session_id provided and auto_create_session is False"
                )

            # Create new session
            session = await self.start_session(title="Auto-created session")
            session_id = session.id
            logger.info(f"Auto-created session for conversation: {session_id}")

        return await self.ask(query, session_id, **kwargs)

    def continue_conversation_sync(
        self,
        query: str,
        session_id: Optional[str] = None,
        auto_create_session: bool = True,
        **kwargs
    ) -> ConversationTurn:
        """
        Continue conversation synchronously.

        Args:
            query: User query
            session_id: Session identifier (optional)
            auto_create_session: Create new session if none provided (default: True)
            **kwargs: Additional arguments for ask_sync() method

        Returns:
            ConversationTurn with response
        """
        if not session_id:
            if not auto_create_session:
                raise CognifyValidationError(
                    "No session_id provided and auto_create_session is False"
                )

            # Create new session
            session = self.start_session_sync(title="Auto-created session")
            session_id = session.id

        return self.ask_sync(query, session_id, **kwargs)

    # History Management

    async def get_history(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[ConversationStatus] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        include_context: bool = False,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[ConversationSession]:
        """
        Get user's conversation history.

        Args:
            limit: Maximum number of sessions to return (default: 10)
            offset: Number of sessions to skip (default: 0)
            status: Filter by status (optional)
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            include_context: Include session context (default: False)
            date_from: Filter from date (optional)
            date_to: Filter to date (optional)

        Returns:
            List of ConversationSession objects

        Raises:
            CognifyAPIError: If history request fails
        """
        request = ConversationHistoryRequest(
            limit=limit,
            offset=offset,
            status=status,
            collection_id=collection_id,
            workspace_id=workspace_id,
            include_context=include_context,
            date_from=date_from,
            date_to=date_to
        )

        logger.debug(f"Getting conversation history: limit={limit}, offset={offset}")

        response = await self.client.http.arequest(
            'GET',
            '/conversations/history',
            params=request.dict(exclude_none=True)
        )

        sessions_data = response.get('data', [])
        sessions = []

        for session_data in sessions_data:
            session = ConversationSession(**session_data)
            sessions.append(session)

        logger.debug(f"Retrieved {len(sessions)} conversation sessions")
        return sessions

    def get_history_sync(
        self,
        limit: int = 10,
        offset: int = 0,
        status: Optional[ConversationStatus] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        include_context: bool = False,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[ConversationSession]:
        """
        Get conversation history synchronously.

        Args:
            limit: Maximum number of sessions to return (default: 10)
            offset: Number of sessions to skip (default: 0)
            status: Filter by status (optional)
            collection_id: Filter by collection (optional)
            workspace_id: Filter by workspace (optional)
            include_context: Include session context (default: False)
            date_from: Filter from date (optional)
            date_to: Filter to date (optional)

        Returns:
            List of ConversationSession objects
        """
        request = ConversationHistoryRequest(
            limit=limit,
            offset=offset,
            status=status,
            collection_id=collection_id,
            workspace_id=workspace_id,
            include_context=include_context,
            date_from=date_from,
            date_to=date_to
        )

        response = self.client.http.request(
            'GET',
            '/conversations/history',
            params=request.dict(exclude_none=True)
        )

        sessions_data = response.get('data', [])
        sessions = []

        for session_data in sessions_data:
            session = ConversationSession(**session_data)
            sessions.append(session)

        return sessions

    async def get_session_turns(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationTurn]:
        """
        Get all turns for a specific session.

        Args:
            session_id: Session identifier
            limit: Maximum number of turns to return (default: 50)
            offset: Number of turns to skip (default: 0)

        Returns:
            List of ConversationTurn objects

        Raises:
            CognifyNotFoundError: If session not found
            CognifyAPIError: If turns request fails
        """
        if limit < 1 or limit > 100:
            raise CognifyValidationError("Limit must be between 1 and 100")

        if offset < 0:
            raise CognifyValidationError("Offset cannot be negative")

        logger.debug(f"Getting turns for session {session_id}: limit={limit}, offset={offset}")

        try:
            response = await self.client.http.arequest(
                'GET',
                f'/conversations/sessions/{session_id}/turns',
                params={'limit': limit, 'offset': offset}
            )

            turns_data = response.get('data', [])
            turns = []

            for turn_data in turns_data:
                turn = ConversationTurn(**turn_data)
                turns.append(turn)

            logger.debug(f"Retrieved {len(turns)} turns for session {session_id}")
            return turns

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    def get_session_turns_sync(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[ConversationTurn]:
        """
        Get session turns synchronously.

        Args:
            session_id: Session identifier
            limit: Maximum number of turns to return (default: 50)
            offset: Number of turns to skip (default: 0)

        Returns:
            List of ConversationTurn objects
        """
        if limit < 1 or limit > 100:
            raise CognifyValidationError("Limit must be between 1 and 100")

        if offset < 0:
            raise CognifyValidationError("Offset cannot be negative")

        try:
            response = self.client.http.request(
                'GET',
                f'/conversations/sessions/{session_id}/turns',
                params={'limit': limit, 'offset': offset}
            )

            turns_data = response.get('data', [])
            turns = []

            for turn_data in turns_data:
                turn = ConversationTurn(**turn_data)
                turns.append(turn)

            return turns

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Session not found: {session_id}",
                    resource_type="conversation_session",
                    resource_id=session_id
                )
            raise

    # Sub-module properties

    @property
    def analytics(self):
        """Access analytics sub-module."""
        if not hasattr(self, '_analytics'):
            from .analytics import ConversationAnalytics
            self._analytics = ConversationAnalytics(self)
        return self._analytics

    # Utility Methods

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """
        Clean up old inactive sessions from context manager.

        Args:
            max_age_hours: Maximum age in hours before cleanup (default: 24)
        """
        self.context_manager.cleanup_old_sessions(max_age_hours)

    def get_context_stats(self) -> Dict[str, Any]:
        """
        Get context manager statistics.

        Returns:
            Dictionary with context statistics
        """
        return self.context_manager.get_stats()