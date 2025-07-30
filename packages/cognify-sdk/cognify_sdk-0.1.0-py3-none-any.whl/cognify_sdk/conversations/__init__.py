"""
Conversations module for the Cognify SDK.

This module provides comprehensive conversation management functionality
including multi-turn dialogue, context management, session handling,
and conversation analytics.
"""

from .conversations_module import ConversationsModule
from .analytics import ConversationAnalytics
from .context_manager import ConversationContextManager
from .models import (
    ConversationSession,
    ConversationTurn,
    ConversationContext,
    ConversationStatus,
    ConversationStartRequest,
    ConversationQueryRequest,
    ConversationHistoryRequest,
    ConversationStats,
    UserProfile,
    TeamAnalytics,
    ConversationExportRequest,
)

__all__ = [
    "ConversationsModule",
    "ConversationAnalytics",
    "ConversationContextManager",
    "ConversationSession",
    "ConversationTurn",
    "ConversationContext",
    "ConversationStatus",
    "ConversationStartRequest",
    "ConversationQueryRequest",
    "ConversationHistoryRequest",
    "ConversationStats",
    "UserProfile",
    "TeamAnalytics",
    "ConversationExportRequest",
]
