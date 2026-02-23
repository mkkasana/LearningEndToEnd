"""Unit tests for LocalStorage.

Tests cover:
- File upload (round-trip read back)
- File deletion
- URL format

Requirements: 1.2, 1.4, 1.6
"""

import os
import tempfile

import pytest

from app.services.storage.local_storage import LocalStorage


@pytest.fixture
def storage(tmp_path: str) -> LocalStorage:
    """Create a LocalStorage instance using a temp directory."""
    upload_dir = os.path.join(tmp_path, "person-images")
    return LocalStorage(upload_dir=upload_dir)


@pytest.mark.unit
class TestLocalStorageUpload:
    """Tests for LocalStorage.upload()."""

    def test_upload_writes_file(self, storage: LocalStorage) -> None:
        data = b"fake image data"
        key = storage.upload(data, "test.jpg")
        assert key == "test.jpg"

        file_path = storage.upload_dir / "test.jpg"
        assert file_path.exists()
        assert file_path.read_bytes() == data

    def test_upload_round_trip(self, storage: LocalStorage) -> None:
        """Round-trip: upload then read back returns same bytes."""
        data = b"\x89PNG\r\n\x1a\n" + os.urandom(256)
        storage.upload(data, "roundtrip.jpg")

        read_back = (storage.upload_dir / "roundtrip.jpg").read_bytes()
        assert read_back == data

    def test_upload_creates_directory(self, tmp_path: str) -> None:
        nested = os.path.join(tmp_path, "deep", "nested", "dir")
        s = LocalStorage(upload_dir=nested)
        s.upload(b"data", "file.jpg")
        assert os.path.exists(os.path.join(nested, "file.jpg"))


@pytest.mark.unit
class TestLocalStorageDelete:
    """Tests for LocalStorage.delete()."""

    def test_delete_removes_file(self, storage: LocalStorage) -> None:
        storage.upload(b"data", "to_delete.jpg")
        assert (storage.upload_dir / "to_delete.jpg").exists()

        storage.delete("to_delete.jpg")
        assert not (storage.upload_dir / "to_delete.jpg").exists()

    def test_delete_nonexistent_file_no_error(self, storage: LocalStorage) -> None:
        storage.delete("does_not_exist.jpg")  # should not raise


@pytest.mark.unit
class TestLocalStorageGetUrl:
    """Tests for LocalStorage.get_url()."""

    def test_url_format(self, storage: LocalStorage) -> None:
        url = storage.get_url("abc123.jpg")
        assert url == "/api/v1/uploads/person-images/abc123.jpg"

    def test_url_contains_filename(self, storage: LocalStorage) -> None:
        url = storage.get_url("my-image.jpg")
        assert "my-image.jpg" in url
        assert url.startswith("/api/v1/uploads/person-images/")
