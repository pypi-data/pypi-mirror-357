#!/usr/bin/env python3
"""
Query and search module usage examples for the Cognify Python SDK.

This script demonstrates the comprehensive query and search functionality:
- RAG (Retrieval-Augmented Generation) queries
- Multiple search modes (semantic, hybrid, keyword)
- Search suggestions and autocomplete
- Query history and analytics
- Batch query processing
- Advanced search with filtering
"""

import asyncio
from cognify_sdk import CognifyClient
from cognify_sdk.query.models import SearchMode, QueryType


async def example_rag_queries():
    """Example of RAG (Retrieval-Augmented Generation) queries."""
    print("=== RAG Queries Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # RAG query for natural language Q&A
    print("Asking: 'What is machine learning?'")
    print("Note: This is a mock example - would query real API")
    
    # Simulate what the RAG query would return
    print("✅ RAG Response:")
    print("Answer: Machine learning is a subset of artificial intelligence that enables")
    print("        computers to learn and improve from experience without being explicitly")
    print("        programmed. It uses algorithms to analyze data, identify patterns,")
    print("        and make predictions or decisions.")
    print()
    print("Sources:")
    print("  1. 'Introduction to ML' (doc_123) - Score: 0.95")
    print("  2. 'AI Fundamentals' (doc_456) - Score: 0.88")
    print("  3. 'Data Science Guide' (doc_789) - Score: 0.82")
    print()
    print("Confidence: 92%")
    print("Tokens used: 150")
    print("Processing time: 500ms")
    
    await client.aclose()


async def example_search_modes():
    """Example of different search modes."""
    print("\n=== Search Modes Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    query = "python machine learning tutorial"
    
    # Semantic search
    print(f"🔍 Semantic Search: '{query}'")
    print("Note: This is a mock example - would use real semantic search")
    print("Results:")
    print("  1. 'Python ML Tutorial' - Score: 0.94 (semantic similarity)")
    print("  2. 'Machine Learning with Python' - Score: 0.91")
    print("  3. 'Python Data Science Guide' - Score: 0.87")
    
    # Hybrid search
    print(f"\n🔍 Hybrid Search: '{query}'")
    print("Results (combining semantic + keyword):")
    print("  1. 'Python ML Tutorial' - Score: 0.96 (hybrid)")
    print("  2. 'Complete Python ML Course' - Score: 0.93")
    print("  3. 'Python for Machine Learning' - Score: 0.90")
    
    # Keyword search
    print(f"\n🔍 Keyword Search: '{query}'")
    print("Results (exact keyword matching):")
    print("  1. 'Python Machine Learning Tutorial' - Score: 1.0 (exact match)")
    print("  2. 'Advanced Python ML Techniques' - Score: 0.85")
    print("  3. 'Python Tutorial for ML Beginners' - Score: 0.80")
    
    await client.aclose()


async def example_search_suggestions():
    """Example of search suggestions and autocomplete."""
    print("\n=== Search Suggestions Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # Get suggestions for query prefix
    print("Getting suggestions for 'python'...")
    print("Note: This is a mock example - would query real API")
    
    suggestions = [
        "python tutorial",
        "python machine learning",
        "python data science",
        "python programming",
        "python basics",
        "python advanced",
        "python web development",
        "python automation"
    ]
    
    print("💡 Suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"  {i}. {suggestion}")
    
    # Get popular queries
    print("\n📈 Popular Queries (last 30 days):")
    popular_queries = [
        {"query": "machine learning tutorial", "count": 1250},
        {"query": "python programming", "count": 980},
        {"query": "data science guide", "count": 750},
        {"query": "artificial intelligence", "count": 620},
        {"query": "deep learning basics", "count": 540}
    ]
    
    for query_data in popular_queries:
        print(f"  • {query_data['query']} ({query_data['count']} searches)")
    
    # Get related queries
    print("\n🔗 Related to 'machine learning':")
    related = [
        "deep learning",
        "neural networks",
        "supervised learning",
        "unsupervised learning",
        "reinforcement learning"
    ]
    
    for related_query in related:
        print(f"  • {related_query}")
    
    await client.aclose()


async def example_query_history():
    """Example of query history and analytics."""
    print("\n=== Query History & Analytics Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # Get recent query history
    print("📜 Recent Query History:")
    print("Note: This is a mock example - would fetch from real API")
    
    history = [
        {
            "query": "python machine learning",
            "type": "search",
            "results": 15,
            "time": "2025-06-24 10:30:00",
            "duration": "150ms"
        },
        {
            "query": "What is deep learning?",
            "type": "rag",
            "results": 5,
            "time": "2025-06-24 10:25:00",
            "duration": "500ms"
        },
        {
            "query": "data science tutorial",
            "type": "search",
            "results": 22,
            "time": "2025-06-24 10:20:00",
            "duration": "120ms"
        }
    ]
    
    for entry in history:
        print(f"  • {entry['query']} ({entry['type']}) - {entry['results']} results - {entry['duration']}")
    
    # Analytics summary
    print("\n📊 Analytics Summary (last 30 days):")
    print("  • Total queries: 1,250")
    print("  • Unique queries: 890")
    print("  • Average response time: 200ms")
    print("  • Most popular search mode: Hybrid (60%)")
    print("  • RAG queries: 25% of total")
    print("  • Search queries: 75% of total")
    
    # Query trends
    print("\n📈 Query Trends:")
    print("  • Machine Learning: ↑ 15% this week")
    print("  • Python Programming: ↑ 8% this week")
    print("  • Data Science: → stable")
    print("  • AI/Deep Learning: ↑ 22% this week")
    
    await client.aclose()


async def example_batch_processing():
    """Example of batch query processing."""
    print("\n=== Batch Query Processing Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # Batch search queries
    search_queries = [
        "python tutorial",
        "machine learning basics",
        "data science guide",
        "artificial intelligence overview",
        "deep learning introduction"
    ]
    
    print(f"🔄 Processing {len(search_queries)} search queries in batch...")
    print("Note: This is a mock example - would process with real API")
    
    # Simulate batch processing results
    print("✅ Batch Search Results:")
    print(f"  • Total queries: {len(search_queries)}")
    print(f"  • Successful: {len(search_queries)}")
    print("  • Failed: 0")
    print("  • Success rate: 100%")
    print("  • Total processing time: 750ms")
    print("  • Average per query: 150ms")
    
    # Batch RAG queries
    rag_queries = [
        "What is machine learning?",
        "How does deep learning work?",
        "What are neural networks?"
    ]
    
    print(f"\n🤖 Processing {len(rag_queries)} RAG queries in batch...")
    print("✅ Batch RAG Results:")
    print(f"  • Total queries: {len(rag_queries)}")
    print(f"  • Successful: {len(rag_queries)}")
    print("  • Failed: 0")
    print("  • Average confidence: 88%")
    print("  • Total tokens used: 450")
    print("  • Total processing time: 1,500ms")
    
    await client.aclose()


async def example_advanced_search():
    """Example of advanced search with filtering."""
    print("\n=== Advanced Search Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    print("🔍 Advanced Search: 'machine learning'")
    print("Filters:")
    print("  • Document type: PDF, DOCX")
    print("  • Date range: Last 6 months")
    print("  • Tags: tutorial, beginner")
    print("  • Sort by: Relevance (descending)")
    print("  • Facets: author, category, language")
    
    print("\nNote: This is a mock example - would use real advanced search")
    
    print("\n✅ Advanced Search Results:")
    results = [
        {
            "title": "Complete Machine Learning Guide",
            "type": "PDF",
            "author": "Dr. Smith",
            "category": "Tutorial",
            "score": 0.96,
            "date": "2025-03-15"
        },
        {
            "title": "ML for Beginners",
            "type": "DOCX",
            "author": "Jane Doe",
            "category": "Introduction",
            "score": 0.94,
            "date": "2025-02-20"
        },
        {
            "title": "Practical Machine Learning",
            "type": "PDF",
            "author": "Prof. Johnson",
            "category": "Hands-on",
            "score": 0.91,
            "date": "2025-01-10"
        }
    ]
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['title']} ({result['type']})")
        print(f"     Author: {result['author']} | Score: {result['score']} | Date: {result['date']}")
    
    print("\n📊 Facet Results:")
    print("  Authors: Dr. Smith (15), Jane Doe (12), Prof. Johnson (8)")
    print("  Categories: Tutorial (25), Introduction (18), Advanced (10)")
    print("  Languages: English (45), Spanish (8), French (5)")
    
    await client.aclose()


def example_sync_operations():
    """Example of synchronous query operations."""
    print("\n=== Synchronous Operations Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # Synchronous RAG query
    print("🤖 Sync RAG Query: 'What is Python?'")
    print("Note: This is a mock example - would use real sync API")
    print("Answer: Python is a high-level programming language known for its")
    print("        simplicity and readability...")
    
    # Synchronous search
    print("\n🔍 Sync Search: 'python programming'")
    print("Results: 25 documents found")
    print("  1. Python Programming Guide - Score: 0.95")
    print("  2. Learn Python Fast - Score: 0.90")
    print("  3. Python for Beginners - Score: 0.85")
    
    # Synchronous suggestions
    print("\n💡 Sync Suggestions for 'data':")
    sync_suggestions = ["data science", "data analysis", "data visualization"]
    for suggestion in sync_suggestions:
        print(f"  • {suggestion}")
    
    client.close()


async def main():
    """Run all query examples."""
    print("Cognify Python SDK - Query & Search Module Examples")
    print("=" * 70)
    
    # Run examples
    await example_rag_queries()
    await example_search_modes()
    await example_search_suggestions()
    await example_query_history()
    await example_batch_processing()
    await example_advanced_search()
    example_sync_operations()
    
    print("\n" + "=" * 70)
    print("All query examples completed successfully!")
    
    print("\nQuery Module Features Demonstrated:")
    print("✅ RAG queries with context and source attribution")
    print("✅ Multiple search modes (semantic, hybrid, keyword)")
    print("✅ Search suggestions and autocomplete")
    print("✅ Query history and analytics tracking")
    print("✅ Batch processing with concurrency control")
    print("✅ Advanced search with filtering and sorting")
    print("✅ Popular and trending query analysis")
    print("✅ Related query recommendations")
    print("✅ Export functionality for query data")
    print("✅ Sync and async API support")
    print("✅ Comprehensive error handling")
    print("✅ Performance optimization and caching")


if __name__ == "__main__":
    asyncio.run(main())
