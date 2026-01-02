"""Unit tests for PersonService.

Tests cover:
- Person creation with valid data
- Person updates
- get_my_contributions method
- Person queries

Requirements: 2.3, 2.18, 2.19
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.enums import GENDER_DATA, GenderEnum
from app.schemas.person import PersonCreate, PersonUpdate
from app.services.person.person_service import PersonService


@pytest.mark.unit
class TestPersonServiceQueries:
    """Tests for person query operations."""

    def test_get_person_by_user_id_returns_person(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting person by user ID returns the person."""
        # Arrange
        user_id = uuid.uuid4()
        mock_person = Person(
            id=uuid.uuid4(),
            user_id=user_id,
            created_by_user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.MALE].id,
            date_of_birth=date(1990, 1, 1),
        )

        service = PersonService(mock_session)
        with patch.object(service.person_repo, "get_by_user_id", return_value=mock_person):
            # Act
            result = service.get_person_by_user_id(user_id)

            # Assert
            assert result is not None
            assert result.user_id == user_id
            assert result.first_name == "John"

    def test_get_person_by_user_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent person by user ID returns None."""
        # Arrange
        service = PersonService(mock_session)
        with patch.object(service.person_repo, "get_by_user_id", return_value=None):
            # Act
            result = service.get_person_by_user_id(uuid.uuid4())

            # Assert
            assert result is None

    def test_user_has_person_returns_true_when_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test user_has_person returns True when person exists."""
        # Arrange
        user_id = uuid.uuid4()
        service = PersonService(mock_session)
        with patch.object(service.person_repo, "user_has_person", return_value=True):
            # Act
            result = service.user_has_person(user_id)

            # Assert
            assert result is True

    def test_user_has_person_returns_false_when_not_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test user_has_person returns False when person doesn't exist."""
        # Arrange
        service = PersonService(mock_session)
        with patch.object(service.person_repo, "user_has_person", return_value=False):
            # Act
            result = service.user_has_person(uuid.uuid4())

            # Assert
            assert result is False


@pytest.mark.unit
class TestPersonServiceCreate:
    """Tests for person creation."""

    def test_create_person_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating person with valid data."""
        # Arrange
        user_id = uuid.uuid4()
        person_create = PersonCreate(
            user_id=user_id,
            first_name="John",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.MALE].id,
            date_of_birth=date(1990, 1, 1),
            is_primary=True,
        )

        service = PersonService(mock_session)
        
        def return_person(person: Person) -> Person:
            return person

        with patch.object(service.person_repo, "create", side_effect=return_person):
            # Act
            result = service.create_person(person_create)

            # Assert
            assert result.first_name == "John"
            assert result.last_name == "Doe"
            assert result.user_id == user_id
            assert result.is_primary is True

    def test_create_person_with_middle_name(self, mock_session: MagicMock) -> None:
        """Test creating person with middle name."""
        # Arrange
        user_id = uuid.uuid4()
        person_create = PersonCreate(
            user_id=user_id,
            first_name="John",
            middle_name="Michael",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.MALE].id,
            date_of_birth=date(1990, 1, 1),
        )

        service = PersonService(mock_session)
        
        def return_person(person: Person) -> Person:
            return person

        with patch.object(service.person_repo, "create", side_effect=return_person):
            # Act
            result = service.create_person(person_create)

            # Assert
            assert result.middle_name == "Michael"

    def test_create_person_without_user_id(self, mock_session: MagicMock) -> None:
        """Test creating person without linked user (family member)."""
        # Arrange
        person_create = PersonCreate(
            user_id=None,
            first_name="Jane",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.FEMALE].id,
            date_of_birth=date(1995, 5, 15),
            is_primary=False,
        )

        service = PersonService(mock_session)
        
        def return_person(person: Person) -> Person:
            return person

        with patch.object(service.person_repo, "create", side_effect=return_person):
            # Act
            result = service.create_person(person_create)

            # Assert
            assert result.user_id is None
            assert result.is_primary is False
            assert result.first_name == "Jane"


@pytest.mark.unit
class TestPersonServiceUpdate:
    """Tests for person update operations."""

    def test_update_person_first_name(self, mock_session: MagicMock) -> None:
        """Test updating person first name."""
        # Arrange
        mock_person = Person(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            first_name="John",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.MALE].id,
            date_of_birth=date(1990, 1, 1),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        person_update = PersonUpdate(first_name="Jonathan")

        service = PersonService(mock_session)
        
        def return_person(person: Person) -> Person:
            return person

        with patch.object(service.person_repo, "update", side_effect=return_person):
            # Act
            result = service.update_person(mock_person, person_update)

            # Assert
            assert result.first_name == "Jonathan"

    def test_update_person_multiple_fields(self, mock_session: MagicMock) -> None:
        """Test updating multiple person fields."""
        # Arrange
        mock_person = Person(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            first_name="John",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.MALE].id,
            date_of_birth=date(1990, 1, 1),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        person_update = PersonUpdate(
            first_name="Jonathan",
            middle_name="Michael",
            last_name="Smith",
        )

        service = PersonService(mock_session)
        
        def return_person(person: Person) -> Person:
            return person

        with patch.object(service.person_repo, "update", side_effect=return_person):
            # Act
            result = service.update_person(mock_person, person_update)

            # Assert
            assert result.first_name == "Jonathan"
            assert result.middle_name == "Michael"
            assert result.last_name == "Smith"

    def test_update_person_updates_timestamp(self, mock_session: MagicMock) -> None:
        """Test that updating person updates the updated_at timestamp."""
        # Arrange
        old_timestamp = datetime(2020, 1, 1, 0, 0, 0)
        mock_person = Person(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            first_name="John",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.MALE].id,
            date_of_birth=date(1990, 1, 1),
            created_at=old_timestamp,
            updated_at=old_timestamp,
        )
        person_update = PersonUpdate(first_name="Jonathan")

        service = PersonService(mock_session)
        
        def return_person(person: Person) -> Person:
            return person

        with patch.object(service.person_repo, "update", side_effect=return_person):
            # Act
            result = service.update_person(mock_person, person_update)

            # Assert
            assert result.updated_at > old_timestamp


@pytest.mark.unit
class TestPersonServiceDelete:
    """Tests for person deletion."""

    def test_delete_person_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete_person calls the repository delete method."""
        # Arrange
        mock_person = Person(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            created_by_user_id=uuid.uuid4(),
            first_name="John",
            last_name="Doe",
            gender_id=GENDER_DATA[GenderEnum.MALE].id,
            date_of_birth=date(1990, 1, 1),
        )

        service = PersonService(mock_session)
        mock_delete = MagicMock()
        
        with patch.object(service.person_repo, "delete", mock_delete):
            # Act
            service.delete_person(mock_person)

            # Assert
            mock_delete.assert_called_once_with(mock_person)


@pytest.mark.unit
class TestGetMyContributions:
    """Tests for get_my_contributions method."""

    def test_get_my_contributions_with_no_contributions(self, db: Session) -> None:
        """Test get_my_contributions with user who has no contributions.

        Requirements: 1.7
        """
        service = PersonService(db)
        user_id = uuid.uuid4()

        # Mock repository to return empty list
        with patch.object(service.person_repo, "get_by_creator", return_value=[]):
            result = service.get_my_contributions(user_id)

            # Verify empty list returned
            assert result == []

    def test_get_my_contributions_with_multiple_contributions(
        self, db: Session
    ) -> None:
        """Test get_my_contributions with user who has multiple contributions.

        Requirements: 1.7, 5.5, 5.6
        """
        service = PersonService(db)
        user_id = uuid.uuid4()

        # Create mock persons
        person1_id = uuid.uuid4()
        person2_id = uuid.uuid4()
        person3_id = uuid.uuid4()

        person1 = Person(
            id=person1_id,
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1980, 1, 1),
            date_of_death=None,
            gender_id=uuid.uuid4(),
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        person2 = Person(
            id=person2_id,
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(1990, 5, 15),
            date_of_death=date(2020, 10, 20),
            gender_id=uuid.uuid4(),
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        person3 = Person(
            id=person3_id,
            first_name="Bob",
            last_name="Johnson",
            date_of_birth=date(1975, 3, 10),
            date_of_death=None,
            gender_id=uuid.uuid4(),
            created_by_user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        persons = [person1, person2, person3]

        # Mock view counts (person2 has most views, person3 has none)
        view_counts = {
            person1_id: 5,
            person2_id: 10,
            person3_id: 0,
        }

        # Mock addresses
        address1 = PersonAddress(
            id=uuid.uuid4(),
            person_id=person1_id,
            country_id=uuid.uuid4(),
            address_line="123 Main St",
            start_date=date(2000, 1, 1),
        )

        address2 = PersonAddress(
            id=uuid.uuid4(),
            person_id=person2_id,
            country_id=uuid.uuid4(),
            address_line="456 Oak Ave",
            start_date=date(2010, 1, 1),
        )

        # person3 has no addresses

        # Mock repository and service methods
        with patch.object(
            service.person_repo, "get_by_creator", return_value=persons
        ), patch(
            "app.services.person.person_service.ProfileViewTrackingService"
        ) as mock_view_service_class, patch(
            "app.services.person.person_service.PersonAddressRepository"
        ) as mock_address_repo_class:
            # Setup mock view tracking service
            mock_view_service = MagicMock()
            mock_view_service.get_total_views_bulk.return_value = view_counts
            mock_view_service_class.return_value = mock_view_service

            # Setup mock address repository
            mock_address_repo = MagicMock()

            def get_addresses_side_effect(person_id):
                if person_id == person1_id:
                    return [address1]
                elif person_id == person2_id:
                    return [address2]
                else:
                    return []

            mock_address_repo.get_by_person_id.side_effect = get_addresses_side_effect
            mock_address_repo_class.return_value = mock_address_repo

            # Call the method
            result = service.get_my_contributions(user_id)

            # Verify results
            assert len(result) == 3

            # Verify sorting by view count (descending)
            assert result[0]["id"] == person2_id  # 10 views
            assert result[0]["total_views"] == 10
            assert result[1]["id"] == person1_id  # 5 views
            assert result[1]["total_views"] == 5
            assert result[2]["id"] == person3_id  # 0 views
            assert result[2]["total_views"] == 0

            # Verify person details
            assert result[0]["first_name"] == "Jane"
            assert result[0]["last_name"] == "Smith"
            assert result[0]["date_of_birth"] == date(1990, 5, 15)
            assert result[0]["date_of_death"] == date(2020, 10, 20)
            assert result[0]["address"] == "456 Oak Ave"

            assert result[1]["first_name"] == "John"
            assert result[1]["last_name"] == "Doe"
            assert result[1]["address"] == "123 Main St"

            assert result[2]["first_name"] == "Bob"
            assert result[2]["last_name"] == "Johnson"
            assert result[2]["address"] == ""  # No addresses


@pytest.mark.unit
class TestFormatAddresses:
    """Tests for _format_addresses helper method."""

    def test_format_addresses_with_empty_list(self, db: Session) -> None:
        """Test _format_addresses with empty address list.

        Requirements: 1.3, 5.3
        """
        service = PersonService(db)
        result = service._format_addresses([])
        assert result == ""

    def test_format_addresses_with_single_address(self, db: Session) -> None:
        """Test _format_addresses with single address.

        Requirements: 1.3, 5.3
        """
        service = PersonService(db)

        address = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            address_line="123 Main Street",
            start_date=date(2000, 1, 1),
        )

        result = service._format_addresses([address])
        assert result == "123 Main Street"

    def test_format_addresses_with_multiple_addresses(self, db: Session) -> None:
        """Test _format_addresses with multiple addresses.

        Requirements: 1.3, 5.3
        """
        service = PersonService(db)

        address1 = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            address_line="123 Main Street",
            start_date=date(2000, 1, 1),
        )

        address2 = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            address_line="456 Oak Avenue",
            start_date=date(2010, 1, 1),
        )

        address3 = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            address_line="789 Pine Road",
            start_date=date(2015, 1, 1),
        )

        result = service._format_addresses([address1, address2, address3])
        assert result == "123 Main Street, 456 Oak Avenue, 789 Pine Road"

    def test_format_addresses_with_none_address_line(self, db: Session) -> None:
        """Test _format_addresses with addresses that have None address_line."""
        service = PersonService(db)

        address1 = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            address_line="123 Main Street",
            start_date=date(2000, 1, 1),
        )

        address2 = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            address_line=None,  # No address line
            start_date=date(2010, 1, 1),
        )

        address3 = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            address_line="789 Pine Road",
            start_date=date(2015, 1, 1),
        )

        result = service._format_addresses([address1, address2, address3])
        # Should skip address2 since it has no address_line
        assert result == "123 Main Street, 789 Pine Road"
