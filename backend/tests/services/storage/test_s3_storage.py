"""Unit tests for S3Storage.

Tests cover:
- URL generation (CloudFront vs S3 fallback)
- Upload calls boto3 correctly
- Delete calls boto3 correctly

Requirements: 1.3, 1.5, 1.7
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.storage.s3_storage import S3Storage


@pytest.fixture
def s3_with_cloudfront() -> S3Storage:
    with patch("app.services.storage.s3_storage.boto3") as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        storage = S3Storage(
            bucket="my-bucket",
            cloudfront_url="https://cdn.example.com",
        )
        return storage


@pytest.fixture
def s3_without_cloudfront() -> S3Storage:
    with patch("app.services.storage.s3_storage.boto3") as mock_boto3:
        mock_client = MagicMock()
        mock_boto3.client.return_value = mock_client
        storage = S3Storage(bucket="my-bucket", cloudfront_url="")
        return storage


@pytest.mark.unit
class TestS3StorageGetUrl:
    """Tests for S3Storage.get_url()."""

    def test_url_uses_cloudfront_when_configured(self, s3_with_cloudfront: S3Storage) -> None:
        url = s3_with_cloudfront.get_url("abc123.jpg")
        assert url == "https://cdn.example.com/person-images/abc123.jpg"

    def test_url_falls_back_to_s3_when_no_cloudfront(self, s3_without_cloudfront: S3Storage) -> None:
        url = s3_without_cloudfront.get_url("abc123.jpg")
        assert url == "https://my-bucket.s3.amazonaws.com/person-images/abc123.jpg"

    def test_url_strips_trailing_slash_from_cloudfront(self) -> None:
        with patch("app.services.storage.s3_storage.boto3"):
            storage = S3Storage(bucket="b", cloudfront_url="https://cdn.example.com/")
        url = storage.get_url("file.jpg")
        assert url == "https://cdn.example.com/person-images/file.jpg"

    def test_url_includes_person_images_prefix(self, s3_with_cloudfront: S3Storage) -> None:
        url = s3_with_cloudfront.get_url("test.jpg")
        assert "/person-images/" in url


@pytest.mark.unit
class TestS3StorageUpload:
    """Tests for S3Storage.upload()."""

    def test_upload_calls_put_object(self, s3_with_cloudfront: S3Storage) -> None:
        result = s3_with_cloudfront.upload(b"image data", "test.jpg")

        assert result == "test.jpg"
        s3_with_cloudfront.s3_client.put_object.assert_called_once_with(
            Bucket="my-bucket",
            Key="person-images/test.jpg",
            Body=b"image data",
            ContentType="image/jpeg",
        )


@pytest.mark.unit
class TestS3StorageDelete:
    """Tests for S3Storage.delete()."""

    def test_delete_calls_delete_object(self, s3_with_cloudfront: S3Storage) -> None:
        s3_with_cloudfront.delete("test.jpg")

        s3_with_cloudfront.s3_client.delete_object.assert_called_once_with(
            Bucket="my-bucket",
            Key="person-images/test.jpg",
        )
