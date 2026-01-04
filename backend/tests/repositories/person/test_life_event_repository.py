"""Unit tests for LifeEventRepository."""

import uuid
from datetime import datetime

import pytest
from sqlmodel import Session, select

from app.db_models.person.person import Person
from app.db_models.person.person_life_event import PersonLifeEvent
from app.db_models.person.gender import Gender
from app.db_models.user import User
from app.repositories.person.life_event_repository import LifeEventRepository
from app.schemas.person.life_event import LifeEventType
from app.core.security import get_password_hash


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    user = User(
        id=uuid.uuid4(),
        email=f"test_{uuid.uuid4()}@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_person(db: Session, test_user: User) -> Person:
    """Create a test person."""
    # Get male gender
    gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()

    person = Person(
        id=uuid.uuid4(),
        user_id=test_user.id,
        first_name="Test",
        last_name="Person",
        gender_id=gender.id,
        date_of_birth="1990-01-01",
        created_by_user_id=test_user.id,
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


@pytest.fixture
def life_event_repository(db: Session) -> LifeEventRepository:
    """Create a LifeEventRepository instance."""
    return LifeEventRepository(db)


class TestLifeEventRepositoryQueries:
    """Test query methods of LifeEventRepository."""

    def test_get_by_person_returns_list(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test get_by_person returns list of events."""
        # Arrange - Create multiple life events
        event1 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.BIRTH,
            title="Birth",
            event_year=1990,
            event_month=5,
            event_date=15,
        )
        event2 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.MARRIAGE,
            title="Wedding",
            event_year=2015,
            event_month=6,
            event_date=20,
        )
        db.add(event1)
        db.add(event2)
        db.commit()

        # Act
        events = life_event_repository.get_by_person(test_person.id)

        # Assert
        assert len(events) == 2
        assert events[0].title in ["Birth", "Wedding"]

    def test_get_by_person_returns_empty_list_for_no_events(
        self,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test get_by_person returns empty list when no events exist."""
        # Act
        events = life_event_repository.get_by_person(test_person.id)

        # Assert
        assert len(events) == 0

    def test_get_by_person_sorts_by_date_descending(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test get_by_person sorts events by date descending."""
        # Arrange - Create events in non-chronological order
        event1 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.BIRTH,
            title="Birth",
            event_year=1990,
        )
        event2 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Graduation",
            event_year=2012,
        )
        event3 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.MARRIAGE,
            title="Wedding",
            event_year=2015,
        )
        db.add_all([event1, event2, event3])
        db.commit()

        # Act
        events = life_event_repository.get_by_person(test_person.id)

        # Assert
        assert len(events) == 3
        assert events[0].event_year == 2015  # Most recent first
        assert events[1].event_year == 2012
        assert events[2].event_year == 1990

    def test_get_by_person_sorts_by_month_when_same_year(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test get_by_person sorts by month DESC when same year."""
        # Arrange
        event1 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Event March",
            event_year=2020,
            event_month=3,
        )
        event2 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Event December",
            event_year=2020,
            event_month=12,
        )
        event3 = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Event June",
            event_year=2020,
            event_month=6,
        )
        db.add_all([event1, event2, event3])
        db.commit()

        # Act
        events = life_event_repository.get_by_person(test_person.id)

        # Assert
        assert len(events) == 3
        assert events[0].event_month == 12  # December first
        assert events[1].event_month == 6  # June second
        assert events[2].event_month == 3  # March last

    def test_get_by_person_handles_null_months(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test get_by_person handles NULL months correctly (NULLS LAST)."""
        # Arrange
        event_with_month = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Event with month",
            event_year=2020,
            event_month=6,
        )
        event_without_month = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Event without month",
            event_year=2020,
            event_month=None,
        )
        db.add_all([event_with_month, event_without_month])
        db.commit()

        # Act
        events = life_event_repository.get_by_person(test_person.id)

        # Assert
        assert len(events) == 2
        assert events[0].event_month == 6  # With month comes first
        assert events[1].event_month is None  # NULL month comes last

    def test_get_by_person_with_pagination(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test get_by_person respects skip and limit parameters."""
        # Arrange - Create 5 events
        for i in range(5):
            event = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=test_person.id,
                event_type=LifeEventType.ACHIEVEMENT,
                title=f"Event {i}",
                event_year=2020 + i,
            )
            db.add(event)
        db.commit()

        # Act
        events = life_event_repository.get_by_person(test_person.id, skip=2, limit=2)

        # Assert
        assert len(events) == 2

    def test_count_by_person_returns_correct_count(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test count_by_person returns correct count."""
        # Arrange - Create 3 events
        for i in range(3):
            event = PersonLifeEvent(
                id=uuid.uuid4(),
                person_id=test_person.id,
                event_type=LifeEventType.ACHIEVEMENT,
                title=f"Event {i}",
                event_year=2020 + i,
            )
            db.add(event)
        db.commit()

        # Act
        count = life_event_repository.count_by_person(test_person.id)

        # Assert
        assert count == 3

    def test_count_by_person_returns_zero_for_no_events(
        self,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test count_by_person returns 0 when no events exist."""
        # Act
        count = life_event_repository.count_by_person(test_person.id)

        # Assert
        assert count == 0


class TestLifeEventRepositoryCRUD:
    """Test CRUD operations of LifeEventRepository."""

    def test_create_life_event(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test creating a life event."""
        # Arrange
        event = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.MARRIAGE,
            title="Wedding Day",
            description="Got married",
            event_year=2020,
            event_month=6,
            event_date=15,
        )

        # Act
        created_event = life_event_repository.create(event)

        # Assert
        assert created_event.id is not None
        assert created_event.title == "Wedding Day"
        assert created_event.event_type == LifeEventType.MARRIAGE

        # Verify in database
        db_event = db.get(PersonLifeEvent, created_event.id)
        assert db_event is not None
        assert db_event.title == "Wedding Day"

    def test_get_life_event_by_id(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test getting a life event by ID."""
        # Arrange
        event = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.BIRTH,
            title="Birth",
            event_year=1990,
        )
        db.add(event)
        db.commit()

        # Act
        retrieved_event = life_event_repository.get_by_id(event.id)

        # Assert
        assert retrieved_event is not None
        assert retrieved_event.id == event.id
        assert retrieved_event.title == "Birth"

    def test_get_life_event_returns_none_for_nonexistent(
        self,
        life_event_repository: LifeEventRepository,
    ):
        """Test get_by_id returns None for non-existent event."""
        # Act
        event = life_event_repository.get_by_id(uuid.uuid4())

        # Assert
        assert event is None

    def test_update_life_event(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test updating a life event."""
        # Arrange
        event = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Original Title",
            event_year=2020,
        )
        db.add(event)
        db.commit()

        # Act
        event.title = "Updated Title"
        event.description = "New description"
        updated_event = life_event_repository.update(event)

        # Assert
        assert updated_event.title == "Updated Title"
        assert updated_event.description == "New description"

        # Verify in database
        db_event = db.get(PersonLifeEvent, event.id)
        assert db_event.title == "Updated Title"

    def test_delete_life_event(
        self,
        db: Session,
        life_event_repository: LifeEventRepository,
        test_person: Person,
    ):
        """Test deleting a life event."""
        # Arrange
        event = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=test_person.id,
            event_type=LifeEventType.TRAVEL,
            title="Trip to Paris",
            event_year=2019,
        )
        db.add(event)
        db.commit()
        event_id = event.id

        # Act
        life_event_repository.delete(event)

        # Assert
        db_event = db.get(PersonLifeEvent, event_id)
        assert db_event is None
