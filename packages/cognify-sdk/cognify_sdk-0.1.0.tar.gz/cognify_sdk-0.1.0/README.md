# Cognify Python SDK

[![PyPI version](https://badge.fury.io/py/cognify-sdk.svg)](https://badge.fury.io/py/cognify-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/cognify-sdk.svg)](https://pypi.org/project/cognify-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python SDK for the Cognify AI platform, providing easy access to document management, search, RAG (Retrieval-Augmented Generation), and conversation capabilities.

## 🚀 Features

- **📄 Document Management**: Upload, process, and manage documents with metadata
- **🔍 Search & Query**: Semantic, keyword, and hybrid search capabilities
- **🤖 RAG Operations**: Retrieval-Augmented Generation for intelligent Q&A
- **💬 Conversations**: Chat and conversation management with context
- **📁 Collections**: Organize documents into collections with permissions
- **🏢 Multi-tenant Support**: Organization-level isolation and workspaces
- **🔐 Authentication**: Secure API key and JWT token support
- **⚡ Async/Sync Support**: Both asynchronous and synchronous API methods
- **🎯 Type Safety**: Full type hints and Pydantic models
- **🛡️ Error Handling**: Comprehensive exception hierarchy

## Installation

```bash
pip install cognify-sdk
```

## Quick Start

```python
from cognify_sdk import CognifyClient

# Initialize the client
client = CognifyClient(api_key="your_api_key")

# Upload a document
with open("document.pdf", "rb") as f:
    document = client.documents.upload(
        name="My Document",
        file=f,
        metadata={"category": "research"}
    )

# Search documents
results = client.query.search(
    query="artificial intelligence",
    limit=10
)

# Start a conversation
conversation = client.conversations.create(
    title="AI Discussion",
    initial_message="What is artificial intelligence?"
)
```

## Async Support

The SDK supports both synchronous and asynchronous operations:

```python
import asyncio
from cognify_sdk import CognifyClient

async def main():
    async with CognifyClient(api_key="your_api_key") as client:
        # Async operations
        documents = await client.documents.alist()
        results = await client.query.asearch("machine learning")

asyncio.run(main())
```

## Configuration

Configure the SDK using environment variables or direct parameters:

```bash
# Environment variables
export COGNIFY_API_KEY="your_api_key"
export COGNIFY_BASE_URL="https://api.cognify.ai"
export COGNIFY_TIMEOUT=30
```

```python
# Direct configuration
client = CognifyClient(
    api_key="your_api_key",
    base_url="https://api.cognify.ai",
    timeout=60,
    max_retries=3,
    debug=True
)
```

## Development Status

This SDK is currently in active development. The following modules are planned:

- [x] Core Client Architecture
- [ ] Authentication Module
- [ ] Documents Module
- [ ] Query/Search Module
- [ ] RAG/Agents Module
- [ ] Conversations Module
- [ ] Collections/Organizations Module

## Requirements

- Python 3.11+
- httpx >= 0.25.0
- pydantic >= 2.0.0

## License

MIT License - see LICENSE file for details.

## Support

For support and questions, please contact support@cognify.ai or visit our documentation at https://docs.cognify.ai
