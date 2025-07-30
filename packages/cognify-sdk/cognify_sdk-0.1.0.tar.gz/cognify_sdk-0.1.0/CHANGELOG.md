# Changelog

All notable changes to the Cognify Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-06-24

### Added
- Initial release of Cognify Python SDK
- Core client architecture with async/sync support
- Authentication module with API key and JWT support
- Document management with upload, list, and metadata operations
- Search and query operations with multiple modes:
  - Semantic search using vector embeddings
  - Keyword search with full-text capabilities
  - Hybrid search combining semantic and keyword
- RAG (Retrieval-Augmented Generation) operations:
  - Natural language Q&A with document context
  - Citation support with relevance scoring
  - Structured response formatting
- Conversation management:
  - Session-based chat functionality
  - Context-aware responses
  - Turn management and history
- Collection operations:
  - Document organization and grouping
  - Permission management
  - Collaboration features
- Comprehensive error handling with custom exception hierarchy
- Type safety with full type hints and Pydantic models
- HTTP client with connection pooling and retry logic
- Configuration management with environment variable support
- Examples and documentation for all features

### Technical Details
- Python 3.11+ support
- Built on httpx for HTTP operations
- Pydantic v2 for data validation and serialization
- Comprehensive test suite with 100% API compatibility
- Production-ready with real API integration testing

### Dependencies
- httpx >= 0.25.0
- pydantic >= 2.0.0
- pydantic-settings >= 2.0.0
- typing-extensions >= 4.0.0
- python-dotenv >= 1.0.0
- PyJWT >= 2.8.0
- cryptography >= 41.0.0
- python-dateutil >= 2.8.0
- aiofiles >= 23.2.0
- python-multipart >= 0.0.6
