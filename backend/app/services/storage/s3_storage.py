"""AWS S3 storage backend for staging/production."""

import logging

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from app.services.storage.base import StorageBackend

logger = logging.getLogger(__name__)

PERSON_IMAGES_PREFIX = "person-images"


class S3Storage(StorageBackend):
    """Stores files in AWS S3. Used in staging/production environments."""

    def __init__(self, bucket: str, cloudfront_url: str = "") -> None:
        self.bucket = bucket
        self.cloudfront_url = cloudfront_url.rstrip("/")
        self.s3_client = boto3.client("s3")

    def _s3_key(self, filename: str) -> str:
        return f"{PERSON_IMAGES_PREFIX}/{filename}"

    def upload(self, file_data: bytes, filename: str) -> str:
        """Upload file to S3 and return the filename as storage key."""
        key = self._s3_key(filename)
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=file_data,
            ContentType="image/jpeg",
        )
        logger.info("Uploaded %s to s3://%s/%s", filename, self.bucket, key)
        return filename

    def delete(self, filename: str) -> None:
        """Delete a file from S3."""
        key = self._s3_key(filename)
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            logger.info("Deleted s3://%s/%s", self.bucket, key)
        except ClientError:
            logger.exception("Failed to delete s3://%s/%s", self.bucket, key)

    def get_url(self, filename: str) -> str:
        """Return the CloudFront or S3 URL for the file."""
        key = self._s3_key(filename)
        if self.cloudfront_url:
            return f"{self.cloudfront_url}/{key}"
        return f"https://{self.bucket}.s3.amazonaws.com/{key}"
