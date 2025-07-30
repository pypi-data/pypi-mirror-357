"""
Context manager for conversation sessions.

This module handles conversation context, memory management,
and intelligent context building for multi-turn conversations.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .models import ConversationTurn, ConversationContext


logger = logging.getLogger(__name__)


class ConversationContextManager:
    """
    Manages conversation context and memory for sessions.
    """
    
    def __init__(self) -> None:
        """Initialize context manager."""
        self.active_sessions: Dict[str, ConversationContext] = {}
        self.max_context_length = 4000  # Maximum context length in characters
        self.max_turns_in_context = 10  # Maximum turns to keep in context
        self.context_summary_threshold = 8  # Summarize when exceeding this many turns
    
    def add_turn(
        self,
        session_id: str,
        turn: ConversationTurn
    ) -> None:
        """
        Add a new turn to session context.
        
        Args:
            session_id: Session identifier
            turn: Conversation turn to add
        """
        logger.debug(f"Adding turn to session {session_id}")
        
        # Get or create context
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = ConversationContext(
                session_id=session_id,
                recent_turns=[],
                last_updated=datetime.now()
            )
        
        context = self.active_sessions[session_id]
        
        # Add turn
        context.recent_turns.append(turn)
        context.last_updated = datetime.now()
        
        # Update key topics
        self._update_key_topics(context, turn)
        
        # Manage context size
        self._manage_context_size(context)
        
        # Update context length
        context.context_length = self._calculate_context_length(context)
        
        logger.debug(f"Session {session_id} now has {len(context.recent_turns)} turns")
    
    def get_context_for_query(
        self,
        session_id: str,
        max_turns: int = 5
    ) -> str:
        """
        Get formatted context for a new query.
        
        Args:
            session_id: Session identifier
            max_turns: Maximum number of recent turns to include
            
        Returns:
            Formatted context string
        """
        if session_id not in self.active_sessions:
            return ""
        
        context = self.active_sessions[session_id]
        
        # Get recent turns (limited by max_turns)
        recent_turns = context.recent_turns[-max_turns:] if context.recent_turns else []
        
        if not recent_turns:
            return ""
        
        # Build context string
        context_parts = []
        
        # Add conversation summary if available
        if context.conversation_summary:
            context_parts.append(f"Conversation Summary: {context.conversation_summary}")
        
        # Add key topics if available
        if context.key_topics:
            topics_str = ", ".join(context.key_topics[:5])  # Limit to top 5 topics
            context_parts.append(f"Key Topics: {topics_str}")
        
        # Add recent conversation turns
        context_parts.append("Recent Conversation:")
        for turn in recent_turns:
            context_parts.append(f"User: {turn.query}")
            context_parts.append(f"Assistant: {turn.response}")
        
        formatted_context = "\n".join(context_parts)
        
        # Ensure context doesn't exceed max length
        if len(formatted_context) > self.max_context_length:
            formatted_context = self._truncate_context(formatted_context)
        
        logger.debug(f"Generated context for session {session_id}: {len(formatted_context)} chars")
        return formatted_context
    
    def get_session_context(self, session_id: str) -> Optional[ConversationContext]:
        """
        Get full context for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ConversationContext or None if not found
        """
        return self.active_sessions.get(session_id)
    
    def summarize_conversation(self, session_id: str) -> str:
        """
        Generate a summary of the conversation.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Conversation summary
        """
        if session_id not in self.active_sessions:
            return ""
        
        context = self.active_sessions[session_id]
        
        if not context.recent_turns:
            return ""
        
        # Simple summarization based on key topics and turn patterns
        topics = context.key_topics[:3]  # Top 3 topics
        turn_count = len(context.recent_turns)
        
        if topics:
            topics_str = ", ".join(topics)
            summary = f"Discussion about {topics_str} over {turn_count} turns."
        else:
            summary = f"Conversation with {turn_count} turns covering various topics."
        
        # Add recent focus if available
        if context.recent_turns:
            latest_turn = context.recent_turns[-1]
            if len(latest_turn.query) < 100:  # Short queries are usually focused
                summary += f" Recent focus: {latest_turn.query}"
        
        context.conversation_summary = summary
        logger.debug(f"Generated summary for session {session_id}: {summary}")
        
        return summary
    
    def extract_key_topics(self, session_id: str) -> List[str]:
        """
        Extract key topics from conversation.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of key topics
        """
        if session_id not in self.active_sessions:
            return []
        
        context = self.active_sessions[session_id]
        
        if not context.recent_turns:
            return []
        
        # Simple keyword extraction from queries and responses
        all_text = []
        for turn in context.recent_turns:
            all_text.append(turn.query)
            all_text.append(turn.response)
        
        combined_text = " ".join(all_text).lower()
        
        # Extract potential topics (simple approach)
        # In a real implementation, this would use NLP techniques
        topic_patterns = [
            r'\b(authentication|auth|login|password)\b',
            r'\b(database|db|sql|query)\b',
            r'\b(api|endpoint|rest|http)\b',
            r'\b(security|encryption|hash)\b',
            r'\b(user|users|account)\b',
            r'\b(python|javascript|java|code)\b',
            r'\b(error|bug|issue|problem)\b',
            r'\b(performance|optimization|speed)\b',
            r'\b(test|testing|unit|integration)\b',
            r'\b(deployment|deploy|production)\b'
        ]
        
        topics = []
        for pattern in topic_patterns:
            matches = re.findall(pattern, combined_text)
            if matches:
                # Use the first match as the topic
                topic = matches[0]
                if topic not in topics:
                    topics.append(topic)
        
        # Limit to top topics
        context.key_topics = topics[:10]
        logger.debug(f"Extracted {len(topics)} topics for session {session_id}")
        
        return topics
    
    def cleanup_old_sessions(self, max_age_hours: int = 24) -> None:
        """
        Clean up old inactive sessions.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        sessions_to_remove = []
        for session_id, context in self.active_sessions.items():
            if context.last_updated < cutoff_time:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del self.active_sessions[session_id]
            logger.debug(f"Cleaned up old session: {session_id}")
        
        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")
    
    def _update_key_topics(
        self,
        context: ConversationContext,
        turn: ConversationTurn
    ) -> None:
        """Update key topics based on new turn."""
        # Extract topics from the new turn
        turn_text = f"{turn.query} {turn.response}".lower()
        
        # Simple keyword detection
        keywords = [
            "authentication", "database", "api", "security", "user",
            "python", "javascript", "error", "performance", "test"
        ]
        
        for keyword in keywords:
            if keyword in turn_text and keyword not in context.key_topics:
                context.key_topics.append(keyword)
        
        # Limit key topics
        context.key_topics = context.key_topics[:10]
    
    def _manage_context_size(self, context: ConversationContext) -> None:
        """Manage context size by removing old turns or summarizing."""
        if len(context.recent_turns) > self.max_turns_in_context:
            # Remove oldest turns
            excess_turns = len(context.recent_turns) - self.max_turns_in_context
            context.recent_turns = context.recent_turns[excess_turns:]
            
            # Update summary to capture removed context
            if not context.conversation_summary:
                context.conversation_summary = self.summarize_conversation(context.session_id)
    
    def _calculate_context_length(self, context: ConversationContext) -> int:
        """Calculate total context length in characters."""
        total_length = len(context.conversation_summary)
        
        for turn in context.recent_turns:
            total_length += len(turn.query) + len(turn.response)
        
        return total_length
    
    def _truncate_context(self, context_str: str) -> str:
        """Truncate context to fit within max length."""
        if len(context_str) <= self.max_context_length:
            return context_str
        
        # Try to truncate at sentence boundaries
        sentences = context_str.split('. ')
        truncated = ""
        
        for sentence in sentences:
            if len(truncated + sentence + '. ') > self.max_context_length:
                break
            truncated += sentence + '. '
        
        # If no sentences fit, do hard truncation
        if not truncated:
            truncated = context_str[:self.max_context_length - 3] + "..."
        
        return truncated.strip()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get context manager statistics."""
        total_sessions = len(self.active_sessions)
        total_turns = sum(len(ctx.recent_turns) for ctx in self.active_sessions.values())
        avg_turns = total_turns / total_sessions if total_sessions > 0 else 0
        
        return {
            "active_sessions": total_sessions,
            "total_turns": total_turns,
            "avg_turns_per_session": avg_turns,
            "max_context_length": self.max_context_length,
            "max_turns_in_context": self.max_turns_in_context
        }
