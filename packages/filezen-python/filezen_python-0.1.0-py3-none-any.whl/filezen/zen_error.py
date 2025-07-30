"""Error handling for the FileZen Python SDK."""

from typing import Any, Dict, Optional


class ZenError(Exception):
    """Base exception for FileZen SDK errors."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize ZenError.

        Args:
            message: Error message
            code: Error code
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }


class ZenUploadError(ZenError):
    """Exception raised during file upload operations."""

    pass


class ZenAuthenticationError(ZenError):
    """Exception raised for authentication failures."""

    pass


class ZenValidationError(ZenError):
    """Exception raised for validation failures."""

    pass


class ZenNetworkError(ZenError):
    """Exception raised for network-related errors."""

    pass
