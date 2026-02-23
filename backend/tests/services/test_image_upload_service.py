"""Unit tests for ImageUploadService.

Tests cover:
- Upload flow (validate, process, store, update DB)
- Delete flow (remove files, clear DB)
- Get URLs
- Old image cleanup on replacement
- Unique filename generation

Requirements: 3.1, 3.2, 3.3, 3.6, 3.7
"""

import io
import uuid
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from app.db_models.person.person import Person
from app.services.image_upload_service import ImageUploadService


def _make_jpeg(width: int = 200, height: int = 200) -> bytes:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def mock_person() -> Person:
    return Person(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        created_by_user_id=uuid.uuid4(),
        first_name="Test",
        last_name="User",
        gender_id=uuid.uuid4(),
        date_of_birth="2000-01-01",
        profile_image_key=None,
    )


@pytest.fixture
def service(mock_session: MagicMock) -> ImageUploadService:
    with patch("app.services.image_upload_service.get_storage_backend") as mock_storage_fn:
        mock_storage = MagicMock()
        mock_storage.get_url.side_effect = lambda f: f"/api/v1/uploads/person-images/{f}"
        mock_storage_fn.return_value = mock_storage

        svc = ImageUploadService(mock_session)
        svc.storage = mock_storage
        return svc


@pytest.mark.unit
class TestImageUploadServiceUpload:
    """Tests for ImageUploadService.upload_profile_image()."""

    def test_upload_returns_urls(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        service.session = mock_session
        data = _make_jpeg()
        result = service.upload_profile_image(mock_person, data)

        assert "main_url" in result
        assert "thumbnail_url" in result
        assert "message" in result
        assert result["main_url"].endswith(".jpg")
        assert "_thumb.jpg" in result["thumbnail_url"]

    def test_upload_calls_storage_twice(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        """Should upload both main and thumbnail."""
        service.session = mock_session
        data = _make_jpeg()
        service.upload_profile_image(mock_person, data)

        assert service.storage.upload.call_count == 2

    def test_upload_updates_person_record(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        service.session = mock_session
        data = _make_jpeg()
        service.upload_profile_image(mock_person, data)

        assert mock_person.profile_image_key is not None
        assert mock_person.profile_image_key.endswith(".jpg")
        mock_session.add.assert_called()
        mock_session.commit.assert_called()

    def test_upload_cleans_old_image(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        mock_person.profile_image_key = "old_image.jpg"
        service.session = mock_session
        data = _make_jpeg()
        service.upload_profile_image(mock_person, data)

        # Should have deleted old main + old thumb, then uploaded new main + new thumb
        assert service.storage.delete.call_count == 2
        delete_calls = [c.args[0] for c in service.storage.delete.call_args_list]
        assert "old_image.jpg" in delete_calls
        assert "old_image_thumb.jpg" in delete_calls

    def test_upload_rejects_invalid_image(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        service.session = mock_session
        with pytest.raises(ValueError, match="Invalid image format"):
            service.upload_profile_image(mock_person, b"not an image")

    def test_upload_generates_unique_filenames(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        service.session = mock_session
        data = _make_jpeg()

        result1 = service.upload_profile_image(mock_person, data)
        mock_person.profile_image_key = None
        service.storage.reset_mock()

        result2 = service.upload_profile_image(mock_person, data)

        assert result1["main_url"] != result2["main_url"]


@pytest.mark.unit
class TestImageUploadServiceDelete:
    """Tests for ImageUploadService.delete_profile_image()."""

    def test_delete_removes_files_and_clears_record(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        mock_person.profile_image_key = "existing.jpg"
        service.session = mock_session
        service.delete_profile_image(mock_person)

        assert service.storage.delete.call_count == 2
        assert mock_person.profile_image_key is None
        mock_session.commit.assert_called()

    def test_delete_noop_when_no_image(
        self, service: ImageUploadService, mock_person: Person, mock_session: MagicMock
    ) -> None:
        mock_person.profile_image_key = None
        service.session = mock_session
        service.delete_profile_image(mock_person)

        service.storage.delete.assert_not_called()


@pytest.mark.unit
class TestImageUploadServiceGetUrls:
    """Tests for ImageUploadService.get_image_urls()."""

    def test_get_urls_returns_both(
        self, service: ImageUploadService, mock_person: Person
    ) -> None:
        mock_person.profile_image_key = "abc123.jpg"
        result = service.get_image_urls(mock_person)

        assert result is not None
        assert "main_url" in result
        assert "thumbnail_url" in result
        assert "abc123.jpg" in result["main_url"]
        assert "abc123_thumb.jpg" in result["thumbnail_url"]

    def test_get_urls_returns_none_when_no_image(
        self, service: ImageUploadService, mock_person: Person
    ) -> None:
        mock_person.profile_image_key = None
        result = service.get_image_urls(mock_person)
        assert result is None
