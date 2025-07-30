"""API communication for the FileZen Python SDK."""

import os
from typing import Any, Dict, Optional

import httpx

from .constants import DEFAULT_API_URL
from .zen_error import ZenAuthenticationError, ZenNetworkError


class ZenApi:
    """Handles API communication with FileZen."""

    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        """Initialize ZenApi.

        Args:
            options: Configuration options
        """
        self.options = options or {}

        # Get API key from options or environment
        self.api_key = (
            self.options.get("api_key")
            or os.getenv("FILEZEN_API_KEY")
            or os.getenv("REACT_APP_FILEZEN_API_KEY")
            or os.getenv("NEXT_PUBLIC_FILEZEN_API_KEY")
        )

        if not self.api_key:
            raise ZenAuthenticationError(
                "No API key provided. Set FILEZEN_API_KEY environment variable or pass api_key in options."
            )

        # Get API URL with fallback
        self.api_url = self.options.get("api_url") or DEFAULT_API_URL

        # Ensure we have a valid API URL
        if not self.api_url:
            raise ValueError("No API URL provided and DEFAULT_API_URL is not set")

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "ApiKey": self.api_key,
            },
            timeout=httpx.Timeout(
                connect=30.0,  # Connection timeout
                read=300.0,  # Read timeout (5 minutes for large files)
                write=300.0,  # Write timeout (5 minutes for large files)
                pool=30.0,  # Pool timeout
            ),
        )

    async def upload_file(
        self, source: bytes, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Upload a file to FileZen.

        Args:
            source: File content as bytes
            params: Upload parameters

        Returns:
            Upload result
        """
        try:
            # Prepare multipart form data
            files = {
                "file": (
                    params["name"],
                    source,
                    params.get("mimeType", "application/octet-stream"),
                )
            }

            # Additional form data
            data = {}
            if "mimeType" in params:
                data["mimeType"] = params["mimeType"]

            response = await self.client.post("/files/upload", files=files, data=data)
            response.raise_for_status()

            return {"data": response.json()}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ZenAuthenticationError("Invalid API key") from e
            elif e.response.status_code == 413:
                raise ZenNetworkError("File too large") from e
            else:
                raise ZenNetworkError(f"Upload failed: {e.response.text}") from e
        except httpx.RequestError as e:
            raise ZenNetworkError(f"Network error: {str(e)}") from e

    async def delete_file_by_url(self, url: str) -> Dict[str, Any]:
        """Delete a file by URL.

        Args:
            url: File URL to delete

        Returns:
            Delete result
        """
        try:
            response = await self.client.delete(
                "/files/delete-by-url", params={"url": url}
            )
            response.raise_for_status()

            return {"data": True}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ZenAuthenticationError("Invalid API key") from e
            else:
                raise ZenNetworkError(f"Delete failed: {e.response.text}") from e
        except httpx.RequestError as e:
            raise ZenNetworkError(f"Network error: {str(e)}") from e

    async def initialize_multipart_upload(
        self, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Initialize a multipart upload.

        Args:
            params: Multipart upload parameters

        Returns:
            Multipart upload initialization result
        """
        try:
            response = await self.client.post(
                "/files/chunk-upload/initialize", json=params
            )
            response.raise_for_status()

            return {"data": response.json()}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ZenAuthenticationError("Invalid API key") from e
            else:
                raise ZenNetworkError(
                    f"Multipart upload initialization failed: {e.response.text}"
                ) from e
        except httpx.RequestError as e:
            raise ZenNetworkError(f"Network error: {str(e)}") from e

    async def upload_chunk(
        self, session_id: str, chunk: bytes, chunk_index: int, chunk_size: int
    ) -> Dict[str, Any]:
        """Upload a chunk in multipart upload.

        Args:
            session_id: Multipart upload session ID
            chunk: Chunk data
            chunk_index: Index of the chunk
            chunk_size: Size of the chunk

        Returns:
            Chunk upload result
        """
        try:
            files = {
                "chunk": (f"chunk_{chunk_index}", chunk, "application/octet-stream")
            }
            headers = {
                "Chunk-Session-Id": session_id,
                "Chunk-Size": str(chunk_size),
                "Chunk-Index": str(chunk_index),
            }

            response = await self.client.post(
                "/files/chunk-upload/part", files=files, headers=headers
            )
            response.raise_for_status()

            return {"data": response.json()}

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ZenAuthenticationError("Invalid API key") from e
            else:
                raise ZenNetworkError(f"Chunk upload failed: {e.response.text}") from e
        except httpx.RequestError as e:
            raise ZenNetworkError(f"Network error: {str(e)}") from e

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "ZenApi":
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> None:
        """Async context manager exit."""
        await self.close()
