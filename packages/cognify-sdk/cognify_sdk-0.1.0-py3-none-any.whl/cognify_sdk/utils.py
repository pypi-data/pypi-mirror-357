"""
Utility functions for the Cognify SDK.

This module contains helper functions and utilities used throughout the SDK.
"""

import hashlib
import mimetypes
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import quote, unquote

from .exceptions import CognifyValidationError


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: API key to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic format validation for Cognify API keys
    return api_key.startswith("cog_") and len(api_key) > 10


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "untitled"
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = os.path.splitext(sanitized)
        max_name_len = 255 - len(ext)
        sanitized = name[:max_name_len] + ext
    
    return sanitized


def get_file_mime_type(file_path: Union[str, Path]) -> str:
    """
    Get MIME type for a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return mime_type or "application/octet-stream"


def calculate_file_hash(file_path: Union[str, Path], algorithm: str = "sha256") -> str:
    """
    Calculate hash of a file.
    
    Args:
        file_path: Path to the file
        algorithm: Hash algorithm (md5, sha1, sha256, etc.)
        
    Returns:
        Hex digest of the file hash
        
    Raises:
        CognifyValidationError: If file doesn't exist or algorithm is invalid
    """
    if not os.path.exists(file_path):
        raise CognifyValidationError(f"File not found: {file_path}")
    
    try:
        hasher = hashlib.new(algorithm)
    except ValueError:
        raise CognifyValidationError(f"Invalid hash algorithm: {algorithm}")
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def parse_datetime(dt_string: str) -> datetime:
    """
    Parse datetime string in various formats.
    
    Args:
        dt_string: Datetime string
        
    Returns:
        Parsed datetime object
        
    Raises:
        CognifyValidationError: If datetime format is invalid
    """
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
        "%Y-%m-%dT%H:%M:%SZ",     # ISO format without microseconds
        "%Y-%m-%dT%H:%M:%S",      # ISO format without timezone
        "%Y-%m-%d %H:%M:%S",      # Standard format
        "%Y-%m-%d",               # Date only
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(dt_string, fmt)
        except ValueError:
            continue
    
    raise CognifyValidationError(f"Invalid datetime format: {dt_string}")


def url_encode(value: str) -> str:
    """
    URL encode a string value.
    
    Args:
        value: String to encode
        
    Returns:
        URL-encoded string
    """
    return quote(str(value), safe="")


def url_decode(value: str) -> str:
    """
    URL decode a string value.
    
    Args:
        value: String to decode
        
    Returns:
        URL-decoded string
    """
    return unquote(value)


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
        
    Raises:
        CognifyValidationError: If chunk_size is invalid
    """
    if chunk_size <= 0:
        raise CognifyValidationError("Chunk size must be positive")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later ones taking precedence.
    
    Args:
        *dicts: Dictionaries to merge
        
    Returns:
        Merged dictionary
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def filter_none_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Remove keys with None values from a dictionary.
    
    Args:
        data: Dictionary to filter
        
    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if v is not None}


def validate_pagination_params(
    page: Optional[int] = None,
    per_page: Optional[int] = None,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
) -> Dict[str, int]:
    """
    Validate and normalize pagination parameters.
    
    Args:
        page: Page number (1-based)
        per_page: Items per page
        offset: Offset for cursor-based pagination
        limit: Maximum number of items
        
    Returns:
        Normalized pagination parameters
        
    Raises:
        CognifyValidationError: If parameters are invalid
    """
    params = {}
    
    if page is not None:
        if page < 1:
            raise CognifyValidationError("Page must be >= 1")
        params["page"] = page
    
    if per_page is not None:
        if per_page < 1 or per_page > 1000:
            raise CognifyValidationError("Per page must be between 1 and 1000")
        params["per_page"] = per_page
    
    if offset is not None:
        if offset < 0:
            raise CognifyValidationError("Offset must be >= 0")
        params["offset"] = offset
    
    if limit is not None:
        if limit < 1 or limit > 1000:
            raise CognifyValidationError("Limit must be between 1 and 1000")
        params["limit"] = limit
    
    return params


def extract_error_details(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract error details from API response.
    
    Args:
        response_data: API response data
        
    Returns:
        Extracted error details
    """
    details = {}
    
    # Extract common error fields
    if "error" in response_data:
        error = response_data["error"]
        if isinstance(error, dict):
            details.update(error)
        else:
            details["message"] = str(error)
    
    if "message" in response_data:
        details["message"] = response_data["message"]
    
    if "code" in response_data:
        details["code"] = response_data["code"]
    
    if "details" in response_data:
        details["details"] = response_data["details"]
    
    return details


def is_valid_uuid(uuid_string: str) -> bool:
    """
    Check if a string is a valid UUID.
    
    Args:
        uuid_string: String to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(uuid_string))


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate a string to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix
