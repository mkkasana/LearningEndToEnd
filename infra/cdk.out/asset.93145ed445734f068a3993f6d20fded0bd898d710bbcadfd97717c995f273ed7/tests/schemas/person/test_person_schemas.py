"""Unit tests for Person schemas."""

import uuid
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.schemas.person.person import PersonBase, PersonCreate, PersonUpdate, PersonPublic


@pytest.mark.unit
class TestPersonBase:
    """Tests for PersonBase schema."""

    def test_valid_person_base(self) -> None:
        """Test PersonBase with valid data."""
        person = PersonBase(
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
        )
        assert person.first_name == "John"
        assert person.last_name == "Doe"
        assert person.middle_name is None
        assert person.date_of_death is None

    def test_person_base_with_all_fields(self) -> None:
        """Test PersonBase with all optional fields."""
        person = PersonBase(
            first_name="John",
            middle_name="Michael",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
            date_of_death=date(2020, 5, 20),
        )
        assert person.middle_name == "Michael"
        assert person.date_of_death == date(2020, 5, 20)

    def test_person_base_first_name_required(self) -> None:
        """Test PersonBase requires first_name."""
        with pytest.raises(ValidationError) as exc_info:
            PersonBase(
                last_name="Doe",
                gender_id=uuid.uuid4(),
                date_of_birth=date(1990, 1, 15),
            )
        assert "first_name" in str(exc_info.value)

    def test_person_base_last_name_required(self) -> None:
        """Test PersonBase requires last_name."""
        with pytest.raises(ValidationError) as exc_info:
            PersonBase(
                first_name="John",
                gender_id=uuid.uuid4(),
                date_of_birth=date(1990, 1, 15),
            )
        assert "last_name" in str(exc_info.value)

    def test_person_base_gender_id_required(self) -> None:
        """Test PersonBase requires gender_id."""
        with pytest.raises(ValidationError) as exc_info:
            PersonBase(
                first_name="John",
                last_name="Doe",
                date_of_birth=date(1990, 1, 15),
            )
        assert "gender_id" in str(exc_info.value)

    def test_person_base_date_of_birth_required(self) -> None:
        """Test PersonBase requires date_of_birth."""
        with pytest.raises(ValidationError) as exc_info:
            PersonBase(
                first_name="John",
                last_name="Doe",
                gender_id=uuid.uuid4(),
            )
        assert "date_of_birth" in str(exc_info.value)

    def test_person_base_first_name_max_length(self) -> None:
        """Test PersonBase first_name max length validation."""
        with pytest.raises(ValidationError) as exc_info:
            PersonBase(
                first_name="A" * 101,  # Exceeds max_length=100
                last_name="Doe",
                gender_id=uuid.uuid4(),
                date_of_birth=date(1990, 1, 15),
            )
        assert "first_name" in str(exc_info.value)


@pytest.mark.unit
class TestPersonCreate:
    """Tests for PersonCreate schema."""

    def test_valid_person_create(self) -> None:
        """Test PersonCreate with valid data."""
        person = PersonCreate(
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
        )
        assert person.user_id is None
        assert person.is_primary is False

    def test_person_create_with_user_id(self) -> None:
        """Test PersonCreate with user_id."""
        user_id = uuid.uuid4()
        person = PersonCreate(
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
            user_id=user_id,
            is_primary=True,
        )
        assert person.user_id == user_id
        assert person.is_primary is True

    def test_person_create_defaults(self) -> None:
        """Test PersonCreate default values."""
        person = PersonCreate(
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
        )
        assert person.user_id is None
        assert person.is_primary is False
        assert person.middle_name is None
        assert person.date_of_death is None


@pytest.mark.unit
class TestPersonUpdate:
    """Tests for PersonUpdate schema."""

    def test_person_update_all_optional(self) -> None:
        """Test PersonUpdate with no fields (all optional)."""
        person = PersonUpdate()
        assert person.first_name is None
        assert person.last_name is None
        assert person.gender_id is None
        assert person.date_of_birth is None

    def test_person_update_partial(self) -> None:
        """Test PersonUpdate with partial fields."""
        person = PersonUpdate(first_name="Jane", last_name="Smith")
        assert person.first_name == "Jane"
        assert person.last_name == "Smith"
        assert person.gender_id is None

    def test_person_update_with_religion(self) -> None:
        """Test PersonUpdate with religion fields."""
        religion_id = uuid.uuid4()
        category_id = uuid.uuid4()
        person = PersonUpdate(
            religion_id=religion_id,
            religion_category_id=category_id,
        )
        assert person.religion_id == religion_id
        assert person.religion_category_id == category_id

    def test_person_update_first_name_max_length(self) -> None:
        """Test PersonUpdate first_name max length validation."""
        with pytest.raises(ValidationError) as exc_info:
            PersonUpdate(first_name="A" * 101)
        assert "first_name" in str(exc_info.value)


@pytest.mark.unit
class TestPersonPublic:
    """Tests for PersonPublic schema."""

    def test_valid_person_public(self) -> None:
        """Test PersonPublic with valid data."""
        now = datetime.now()
        person = PersonPublic(
            id=uuid.uuid4(),
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
            user_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            is_primary=True,
            created_at=now,
            updated_at=now,
        )
        assert person.first_name == "John"
        assert person.is_primary is True

    def test_person_public_requires_id(self) -> None:
        """Test PersonPublic requires id."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            PersonPublic(
                first_name="John",
                last_name="Doe",
                gender_id=uuid.uuid4(),
                date_of_birth=date(1990, 1, 15),
                created_by_user_id=uuid.uuid4(),
                is_primary=True,
                created_at=now,
                updated_at=now,
            )
        assert "id" in str(exc_info.value)

    def test_person_public_requires_created_by_user_id(self) -> None:
        """Test PersonPublic requires created_by_user_id."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            PersonPublic(
                id=uuid.uuid4(),
                first_name="John",
                last_name="Doe",
                gender_id=uuid.uuid4(),
                date_of_birth=date(1990, 1, 15),
                is_primary=True,
                created_at=now,
                updated_at=now,
            )
        assert "created_by_user_id" in str(exc_info.value)
