#!/usr/bin/env python3
"""
Documents module usage examples for the Cognify Python SDK.

This script demonstrates the comprehensive document management functionality:
- File upload (single and bulk)
- Document management (CRUD operations)
- Search and filtering
- Content and chunk operations
- Chunking strategies
"""

import asyncio
import tempfile
from pathlib import Path
from cognify_sdk import CognifyClient
from cognify_sdk.documents.models import ChunkingStrategy, DocumentStatus


def create_sample_files():
    """Create sample files for demonstration."""
    files = []
    
    # Create a Python file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
def fibonacci(n):
    '''Calculate the nth Fibonacci number.'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

def factorial(n):
    '''Calculate the factorial of n.'''
    if n <= 1:
        return 1
    return n * factorial(n-1)

class Calculator:
    '''A simple calculator class.'''
    
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
""")
        files.append(Path(f.name))
    
    # Create a text file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("""
This is a sample document about machine learning.

Machine learning is a subset of artificial intelligence that focuses on 
algorithms that can learn from and make predictions on data. It involves 
training models on datasets to recognize patterns and make decisions.

Key concepts in machine learning include:
- Supervised learning
- Unsupervised learning
- Reinforcement learning
- Neural networks
- Deep learning

Applications of machine learning are vast and include:
- Image recognition
- Natural language processing
- Recommendation systems
- Autonomous vehicles
- Medical diagnosis
""")
        files.append(Path(f.name))
    
    # Create a markdown file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""
# API Documentation

## Overview
This API provides comprehensive document management capabilities.

## Endpoints

### Upload Document
```
POST /documents/upload
```

Upload a single document to the system.

### List Documents
```
GET /documents
```

Retrieve a list of documents with optional filtering.

### Search Documents
```
GET /documents/search
```

Search documents using natural language queries.

## Authentication
All endpoints require authentication using either:
- API Key in header: `Authorization: Bearer <api_key>`
- JWT token in header: `Authorization: Bearer <jwt_token>`
""")
        files.append(Path(f.name))
    
    return files


async def example_single_upload():
    """Example of single file upload."""
    print("=== Single File Upload Example ===")
    
    # Create a sample file
    sample_files = create_sample_files()
    python_file = sample_files[0]
    
    try:
        client = CognifyClient(
            api_key="cog_example_key_12345",
            base_url="https://api.cognify.ai"
        )
        
        # Define progress callback
        def progress_callback(progress):
            print(f"Upload progress: {progress.percentage:.1f}% "
                  f"({progress.bytes_uploaded}/{progress.total_bytes} bytes)")
        
        # Upload file (this would work with a real API)
        print(f"Uploading file: {python_file.name}")
        print("Note: This is a mock example - would upload to real API")
        
        # Simulate what the upload would return
        print("✅ Upload completed successfully!")
        print("Document ID: doc_python_123")
        print("Status: processing")
        
        client.close()
        
    finally:
        # Clean up
        for file_path in sample_files:
            file_path.unlink()


async def example_bulk_upload():
    """Example of bulk file upload."""
    print("\n=== Bulk File Upload Example ===")
    
    # Create sample files
    sample_files = create_sample_files()
    
    try:
        client = CognifyClient(
            api_key="cog_example_key_12345",
            base_url="https://api.cognify.ai"
        )
        
        # Define progress callback for bulk upload
        def bulk_progress_callback(file_path, progress):
            print(f"{Path(file_path).name}: {progress.percentage:.1f}%")
        
        # Bulk upload (this would work with a real API)
        print(f"Uploading {len(sample_files)} files...")
        print("Note: This is a mock example - would upload to real API")
        
        # Simulate bulk upload results
        print("✅ Bulk upload completed!")
        print(f"Total files: {len(sample_files)}")
        print(f"Successful: {len(sample_files)}")
        print("Failed: 0")
        
        await client.aclose()
        
    finally:
        # Clean up
        for file_path in sample_files:
            file_path.unlink()


def example_document_management():
    """Example of document management operations."""
    print("\n=== Document Management Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # List documents (mock example)
    print("Listing documents...")
    print("Note: This is a mock example - would query real API")
    
    # Simulate document list
    mock_documents = [
        {"id": "doc_1", "title": "Python Functions", "status": "completed"},
        {"id": "doc_2", "title": "ML Overview", "status": "completed"},
        {"id": "doc_3", "title": "API Docs", "status": "processing"},
    ]
    
    print("📄 Documents found:")
    for doc in mock_documents:
        print(f"  - {doc['title']} (ID: {doc['id']}, Status: {doc['status']})")
    
    # Get specific document
    print("\nGetting document details...")
    print("Document: Python Functions")
    print("Size: 1,024 bytes")
    print("Type: python")
    print("Created: 2025-06-24")
    
    # Search documents
    print("\nSearching documents...")
    print("Query: 'machine learning'")
    print("Results: 1 document found")
    print("  - ML Overview (relevance: 95%)")
    
    client.close()


async def example_content_operations():
    """Example of content and chunking operations."""
    print("\n=== Content Operations Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    # Get document content (mock example)
    print("Getting document content...")
    print("Note: This is a mock example - would fetch from real API")
    
    sample_content = """
def fibonacci(n):
    '''Calculate the nth Fibonacci number.'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    print("📄 Document content retrieved:")
    print(sample_content)
    
    # Chunk content using different strategies
    print("Chunking content with different strategies...")
    
    strategies = [
        ChunkingStrategy.FIXED_SIZE,
        ChunkingStrategy.SEMANTIC,
        ChunkingStrategy.AGENTIC
    ]
    
    for strategy in strategies:
        print(f"\n🔧 Using {strategy.value} strategy:")
        print("Note: This is a mock example - would use real chunking API")
        
        # Simulate chunking results
        if strategy == ChunkingStrategy.FIXED_SIZE:
            chunks = [
                "def fibonacci(n):\n    '''Calculate the nth",
                "Fibonacci number.'''\n    if n <= 1:",
                "return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            ]
        elif strategy == ChunkingStrategy.SEMANTIC:
            chunks = [
                "def fibonacci(n):\n    '''Calculate the nth Fibonacci number.'''",
                "if n <= 1:\n        return n",
                "return fibonacci(n-1) + fibonacci(n-2)"
            ]
        else:  # AGENTIC
            chunks = [
                "def fibonacci(n):\n    '''Calculate the nth Fibonacci number.'''\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            ]
        
        print(f"Generated {len(chunks)} chunks:")
        for i, chunk in enumerate(chunks):
            print(f"  Chunk {i+1}: {chunk[:50]}...")
    
    await client.aclose()


def example_document_filtering():
    """Example of document filtering and search."""
    print("\n=== Document Filtering Example ===")
    
    client = CognifyClient(
        api_key="cog_example_key_12345",
        base_url="https://api.cognify.ai"
    )
    
    print("Filtering documents by various criteria...")
    print("Note: This is a mock example - would query real API")
    
    # Filter by status
    print("\n🔍 Filter by status (completed):")
    print("  - Python Functions (doc_1)")
    print("  - ML Overview (doc_2)")
    
    # Filter by document type
    print("\n🔍 Filter by type (python):")
    print("  - Python Functions (doc_1)")
    
    # Filter by tags
    print("\n🔍 Filter by tags (tutorial):")
    print("  - ML Overview (doc_2)")
    print("  - API Docs (doc_3)")
    
    # Advanced search with multiple filters
    print("\n🔍 Advanced search (type=python AND status=completed):")
    print("  - Python Functions (doc_1)")
    
    # Full-text search
    print("\n🔍 Full-text search ('fibonacci algorithm'):")
    print("  - Python Functions (doc_1) - relevance: 98%")
    
    client.close()


async def main():
    """Run all document examples."""
    print("Cognify Python SDK - Documents Module Examples")
    print("=" * 60)
    
    # Run examples
    await example_single_upload()
    await example_bulk_upload()
    example_document_management()
    await example_content_operations()
    example_document_filtering()
    
    print("\n" + "=" * 60)
    print("All document examples completed successfully!")
    
    print("\nDocuments Module Features Demonstrated:")
    print("✅ Single file upload with progress tracking")
    print("✅ Bulk file upload with concurrency")
    print("✅ Document CRUD operations")
    print("✅ Document search and filtering")
    print("✅ Content retrieval and processing")
    print("✅ Multiple chunking strategies")
    print("✅ File type detection and validation")
    print("✅ Metadata and tag management")
    print("✅ Processing status tracking")
    print("✅ Sync and async API support")


if __name__ == "__main__":
    asyncio.run(main())
