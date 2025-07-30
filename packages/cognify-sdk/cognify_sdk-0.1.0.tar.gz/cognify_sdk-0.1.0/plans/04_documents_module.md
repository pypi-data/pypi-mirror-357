# Documents Module Implementation Plan

## 📋 **SCOPE & OBJECTIVES**

### **Primary Goals**
- Implement comprehensive document management functionality
- Support file upload (single & bulk) with progress tracking
- Provide document lifecycle management (CRUD operations)
- Integrate advanced chunking capabilities
- Handle various document formats and processing status

### **Deliverables**
1. Document upload functionality (single & bulk)
2. Document management (list, get, delete, search)
3. Content and chunks retrieval
4. Chunking functionality with multiple strategies
5. Processing status tracking
6. File download capabilities
7. Metadata management

## 🛠️ **TECHNOLOGY STACK**

### **Core Dependencies**
- **aiofiles**: Async file operations
- **mimetypes**: File type detection
- **pathlib**: File path handling
- **typing**: Type annotations for file operations

### **Cognify API Endpoints Covered**
Based on OpenAPI analysis:
- `POST /api/v1/documents/upload` - Single file upload
- `POST /api/v1/documents/bulk-upload` - Bulk file upload
- `GET /api/v1/documents/` - List documents
- `GET /api/v1/documents/search` - Search documents
- `GET /api/v1/documents/{id}` - Get document details
- `DELETE /api/v1/documents/{id}` - Delete document
- `GET /api/v1/documents/{id}/content` - Get content
- `GET /api/v1/documents/{id}/chunks` - Get chunks
- `POST /api/v1/documents/chunk` - Chunk content
- `GET /api/v1/documents/{id}/status` - Processing status

## 🏗️ **IMPLEMENTATION STRATEGY**

### **Step 1: Document Models**
```python
# documents/models.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(BaseModel):
    id: str
    title: str
    filename: str
    file_size: int
    document_type: str
    status: DocumentStatus
    collection_id: Optional[str] = None
    workspace_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

class DocumentChunk(BaseModel):
    id: str
    document_id: str
    content: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any] = {}

class ChunkingStrategy(str, Enum):
    AST_FALLBACK = "ast_fallback"
    HYBRID = "hybrid"
    AGENTIC = "agentic"
```

### **Step 2: Documents Module**
```python
# documents/documents_module.py
class DocumentsModule:
    def __init__(self, client: 'CognifyClient'):
        self.client = client
    
    # Upload Operations
    async def upload(
        self,
        file_path: Union[str, Path],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        progress_callback: Optional[Callable] = None
    ) -> Document:
        """Upload a single document"""
    
    async def bulk_upload(
        self,
        file_paths: List[Union[str, Path]],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> BulkUploadSession:
        """Upload multiple documents"""
    
    # Document Management
    async def list(
        self,
        workspace_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[DocumentStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """List documents with filtering"""
    
    async def get(self, document_id: str) -> Document:
        """Get document by ID"""
    
    async def delete(self, document_id: str) -> bool:
        """Delete document"""
    
    async def search(
        self,
        query: str,
        workspace_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Document]:
        """Search documents"""
```

### **Step 3: Content and Chunking**
```python
# documents/content.py
class ContentModule:
    def __init__(self, documents_module: DocumentsModule):
        self.documents = documents_module
    
    async def get_content(self, document_id: str) -> str:
        """Get document content"""
    
    async def get_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Get document chunks"""
    
    async def chunk_content(
        self,
        content: str,
        language: Optional[str] = None,
        strategy: ChunkingStrategy = ChunkingStrategy.HYBRID,
        max_chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[DocumentChunk]:
        """Chunk content using specified strategy"""
    
    async def reprocess(self, document_id: str) -> bool:
        """Reprocess document (re-chunk and re-embed)"""
```

### **Step 4: File Upload Handling**
```python
# documents/upload.py
class FileUploader:
    def __init__(self, http_client: HTTPClient):
        self.http = http_client
    
    async def upload_file(
        self,
        file_path: Path,
        collection_id: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Document:
        """Upload single file with progress tracking"""
        
        file_size = file_path.stat().st_size
        mime_type = mimetypes.guess_type(str(file_path))[0]
        
        async with aiofiles.open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, mime_type)
            }
            data = {}
            if collection_id:
                data['collection_id'] = collection_id
            
            # Upload with progress tracking
            response = await self.http.arequest(
                'POST',
                '/api/v1/documents/upload',
                files=files,
                data=data,
                progress_callback=progress_callback
            )
            
        return Document(**response.json()['data'])
```

## 🔗 **DEPENDENCIES**

### **Prerequisites**
- Core client architecture (Plan 02) completed
- Authentication module (Plan 03) implemented
- HTTP client with file upload support

### **External Dependencies**
- aiofiles >= 23.2.0
- python-multipart >= 0.0.6 (for file uploads)

## ✅ **SUCCESS CRITERIA**

### **Functional Requirements**
- [ ] Single file upload working with progress tracking
- [ ] Bulk file upload with session management
- [ ] Document CRUD operations complete
- [ ] Content and chunks retrieval working
- [ ] Chunking strategies implemented
- [ ] Processing status tracking functional
- [ ] File download capabilities

### **Performance Requirements**
- **Upload Speed**: Efficient streaming for large files
- **Progress Tracking**: Real-time upload progress
- **Memory Usage**: Streaming uploads without loading entire file
- **Concurrent Uploads**: Support for parallel bulk uploads

### **API Design**
```python
# Single file upload
document = await client.documents.upload(
    "path/to/file.py",
    collection_id="collection_123",
    progress_callback=lambda progress: print(f"Upload: {progress}%")
)

# Bulk upload
session = await client.documents.bulk_upload([
    "file1.py", "file2.py", "file3.py"
])

# Document management
documents = await client.documents.list(
    workspace_id="workspace_123",
    status=DocumentStatus.COMPLETED
)

# Content operations
content = await client.documents.get_content(document.id)
chunks = await client.documents.get_chunks(document.id)

# Chunking
chunks = await client.documents.chunk_content(
    content="def hello(): pass",
    language="python",
    strategy=ChunkingStrategy.AGENTIC
)
```

## ⏱️ **TIMELINE**

### **Day 1: Core Document Operations**
- Document models and types
- Basic CRUD operations
- Document listing and search

### **Day 2: File Upload System**
- Single file upload
- Progress tracking
- File validation and handling

### **Day 3: Advanced Features**
- Bulk upload functionality
- Content and chunking operations
- Processing status tracking

### **Day 4: Testing & Optimization**
- Comprehensive testing
- Performance optimization
- Error handling refinement

## 🧪 **TESTING STRATEGY**

### **Unit Tests**
```python
async def test_document_upload():
    # Mock file upload
    # Test progress callback
    # Verify document creation

async def test_document_list():
    # Test filtering options
    # Test pagination
    # Verify response format

async def test_chunking():
    # Test different strategies
    # Test various content types
    # Verify chunk quality
```

### **Integration Tests**
```python
async def test_upload_workflow():
    # Upload file
    # Check processing status
    # Retrieve content and chunks
    # Verify end-to-end flow

async def test_bulk_upload():
    # Upload multiple files
    # Track session progress
    # Verify all files processed
```

### **Performance Tests**
- Large file upload (>100MB)
- Concurrent upload handling
- Memory usage during uploads
- Progress tracking accuracy

## 📚 **DOCUMENTATION**

### **Upload Guide**
```python
# Basic file upload
from cognify_sdk import CognifyClient

client = CognifyClient(api_key="your_key")

# Upload with progress tracking
def progress_handler(progress):
    print(f"Upload progress: {progress:.1f}%")

document = await client.documents.upload(
    "my_code.py",
    collection_id="my_collection",
    progress_callback=progress_handler
)

# Bulk upload
files = ["file1.py", "file2.py", "file3.py"]
session = await client.documents.bulk_upload(files)

# Monitor bulk upload progress
status = await client.documents.get_bulk_upload_status(session.id)
```

### **Content Processing**
```python
# Get document content
content = await client.documents.get_content(document.id)

# Get processed chunks
chunks = await client.documents.get_chunks(document.id)

# Custom chunking
chunks = await client.documents.chunk_content(
    content=source_code,
    language="python",
    strategy="agentic",
    max_chunk_size=1500
)
```

## 🔄 **RISK MITIGATION**

### **Technical Risks**
- **Large File Handling**: Streaming uploads and progress tracking
- **Network Issues**: Retry logic and resumable uploads
- **File Format Support**: Comprehensive format detection

### **Performance Risks**
- **Memory Usage**: Streaming operations
- **Upload Speed**: Optimized chunk sizes
- **Concurrent Limits**: Rate limiting and queue management

---

**Plan Status**: 🟡 Ready for Implementation
**Dependencies**: Core client (02), Authentication (03)
**Estimated Effort**: 4 days
**Priority**: High (Core functionality)
