"""Unit tests for PersonRelationship schemas."""

import uuid
from datetime import date, datetime

import pytest
from pydantic import ValidationError

from app.enums import RelationshipType
from app.schemas.person.person_relationship import (
    PersonRelationshipBase,
    PersonRelationshipCreate,
    PersonRelationshipUpdate,
    PersonRelationshipPublic,
    PersonDetails,
)


@pytest.mark.unit
class TestPersonRelationshipBase:
    """Tests for PersonRelationshipBase schema."""

    def test_valid_relationship_base(self) -> None:
        """Test PersonRelationshipBase with valid data."""
        rel = PersonRelationshipBase(
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.FATHER,
        )
        assert rel.relationship_type == RelationshipType.FATHER
        assert rel.is_active is True
        assert rel.start_date is None
        assert rel.end_date is None

    def test_relationship_base_with_all_fields(self) -> None:
        """Test PersonRelationshipBase with all fields."""
        rel = PersonRelationshipBase(
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.MOTHER,
            start_date=date(1990, 1, 1),
            end_date=date(2020, 12, 31),
            is_active=False,
        )
        assert rel.start_date == date(1990, 1, 1)
        assert rel.end_date == date(2020, 12, 31)
        assert rel.is_active is False

    def test_relationship_base_related_person_id_required(self) -> None:
        """Test PersonRelationshipBase requires related_person_id."""
        with pytest.raises(ValidationError) as exc_info:
            PersonRelationshipBase(relationship_type=RelationshipType.FATHER)
        assert "related_person_id" in str(exc_info.value)

    def test_relationship_base_relationship_type_required(self) -> None:
        """Test PersonRelationshipBase requires relationship_type."""
        with pytest.raises(ValidationError) as exc_info:
            PersonRelationshipBase(related_person_id=uuid.uuid4())
        assert "relationship_type" in str(exc_info.value)

    def test_relationship_base_invalid_relationship_type(self) -> None:
        """Test PersonRelationshipBase with invalid relationship type."""
        with pytest.raises(ValidationError) as exc_info:
            PersonRelationshipBase(
                related_person_id=uuid.uuid4(),
                relationship_type="INVALID_TYPE",
            )
        assert "relationship_type" in str(exc_info.value)


@pytest.mark.unit
class TestPersonRelationshipCreate:
    """Tests for PersonRelationshipCreate schema."""

    def test_valid_relationship_create(self) -> None:
        """Test PersonRelationshipCreate with valid data."""
        rel = PersonRelationshipCreate(
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.SON,
        )
        assert rel.relationship_type == RelationshipType.SON

    def test_relationship_create_all_types(self) -> None:
        """Test PersonRelationshipCreate with all relationship types."""
        for rel_type in RelationshipType:
            rel = PersonRelationshipCreate(
                related_person_id=uuid.uuid4(),
                relationship_type=rel_type,
            )
            assert rel.relationship_type == rel_type


@pytest.mark.unit
class TestPersonRelationshipUpdate:
    """Tests for PersonRelationshipUpdate schema."""

    def test_relationship_update_all_optional(self) -> None:
        """Test PersonRelationshipUpdate with no fields."""
        rel = PersonRelationshipUpdate()
        assert rel.related_person_id is None
        assert rel.relationship_type is None
        assert rel.start_date is None
        assert rel.end_date is None
        assert rel.is_active is None

    def test_relationship_update_partial(self) -> None:
        """Test PersonRelationshipUpdate with partial fields."""
        rel = PersonRelationshipUpdate(
            relationship_type=RelationshipType.DAUGHTER,
            is_active=False,
        )
        assert rel.relationship_type == RelationshipType.DAUGHTER
        assert rel.is_active is False
        assert rel.related_person_id is None

    def test_relationship_update_dates(self) -> None:
        """Test PersonRelationshipUpdate with date fields."""
        rel = PersonRelationshipUpdate(
            start_date=date(2000, 1, 1),
            end_date=date(2020, 12, 31),
        )
        assert rel.start_date == date(2000, 1, 1)
        assert rel.end_date == date(2020, 12, 31)


@pytest.mark.unit
class TestPersonRelationshipPublic:
    """Tests for PersonRelationshipPublic schema."""

    def test_valid_relationship_public(self) -> None:
        """Test PersonRelationshipPublic with valid data."""
        now = datetime.now()
        rel = PersonRelationshipPublic(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            related_person_id=uuid.uuid4(),
            relationship_type=RelationshipType.FATHER,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        assert rel.relationship_type == RelationshipType.FATHER
        assert rel.relationship_type_label == "Father"

    def test_relationship_public_requires_id(self) -> None:
        """Test PersonRelationshipPublic requires id."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            PersonRelationshipPublic(
                person_id=uuid.uuid4(),
                related_person_id=uuid.uuid4(),
                relationship_type=RelationshipType.FATHER,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        assert "id" in str(exc_info.value)

    def test_relationship_public_requires_person_id(self) -> None:
        """Test PersonRelationshipPublic requires person_id."""
        now = datetime.now()
        with pytest.raises(ValidationError) as exc_info:
            PersonRelationshipPublic(
                id=uuid.uuid4(),
                related_person_id=uuid.uuid4(),
                relationship_type=RelationshipType.FATHER,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        assert "person_id" in str(exc_info.value)

    def test_relationship_public_label_property(self) -> None:
        """Test PersonRelationshipPublic relationship_type_label property."""
        now = datetime.now()
        test_cases = [
            (RelationshipType.FATHER, "Father"),
            (RelationshipType.MOTHER, "Mother"),
            (RelationshipType.SON, "Son"),
            (RelationshipType.DAUGHTER, "Daughter"),
            (RelationshipType.WIFE, "Wife"),
            (RelationshipType.HUSBAND, "Husband"),
            (RelationshipType.SPOUSE, "Spouse"),
        ]
        for rel_type, expected_label in test_cases:
            rel = PersonRelationshipPublic(
                id=uuid.uuid4(),
                person_id=uuid.uuid4(),
                related_person_id=uuid.uuid4(),
                relationship_type=rel_type,
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            assert rel.relationship_type_label == expected_label


@pytest.mark.unit
class TestPersonDetails:
    """Tests for PersonDetails schema."""

    def test_valid_person_details(self) -> None:
        """Test PersonDetails with valid data."""
        now = datetime.now()
        person = PersonDetails(
            id=uuid.uuid4(),
            first_name="John",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
            created_by_user_id=uuid.uuid4(),
            is_primary=True,
            created_at=now,
            updated_at=now,
        )
        assert person.first_name == "John"
        assert person.middle_name is None
        assert person.user_id is None

    def test_person_details_with_all_fields(self) -> None:
        """Test PersonDetails with all optional fields."""
        now = datetime.now()
        person = PersonDetails(
            id=uuid.uuid4(),
            first_name="John",
            middle_name="Michael",
            last_name="Doe",
            gender_id=uuid.uuid4(),
            date_of_birth=date(1990, 1, 15),
            date_of_death=date(2020, 5, 20),
            user_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            is_primary=True,
            created_at=now,
            updated_at=now,
        )
        assert person.middle_name == "Michael"
        assert person.date_of_death == date(2020, 5, 20)
        assert person.user_id is not None
