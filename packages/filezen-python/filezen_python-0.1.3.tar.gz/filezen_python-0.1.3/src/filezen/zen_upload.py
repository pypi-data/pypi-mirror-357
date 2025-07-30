"""Upload functionality for the FileZen Python SDK."""

from typing import Optional

from pydantic import BaseModel, Field

from .constants import MULTIPART_CHUNK_SIZE, MULTIPART_THRESHOLD
from .zen_api import ZenApi
from .zen_error import ZenError, ZenUploadError
from .zen_file import ZenFile


class UploadOptions(BaseModel):
    """Options for file upload."""

    name: str = Field(..., description="Name of the file")
    mime_type: Optional[str] = Field(None, description="MIME type of the file")
    folder: Optional[str] = Field(None, description="Folder to upload to")

    class Config:
        """Pydantic configuration."""

        extra = "forbid"


class ZenUpload(BaseModel):
    """Represents a file upload operation."""

    local_id: str = Field(..., description="Local upload identifier")
    name: str = Field(..., description="Name of the file")
    size: int = Field(..., description="Size of the file in bytes")
    mime_type: str = Field(..., description="MIME type of the file")
    file: Optional[ZenFile] = Field(None, description="Uploaded file information")
    error: Optional[ZenError] = Field(None, description="Upload error if any")
    is_completed: bool = Field(False, description="Whether upload is completed")
    is_cancelled: bool = Field(False, description="Whether upload is cancelled")

    # Internal fields (no leading underscores for Pydantic v2 compatibility)
    api: Optional[ZenApi] = Field(None, description="API client")
    source: Optional[bytes] = Field(None, description="File source data")
    options: Optional[UploadOptions] = Field(None, description="Upload options")

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True

    async def upload(self) -> "ZenUpload":
        """Perform the upload operation.

        Returns:
            Self with updated file information
        """
        if self.api is None:
            raise ZenUploadError("Upload not properly initialized: api is None")
        if self.source is None:
            raise ZenUploadError("Upload not properly initialized: source is None")
        if self.options is None:
            raise ZenUploadError("Upload not properly initialized: options is None")

        try:
            # Determine if we should use multipart upload
            if self.size > MULTIPART_THRESHOLD:
                await self._multipart_upload()
            else:
                await self._regular_upload()

            self.is_completed = True

        except Exception as e:
            if isinstance(e, ZenError):
                self.error = e
            else:
                self.error = ZenUploadError(str(e))
            raise

        return self

    async def _regular_upload(self) -> None:
        """Perform a regular upload."""
        assert self.api is not None
        assert self.source is not None
        assert self.options is not None
        # Perform actual upload
        result = await self.api.upload_file(
            self.source,
            {
                "name": self.options.name,
                "mimeType": self.options.mime_type or "application/octet-stream",
            },
        )

        if result.get("error"):
            raise ZenUploadError(result["error"].get("message", "Upload failed"))

        # Use the API response directly - it should already match ZenFile structure
        self.file = ZenFile(**result["data"])

    async def _multipart_upload(self) -> None:
        """Perform a multipart upload for large files."""
        assert self.api is not None
        assert self.source is not None
        assert self.options is not None
        # Initialize multipart upload
        init_result = await self.api.initialize_multipart_upload(
            {
                "fileName": self.options.name,
                "mimeType": self.options.mime_type or "application/octet-stream",
                "totalSize": self.size,
                "chunkSize": MULTIPART_CHUNK_SIZE,
            }
        )

        if init_result.get("error"):
            raise ZenUploadError(
                init_result["error"].get(
                    "message", "Multipart upload initialization failed"
                )
            )

        session_id = init_result["data"]["id"]
        total_chunks = (self.size + MULTIPART_CHUNK_SIZE - 1) // MULTIPART_CHUNK_SIZE
        current_chunk_index = 0

        while current_chunk_index < total_chunks:
            # Calculate chunk boundaries
            start = current_chunk_index * MULTIPART_CHUNK_SIZE
            end = min(start + MULTIPART_CHUNK_SIZE, self.size)
            chunk = self.source[start:end]
            chunk_size = len(chunk)

            # Upload chunk
            chunk_result = await self.api.upload_chunk(
                session_id, chunk, current_chunk_index, chunk_size
            )

            if chunk_result.get("error"):
                raise ZenUploadError(
                    chunk_result["error"].get(
                        "message", f"Chunk {current_chunk_index} upload failed"
                    )
                )

            chunk_data = chunk_result["data"]

            # Check if upload is complete
            if chunk_data.get("isComplete"):
                if "file" in chunk_data:
                    # Use the API response directly - it should already match ZenFile structure
                    self.file = ZenFile(**chunk_data["file"])
                break

            # Move to next chunk
            current_chunk_index = chunk_data.get(
                "nextChunkIndex", current_chunk_index + 1
            )

        if not self.file:
            raise ZenUploadError("Multipart upload did not complete as expected")

    def cancel(self) -> None:
        """Cancel the upload operation."""
        self.is_cancelled = True
