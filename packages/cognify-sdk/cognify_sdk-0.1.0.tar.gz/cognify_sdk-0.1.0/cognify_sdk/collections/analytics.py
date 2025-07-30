"""
Collection analytics module for the Cognify SDK.

This module provides functionality for retrieving collection statistics,
analytics, and insights including usage patterns and performance metrics.
"""

import asyncio
from typing import Optional, List, Dict, Any
from urllib.parse import urlencode

from ..exceptions import (
    CognifyAPIError,
    CognifyValidationError,
    CognifyNotFoundError,
    CognifyPermissionError,
)
from .models import (
    CollectionStats,
    CollectionStatsResponse,
    CollectionStatusResponse,
)


class CollectionAnalytics:
    """
    Collection analytics and insights module.

    Provides functionality for retrieving detailed statistics, usage analytics,
    and performance insights for collections in the Cognify platform.
    """

    def __init__(self, collections_module: 'CollectionsModule'):
        """Initialize the collection analytics module."""
        self.collections = collections_module
        self.client = collections_module.client
        self._base_url = "/api/v1/collections"

    async def get_collection_stats(self, collection_id: str) -> CollectionStats:
        """
        Get detailed statistics for a collection.

        Args:
            collection_id: Collection ID

        Returns:
            Collection statistics and analytics

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Make API request
            response = await self.client.http.arequest(
                "GET", f"/collections/{collection_id}/analytics"
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot access analytics for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to get collection stats: {response.get('message', 'Unknown error')}"
                )

            stats_data = response.get("data", {})
            return CollectionStats(**stats_data)

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting collection stats: {str(e)}", status_code=500)

    async def get_collection_status(self, collection_id: str) -> Dict[str, Any]:
        """
        Get collection processing status and health information.

        Args:
            collection_id: Collection ID

        Returns:
            Collection status and health information

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Make API request
            response = await self.client.http.arequest(
                "GET", f"/collections/{collection_id}/status"
            )

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot access status for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to get collection status: {response.get('message', 'Unknown error')}"
                )

            return response.get("data", {})

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting collection status: {str(e)}", status_code=500)

    async def get_collection_documents(
        self,
        collection_id: str,
        limit: int = 50,
        offset: int = 0,
        doc_status: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get documents in a collection with optional filtering.

        Args:
            collection_id: Collection ID
            limit: Maximum number of results (1-100)
            offset: Number of results to skip
            doc_status: Filter by document status
            document_type: Filter by document type

        Returns:
            List of documents in the collection

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyValidationError: If request parameters are invalid
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")
            if limit < 1 or limit > 100:
                raise CognifyValidationError("Limit must be between 1 and 100")
            if offset < 0:
                raise CognifyValidationError("Offset must be non-negative")

            # Build query parameters
            params = {
                "limit": limit,
                "offset": offset,
            }
            if doc_status:
                params["doc_status"] = doc_status
            if document_type:
                params["document_type"] = document_type

            # Make API request
            url = f"{self._base_url}/{collection_id}/documents"
            if params:
                url += f"?{urlencode(params)}"

            response = await self.client.http.arequest("GET", url)

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot access documents for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to get collection documents: {response.get('message', 'Unknown error')}"
                )

            data = response.get("data", {})
            return data.get("documents", [])

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting collection documents: {str(e)}", status_code=500)

    async def get_usage_analytics(
        self,
        collection_id: str,
        days_back: int = 30,
    ) -> Dict[str, Any]:
        """
        Get usage analytics for a collection.

        Args:
            collection_id: Collection ID
            days_back: Number of days to look back (1-365)

        Returns:
            Usage analytics data

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyValidationError: If request parameters are invalid
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")
            if days_back < 1 or days_back > 365:
                raise CognifyValidationError("Days back must be between 1 and 365")

            # Make API request
            url = f"{self._base_url}/{collection_id}/analytics?days_back={days_back}"
            response = await self.client.http.arequest("GET", url)

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot access analytics for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to get usage analytics: {response.get('message', 'Unknown error')}"
                )

            return response.get("data", {})

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting usage analytics: {str(e)}", status_code=500)

    async def get_performance_metrics(
        self,
        collection_id: str,
        metric_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a collection.

        Args:
            collection_id: Collection ID
            metric_type: Type of metrics to retrieve (optional)

        Returns:
            Performance metrics data

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")

            # Build URL
            url = f"{self._base_url}/{collection_id}/metrics"
            if metric_type:
                url += f"?type={metric_type}"

            # Make API request
            response = await self.client.http.arequest("GET", url)

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot access metrics for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to get performance metrics: {response.get('message', 'Unknown error')}"
                )

            return response.get("data", {})

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error getting performance metrics: {str(e)}", status_code=500)

    async def export_analytics(
        self,
        collection_id: str,
        format: str = "json",
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Export collection analytics data.

        Args:
            collection_id: Collection ID
            format: Export format (json, csv, xlsx)
            include_details: Whether to include detailed data

        Returns:
            Export data or download information

        Raises:
            CognifyNotFoundError: If collection not found
            CognifyPermissionError: If user lacks permission
            CognifyValidationError: If request parameters are invalid
            CognifyAPIError: If API request fails
        """
        try:
            if not collection_id or not collection_id.strip():
                raise CognifyValidationError("Collection ID cannot be empty")
            if format not in ["json", "csv", "xlsx"]:
                raise CognifyValidationError("Format must be one of: json, csv, xlsx")

            # Build query parameters
            params = {
                "format": format,
                "include_details": str(include_details).lower(),
            }

            # Make API request
            url = f"{self._base_url}/{collection_id}/export?{urlencode(params)}"
            response = await self.client.http.arequest("GET", url)

            # Parse response
            if not response.get("success", False):
                error = response.get("error", {})
                if error.get("code") == "NOT_FOUND":
                    raise CognifyNotFoundError(f"Collection not found: {collection_id}")
                elif error.get("code") == "PERMISSION_DENIED":
                    raise CognifyPermissionError(
                        f"Permission denied: Cannot export analytics for collection {collection_id}"
                    )
                raise CognifyAPIError(
                    f"Failed to export analytics: {response.get('message', 'Unknown error')}"
                )

            return response.get("data", {})

        except CognifyValidationError:
            raise
        except CognifyNotFoundError:
            raise
        except CognifyPermissionError:
            raise
        except CognifyAPIError:
            raise
        except Exception as e:
            raise CognifyAPIError(f"Unexpected error exporting analytics: {str(e)}", status_code=500)

    # Sync versions of async methods
    def get_collection_stats_sync(self, *args, **kwargs) -> CollectionStats:
        """Synchronous version of get_collection_stats()."""
        return asyncio.run(self.get_collection_stats(*args, **kwargs))

    def get_collection_status_sync(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous version of get_collection_status()."""
        return asyncio.run(self.get_collection_status(*args, **kwargs))

    def get_collection_documents_sync(self, *args, **kwargs) -> List[Dict[str, Any]]:
        """Synchronous version of get_collection_documents()."""
        return asyncio.run(self.get_collection_documents(*args, **kwargs))

    def get_usage_analytics_sync(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous version of get_usage_analytics()."""
        return asyncio.run(self.get_usage_analytics(*args, **kwargs))

    def get_performance_metrics_sync(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous version of get_performance_metrics()."""
        return asyncio.run(self.get_performance_metrics(*args, **kwargs))

    def export_analytics_sync(self, *args, **kwargs) -> Dict[str, Any]:
        """Synchronous version of export_analytics()."""
        return asyncio.run(self.export_analytics(*args, **kwargs))
