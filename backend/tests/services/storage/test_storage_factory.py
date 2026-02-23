"""Unit tests for storage factory function.

Tests cover:
- Returns LocalStorage when ENVIRONMENT=local
- Returns S3Storage when ENVIRONMENT=staging or production

Requirements: 1.2, 1.3
"""

from unittest.mock import patch

import pytest

from app.services.storage.local_storage import LocalStorage


@pytest.mark.unit
class TestGetStorageBackend:
    """Tests for get_storage_backend() factory."""

    def test_returns_local_storage_for_local_env(self) -> None:
        with patch("app.services.storage.settings") as mock_settings:
            mock_settings.ENVIRONMENT = "local"
            from app.services.storage import get_storage_backend

            backend = get_storage_backend()
            assert isinstance(backend, LocalStorage)

    def test_returns_s3_storage_for_staging_env(self) -> None:
        with patch("app.services.storage.settings") as mock_settings, \
             patch("app.services.storage.s3_storage.boto3"):
            mock_settings.ENVIRONMENT = "staging"
            mock_settings.S3_IMAGES_BUCKET = "test-bucket"
            mock_settings.CLOUDFRONT_IMAGES_URL = ""

            from app.services.storage import get_storage_backend
            from app.services.storage.s3_storage import S3Storage

            backend = get_storage_backend()
            assert isinstance(backend, S3Storage)

    def test_returns_s3_storage_for_production_env(self) -> None:
        with patch("app.services.storage.settings") as mock_settings, \
             patch("app.services.storage.s3_storage.boto3"):
            mock_settings.ENVIRONMENT = "production"
            mock_settings.S3_IMAGES_BUCKET = "prod-bucket"
            mock_settings.CLOUDFRONT_IMAGES_URL = "https://cdn.example.com"

            from app.services.storage import get_storage_backend
            from app.services.storage.s3_storage import S3Storage

            backend = get_storage_backend()
            assert isinstance(backend, S3Storage)
