# RAG & Agents Module Implementation Plan

## 📋 **SCOPE & OBJECTIVES**

### **Primary Goals**
- Implement advanced RAG (Retrieval-Augmented Generation) functionality
- Integrate with Cognify's specialized AI agents
- Support structured responses with citations
- Enable streaming responses for real-time interaction
- Provide agent selection and routing capabilities

### **Deliverables**
1. RAG query processing with structured responses
2. AI agent integration and routing
3. Streaming response capabilities
4. Citation and source management
5. Agent health monitoring and stats
6. Response format customization
7. Context-aware answer generation

## 🛠️ **TECHNOLOGY STACK**

### **Core Dependencies**
- **asyncio**: Async streaming support
- **json**: Response parsing
- **typing**: Type annotations for complex responses

### **Cognify API Endpoints Covered**
Based on OpenAPI analysis:
- `POST /api/v1/rag/ask` - Natural language Q&A
- `POST /api/v1/rag/ask-structured` - Structured responses
- `GET /api/v1/rag/stats` - RAG service statistics
- `GET /api/v1/rag/health` - RAG health check
- `POST /api/v1/agents/ask` - Agent queries
- `POST /api/v1/agents/ask/stream` - Streaming agent responses
- `GET /api/v1/agents/agents` - Available agents
- `GET /api/v1/agents/stats` - Agent statistics

## 🏗️ **IMPLEMENTATION STRATEGY**

### **Step 1: RAG Models**
```python
# rag/models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class ResponseFormat(str, Enum):
    SIMPLE = "simple"
    STRUCTURED = "structured"
    DETAILED = "detailed"
    MARKDOWN = "markdown"

class CitationStyle(str, Enum):
    INLINE = "inline"
    FOOTNOTE = "footnote"
    BIBLIOGRAPHY = "bibliography"

class RAGQueryRequest(BaseModel):
    query: str
    collection_id: Optional[str] = None
    workspace_id: Optional[str] = None
    response_format: ResponseFormat = ResponseFormat.SIMPLE
    citation_style: CitationStyle = CitationStyle.INLINE
    max_context_length: int = 4000
    include_sources: bool = True
    temperature: float = 0.7

class Citation(BaseModel):
    id: str
    document_id: str
    chunk_id: str
    filename: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    relevance_score: float
    content_preview: str

class RAGResponse(BaseModel):
    query_id: str
    query: str
    answer: str
    citations: List[Citation] = []
    confidence_score: float
    processing_time_ms: float
    model_used: str
    metadata: Dict[str, Any] = {}

class StructuredResponse(BaseModel):
    query_id: str
    query: str
    summary: str
    sections: List[Dict[str, Any]] = []
    code_examples: List[Dict[str, str]] = []
    recommendations: List[str] = []
    warnings: List[str] = []
    citations: List[Citation] = []
    confidence_score: float
```

### **Step 2: RAG Module**
```python
# rag/rag_module.py
class RAGModule:
    def __init__(self, client: 'CognifyClient'):
        self.client = client
    
    async def ask(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        response_format: ResponseFormat = ResponseFormat.SIMPLE,
        citation_style: CitationStyle = CitationStyle.INLINE,
        max_context_length: int = 4000,
        temperature: float = 0.7
    ) -> RAGResponse:
        """Ask a natural language question with RAG"""
    
    async def ask_structured(
        self,
        query: str,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        include_code_examples: bool = True,
        include_recommendations: bool = True
    ) -> StructuredResponse:
        """Ask a question and get a structured response"""
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get RAG service statistics"""
    
    async def health_check(self) -> Dict[str, Any]:
        """Check RAG service health"""
```

### **Step 3: Agents Integration**
```python
# rag/agents.py
class AgentInfo(BaseModel):
    id: str
    name: str
    description: str
    capabilities: List[str]
    specialization: str
    status: str
    performance_metrics: Dict[str, float]

class AgentQueryRequest(BaseModel):
    query: str
    agent_id: Optional[str] = None  # Auto-select if None
    collection_id: Optional[str] = None
    workspace_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    stream: bool = False

class AgentsModule:
    def __init__(self, client: 'CognifyClient'):
        self.client = client
    
    async def ask(
        self,
        query: str,
        agent_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RAGResponse:
        """Ask a question using specialized agents"""
    
    async def ask_stream(
        self,
        query: str,
        agent_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Ask a question with streaming response"""
    
    async def get_available_agents(self) -> List[AgentInfo]:
        """Get information about available agents"""
    
    async def get_agent_stats(self) -> Dict[str, Any]:
        """Get statistics for all agents"""
    
    async def select_best_agent(
        self,
        query: str,
        collection_id: Optional[str] = None
    ) -> str:
        """Automatically select the best agent for a query"""
```

### **Step 4: Streaming Support**
```python
# rag/streaming.py
class StreamingResponse:
    def __init__(self, response_stream):
        self.stream = response_stream
        self.buffer = ""
        self.complete_response = ""
    
    async def __aiter__(self):
        async for chunk in self.stream:
            if chunk.startswith("data: "):
                data = chunk[6:]  # Remove "data: " prefix
                if data.strip() == "[DONE]":
                    break
                
                try:
                    parsed = json.loads(data)
                    content = parsed.get("content", "")
                    self.complete_response += content
                    yield content
                except json.JSONDecodeError:
                    continue
    
    async def collect_all(self) -> str:
        """Collect all streaming chunks into complete response"""
        async for chunk in self:
            pass  # Chunks are automatically collected
        return self.complete_response
```

## 🔗 **DEPENDENCIES**

### **Prerequisites**
- Core client architecture (Plan 02) completed
- Authentication module (Plan 03) implemented
- Query module (Plan 05) for search integration

### **External Dependencies**
- No additional external dependencies required

## ✅ **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] RAG queries generating accurate answers
- [ ] Structured responses with proper citations
- [ ] Agent routing working automatically
- [ ] Streaming responses functional
- [ ] Citation management complete
- [ ] Agent health monitoring working

### **Quality Requirements**
- **Answer Accuracy**: Relevant and factual responses
- **Citation Quality**: Proper source attribution
- **Response Time**: <2s for simple queries, <5s for complex
- **Streaming Latency**: <100ms for first token

### **API Design**
```python
# Simple RAG Query
response = await client.rag.ask(
    "How do I implement user authentication?",
    collection_id="my_codebase"
)
print(f"Answer: {response.answer}")

# Structured Response
structured = await client.rag.ask_structured(
    "Explain the database schema design",
    include_code_examples=True
)
print(f"Summary: {structured.summary}")
for example in structured.code_examples:
    print(f"Code: {example['code']}")

# Agent Queries
response = await client.agents.ask(
    "Optimize this SQL query performance",
    agent_id="sql_expert"
)

# Streaming Response
async for chunk in client.agents.ask_stream(
    "Explain this complex algorithm step by step"
):
    print(chunk, end="", flush=True)

# Auto Agent Selection
agents = await client.agents.get_available_agents()
best_agent = await client.agents.select_best_agent(
    "Debug this Python error"
)
```

## ⏱️ **TIMELINE**

### **Day 1: Core RAG Functionality**
- RAG models and types
- Basic ask functionality
- Citation handling

### **Day 2: Structured Responses**
- Structured response format
- Advanced citation styles
- Response customization

### **Day 3: Agents Integration**
- Agent routing and selection
- Agent statistics and health
- Performance optimization

### **Day 4: Streaming & Polish**
- Streaming response implementation
- Error handling refinement
- Comprehensive testing

## 🧪 **TESTING STRATEGY**

### **Unit Tests**
```python
async def test_rag_query():
    response = await client.rag.ask("test question")
    assert response.answer
    assert response.confidence_score > 0
    assert len(response.citations) > 0

async def test_structured_response():
    response = await client.rag.ask_structured("complex question")
    assert response.summary
    assert len(response.sections) > 0

async def test_agent_selection():
    agents = await client.agents.get_available_agents()
    assert len(agents) > 0
    
    best_agent = await client.agents.select_best_agent("python question")
    assert best_agent in [agent.id for agent in agents]

async def test_streaming():
    chunks = []
    async for chunk in client.agents.ask_stream("test question"):
        chunks.append(chunk)
    
    complete_response = "".join(chunks)
    assert len(complete_response) > 0
```

### **Integration Tests**
```python
async def test_rag_workflow():
    # Upload document
    document = await client.documents.upload("test_code.py")
    
    # Wait for processing
    await wait_for_processing(document.id)
    
    # Ask RAG question
    response = await client.rag.ask(
        "What does this code do?",
        collection_id=document.collection_id
    )
    
    assert response.answer
    assert any(citation.document_id == document.id for citation in response.citations)
```

### **Performance Tests**
- Response time benchmarks
- Streaming latency measurement
- Citation accuracy validation
- Agent selection efficiency

## 📚 **DOCUMENTATION**

### **RAG Usage Guide**
```python
# Basic RAG Query
from cognify_sdk import CognifyClient, ResponseFormat, CitationStyle

client = CognifyClient(api_key="your_key")

# Simple question
response = await client.rag.ask(
    "How is error handling implemented in this codebase?"
)

# Structured response with citations
structured = await client.rag.ask_structured(
    "Explain the authentication flow",
    citation_style=CitationStyle.FOOTNOTE
)

print(f"Summary: {structured.summary}")
for section in structured.sections:
    print(f"Section: {section['title']}")
    print(f"Content: {section['content']}")
```

### **Agent Integration**
```python
# Available agents
agents = await client.agents.get_available_agents()
for agent in agents:
    print(f"{agent.name}: {agent.description}")

# Specific agent query
response = await client.agents.ask(
    "Review this code for security vulnerabilities",
    agent_id="security_expert"
)

# Streaming response
print("Agent response: ", end="")
async for chunk in client.agents.ask_stream(
    "Explain this algorithm step by step"
):
    print(chunk, end="", flush=True)
print()  # New line after streaming
```

## 🔄 **RISK MITIGATION**

### **Technical Risks**
- **Response Quality**: Multiple validation layers
- **Streaming Issues**: Robust error handling
- **Agent Availability**: Fallback mechanisms

### **Performance Risks**
- **Response Time**: Caching and optimization
- **Resource Usage**: Efficient streaming
- **Concurrent Requests**: Rate limiting

---

**Plan Status**: 🟡 Ready for Implementation
**Dependencies**: Core client (02), Authentication (03), Query (05)
**Estimated Effort**: 4 days
**Priority**: High (Advanced AI functionality)
