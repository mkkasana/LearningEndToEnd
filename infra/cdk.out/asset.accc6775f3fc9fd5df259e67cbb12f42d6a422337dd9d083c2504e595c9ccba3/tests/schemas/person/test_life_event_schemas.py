"""Unit tests for Life Event schemas."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.schemas.person.life_event import (
    LifeEventBase,
    LifeEventCreate,
    LifeEventPublic,
    LifeEventType,
    LifeEventUpdate,
    LifeEventsPublic,
)


class TestLifeEventType:
    """Test LifeEventType enum."""

    def test_all_event_types_defined(self):
        """Test all expected event types are defined."""
        expected_types = {
            "birth",
            "marriage",
            "death",
            "purchase",
            "sale",
            "achievement",
            "education",
            "career",
            "health",
            "travel",
            "other",
        }
        actual_types = {e.value for e in LifeEventType}
        assert actual_types == expected_types

    def test_event_type_values(self):
        """Test event type enum values."""
        assert LifeEventType.BIRTH.value == "birth"
        assert LifeEventType.MARRIAGE.value == "marriage"
        assert LifeEventType.DEATH.value == "death"


class TestLifeEventBase:
    """Test LifeEventBase schema."""

    def test_valid_life_event_base(self):
        """Test creating valid LifeEventBase."""
        event = LifeEventBase(
            event_type=LifeEventType.MARRIAGE,
            title="Wedding Day",
            description="Got married",
            event_year=2020,
            event_month=6,
            event_date=15,
        )
        assert event.event_type == LifeEventType.MARRIAGE
        assert event.title == "Wedding Day"
        assert event.event_year == 2020

    def test_life_event_base_with_only_required_fields(self):
        """Test LifeEventBase with only required fields."""
        event = LifeEventBase(
            event_type=LifeEventType.BIRTH,
            title="Birth",
            event_year=1990,
        )
        assert event.event_type == LifeEventType.BIRTH
        assert event.title == "Birth"
        assert event.description is None
        assert event.event_month is None

    def test_life_event_base_title_required(self):
        """Test that title is required."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventBase(
                event_type=LifeEventType.BIRTH,
                event_year=1990,
            )
        assert "title" in str(exc_info.value)

    def test_life_event_base_event_type_required(self):
        """Test that event_type is required."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventBase(
                title="Some Event",
                event_year=2020,
            )
        assert "event_type" in str(exc_info.value)

    def test_life_event_base_event_year_required(self):
        """Test that event_year is required."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventBase(
                event_type=LifeEventType.ACHIEVEMENT,
                title="Graduation",
            )
        assert "event_year" in str(exc_info.value)

    def test_life_event_base_title_max_length(self):
        """Test title max length validation."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventBase(
                event_type=LifeEventType.OTHER,
                title="x" * 101,  # Max is 100
                event_year=2020,
            )
        assert "title" in str(exc_info.value)

    def test_life_event_base_description_max_length(self):
        """Test description max length validation."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventBase(
                event_type=LifeEventType.OTHER,
                title="Event",
                description="x" * 501,  # Max is 500
                event_year=2020,
            )
        assert "description" in str(exc_info.value)

    def test_life_event_base_address_details_max_length(self):
        """Test address_details max length validation."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventBase(
                event_type=LifeEventType.PURCHASE,
                title="Bought House",
                event_year=2020,
                address_details="x" * 31,  # Max is 30
            )
        assert "address_details" in str(exc_info.value)

    def test_life_event_base_with_address_fields(self):
        """Test LifeEventBase with address fields."""
        country_id = uuid.uuid4()
        state_id = uuid.uuid4()
        district_id = uuid.uuid4()

        event = LifeEventBase(
            event_type=LifeEventType.PURCHASE,
            title="Bought House",
            event_year=2022,
            country_id=country_id,
            state_id=state_id,
            district_id=district_id,
            address_details="123 Main St",
        )
        assert event.country_id == country_id
        assert event.state_id == state_id
        assert event.address_details == "123 Main St"


class TestLifeEventCreate:
    """Test LifeEventCreate schema."""

    def test_valid_life_event_create(self):
        """Test creating valid LifeEventCreate."""
        event = LifeEventCreate(
            event_type=LifeEventType.MARRIAGE,
            title="Wedding",
            event_year=2020,
        )
        assert event.event_type == LifeEventType.MARRIAGE
        assert event.title == "Wedding"

    def test_life_event_create_inherits_from_base(self):
        """Test LifeEventCreate inherits all base validations."""
        with pytest.raises(ValidationError):
            LifeEventCreate(
                event_type=LifeEventType.BIRTH,
                title="x" * 101,  # Exceeds max length
                event_year=1990,
            )


class TestLifeEventUpdate:
    """Test LifeEventUpdate schema."""

    def test_life_event_update_all_optional(self):
        """Test that all fields in LifeEventUpdate are optional."""
        event = LifeEventUpdate()
        assert event.event_type is None
        assert event.title is None
        assert event.event_year is None

    def test_life_event_update_partial(self):
        """Test updating only some fields."""
        event = LifeEventUpdate(
            title="Updated Title",
            description="Updated description",
        )
        assert event.title == "Updated Title"
        assert event.description == "Updated description"
        assert event.event_year is None

    def test_life_event_update_respects_max_lengths(self):
        """Test LifeEventUpdate respects max length constraints."""
        with pytest.raises(ValidationError):
            LifeEventUpdate(title="x" * 101)

    def test_life_event_update_can_update_date_fields(self):
        """Test updating date fields."""
        event = LifeEventUpdate(
            event_year=2021,
            event_month=12,
            event_date=25,
        )
        assert event.event_year == 2021
        assert event.event_month == 12
        assert event.event_date == 25


class TestLifeEventPublic:
    """Test LifeEventPublic schema."""

    def test_valid_life_event_public(self):
        """Test creating valid LifeEventPublic."""
        event_id = uuid.uuid4()
        person_id = uuid.uuid4()
        now = datetime.utcnow()

        event = LifeEventPublic(
            id=event_id,
            person_id=person_id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Graduation",
            event_year=2015,
            created_at=now,
            updated_at=now,
        )
        assert event.id == event_id
        assert event.person_id == person_id
        assert event.title == "Graduation"

    def test_life_event_public_requires_id(self):
        """Test that id is required in LifeEventPublic."""
        person_id = uuid.uuid4()
        now = datetime.utcnow()

        with pytest.raises(ValidationError) as exc_info:
            LifeEventPublic(
                person_id=person_id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                event_year=1990,
                created_at=now,
                updated_at=now,
            )
        assert "id" in str(exc_info.value)

    def test_life_event_public_requires_person_id(self):
        """Test that person_id is required in LifeEventPublic."""
        event_id = uuid.uuid4()
        now = datetime.utcnow()

        with pytest.raises(ValidationError) as exc_info:
            LifeEventPublic(
                id=event_id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                event_year=1990,
                created_at=now,
                updated_at=now,
            )
        assert "person_id" in str(exc_info.value)

    def test_life_event_public_requires_timestamps(self):
        """Test that timestamps are required in LifeEventPublic."""
        event_id = uuid.uuid4()
        person_id = uuid.uuid4()

        with pytest.raises(ValidationError) as exc_info:
            LifeEventPublic(
                id=event_id,
                person_id=person_id,
                event_type=LifeEventType.BIRTH,
                title="Birth",
                event_year=1990,
            )
        assert "created_at" in str(exc_info.value) or "updated_at" in str(exc_info.value)


class TestLifeEventsPublic:
    """Test LifeEventsPublic schema."""

    def test_valid_life_events_public(self):
        """Test creating valid LifeEventsPublic."""
        event_id = uuid.uuid4()
        person_id = uuid.uuid4()
        now = datetime.utcnow()

        event = LifeEventPublic(
            id=event_id,
            person_id=person_id,
            event_type=LifeEventType.MARRIAGE,
            title="Wedding",
            event_year=2020,
            created_at=now,
            updated_at=now,
        )

        events = LifeEventsPublic(data=[event], count=1)
        assert len(events.data) == 1
        assert events.count == 1
        assert events.data[0].title == "Wedding"

    def test_life_events_public_empty_list(self):
        """Test LifeEventsPublic with empty list."""
        events = LifeEventsPublic(data=[], count=0)
        assert len(events.data) == 0
        assert events.count == 0

    def test_life_events_public_requires_data(self):
        """Test that data is required in LifeEventsPublic."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventsPublic(count=0)
        assert "data" in str(exc_info.value)

    def test_life_events_public_requires_count(self):
        """Test that count is required in LifeEventsPublic."""
        with pytest.raises(ValidationError) as exc_info:
            LifeEventsPublic(data=[])
        assert "count" in str(exc_info.value)


class TestLifeEventSchemaEdgeCases:
    """Test edge cases for life event schemas."""

    def test_event_with_year_only(self):
        """Test event with only year (no month/date)."""
        event = LifeEventCreate(
            event_type=LifeEventType.ACHIEVEMENT,
            title="Graduation",
            event_year=2015,
        )
        assert event.event_year == 2015
        assert event.event_month is None
        assert event.event_date is None

    def test_event_with_year_and_month(self):
        """Test event with year and month (no date)."""
        event = LifeEventCreate(
            event_type=LifeEventType.CAREER,
            title="Started Job",
            event_year=2020,
            event_month=3,
        )
        assert event.event_year == 2020
        assert event.event_month == 3
        assert event.event_date is None

    def test_event_with_full_date(self):
        """Test event with complete date."""
        event = LifeEventCreate(
            event_type=LifeEventType.MARRIAGE,
            title="Wedding",
            event_year=2020,
            event_month=6,
            event_date=15,
        )
        assert event.event_year == 2020
        assert event.event_month == 6
        assert event.event_date == 15

    def test_event_with_all_address_levels(self):
        """Test event with all address hierarchy levels."""
        event = LifeEventCreate(
            event_type=LifeEventType.PURCHASE,
            title="Bought House",
            event_year=2022,
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            sub_district_id=uuid.uuid4(),
            locality_id=uuid.uuid4(),
            address_details="123 Main St",
        )
        assert event.country_id is not None
        assert event.state_id is not None
        assert event.district_id is not None
        assert event.sub_district_id is not None
        assert event.locality_id is not None
        assert event.address_details == "123 Main St"
