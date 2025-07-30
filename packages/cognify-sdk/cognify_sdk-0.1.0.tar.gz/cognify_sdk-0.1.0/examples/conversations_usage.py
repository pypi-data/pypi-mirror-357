#!/usr/bin/env python3
"""
Conversations module usage examples for the Cognify Python SDK.

This script demonstrates the comprehensive conversation management functionality:
- Multi-turn dialogue with context persistence
- Session management and lifecycle
- Context-aware query processing
- Conversation history and analytics
- User behavior insights and team collaboration
"""

import asyncio
from datetime import datetime, timedelta
from cognify_sdk import CognifyClient
from cognify_sdk.conversations import ConversationStatus


async def example_basic_conversation():
    """Example of basic conversation flow."""
    print("=== Basic Conversation Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # Start a new conversation session
    print("🚀 Starting new conversation session...")
    print("Note: This is a mock example - would use real API")
    
    # Simulate session creation
    session_id = "session_conv_123"
    print(f"✅ Session started: {session_id}")
    print("Title: 'Python Learning Session'")
    print("Status: Active")
    print("Collection: 'Programming Tutorials'")
    print()
    
    # Multi-turn conversation
    conversation_turns = [
        {
            "query": "What is Python?",
            "response": "Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991.",
            "context_used": "",
            "confidence": 0.95
        },
        {
            "query": "How do I install Python?",
            "response": "You can install Python by downloading it from python.org. For most systems, you can also use package managers like apt (Ubuntu), brew (macOS), or chocolatey (Windows).",
            "context_used": "Previous discussion about Python basics",
            "confidence": 0.92
        },
        {
            "query": "What's the difference between Python 2 and 3?",
            "response": "Python 3 is the current version with better Unicode support, improved syntax, and many new features. Python 2 reached end-of-life in 2020 and is no longer supported.",
            "context_used": "Previous discussion about Python installation and basics",
            "confidence": 0.90
        }
    ]
    
    print("💬 Multi-turn conversation:")
    for i, turn in enumerate(conversation_turns, 1):
        print(f"\nTurn {i}:")
        print(f"  User: {turn['query']}")
        print(f"  Assistant: {turn['response']}")
        print(f"  Context: {turn['context_used'] or 'None'}")
        print(f"  Confidence: {turn['confidence']*100:.0f}%")
    
    print(f"\n✅ Conversation completed with {len(conversation_turns)} turns")
    print("Session remains active for future questions")
    
    await client.aclose()


async def example_context_management():
    """Example of intelligent context management."""
    print("\n=== Context Management Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    session_id = "session_context_456"
    print(f"📝 Context Management for Session: {session_id}")
    print("Note: This is a mock example - would use real context management")
    
    # Simulate context building over multiple turns
    print("\n🧠 Context Evolution:")
    
    context_states = [
        {
            "turn": 1,
            "query": "How do I create a REST API?",
            "context_summary": "",
            "key_topics": [],
            "context_length": 0
        },
        {
            "turn": 2,
            "query": "What about authentication?",
            "context_summary": "Discussion about REST API creation",
            "key_topics": ["api", "rest"],
            "context_length": 150
        },
        {
            "turn": 3,
            "query": "How do I handle database connections?",
            "context_summary": "REST API development with authentication focus",
            "key_topics": ["api", "rest", "authentication"],
            "context_length": 320
        },
        {
            "turn": 4,
            "query": "What about error handling?",
            "context_summary": "REST API development covering authentication and database integration",
            "key_topics": ["api", "rest", "authentication", "database"],
            "context_length": 480
        }
    ]
    
    for state in context_states:
        print(f"\nAfter Turn {state['turn']}:")
        print(f"  Query: {state['query']}")
        print(f"  Context Summary: {state['context_summary'] or 'None yet'}")
        print(f"  Key Topics: {', '.join(state['key_topics']) if state['key_topics'] else 'None yet'}")
        print(f"  Context Length: {state['context_length']} characters")
    
    print("\n🔄 Context Management Features:")
    print("  • Automatic summarization when context gets long")
    print("  • Key topic extraction from conversation")
    print("  • Intelligent context truncation")
    print("  • Memory management for long conversations")
    print("  • Context-aware response generation")
    
    await client.aclose()


async def example_session_management():
    """Example of conversation session management."""
    print("\n=== Session Management Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    print("📋 Session Lifecycle Management:")
    print("Note: This is a mock example - would use real session management")
    
    # Session creation with metadata
    print("\n1. Creating Session with Metadata:")
    session_data = {
        "id": "session_mgmt_789",
        "title": "Machine Learning Project Discussion",
        "status": "active",
        "collection_id": "ml_tutorials",
        "workspace_id": "team_workspace",
        "tags": ["machine-learning", "project", "tutorial"],
        "metadata": {
            "project_type": "classification",
            "difficulty": "intermediate",
            "estimated_duration": "2 hours"
        },
        "started_at": datetime.now().isoformat(),
        "turn_count": 0,
        "total_tokens": 0
    }
    
    for key, value in session_data.items():
        print(f"  {key}: {value}")
    
    # Session activity simulation
    print("\n2. Session Activity:")
    activities = [
        {"time": "10:00", "action": "Session started", "turns": 0, "tokens": 0},
        {"time": "10:15", "action": "First questions about ML basics", "turns": 3, "tokens": 450},
        {"time": "10:30", "action": "Deep dive into algorithms", "turns": 7, "tokens": 1200},
        {"time": "10:45", "action": "Code examples and implementation", "turns": 12, "tokens": 2100},
        {"time": "11:00", "action": "Session paused for break", "turns": 12, "tokens": 2100},
        {"time": "11:15", "action": "Session resumed", "turns": 12, "tokens": 2100},
        {"time": "11:30", "action": "Final questions and wrap-up", "turns": 15, "tokens": 2800},
        {"time": "11:45", "action": "Session ended", "turns": 15, "tokens": 2800}
    ]
    
    for activity in activities:
        print(f"  {activity['time']}: {activity['action']} (Turns: {activity['turns']}, Tokens: {activity['tokens']})")
    
    # Session statistics
    print("\n3. Final Session Statistics:")
    print("  • Duration: 1 hour 45 minutes")
    print("  • Total turns: 15")
    print("  • Total tokens: 2,800")
    print("  • Average tokens per turn: 187")
    print("  • Key topics: machine learning, algorithms, implementation")
    print("  • Status: Completed successfully")
    
    await client.aclose()


async def example_conversation_history():
    """Example of conversation history and analytics."""
    print("\n=== Conversation History & Analytics Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    print("📚 Conversation History:")
    print("Note: This is a mock example - would fetch real history")
    
    # Mock conversation history
    history = [
        {
            "id": "session_001",
            "title": "Python Basics Tutorial",
            "status": "completed",
            "started_at": "2025-06-24T09:00:00Z",
            "duration": "45 minutes",
            "turns": 8,
            "tokens": 1200,
            "topics": ["python", "programming", "basics"]
        },
        {
            "id": "session_002",
            "title": "Web Development with Flask",
            "status": "completed",
            "started_at": "2025-06-24T10:30:00Z",
            "duration": "1 hour 20 minutes",
            "turns": 12,
            "tokens": 2100,
            "topics": ["flask", "web", "api", "python"]
        },
        {
            "id": "session_003",
            "title": "Machine Learning Project",
            "status": "active",
            "started_at": "2025-06-24T14:00:00Z",
            "duration": "30 minutes (ongoing)",
            "turns": 5,
            "tokens": 800,
            "topics": ["machine-learning", "scikit-learn", "data"]
        }
    ]
    
    print("\n📋 Recent Sessions:")
    for session in history:
        status_emoji = "✅" if session["status"] == "completed" else "🔄"
        print(f"  {status_emoji} {session['title']} ({session['id']})")
        print(f"     Status: {session['status']} | Duration: {session['duration']}")
        print(f"     Turns: {session['turns']} | Tokens: {session['tokens']}")
        print(f"     Topics: {', '.join(session['topics'])}")
        print()
    
    # User analytics
    print("👤 User Analytics (Last 30 Days):")
    user_stats = {
        "total_conversations": 25,
        "total_turns": 180,
        "avg_turns_per_conversation": 7.2,
        "total_time_hours": 15.5,
        "favorite_topics": ["python", "web-development", "machine-learning", "api", "database"],
        "most_active_hours": [9, 10, 14, 15, 16],
        "conversation_patterns": {
            "avg_session_length": "37 minutes",
            "preferred_response_style": "detailed with examples",
            "common_follow_ups": ["code examples", "best practices", "troubleshooting"]
        }
    }
    
    print(f"  • Total conversations: {user_stats['total_conversations']}")
    print(f"  • Total turns: {user_stats['total_turns']}")
    print(f"  • Average turns per conversation: {user_stats['avg_turns_per_conversation']}")
    print(f"  • Total conversation time: {user_stats['total_time_hours']} hours")
    print(f"  • Favorite topics: {', '.join(user_stats['favorite_topics'][:3])}")
    print(f"  • Most active hours: {', '.join(map(str, user_stats['most_active_hours']))}")
    
    await client.aclose()


async def example_team_collaboration():
    """Example of team collaboration analytics."""
    print("\n=== Team Collaboration Analytics Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    print("👥 Team Collaboration Insights:")
    print("Note: This is a mock example - would analyze real team data")
    
    # Team analytics
    team_analytics = {
        "team_id": "dev_team_alpha",
        "team_size": 8,
        "active_users": 6,
        "total_conversations": 150,
        "collaboration_score": 0.85,
        "trending_topics": [
            "microservices architecture",
            "kubernetes deployment",
            "api security",
            "performance optimization",
            "code review practices"
        ],
        "user_contributions": {
            "alice": {"conversations": 35, "expertise": ["python", "api"], "help_given": 28},
            "bob": {"conversations": 28, "expertise": ["devops", "kubernetes"], "help_given": 22},
            "carol": {"conversations": 32, "expertise": ["frontend", "react"], "help_given": 25},
            "david": {"conversations": 25, "expertise": ["database", "sql"], "help_given": 18}
        },
        "knowledge_sharing": {
            "cross_team_questions": 45,
            "knowledge_transfer_sessions": 12,
            "documentation_created": 8,
            "best_practices_shared": 15
        }
    }
    
    print(f"\n📊 Team Overview:")
    print(f"  • Team: {team_analytics['team_id']}")
    print(f"  • Active users: {team_analytics['active_users']}/{team_analytics['team_size']}")
    print(f"  • Total conversations: {team_analytics['total_conversations']}")
    print(f"  • Collaboration score: {team_analytics['collaboration_score']*100:.0f}%")
    
    print(f"\n🔥 Trending Topics:")
    for i, topic in enumerate(team_analytics['trending_topics'], 1):
        print(f"  {i}. {topic}")
    
    print(f"\n👤 Top Contributors:")
    for name, stats in team_analytics['user_contributions'].items():
        print(f"  • {name.title()}: {stats['conversations']} conversations")
        print(f"    Expertise: {', '.join(stats['expertise'])}")
        print(f"    Help given: {stats['help_given']} times")
    
    print(f"\n🤝 Knowledge Sharing Metrics:")
    ks = team_analytics['knowledge_sharing']
    print(f"  • Cross-team questions: {ks['cross_team_questions']}")
    print(f"  • Knowledge transfer sessions: {ks['knowledge_transfer_sessions']}")
    print(f"  • Documentation created: {ks['documentation_created']}")
    print(f"  • Best practices shared: {ks['best_practices_shared']}")
    
    await client.aclose()


async def example_conversation_export():
    """Example of conversation export functionality."""
    print("\n=== Conversation Export Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    print("📤 Conversation Export Options:")
    print("Note: This is a mock example - would export real conversations")
    
    # Export formats
    export_formats = [
        {
            "format": "JSON",
            "description": "Structured data with full metadata",
            "use_case": "Data analysis and backup",
            "file_size": "2.5 MB"
        },
        {
            "format": "Markdown",
            "description": "Human-readable conversation flow",
            "use_case": "Documentation and sharing",
            "file_size": "1.8 MB"
        },
        {
            "format": "CSV",
            "description": "Tabular data for spreadsheet analysis",
            "use_case": "Analytics and reporting",
            "file_size": "1.2 MB"
        },
        {
            "format": "XLSX",
            "description": "Excel workbook with multiple sheets",
            "use_case": "Business reporting and analysis",
            "file_size": "2.1 MB"
        }
    ]
    
    print("\n📋 Available Export Formats:")
    for fmt in export_formats:
        print(f"  • {fmt['format']}: {fmt['description']}")
        print(f"    Use case: {fmt['use_case']}")
        print(f"    Estimated size: {fmt['file_size']}")
        print()
    
    # Export options
    print("⚙️ Export Configuration:")
    export_config = {
        "date_range": "Last 30 days",
        "sessions_included": 25,
        "include_context": True,
        "include_metadata": True,
        "include_analytics": True,
        "filter_by_topics": ["python", "web-development"],
        "privacy_mode": "anonymize_user_ids"
    }
    
    for key, value in export_config.items():
        print(f"  • {key.replace('_', ' ').title()}: {value}")
    
    print("\n✅ Export Process:")
    print("  1. Filtering conversations by criteria")
    print("  2. Processing conversation data")
    print("  3. Applying privacy settings")
    print("  4. Generating export file")
    print("  5. Creating download link")
    print("  📁 Export completed: conversations_export_2025-06-24.json")
    
    await client.aclose()


def example_sync_operations():
    """Example of synchronous conversation operations."""
    print("\n=== Synchronous Operations Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    print("🔄 Sync Conversation Operations:")
    print("Note: This is a mock example - would use real sync API")
    
    # Sync session creation
    print("\n1. Sync Session Creation:")
    print("   Session ID: session_sync_999")
    print("   Title: 'Quick Python Question'")
    print("   Status: Active")
    
    # Sync conversation
    print("\n2. Sync Question & Answer:")
    print("   User: 'How do I read a CSV file in Python?'")
    print("   Assistant: 'You can use pandas.read_csv() or the built-in csv module...'")
    print("   Response time: 180ms")
    print("   Confidence: 94%")
    
    # Sync history retrieval
    print("\n3. Sync History Retrieval:")
    print("   Retrieved 10 recent sessions")
    print("   Total processing time: 45ms")
    
    # Sync session end
    print("\n4. Sync Session End:")
    print("   Session ended successfully")
    print("   Final stats: 1 turn, 95 tokens, 3 minutes duration")
    
    client.close()


async def main():
    """Run all conversation examples."""
    print("Cognify Python SDK - Conversations Module Examples")
    print("=" * 70)
    
    # Run examples
    await example_basic_conversation()
    await example_context_management()
    await example_session_management()
    await example_conversation_history()
    await example_team_collaboration()
    await example_conversation_export()
    example_sync_operations()
    
    print("\n" + "=" * 70)
    print("All conversation examples completed successfully!")
    
    print("\nConversations Module Features Demonstrated:")
    print("✅ Multi-turn dialogue with context persistence")
    print("✅ Intelligent context management and summarization")
    print("✅ Session lifecycle management (start, pause, end)")
    print("✅ Context-aware query processing")
    print("✅ Conversation history with filtering and analytics")
    print("✅ User behavior profiling and insights")
    print("✅ Team collaboration analytics")
    print("✅ Conversation export in multiple formats")
    print("✅ Real-time conversation statistics")
    print("✅ Auto-session creation for seamless flow")
    print("✅ Memory management and context cleanup")
    print("✅ Analytics sub-module for deep insights")
    print("✅ Sync and async API support")


if __name__ == "__main__":
    asyncio.run(main())
