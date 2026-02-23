"""Unit tests for person image response schemas.

Tests cover:
- PersonImageResponse validation
- PersonImageUploadResponse validation

Requirements: 3.2
"""

import pytest

from app.schemas.person.person_image import PersonImageResponse, PersonImageUploadResponse


@pytest.mark.unit
class TestPersonImageResponse:
    """Tests for PersonImageResponse schema."""

    def test_valid_response(self) -> None:
        resp = PersonImageResponse(
            main_url="/api/v1/uploads/person-images/abc.jpg",
            thumbnail_url="/api/v1/uploads/person-images/abc_thumb.jpg",
        )
        assert resp.main_url == "/api/v1/uploads/person-images/abc.jpg"
        assert resp.thumbnail_url == "/api/v1/uploads/person-images/abc_thumb.jpg"

    def test_requires_main_url(self) -> None:
        with pytest.raises(Exception):
            PersonImageResponse(thumbnail_url="/thumb.jpg")  # type: ignore[call-arg]

    def test_requires_thumbnail_url(self) -> None:
        with pytest.raises(Exception):
            PersonImageResponse(main_url="/main.jpg")  # type: ignore[call-arg]


@pytest.mark.unit
class TestPersonImageUploadResponse:
    """Tests for PersonImageUploadResponse schema."""

    def test_valid_upload_response(self) -> None:
        resp = PersonImageUploadResponse(
            message="Profile image uploaded successfully",
            main_url="/main.jpg",
            thumbnail_url="/thumb.jpg",
        )
        assert resp.message == "Profile image uploaded successfully"
        assert resp.main_url == "/main.jpg"
        assert resp.thumbnail_url == "/thumb.jpg"

    def test_requires_message(self) -> None:
        with pytest.raises(Exception):
            PersonImageUploadResponse(main_url="/m.jpg", thumbnail_url="/t.jpg")  # type: ignore[call-arg]
