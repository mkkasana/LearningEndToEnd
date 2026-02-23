"""Storage backend package with factory function."""

from app.core.config import settings
from app.services.storage.base import StorageBackend
from app.services.storage.local_storage import LocalStorage


def get_storage_backend() -> StorageBackend:
    """Return the appropriate storage backend based on environment."""
    if settings.ENVIRONMENT == "local":
        return LocalStorage(upload_dir="uploads/person-images")
    # Lazy import to avoid requiring boto3 in local dev
    from app.services.storage.s3_storage import S3Storage

    return S3Storage(
        bucket=settings.S3_IMAGES_BUCKET,
        cloudfront_url=settings.CLOUDFRONT_IMAGES_URL,
    )


__all__ = ["StorageBackend", "LocalStorage", "get_storage_backend"]
