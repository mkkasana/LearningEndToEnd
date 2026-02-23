"""Abstract base class for storage backends."""

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    """Interface for file storage operations."""

    @abstractmethod
    def upload(self, file_data: bytes, filename: str) -> str:
        """Upload file and return the storage key."""
        ...

    @abstractmethod
    def delete(self, filename: str) -> None:
        """Delete a file by its storage key."""
        ...

    @abstractmethod
    def get_url(self, filename: str) -> str:
        """Get the public URL for a stored file."""
        ...
