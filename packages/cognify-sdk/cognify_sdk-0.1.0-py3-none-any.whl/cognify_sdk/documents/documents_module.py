"""
Main documents module for the Cognify SDK.

This module provides the primary interface for document management operations
including upload, retrieval, search, and content processing.
"""

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING

import httpx

from .models import (
    Document,
    DocumentChunk,
    DocumentFilter,
    DocumentSearchRequest,
    DocumentStatus,
    BulkUploadSession,
    ChunkingRequest,
    ChunkingStrategy,
    UploadProgress,
)
from .upload import FileUploader
from ..exceptions import CognifyValidationError, CognifyAPIError, CognifyNotFoundError
from ..types import APIResponse

if TYPE_CHECKING:
    from ..client import CognifyClient


logger = logging.getLogger(__name__)


class DocumentsModule:
    """
    Main documents module for the Cognify SDK.

    This class provides methods for document management, upload, search,
    and content processing operations.
    """

    def __init__(self, client: "CognifyClient") -> None:
        """
        Initialize documents module.

        Args:
            client: Cognify client instance
        """
        self.client = client
        self.uploader = FileUploader(client.http)

    # Upload Operations

    async def upload(
        self,
        file_path: Union[str, Path],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None
    ) -> Document:
        """
        Upload a single document.

        Args:
            file_path: Path to file to upload
            collection_id: Collection to upload to (optional)
            workspace_id: Workspace to upload to (optional)
            metadata: Additional metadata (optional)
            tags: Tags to apply (optional)
            chunking_strategy: Chunking strategy (optional)
            progress_callback: Progress callback function (optional)

        Returns:
            Document object for uploaded file

        Raises:
            CognifyValidationError: If file is invalid
            CognifyAPIError: If upload fails
        """
        return await self.uploader.upload_file(
            file_path=file_path,
            collection_id=collection_id,
            workspace_id=workspace_id,
            metadata=metadata,
            tags=tags,
            chunking_strategy=chunking_strategy,
            progress_callback=progress_callback
        )

    def upload_sync(
        self,
        file_path: Union[str, Path],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        chunking_strategy: Optional[ChunkingStrategy] = None,
        progress_callback: Optional[Callable[[UploadProgress], None]] = None
    ) -> Document:
        """
        Upload a single document synchronously.

        Args:
            file_path: Path to file to upload
            collection_id: Collection to upload to (optional)
            workspace_id: Workspace to upload to (optional)
            metadata: Additional metadata (optional)
            tags: Tags to apply (optional)
            chunking_strategy: Chunking strategy (optional)
            progress_callback: Progress callback function (optional)

        Returns:
            Document object for uploaded file
        """
        # For sync version, we'll use the HTTP client's sync methods
        # This is a simplified implementation
        file_path = Path(file_path)

        if not file_path.exists():
            raise CognifyValidationError(f"File does not exist: {file_path}")

        # Validate required parameters
        if not collection_id:
            raise CognifyValidationError("collection_id is required for upload")
        if not workspace_id:
            raise CognifyValidationError("workspace_id is required for upload")

        # Prepare form data (matching curl format)
        data = {
            'collection_id': collection_id,
            'workspace_id': workspace_id
        }

        # Add optional fields
        if metadata:
            import json
            data['metadata'] = json.dumps(metadata)
        if tags:
            data['tags'] = ','.join(tags) if isinstance(tags, list) else tags
        if chunking_strategy:
            data['chunking_strategy'] = chunking_strategy.value

        # Use httpx directly like successful curl command

        # Prepare headers with auth
        headers = {}
        if self.client.http._auth_middleware:
            try:
                auth_headers = self.client.http._auth_middleware.get_auth_provider().get_auth_headers()
                headers.update(auth_headers)
            except Exception as e:
                logger.warning(f"Failed to add auth headers: {e}")

        # Upload file using httpx directly (like curl)
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, 'text/markdown')
            }

            with httpx.Client() as client:
                http_response = client.post(
                    self.client.http._prepare_url('/documents/upload'),
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=self.client.config.timeout
                )

                # Handle response using HTTP client's method
                response = self.client.http._handle_response(http_response)

        document_data = response.get('data', {})
        return Document(**document_data)

    async def bulk_upload(
        self,
        file_paths: List[Union[str, Path]],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        max_concurrent: int = 3,
        progress_callback: Optional[Callable[[str, UploadProgress], None]] = None
    ) -> BulkUploadSession:
        """
        Upload multiple documents concurrently.

        Args:
            file_paths: List of file paths to upload
            collection_id: Collection to upload to (optional)
            workspace_id: Workspace to upload to (optional)
            max_concurrent: Maximum concurrent uploads
            progress_callback: Progress callback function (optional)

        Returns:
            BulkUploadSession object with upload results
        """
        return await self.uploader.bulk_upload(
            file_paths=file_paths,
            collection_id=collection_id,
            workspace_id=workspace_id,
            max_concurrent=max_concurrent,
            progress_callback=progress_callback
        )

    # Document Management

    async def list(
        self,
        workspace_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[DocumentStatus] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """
        List documents with filtering options.

        Args:
            workspace_id: Filter by workspace (optional)
            collection_id: Filter by collection (optional)
            document_type: Filter by document type (optional)
            status: Filter by status (optional)
            tags: Filter by tags (optional)
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Document objects
        """
        params = {
            'limit': limit,
            'offset': offset
        }

        if workspace_id:
            params['workspace_id'] = workspace_id
        if collection_id:
            params['collection_id'] = collection_id
        if document_type:
            params['document_type'] = document_type
        if status:
            params['status'] = status.value
        if tags:
            params['tags'] = ','.join(tags)

        response = await self.client.http.arequest(
            'GET',
            '/documents/',
            params=params
        )

        documents_data = response.get('data', {}).get('documents', [])
        return [Document(**doc) for doc in documents_data]

    def list_sync(
        self,
        workspace_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        document_type: Optional[str] = None,
        status: Optional[DocumentStatus] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """
        List documents synchronously.

        Args:
            workspace_id: Filter by workspace (optional)
            collection_id: Filter by collection (optional)
            document_type: Filter by document type (optional)
            status: Filter by status (optional)
            tags: Filter by tags (optional)
            limit: Maximum number of results (default: 50)
            offset: Number of results to skip (default: 0)

        Returns:
            List of Document objects
        """
        params = {
            'limit': limit,
            'offset': offset
        }

        if workspace_id:
            params['workspace_id'] = workspace_id
        if collection_id:
            params['collection_id'] = collection_id
        if document_type:
            params['document_type'] = document_type
        if status:
            params['status'] = status.value
        if tags:
            params['tags'] = ','.join(tags)

        response = self.client.http.request(
            'GET',
            '/documents/',
            params=params
        )

        documents_data = response.get('data', {}).get('documents', [])
        return [Document(**doc) for doc in documents_data]

    async def get(self, document_id: str) -> Document:
        """
        Get document by ID.

        Args:
            document_id: Document ID

        Returns:
            Document object

        Raises:
            CognifyNotFoundError: If document not found
        """
        try:
            response = await self.client.http.arequest(
                'GET',
                f'/documents/{document_id}'
            )

            document_data = response.get('data', {})
            return Document(**document_data)

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    def get_sync(self, document_id: str) -> Document:
        """
        Get document by ID synchronously.

        Args:
            document_id: Document ID

        Returns:
            Document object
        """
        try:
            response = self.client.http.request(
                'GET',
                f'/documents/{document_id}'
            )

            document_data = response.get('data', {})
            return Document(**document_data)

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    async def delete(self, document_id: str) -> bool:
        """
        Delete document by ID.

        Args:
            document_id: Document ID

        Returns:
            True if deletion was successful

        Raises:
            CognifyNotFoundError: If document not found
        """
        try:
            await self.client.http.arequest(
                'DELETE',
                f'/documents/{document_id}'
            )
            return True

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    def delete_sync(self, document_id: str) -> bool:
        """
        Delete document by ID synchronously.

        Args:
            document_id: Document ID

        Returns:
            True if deletion was successful
        """
        try:
            self.client.http.request(
                'DELETE',
                f'/documents/{document_id}'
            )
            return True

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    # Search Operations

    async def search(
        self,
        query: str,
        workspace_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        document_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        include_content: bool = False
    ) -> List[Document]:
        """
        Search documents by query.

        Args:
            query: Search query
            workspace_id: Workspace to search in (optional)
            collection_id: Collection to search in (optional)
            document_types: Document types to include (optional)
            tags: Tags to filter by (optional)
            limit: Maximum number of results (default: 50)
            include_content: Include document content in results (default: False)

        Returns:
            List of matching Document objects
        """
        if not query or not query.strip():
            raise CognifyValidationError("Search query cannot be empty")

        params = {
            'query': query.strip(),
            'limit': limit,
            'include_content': include_content
        }

        if workspace_id:
            params['workspace_id'] = workspace_id
        if collection_id:
            params['collection_id'] = collection_id
        if document_types:
            params['document_types'] = ','.join(document_types)
        if tags:
            params['tags'] = ','.join(tags)

        response = await self.client.http.arequest(
            'GET',
            '/documents/search',
            params=params
        )

        documents_data = response.get('data', {}).get('documents', [])
        return [Document(**doc) for doc in documents_data]

    def search_sync(
        self,
        query: str,
        workspace_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        document_types: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        include_content: bool = False
    ) -> List[Document]:
        """
        Search documents by query synchronously.

        Args:
            query: Search query
            workspace_id: Workspace to search in (optional)
            collection_id: Collection to search in (optional)
            document_types: Document types to include (optional)
            tags: Tags to filter by (optional)
            limit: Maximum number of results (default: 50)
            include_content: Include document content in results (default: False)

        Returns:
            List of matching Document objects
        """
        if not query or not query.strip():
            raise CognifyValidationError("Search query cannot be empty")

        params = {
            'query': query.strip(),
            'limit': limit,
            'include_content': include_content
        }

        if workspace_id:
            params['workspace_id'] = workspace_id
        if collection_id:
            params['collection_id'] = collection_id
        if document_types:
            params['document_types'] = ','.join(document_types)
        if tags:
            params['tags'] = ','.join(tags)

        response = self.client.http.request(
            'GET',
            '/documents/search',
            params=params
        )

        documents_data = response.get('data', {}).get('documents', [])
        return [Document(**doc) for doc in documents_data]

    # Content Operations

    async def get_content(self, document_id: str) -> str:
        """
        Get document content.

        Args:
            document_id: Document ID

        Returns:
            Document content as string

        Raises:
            CognifyNotFoundError: If document not found
        """
        try:
            response = await self.client.http.arequest(
                'GET',
                f'/documents/{document_id}/content'
            )

            return response.get('data', {}).get('content', '')

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    def get_content_sync(self, document_id: str) -> str:
        """
        Get document content synchronously.

        Args:
            document_id: Document ID

        Returns:
            Document content as string
        """
        try:
            response = self.client.http.request(
                'GET',
                f'/documents/{document_id}/content'
            )

            return response.get('data', {}).get('content', '')

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    async def get_chunks(self, document_id: str) -> List[DocumentChunk]:
        """
        Get document chunks.

        Args:
            document_id: Document ID

        Returns:
            List of DocumentChunk objects

        Raises:
            CognifyNotFoundError: If document not found
        """
        try:
            response = await self.client.http.arequest(
                'GET',
                f'/documents/{document_id}/chunks'
            )

            chunks_data = response.get('data', [])
            return [DocumentChunk(**chunk) for chunk in chunks_data]

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    def get_chunks_sync(self, document_id: str) -> List[DocumentChunk]:
        """
        Get document chunks synchronously.

        Args:
            document_id: Document ID

        Returns:
            List of DocumentChunk objects
        """
        try:
            response = self.client.http.request(
                'GET',
                f'/documents/{document_id}/chunks'
            )

            chunks_data = response.get('data', [])
            return [DocumentChunk(**chunk) for chunk in chunks_data]

        except CognifyAPIError as e:
            if e.status_code == 404:
                raise CognifyNotFoundError(
                    f"Document not found: {document_id}",
                    resource_type="document",
                    resource_id=document_id
                )
            raise

    async def chunk_content(
        self,
        content: str,
        language: Optional[str] = None,
        strategy: ChunkingStrategy = ChunkingStrategy.HYBRID,
        max_chunk_size: int = 1000,
        overlap: int = 100,
        preserve_structure: bool = True
    ) -> List[DocumentChunk]:
        """
        Chunk content using specified strategy.

        Args:
            content: Content to chunk
            language: Programming language (if applicable)
            strategy: Chunking strategy (default: HYBRID)
            max_chunk_size: Maximum chunk size in characters (default: 1000)
            overlap: Overlap between chunks in characters (default: 100)
            preserve_structure: Preserve code/document structure (default: True)

        Returns:
            List of DocumentChunk objects
        """
        if not content or not content.strip():
            raise CognifyValidationError("Content cannot be empty")

        request_data = {
            'content': content,
            'strategy': strategy.value,
            'max_chunk_size': max_chunk_size,
            'overlap': overlap,
            'preserve_structure': preserve_structure
        }

        if language:
            request_data['language'] = language

        response = await self.client.http.arequest(
            'POST',
            '/documents/chunk',
            json=request_data
        )

        chunks_data = response.get('data', [])
        return [DocumentChunk(**chunk) for chunk in chunks_data]

    def chunk_content_sync(
        self,
        content: str,
        language: Optional[str] = None,
        strategy: ChunkingStrategy = ChunkingStrategy.HYBRID,
        max_chunk_size: int = 1000,
        overlap: int = 100,
        preserve_structure: bool = True
    ) -> List[DocumentChunk]:
        """
        Chunk content using specified strategy synchronously.

        Args:
            content: Content to chunk
            language: Programming language (if applicable)
            strategy: Chunking strategy (default: HYBRID)
            max_chunk_size: Maximum chunk size in characters (default: 1000)
            overlap: Overlap between chunks in characters (default: 100)
            preserve_structure: Preserve code/document structure (default: True)

        Returns:
            List of DocumentChunk objects
        """
        if not content or not content.strip():
            raise CognifyValidationError("Content cannot be empty")

        request_data = {
            'content': content,
            'strategy': strategy.value,
            'max_chunk_size': max_chunk_size,
            'overlap': overlap,
            'preserve_structure': preserve_structure
        }

        if language:
            request_data['language'] = language

        response = self.client.http.request(
            'POST',
            '/documents/chunk',
            json=request_data
        )

        chunks_data = response.get('data', [])
        return [DocumentChunk(**chunk) for chunk in chunks_data]