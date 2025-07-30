"""File model for the FileZen Python SDK."""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class FileType(str, Enum):
    """File type enumeration."""

    file = "file"
    folder = "folder"


class FileState(str, Enum):
    """File state enumeration."""

    deleting = "deleting"
    uploading = "uploading"
    completed = "completed"


class ZenProject(BaseModel):
    """Represents a project in FileZen."""

    id: str = Field(..., description="Project ID")
    created_at: str = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: str = Field(..., alias="updatedAt", description="Last update timestamp")
    name: str = Field(..., description="Project name")
    organisation_id: str = Field(
        ..., alias="organisationId", description="Organization ID"
    )
    region: str = Field(..., description="Project region")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class ZenFile(BaseModel):
    """Represents a file in FileZen."""

    id: str = Field(..., description="Unique identifier of the file")
    created_at: Optional[str] = Field(
        None, alias="createdAt", description="Creation timestamp"
    )
    updated_at: Optional[str] = Field(
        None, alias="updatedAt", description="Last update timestamp"
    )
    type: Optional[FileType] = Field(
        FileType.file, description="File type (file or folder)"
    )
    state: Optional[FileState] = Field(FileState.completed, description="File state")
    name: str = Field(..., description="Name of the file")
    mime_type: str = Field(..., alias="mimeType", description="MIME type of the file")
    size: int = Field(..., description="Size of the file in bytes")
    region: Optional[str] = Field(None, description="File region")
    url: Optional[str] = Field(None, description="Public URL of the file")
    project_id: Optional[str] = Field(None, alias="projectId", description="Project ID")
    project: Optional[ZenProject] = Field(None, description="Project information")
    parent_id: Optional[str] = Field(
        None, alias="parentId", description="Parent file/folder ID"
    )
    parent: Optional["ZenFile"] = Field(None, description="Parent file/folder")
    metadata: Optional[Dict[str, Any]] = Field(None, description="File metadata")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
        json_encoders: Dict[Any, Any] = {
            # Add custom JSON encoders if needed
        }
