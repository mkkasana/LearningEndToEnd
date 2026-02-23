"""Local filesystem storage backend for development."""

import logging
from pathlib import Path

from app.services.storage.base import StorageBackend

logger = logging.getLogger(__name__)


class LocalStorage(StorageBackend):
    """Stores files on the local filesystem. Used in local/dev environments."""

    def __init__(self, upload_dir: str = "uploads/person-images") -> None:
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def upload(self, file_data: bytes, filename: str) -> str:
        """Save file to local disk and return the filename as storage key."""
        file_path = self.upload_dir / filename
        file_path.write_bytes(file_data)
        logger.info("Saved file to %s", file_path)
        return filename

    def delete(self, filename: str) -> None:
        """Delete a file from local disk."""
        file_path = self.upload_dir / filename
        if file_path.exists():
            file_path.unlink()
            logger.info("Deleted file %s", file_path)
        else:
            logger.warning("File not found for deletion: %s", file_path)

    def get_url(self, filename: str) -> str:
        """Return the relative URL path for serving the file locally."""
        return f"/api/v1/uploads/person-images/{filename}"
