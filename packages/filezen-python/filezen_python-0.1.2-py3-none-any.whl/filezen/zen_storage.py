"""Main storage class for the FileZen Python SDK."""

import uuid
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .zen_api import ZenApi
from .zen_upload import UploadOptions, ZenUpload


class ZenStorageListener(BaseModel):
    """Listener for storage events."""

    on_upload_start: Optional[Any] = None
    on_upload_complete: Optional[Any] = None
    on_upload_error: Optional[Any] = None
    on_upload_cancel: Optional[Any] = None
    on_uploads_change: Optional[Any] = None

    class Config:
        """Pydantic configuration."""

        arbitrary_types_allowed = True


class ZenStorageOptions(BaseModel):
    """Options for ZenStorage."""

    api_key: Optional[str] = Field(None, description="FileZen API key")
    api_url: Optional[str] = Field(None, description="FileZen API URL")
    keep_uploads: bool = Field(True, description="Whether to keep track of uploads")

    class Config:
        """Pydantic configuration."""

        extra = "forbid"


class ZenStorage:
    """Main storage class for FileZen operations."""

    def __init__(
        self, options: Optional[Union[Dict[str, Any], ZenStorageOptions]] = None
    ) -> None:
        """Initialize ZenStorage.

        Args:
            options: Configuration options
        """
        if isinstance(options, dict):
            options_obj = ZenStorageOptions(
                api_key=options.get("api_key"),
                api_url=options.get("api_url"),
                keep_uploads=bool(options.get("keep_uploads", True)),
            )
        elif options is None:
            options_obj = ZenStorageOptions(
                api_key=None,
                api_url=None,
                keep_uploads=True,
            )
        else:
            options_obj = ZenStorageOptions(
                api_key=options.api_key,
                api_url=options.api_url,
                keep_uploads=options.keep_uploads,
            )

        self.options = options_obj
        self.api = ZenApi(options_obj.model_dump())
        self.listeners: List[ZenStorageListener] = []
        self.uploads: Dict[str, ZenUpload] = {}

    def add_listener(self, listener: ZenStorageListener) -> None:
        """Add an event listener.

        Args:
            listener: Listener to add
        """
        self.listeners.append(listener)

    def remove_listener(self, listener: ZenStorageListener) -> None:
        """Remove an event listener.

        Args:
            listener: Listener to remove
        """
        if listener in self.listeners:
            self.listeners.remove(listener)

    @property
    def get_uploads(self) -> List[ZenUpload]:
        """Get all uploads."""
        return list(self.uploads.values())

    @property
    def active_uploads(self) -> List[ZenUpload]:
        """Get active uploads."""
        return [
            upload
            for upload in self.uploads.values()
            if not upload.error and not upload.is_completed
        ]

    def _notify_listeners(self, event: str, *args: Any) -> None:
        """Notify all listeners of an event.

        Args:
            event: Event name
            args: Event arguments
        """
        for listener in self.listeners:
            callback = getattr(listener, event, None)
            if callback:
                try:
                    callback(*args)
                except Exception as e:
                    print(f"Listener error in {event}: {e}")

    def build_upload(
        self,
        source: bytes,
        options: Optional[Union[Dict[str, Any], UploadOptions]] = None,
    ) -> ZenUpload:
        """Build an upload object.

        Args:
            source: File content as bytes
            options: Upload options

        Returns:
            ZenUpload object
        """
        if isinstance(options, dict):
            options = UploadOptions(**options)
        elif options is None:
            raise ValueError("Upload options are required")

        local_id = str(uuid.uuid4())

        upload = ZenUpload(
            local_id=local_id,
            name=options.name,
            size=len(source),
            mime_type=options.mime_type or "application/octet-stream",
            api=self.api,
            source=source,
            options=options,
            file=None,
            error=None,
            is_completed=False,
            is_cancelled=False,
        )

        # Store upload if keep_uploads is enabled
        if self.options.keep_uploads:
            self.uploads[local_id] = upload
            self._notify_listeners("on_uploads_change", self.get_uploads)

        return upload

    async def upload(
        self,
        source: bytes,
        options: Optional[Union[Dict[str, Any], UploadOptions]] = None,
    ) -> ZenUpload:
        """Upload a single file.

        Args:
            source: File content as bytes
            options: Upload options

        Returns:
            Completed upload
        """
        upload = self.build_upload(source, options)

        self._notify_listeners("on_upload_start", upload)

        try:
            await upload.upload()
            self._notify_listeners("on_upload_complete", upload)
        except Exception as e:
            self._notify_listeners("on_upload_error", upload, e)
            raise

        return upload

    async def bulk_upload(self, *uploads: Dict[str, Any]) -> List[ZenUpload]:
        """Upload multiple files.

        Args:
            *uploads: Upload items with 'source' and 'options' keys

        Returns:
            List of completed uploads
        """
        upload_objects = []

        # Build upload objects
        for upload_item in uploads:
            source = upload_item["source"]
            options = upload_item["options"]
            upload_obj = self.build_upload(source, options)
            upload_objects.append(upload_obj)

        # Start all uploads
        for upload in upload_objects:
            self._notify_listeners("on_upload_start", upload)

        # Upload all files concurrently
        import asyncio

        tasks = [upload.upload() for upload in upload_objects]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        completed_uploads = []
        for i, result in enumerate(results):
            upload = upload_objects[i]
            if isinstance(result, Exception):
                self._notify_listeners("on_upload_error", upload, result)
            else:
                self._notify_listeners("on_upload_complete", upload)
                completed_uploads.append(upload)

        return completed_uploads

    def generate_signed_url(self, options: Dict[str, Any]) -> str:
        """Generate a signed URL for direct uploads.

        Args:
            options: Signed URL options with 'path', 'file_key', and optional 'expires_in'

        Returns:
            Signed URL string
        """
        import hashlib
        import hmac
        import time
        from urllib.parse import urlencode

        path = options.get("path", "/files/upload")
        file_key = options["file_key"]
        expires_in = options.get("expires_in", 3600)

        # Decode API key to get credentials
        import base64

        api_key = self.api.api_key
        if not api_key:
            raise ValueError("API key is required for signed URL generation")

        decoded_credentials = base64.b64decode(api_key).decode("utf-8").split(",")
        access_key = decoded_credentials[0]
        secret_key = decoded_credentials[1]

        # Calculate expiration time
        expires_at = int(time.time()) + expires_in

        # Create string to sign
        string_to_sign = f"{file_key}/n{expires_at}"

        # Generate signature
        signature = hmac.new(
            secret_key.encode("utf-8"), string_to_sign.encode("utf-8"), hashlib.sha256
        ).hexdigest()

        # Build signed URL
        base_url = self.api.api_url.rstrip("/")
        path = path.lstrip("/")
        url = f"{base_url}/{path}"

        # Add query parameters
        params = {
            "signature": signature,
            "accessKey": access_key,
            "expires": str(expires_at),
        }

        return f"{url}?{urlencode(params)}"

    async def delete_by_url(self, url: str) -> bool:
        """Delete a file by URL.

        Args:
            url: File URL to delete

        Returns:
            True if deletion was successful
        """
        result = await self.api.delete_file_by_url(url)
        return bool(result.get("data", False))

    async def close(self) -> None:
        """Close the storage and cleanup resources."""
        await self.api.close()

    async def __aenter__(self) -> "ZenStorage":
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
