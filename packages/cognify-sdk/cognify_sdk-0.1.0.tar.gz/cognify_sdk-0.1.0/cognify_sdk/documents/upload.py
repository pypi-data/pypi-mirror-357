"""
File upload functionality for the Cognify SDK.

This module handles file uploads with progress tracking, validation,
and support for both single and bulk uploads.
"""

import asyncio
import logging
import mimetypes
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import aiofiles

from .models import (
    Document,
    BulkUploadSession,
    UploadProgress,
    ChunkingStrategy,
)
from ..exceptions import CognifyValidationError, CognifyAPIError


logger = logging.getLogger(__name__)


class FileUploader:
    """
    Handles file uploads with progress tracking and validation.
    """

    def __init__(self, http_client) -> None:
        """
        Initialize file uploader.

        Args:
            http_client: HTTP client instance for making requests
        """
        self.http = http_client
        self._supported_types = {
            '.pdf', '.docx', '.txt', '.md', '.html', '.csv', '.json',
            '.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs',
            '.yml', '.yaml', '.xml', '.sql', '.sh', '.bat'
        }
        self._max_file_size = 100 * 1024 * 1024  # 100MB

    def _validate_file(self, file_path: Path) -> None:
        """
        Validate file before upload.

        Args:
            file_path: Path to file to validate

        Raises:
            CognifyValidationError: If file is invalid
        """
        if not file_path.exists():
            raise CognifyValidationError(f"File does not exist: {file_path}")

        if not file_path.is_file():
            raise CognifyValidationError(f"Path is not a file: {file_path}")

        file_size = file_path.stat().st_size
        if file_size == 0:
            raise CognifyValidationError(f"File is empty: {file_path}")

        if file_size > self._max_file_size:
            size_mb = file_size / (1024 * 1024)
            max_mb = self._max_file_size / (1024 * 1024)
            raise CognifyValidationError(
                f"File too large: {size_mb:.1f}MB (max: {max_mb}MB)"
            )

        # Check file extension
        suffix = file_path.suffix.lower()
        if suffix not in self._supported_types:
            logger.warning(f"Unsupported file type: {suffix}")

    def _get_mime_type(self, file_path: Path) -> str:
        """
        Get MIME type for file.

        Args:
            file_path: Path to file

        Returns:
            MIME type string
        """
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or "application/octet-stream"

    def _create_progress_callback(
        self,
        file_size: int,
        user_callback: Optional[Callable[[UploadProgress], None]] = None
    ) -> Callable[[int], None]:
        """
        Create progress callback for upload tracking.

        Args:
            file_size: Total file size in bytes
            user_callback: User-provided progress callback

        Returns:
            Progress callback function
        """
        start_time = time.time()
        last_update = 0

        def progress_callback(bytes_uploaded: int) -> None:
            nonlocal last_update

            current_time = time.time()
            elapsed = current_time - start_time

            # Calculate progress
            percentage = (bytes_uploaded / file_size) * 100

            # Calculate speed (update every second)
            speed_bps = None
            eta_seconds = None

            if elapsed > 0:
                speed_bps = bytes_uploaded / elapsed
                if speed_bps > 0:
                    remaining_bytes = file_size - bytes_uploaded
                    eta_seconds = remaining_bytes / speed_bps

            # Create progress object
            progress = UploadProgress(
                bytes_uploaded=bytes_uploaded,
                total_bytes=file_size,
                percentage=percentage,
                speed_bps=speed_bps,
                eta_seconds=eta_seconds
            )

            # Call user callback if provided
            if user_callback and (current_time - last_update >= 0.1):  # Throttle updates
                try:
                    user_callback(progress)
                    last_update = current_time
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")

        return progress_callback

    async def upload_file(
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
        Upload a single file.

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
        file_path = Path(file_path)
        self._validate_file(file_path)

        file_size = file_path.stat().st_size
        mime_type = self._get_mime_type(file_path)

        logger.info(f"Uploading file: {file_path.name} ({file_size} bytes)")

        # Prepare form data
        data = {}
        if collection_id:
            data['collection_id'] = collection_id
        if workspace_id:
            data['workspace_id'] = workspace_id
        if metadata:
            data['metadata'] = metadata
        if tags:
            data['tags'] = tags
        if chunking_strategy:
            data['chunking_strategy'] = chunking_strategy.value

        # Create progress callback
        internal_progress_callback = self._create_progress_callback(
            file_size, progress_callback
        )

        try:
            # Open file and upload
            async with aiofiles.open(file_path, 'rb') as f:
                file_content = await f.read()

                files = {
                    'file': (file_path.name, file_content, mime_type)
                }

                # Make upload request
                response = await self.http.arequest(
                    'POST',
                    '/documents/upload',
                    files=files,
                    data=data
                )

                # Simulate progress completion
                internal_progress_callback(file_size)

                # Parse response
                document_data = response.get('data', {})
                document = Document(**document_data)

                logger.info(f"File uploaded successfully: {document.id}")
                return document

        except Exception as e:
            logger.error(f"File upload failed: {e}")
            if isinstance(e, CognifyAPIError):
                raise
            raise CognifyAPIError(f"Upload failed: {e}")

    async def bulk_upload(
        self,
        file_paths: List[Union[str, Path]],
        collection_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        max_concurrent: int = 3,
        progress_callback: Optional[Callable[[str, UploadProgress], None]] = None
    ) -> BulkUploadSession:
        """
        Upload multiple files concurrently.

        Args:
            file_paths: List of file paths to upload
            collection_id: Collection to upload to (optional)
            workspace_id: Workspace to upload to (optional)
            max_concurrent: Maximum concurrent uploads
            progress_callback: Progress callback function (optional)

        Returns:
            BulkUploadSession object with upload results

        Raises:
            CognifyValidationError: If any file is invalid
        """
        if not file_paths:
            raise CognifyValidationError("No files provided for upload")

        # Validate all files first
        validated_paths = []
        for file_path in file_paths:
            path = Path(file_path)
            self._validate_file(path)
            validated_paths.append(path)

        logger.info(f"Starting bulk upload of {len(validated_paths)} files")

        # Create session
        session = BulkUploadSession(
            id=f"bulk_{int(time.time())}",
            total_files=len(validated_paths),
            completed_files=0,
            failed_files=0,
            status="uploading",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            files=[]
        )

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)

        async def upload_single_file(file_path: Path) -> Dict[str, Any]:
            """Upload a single file with semaphore control."""
            async with semaphore:
                try:
                    # Create file-specific progress callback
                    file_progress_callback = None
                    if progress_callback:
                        file_progress_callback = lambda p: progress_callback(str(file_path), p)

                    document = await self.upload_file(
                        file_path=file_path,
                        collection_id=collection_id,
                        workspace_id=workspace_id,
                        progress_callback=file_progress_callback
                    )

                    session.completed_files += 1
                    return {
                        "file_path": str(file_path),
                        "status": "completed",
                        "document_id": document.id,
                        "error": None
                    }

                except Exception as e:
                    session.failed_files += 1
                    logger.error(f"Failed to upload {file_path}: {e}")
                    return {
                        "file_path": str(file_path),
                        "status": "failed",
                        "document_id": None,
                        "error": str(e)
                    }

        # Execute uploads concurrently
        tasks = [upload_single_file(path) for path in validated_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Update session with results
        session.files = [r for r in results if isinstance(r, dict)]
        session.status = "completed"
        session.updated_at = datetime.now()

        logger.info(
            f"Bulk upload completed: {session.completed_files} successful, "
            f"{session.failed_files} failed"
        )

        return session
