# Query & Search Module Implementation Plan

## 📋 **SCOPE & OBJECTIVES**

### **Primary Goals**
- Implement comprehensive query and search functionality
- Support multiple search modes (semantic, hybrid, vector)
- Provide RAG query capabilities with context
- Enable search suggestions and analytics
- Handle query history and batch operations

### **Deliverables**
1. RAG query processing with natural language
2. Vector similarity search capabilities
3. Hybrid search (semantic + keyword)
4. Search suggestions and autocomplete
5. Query history management
6. Batch query processing
7. Search analytics and insights

## 🛠️ **TECHNOLOGY STACK**

### **Core Dependencies**
- **typing**: Type annotations for search parameters
- **datetime**: Query timestamp handling
- **enum**: Search mode definitions

### **Cognify API Endpoints Covered**
Based on OpenAPI analysis:
- `POST /api/v1/query/` - Submit RAG query
- `POST /api/v1/query/search` - Vector search
- `POST /api/v1/query/advanced` - Advanced search
- `POST /api/v1/query/semantic` - Semantic search
- `POST /api/v1/query/hybrid` - Hybrid search
- `GET /api/v1/query/suggestions` - Search suggestions
- `GET /api/v1/query/history/` - Query history
- `POST /api/v1/query/batch` - Batch queries
- `GET /api/v1/query/analytics` - Search analytics

## 🏗️ **IMPLEMENTATION STRATEGY**

### **Step 1: Query Models**
```python
# query/models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class SearchMode(str, Enum):
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    VECTOR = "vector"
    KEYWORD = "keyword"

class QueryType(str, Enum):
    RAG = "rag"
    SEARCH = "search"
    SUGGESTION = "suggestion"

class QueryRequest(BaseModel):
    query: str
    collection_id: Optional[str] = None
    workspace_id: Optional[str] = None
    mode: SearchMode = SearchMode.HYBRID
    limit: int = 10
    filters: Optional[Dict[str, Any]] = None
    include_metadata: bool = True

class SearchResult(BaseModel):
    id: str
    content: str
    score: float
    document_id: str
    chunk_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    highlights: List[str] = []

class QueryResponse(BaseModel):
    query_id: str
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time_ms: float
    suggestions: List[str] = []
    metadata: Dict[str, Any] = {}
```

### **Step 2: Query Module**
```python
# query/query_module.py
class QueryModule:
    def __init__(self, client: 'CognifyClient'):
        self.client = client
    
    # RAG Queries
    async def ask(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context_limit: int = 5,
        include_sources: bool = True
    ) -> QueryResponse:
        """Submit a RAG query for natural language Q&A"""
    
    # Search Operations
    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> QueryResponse:
        """Perform search with specified mode"""
    
    async def semantic_search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> QueryResponse:
        """Perform semantic vector search"""
    
    async def hybrid_search(
        self,
        query: str,
        collection_id: Optional[str] = None,
        limit: int = 10,
        semantic_weight: float = 0.7
    ) -> QueryResponse:
        """Perform hybrid semantic + keyword search"""
    
    # Advanced Search
    async def advanced_search(
        self,
        query: str,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "desc",
        limit: int = 10
    ) -> QueryResponse:
        """Perform advanced search with complex filters"""
```

### **Step 3: Search Suggestions**
```python
# query/suggestions.py
class SuggestionsModule:
    def __init__(self, query_module: QueryModule):
        self.query = query_module
    
    async def get_suggestions(
        self,
        query_prefix: str,
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> List[str]:
        """Get search suggestions based on query prefix"""
    
    async def get_popular_queries(
        self,
        collection_id: Optional[str] = None,
        days: int = 30,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get popular queries for collection"""
    
    async def get_related_queries(
        self,
        query: str,
        limit: int = 5
    ) -> List[str]:
        """Get queries related to the given query"""
```

### **Step 4: Query History & Analytics**
```python
# query/history.py
class QueryHistory:
    def __init__(self, query_module: QueryModule):
        self.query = query_module
    
    async def get_history(
        self,
        collection_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get user's query history"""
    
    async def get_analytics(
        self,
        collection_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get search analytics and statistics"""
    
    async def export_history(
        self,
        format: str = "json",
        date_range: Optional[tuple] = None
    ) -> Union[str, bytes]:
        """Export query history in specified format"""
```

### **Step 5: Batch Operations**
```python
# query/batch.py
class BatchQueryProcessor:
    def __init__(self, query_module: QueryModule):
        self.query = query_module
    
    async def batch_search(
        self,
        queries: List[str],
        mode: SearchMode = SearchMode.HYBRID,
        collection_id: Optional[str] = None,
        limit: int = 10
    ) -> List[QueryResponse]:
        """Process multiple queries in batch"""
    
    async def batch_rag_queries(
        self,
        queries: List[str],
        collection_id: Optional[str] = None,
        context_limit: int = 5
    ) -> List[QueryResponse]:
        """Process multiple RAG queries in batch"""
```

## 🔗 **DEPENDENCIES**

### **Prerequisites**
- Core client architecture (Plan 02) completed
- Authentication module (Plan 03) implemented
- Documents module (Plan 04) for search context

### **External Dependencies**
- No additional external dependencies required

## ✅ **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] RAG queries working with natural language
- [ ] Multiple search modes implemented
- [ ] Search suggestions functional
- [ ] Query history tracking working
- [ ] Batch query processing efficient
- [ ] Analytics and insights available

### **Performance Requirements**
- **Query Response Time**: <500ms for simple queries
- **Batch Processing**: Efficient parallel processing
- **Search Accuracy**: Relevant results ranking
- **Suggestion Speed**: <100ms for autocomplete

### **API Design**
```python
# RAG Query
response = await client.query.ask(
    "How do I implement authentication in this codebase?",
    collection_id="my_project"
)

# Search Operations
results = await client.query.search(
    "authentication function",
    mode=SearchMode.HYBRID,
    limit=20
)

# Semantic Search
results = await client.query.semantic_search(
    "user login implementation",
    collection_id="backend_code"
)

# Search Suggestions
suggestions = await client.query.get_suggestions(
    "auth",
    collection_id="my_project"
)

# Query History
history = await client.query.get_history(limit=100)

# Batch Queries
queries = ["auth implementation", "database setup", "API endpoints"]
results = await client.query.batch_search(queries)
```

## ⏱️ **TIMELINE**

### **Day 1: Core Query Operations**
- Query models and types
- Basic RAG query functionality
- Simple search operations

### **Day 2: Advanced Search**
- Multiple search modes
- Advanced filtering
- Search result ranking

### **Day 3: Suggestions & History**
- Search suggestions system
- Query history management
- Analytics implementation

### **Day 4: Batch & Optimization**
- Batch query processing
- Performance optimization
- Comprehensive testing

## 🧪 **TESTING STRATEGY**

### **Unit Tests**
```python
async def test_rag_query():
    response = await client.query.ask("test question")
    assert response.query_id
    assert len(response.results) > 0

async def test_search_modes():
    # Test semantic search
    semantic_results = await client.query.semantic_search("test")
    
    # Test hybrid search
    hybrid_results = await client.query.hybrid_search("test")
    
    # Compare results
    assert len(semantic_results.results) > 0
    assert len(hybrid_results.results) > 0

async def test_suggestions():
    suggestions = await client.query.get_suggestions("auth")
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
```

### **Integration Tests**
```python
async def test_search_workflow():
    # Upload document
    document = await client.documents.upload("test_file.py")
    
    # Wait for processing
    await wait_for_processing(document.id)
    
    # Search for content
    results = await client.query.search("test content")
    assert len(results.results) > 0

async def test_batch_processing():
    queries = ["query1", "query2", "query3"]
    results = await client.query.batch_search(queries)
    assert len(results) == 3
```

### **Performance Tests**
- Query response time benchmarks
- Batch processing efficiency
- Search accuracy metrics
- Suggestion response time

## 📚 **DOCUMENTATION**

### **Search Guide**
```python
# Basic RAG Query
from cognify_sdk import CognifyClient, SearchMode

client = CognifyClient(api_key="your_key")

# Ask natural language questions
response = await client.query.ask(
    "How is user authentication implemented?",
    collection_id="my_codebase"
)

print(f"Answer: {response.answer}")
for source in response.sources:
    print(f"Source: {source.filename}:{source.line_number}")

# Different search modes
semantic_results = await client.query.semantic_search("login function")
hybrid_results = await client.query.hybrid_search("user auth")
vector_results = await client.query.search("authentication", mode=SearchMode.VECTOR)
```

### **Advanced Features**
```python
# Search with filters
results = await client.query.advanced_search(
    "database connection",
    filters={
        "file_type": "python",
        "modified_after": "2024-01-01",
        "size_range": [100, 10000]
    }
)

# Batch processing
queries = [
    "authentication implementation",
    "database schema",
    "API endpoints"
]
batch_results = await client.query.batch_search(queries)
```

## 🔄 **RISK MITIGATION**

### **Technical Risks**
- **Search Accuracy**: Multiple search modes and ranking
- **Performance**: Efficient query processing and caching
- **Relevance**: Advanced filtering and context

### **Scalability Risks**
- **Large Result Sets**: Pagination and streaming
- **Concurrent Queries**: Rate limiting and queuing
- **Memory Usage**: Efficient result handling

---

**Plan Status**: 🟡 Ready for Implementation
**Dependencies**: Core client (02), Authentication (03), Documents (04)
**Estimated Effort**: 4 days
**Priority**: High (Core search functionality)
