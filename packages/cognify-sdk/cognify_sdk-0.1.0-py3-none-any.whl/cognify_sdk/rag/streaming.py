"""
Streaming response functionality for the Cognify SDK.

This module handles streaming responses from RAG and agent queries,
providing real-time response generation with proper error handling.
"""

import asyncio
import json
import logging
from typing import Any, AsyncIterator, Dict, Optional

from .models import StreamingChunk
from ..exceptions import CognifyAPIError


logger = logging.getLogger(__name__)


class StreamingResponse:
    """
    Handles streaming responses from RAG and agent queries.
    """
    
    def __init__(self, response_stream, query_id: str = None) -> None:
        """
        Initialize streaming response.
        
        Args:
            response_stream: HTTP response stream
            query_id: Query identifier for tracking
        """
        self.stream = response_stream
        self.query_id = query_id or "unknown"
        self.buffer = ""
        self.complete_response = ""
        self.chunks_received = 0
        self.is_complete = False
        self.error_occurred = False
        self.error_message = None
    
    async def __aiter__(self) -> AsyncIterator[str]:
        """
        Async iterator for streaming chunks.
        
        Yields:
            String chunks of the response
            
        Raises:
            CognifyAPIError: If streaming fails
        """
        try:
            async for raw_chunk in self.stream:
                try:
                    # Handle different chunk formats
                    chunk_data = self._parse_chunk(raw_chunk)
                    if chunk_data is None:
                        continue
                    
                    # Check for completion signal
                    if chunk_data.get("done", False) or chunk_data.get("is_final", False):
                        self.is_complete = True
                        break
                    
                    # Extract content
                    content = chunk_data.get("content", "")
                    if content:
                        self.complete_response += content
                        self.chunks_received += 1
                        yield content
                    
                    # Handle metadata
                    if "metadata" in chunk_data:
                        self._handle_metadata(chunk_data["metadata"])
                
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse streaming chunk: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Error processing streaming chunk: {e}")
                    self.error_occurred = True
                    self.error_message = str(e)
                    raise CognifyAPIError(f"Streaming error: {e}")
        
        except Exception as e:
            self.error_occurred = True
            self.error_message = str(e)
            logger.error(f"Streaming failed for query {self.query_id}: {e}")
            raise CognifyAPIError(f"Streaming failed: {e}")
        
        finally:
            logger.debug(
                f"Streaming completed for query {self.query_id}: "
                f"{self.chunks_received} chunks, {len(self.complete_response)} chars"
            )
    
    def _parse_chunk(self, raw_chunk: bytes) -> Optional[Dict[str, Any]]:
        """
        Parse raw chunk data into structured format.
        
        Args:
            raw_chunk: Raw bytes from stream
            
        Returns:
            Parsed chunk data or None if invalid
        """
        try:
            # Convert bytes to string
            chunk_str = raw_chunk.decode('utf-8').strip()
            
            # Handle Server-Sent Events format
            if chunk_str.startswith("data: "):
                data_str = chunk_str[6:]  # Remove "data: " prefix
                
                # Check for completion signal
                if data_str.strip() in ["[DONE]", "[END]", "[COMPLETE]"]:
                    return {"done": True}
                
                # Parse JSON data
                return json.loads(data_str)
            
            # Handle direct JSON format
            elif chunk_str.startswith("{"):
                return json.loads(chunk_str)
            
            # Handle plain text chunks
            elif chunk_str:
                return {"content": chunk_str}
            
            return None
        
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.debug(f"Failed to parse chunk: {e}")
            return None
    
    def _handle_metadata(self, metadata: Dict[str, Any]) -> None:
        """
        Handle metadata from streaming chunks.
        
        Args:
            metadata: Metadata dictionary
        """
        # Log important metadata
        if "tokens_used" in metadata:
            logger.debug(f"Tokens used so far: {metadata['tokens_used']}")
        
        if "processing_stage" in metadata:
            logger.debug(f"Processing stage: {metadata['processing_stage']}")
        
        if "confidence" in metadata:
            logger.debug(f"Current confidence: {metadata['confidence']}")
    
    async def collect_all(self) -> str:
        """
        Collect all streaming chunks into complete response.
        
        Returns:
            Complete response string
            
        Raises:
            CognifyAPIError: If streaming fails
        """
        logger.debug(f"Collecting all chunks for query {self.query_id}")
        
        async for chunk in self:
            pass  # Chunks are automatically collected in complete_response
        
        if self.error_occurred:
            raise CognifyAPIError(f"Streaming failed: {self.error_message}")
        
        logger.info(
            f"Collected complete response for query {self.query_id}: "
            f"{len(self.complete_response)} characters"
        )
        
        return self.complete_response
    
    async def collect_with_callback(
        self,
        callback: callable,
        callback_interval: float = 0.1
    ) -> str:
        """
        Collect chunks with periodic callback for progress updates.
        
        Args:
            callback: Function to call with progress updates
            callback_interval: Seconds between callback calls
            
        Returns:
            Complete response string
        """
        last_callback = 0
        
        async for chunk in self:
            current_time = asyncio.get_event_loop().time()
            
            # Call callback at specified intervals
            if current_time - last_callback >= callback_interval:
                try:
                    callback({
                        "chunks_received": self.chunks_received,
                        "characters_received": len(self.complete_response),
                        "current_chunk": chunk,
                        "is_complete": self.is_complete
                    })
                    last_callback = current_time
                except Exception as e:
                    logger.warning(f"Callback error: {e}")
        
        # Final callback
        try:
            callback({
                "chunks_received": self.chunks_received,
                "characters_received": len(self.complete_response),
                "current_chunk": "",
                "is_complete": True
            })
        except Exception as e:
            logger.warning(f"Final callback error: {e}")
        
        return self.complete_response
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get streaming statistics.
        
        Returns:
            Dictionary with streaming stats
        """
        return {
            "query_id": self.query_id,
            "chunks_received": self.chunks_received,
            "total_characters": len(self.complete_response),
            "is_complete": self.is_complete,
            "error_occurred": self.error_occurred,
            "error_message": self.error_message
        }


class StreamingBuffer:
    """
    Buffer for managing streaming content with windowing.
    """
    
    def __init__(self, max_size: int = 10000) -> None:
        """
        Initialize streaming buffer.
        
        Args:
            max_size: Maximum buffer size in characters
        """
        self.max_size = max_size
        self.buffer = ""
        self.overflow_count = 0
    
    def add_chunk(self, chunk: str) -> None:
        """
        Add chunk to buffer with overflow management.
        
        Args:
            chunk: Text chunk to add
        """
        self.buffer += chunk
        
        # Handle overflow
        if len(self.buffer) > self.max_size:
            # Keep the last max_size characters
            overflow = len(self.buffer) - self.max_size
            self.buffer = self.buffer[overflow:]
            self.overflow_count += overflow
    
    def get_content(self) -> str:
        """Get current buffer content."""
        return self.buffer
    
    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        return {
            "buffer_size": len(self.buffer),
            "max_size": self.max_size,
            "overflow_count": self.overflow_count,
            "utilization": len(self.buffer) / self.max_size
        }
    
    def clear(self) -> None:
        """Clear buffer content."""
        self.buffer = ""
        self.overflow_count = 0


class StreamingManager:
    """
    Manages multiple streaming responses.
    """
    
    def __init__(self) -> None:
        """Initialize streaming manager."""
        self.active_streams: Dict[str, StreamingResponse] = {}
        self.completed_streams: Dict[str, Dict[str, Any]] = {}
    
    def register_stream(self, query_id: str, stream: StreamingResponse) -> None:
        """
        Register a new streaming response.
        
        Args:
            query_id: Query identifier
            stream: StreamingResponse instance
        """
        self.active_streams[query_id] = stream
        logger.debug(f"Registered stream for query {query_id}")
    
    def unregister_stream(self, query_id: str) -> None:
        """
        Unregister a completed streaming response.
        
        Args:
            query_id: Query identifier
        """
        if query_id in self.active_streams:
            stream = self.active_streams.pop(query_id)
            self.completed_streams[query_id] = stream.get_stats()
            logger.debug(f"Unregistered stream for query {query_id}")
    
    def get_active_streams(self) -> Dict[str, StreamingResponse]:
        """Get all active streaming responses."""
        return self.active_streams.copy()
    
    def get_stream_stats(self, query_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific stream.
        
        Args:
            query_id: Query identifier
            
        Returns:
            Stream statistics or None if not found
        """
        if query_id in self.active_streams:
            return self.active_streams[query_id].get_stats()
        elif query_id in self.completed_streams:
            return self.completed_streams[query_id]
        return None
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics for all streams."""
        return {
            "active_streams": len(self.active_streams),
            "completed_streams": len(self.completed_streams),
            "active_details": {
                qid: stream.get_stats() 
                for qid, stream in self.active_streams.items()
            },
            "completed_details": self.completed_streams.copy()
        }
