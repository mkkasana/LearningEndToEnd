"""Unit tests for LifeEventService."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.person.person_life_event import PersonLifeEvent
from app.schemas.person.life_event import (
    LifeEventCreate,
    LifeEventType,
    LifeEventUpdate,
)
from app.services.person.life_event_service import LifeEventService


@pytest.fixture
def mock_session():
    """Create a mock database session."""
    return MagicMock()


@pytest.fixture
def life_event_service(mock_session):
    """Create a LifeEventService instance with mocked session."""
    return LifeEventService(mock_session)


@pytest.fixture
def sample_person_id():
    """Sample person ID for testing."""
    return uuid.uuid4()


@pytest.fixture
def sample_life_event(sample_person_id):
    """Sample life event for testing."""
    return PersonLifeEvent(
        id=uuid.uuid4(),
        person_id=sample_person_id,
        event_type=LifeEventType.BIRTH,
        title="Birth Event",
        description="Test birth event",
        event_year=1990,
        event_month=5,
        event_date=15,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestLifeEventServiceQueries:
    """Test query methods of LifeEventService."""

    def test_get_life_events_returns_list(
        self, life_event_service, sample_person_id, sample_life_event
    ):
        """Test get_life_events returns list of events."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_person.return_value = [sample_life_event]
        mock_repo.count_by_person.return_value = 1

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            events, count = life_event_service.get_life_events(sample_person_id)

            # Assert
            assert len(events) == 1
            assert count == 1
            assert events[0].title == "Birth Event"
            mock_repo.get_by_person.assert_called_once_with(
                sample_person_id, skip=0, limit=100
            )

    def test_get_life_events_with_pagination(
        self, life_event_service, sample_person_id
    ):
        """Test get_life_events respects pagination parameters."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_person.return_value = []
        mock_repo.count_by_person.return_value = 0

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            life_event_service.get_life_events(sample_person_id, skip=10, limit=20)

            # Assert
            mock_repo.get_by_person.assert_called_once_with(
                sample_person_id, skip=10, limit=20
            )

    def test_get_life_event_by_id_returns_event(
        self, life_event_service, sample_life_event
    ):
        """Test get_life_event_by_id returns event when found."""
        # Arrange
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = sample_life_event

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            result = life_event_service.get_life_event_by_id(sample_life_event.id)

            # Assert
            assert result.id == sample_life_event.id
            assert result.title == sample_life_event.title
            mock_repo.get_by_id.assert_called_once_with(sample_life_event.id)

    def test_get_life_event_by_id_returns_none_for_nonexistent(
        self, life_event_service
    ):
        """Test get_life_event_by_id returns None when event not found."""
        # Arrange
        event_id = uuid.uuid4()
        mock_repo = MagicMock()
        mock_repo.get_by_id.return_value = None

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            result = life_event_service.get_life_event_by_id(event_id)

            # Assert
            assert result is None


class TestLifeEventServiceCreate:
    """Test create methods of LifeEventService."""

    def test_create_life_event_with_valid_data(
        self, life_event_service, sample_person_id
    ):
        """Test create_life_event with valid data."""
        # Arrange
        life_event_in = LifeEventCreate(
            event_type=LifeEventType.MARRIAGE,
            title="Wedding Day",
            description="Got married",
            event_year=2020,
            event_month=6,
            event_date=15,
        )

        mock_repo = MagicMock()
        created_event = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=sample_person_id,
            event_type=LifeEventType.MARRIAGE,
            title="Wedding Day",
            description="Got married",
            event_year=2020,
            event_month=6,
            event_date=15,
        )
        mock_repo.create.return_value = created_event

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            result = life_event_service.create_life_event(
                sample_person_id, life_event_in
            )

            # Assert
            assert result.title == "Wedding Day"
            assert result.event_type == LifeEventType.MARRIAGE
            mock_repo.create.assert_called_once()

    def test_create_life_event_with_only_year(
        self, life_event_service, sample_person_id
    ):
        """Test create_life_event with only year (no month/date)."""
        # Arrange
        life_event_in = LifeEventCreate(
            event_type=LifeEventType.ACHIEVEMENT,
            title="Graduation",
            event_year=2015,
        )

        mock_repo = MagicMock()
        created_event = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=sample_person_id,
            event_type=LifeEventType.ACHIEVEMENT,
            title="Graduation",
            event_year=2015,
            event_month=None,
            event_date=None,
        )
        mock_repo.create.return_value = created_event

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            result = life_event_service.create_life_event(
                sample_person_id, life_event_in
            )

            # Assert
            assert result.event_year == 2015
            assert result.event_month is None
            assert result.event_date is None

    def test_create_life_event_with_invalid_date_raises_error(
        self, life_event_service, sample_person_id
    ):
        """Test create_life_event with invalid date raises ValueError."""
        # Arrange
        life_event_in = LifeEventCreate(
            event_type=LifeEventType.BIRTH,
            title="Birth",
            event_year=2020,
            event_month=2,
            event_date=30,  # February 30 doesn't exist
        )

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid date"):
            life_event_service.create_life_event(sample_person_id, life_event_in)

    def test_create_life_event_with_address(
        self, life_event_service, sample_person_id
    ):
        """Test create_life_event with address information."""
        # Arrange
        country_id = uuid.uuid4()
        state_id = uuid.uuid4()

        life_event_in = LifeEventCreate(
            event_type=LifeEventType.PURCHASE,
            title="Bought House",
            event_year=2022,
            country_id=country_id,
            state_id=state_id,
            address_details="123 Main St",
        )

        mock_repo = MagicMock()
        created_event = PersonLifeEvent(
            id=uuid.uuid4(),
            person_id=sample_person_id,
            event_type=LifeEventType.PURCHASE,
            title="Bought House",
            event_year=2022,
            country_id=country_id,
            state_id=state_id,
            address_details="123 Main St",
        )
        mock_repo.create.return_value = created_event

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            result = life_event_service.create_life_event(
                sample_person_id, life_event_in
            )

            # Assert
            assert result.country_id == country_id
            assert result.address_details == "123 Main St"


class TestLifeEventServiceUpdate:
    """Test update methods of LifeEventService."""

    def test_update_life_event_title(self, life_event_service, sample_life_event):
        """Test updating life event title."""
        # Arrange
        life_event_in = LifeEventUpdate(title="Updated Title")

        mock_repo = MagicMock()
        sample_life_event.title = "Updated Title"
        mock_repo.update.return_value = sample_life_event

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            result = life_event_service.update_life_event(
                sample_life_event, life_event_in
            )

            # Assert
            assert result.title == "Updated Title"
            mock_repo.update.assert_called_once()

    def test_update_life_event_date(self, life_event_service, sample_life_event):
        """Test updating life event date."""
        # Arrange
        life_event_in = LifeEventUpdate(event_month=12, event_date=25)

        mock_repo = MagicMock()
        sample_life_event.event_month = 12
        sample_life_event.event_date = 25
        mock_repo.update.return_value = sample_life_event

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            result = life_event_service.update_life_event(
                sample_life_event, life_event_in
            )

            # Assert
            assert result.event_month == 12
            assert result.event_date == 25

    def test_update_life_event_with_invalid_date_raises_error(
        self, life_event_service, sample_life_event
    ):
        """Test updating with invalid date raises ValueError."""
        # Arrange
        life_event_in = LifeEventUpdate(event_month=4, event_date=31)  # April 31

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid date"):
            life_event_service.update_life_event(sample_life_event, life_event_in)

    def test_update_life_event_updates_timestamp(
        self, life_event_service, sample_life_event
    ):
        """Test that update sets updated_at timestamp."""
        # Arrange
        life_event_in = LifeEventUpdate(description="Updated description")
        original_updated_at = sample_life_event.updated_at

        mock_repo = MagicMock()
        mock_repo.update.return_value = sample_life_event

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            life_event_service.update_life_event(sample_life_event, life_event_in)

            # Assert
            assert sample_life_event.updated_at >= original_updated_at


class TestLifeEventServiceDelete:
    """Test delete methods of LifeEventService."""

    def test_delete_life_event_calls_repository(
        self, life_event_service, sample_life_event
    ):
        """Test delete_life_event calls repository delete."""
        # Arrange
        mock_repo = MagicMock()

        with patch.object(life_event_service, "life_event_repo", mock_repo):
            # Act
            life_event_service.delete_life_event(sample_life_event)

            # Assert
            mock_repo.delete.assert_called_once_with(sample_life_event)


class TestLifeEventServiceAuthorization:
    """Test authorization methods of LifeEventService."""

    def test_user_can_access_own_event(self, life_event_service, sample_life_event):
        """Test user can access their own life event."""
        # Arrange
        user = MagicMock()
        user.is_superuser = False
        user_person_id = sample_life_event.person_id

        # Act
        result = life_event_service.user_can_access_event(
            user, sample_life_event, user_person_id
        )

        # Assert
        assert result is True

    def test_user_cannot_access_other_event(
        self, life_event_service, sample_life_event
    ):
        """Test user cannot access another user's life event."""
        # Arrange
        user = MagicMock()
        user.is_superuser = False
        user.is_admin = False
        other_person_id = uuid.uuid4()

        # Act
        result = life_event_service.user_can_access_event(
            user, sample_life_event, other_person_id
        )

        # Assert
        assert result is False

    def test_superuser_can_access_any_event(
        self, life_event_service, sample_life_event
    ):
        """Test superuser can access any life event."""
        # Arrange
        user = MagicMock()
        user.is_superuser = True
        other_person_id = uuid.uuid4()

        # Act
        result = life_event_service.user_can_access_event(
            user, sample_life_event, other_person_id
        )

        # Assert
        assert result is True

    def test_user_without_person_record_cannot_access(
        self, life_event_service, sample_life_event
    ):
        """Test user without person record cannot access events."""
        # Arrange
        user = MagicMock()
        user.is_superuser = False
        user.is_admin = False
        user_person_id = None

        # Act
        result = life_event_service.user_can_access_event(
            user, sample_life_event, user_person_id
        )

        # Assert
        assert result is False


class TestLifeEventServiceDateValidation:
    """Test date validation methods of LifeEventService."""

    def test_validate_date_with_valid_date(self, life_event_service):
        """Test validate_date with valid date."""
        # Act & Assert - should not raise
        life_event_service.validate_date(2020, 2, 29)  # Leap year

    def test_validate_date_with_invalid_february_date(self, life_event_service):
        """Test validate_date with invalid February date."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid date"):
            life_event_service.validate_date(2021, 2, 29)  # Not a leap year

    def test_validate_date_with_invalid_april_date(self, life_event_service):
        """Test validate_date with invalid April date."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid date"):
            life_event_service.validate_date(2020, 4, 31)  # April has 30 days

    def test_validate_date_without_month_or_date(self, life_event_service):
        """Test validate_date with only year (no validation needed)."""
        # Act & Assert - should not raise
        life_event_service.validate_date(2020, None, None)
        life_event_service.validate_date(2020, 5, None)

    def test_validate_date_with_all_month_boundaries(self, life_event_service):
        """Test validate_date with boundary dates for all months."""
        # Act & Assert - should not raise for valid dates
        life_event_service.validate_date(2020, 1, 31)  # January
        life_event_service.validate_date(2020, 3, 31)  # March
        life_event_service.validate_date(2020, 4, 30)  # April
        life_event_service.validate_date(2020, 5, 31)  # May
        life_event_service.validate_date(2020, 6, 30)  # June
        life_event_service.validate_date(2020, 7, 31)  # July
        life_event_service.validate_date(2020, 8, 31)  # August
        life_event_service.validate_date(2020, 9, 30)  # September
        life_event_service.validate_date(2020, 10, 31)  # October
        life_event_service.validate_date(2020, 11, 30)  # November
        life_event_service.validate_date(2020, 12, 31)  # December
