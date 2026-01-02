"""Unit tests for Religion schemas."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.religion.religion import (
    ReligionBase,
    ReligionCreate,
    ReligionUpdate,
    ReligionPublic,
    ReligionDetailPublic,
)


@pytest.mark.unit
class TestReligionBase:
    """Tests for ReligionBase schema."""

    def test_valid_religion_base(self) -> None:
        """Test ReligionBase with valid data."""
        religion = ReligionBase(name="Christianity", code="CHRISTIAN")
        assert religion.name == "Christianity"
        assert religion.code == "CHRISTIAN"
        assert religion.is_active is True
        assert religion.description is None

    def test_religion_base_with_all_fields(self) -> None:
        """Test ReligionBase with all fields."""
        religion = ReligionBase(
            name="Christianity",
            code="CHRISTIAN",
            description="Christian faith",
            is_active=False,
        )
        assert religion.description == "Christian faith"
        assert religion.is_active is False

    def test_religion_base_name_required(self) -> None:
        """Test ReligionBase requires name."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionBase(code="CHRISTIAN")
        assert "name" in str(exc_info.value)

    def test_religion_base_code_required(self) -> None:
        """Test ReligionBase requires code."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionBase(name="Christianity")
        assert "code" in str(exc_info.value)

    def test_religion_base_code_max_length(self) -> None:
        """Test ReligionBase code max length (10 chars)."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionBase(name="Test Religion", code="TOOLONGCODE")
        assert "code" in str(exc_info.value)

    def test_religion_base_name_max_length(self) -> None:
        """Test ReligionBase name max length."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionBase(name="A" * 256, code="TEST")
        assert "name" in str(exc_info.value)

    def test_religion_base_description_max_length(self) -> None:
        """Test ReligionBase description max length."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionBase(name="Test", code="TEST", description="A" * 501)
        assert "description" in str(exc_info.value)


@pytest.mark.unit
class TestReligionCreate:
    """Tests for ReligionCreate schema."""

    def test_valid_religion_create(self) -> None:
        """Test ReligionCreate with valid data."""
        religion = ReligionCreate(name="Islam", code="ISLAM")
        assert religion.name == "Islam"
        assert religion.code == "ISLAM"


@pytest.mark.unit
class TestReligionUpdate:
    """Tests for ReligionUpdate schema."""

    def test_religion_update_all_optional(self) -> None:
        """Test ReligionUpdate with no fields."""
        religion = ReligionUpdate()
        assert religion.name is None
        assert religion.code is None
        assert religion.description is None
        assert religion.is_active is None

    def test_religion_update_partial(self) -> None:
        """Test ReligionUpdate with partial fields."""
        religion = ReligionUpdate(name="New Name", is_active=False)
        assert religion.name == "New Name"
        assert religion.is_active is False
        assert religion.code is None

    def test_religion_update_code_max_length(self) -> None:
        """Test ReligionUpdate code max length."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionUpdate(code="TOOLONGCODE")
        assert "code" in str(exc_info.value)


@pytest.mark.unit
class TestReligionPublic:
    """Tests for ReligionPublic schema."""

    def test_valid_religion_public(self) -> None:
        """Test ReligionPublic with valid data."""
        religion = ReligionPublic(
            religionId=uuid.uuid4(),
            religionName="Christianity",
        )
        assert religion.religionName == "Christianity"

    def test_religion_public_requires_id(self) -> None:
        """Test ReligionPublic requires religionId."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionPublic(religionName="Christianity")
        assert "religionId" in str(exc_info.value)

    def test_religion_public_requires_name(self) -> None:
        """Test ReligionPublic requires religionName."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionPublic(religionId=uuid.uuid4())
        assert "religionName" in str(exc_info.value)


@pytest.mark.unit
class TestReligionDetailPublic:
    """Tests for ReligionDetailPublic schema."""

    def test_valid_religion_detail_public(self) -> None:
        """Test ReligionDetailPublic with valid data."""
        religion = ReligionDetailPublic(
            id=uuid.uuid4(),
            name="Christianity",
            code="CHRISTIAN",
            is_active=True,
        )
        assert religion.name == "Christianity"
        assert religion.code == "CHRISTIAN"

    def test_religion_detail_public_requires_id(self) -> None:
        """Test ReligionDetailPublic requires id."""
        with pytest.raises(ValidationError) as exc_info:
            ReligionDetailPublic(name="Christianity", code="CHRISTIAN")
        assert "id" in str(exc_info.value)
