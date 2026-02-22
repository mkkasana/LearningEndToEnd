"""Unit tests for PersonAddressService.

Tests cover:
- Address CRUD operations
- Current address management

Requirements: 2.5, 2.18
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.person.person_address import PersonAddress
from app.schemas.person import PersonAddressCreate, PersonAddressUpdate
from app.services.person.person_address_service import PersonAddressService


@pytest.mark.unit
class TestPersonAddressServiceQueries:
    """Tests for address query operations."""

    def test_get_addresses_by_person_returns_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting addresses by person ID returns list."""
        # Arrange
        person_id = uuid.uuid4()
        mock_addresses = [
            PersonAddress(
                id=uuid.uuid4(),
                person_id=person_id,
                country_id=uuid.uuid4(),
                start_date=date(2020, 1, 1),
                is_current=True,
            ),
            PersonAddress(
                id=uuid.uuid4(),
                person_id=person_id,
                country_id=uuid.uuid4(),
                start_date=date(2015, 1, 1),
                is_current=False,
            ),
        ]

        service = PersonAddressService(mock_session)
        with patch.object(
            service.address_repo, "get_by_person_id", return_value=mock_addresses
        ):
            # Act
            result = service.get_addresses_by_person(person_id)

            # Assert
            assert len(result) == 2

    def test_get_addresses_by_person_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting addresses for person with no addresses returns empty list."""
        # Arrange
        service = PersonAddressService(mock_session)
        with patch.object(service.address_repo, "get_by_person_id", return_value=[]):
            # Act
            result = service.get_addresses_by_person(uuid.uuid4())

            # Assert
            assert result == []

    def test_get_address_by_id_returns_address(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting address by ID returns the address."""
        # Arrange
        address_id = uuid.uuid4()
        mock_address = PersonAddress(
            id=address_id,
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )

        service = PersonAddressService(mock_session)
        with patch.object(service.address_repo, "get_by_id", return_value=mock_address):
            # Act
            result = service.get_address_by_id(address_id)

            # Assert
            assert result is not None
            assert result.id == address_id

    def test_get_address_by_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent address returns None."""
        # Arrange
        service = PersonAddressService(mock_session)
        with patch.object(service.address_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_address_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestPersonAddressServiceCreate:
    """Tests for address creation."""

    def test_create_address_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating address with valid data."""
        # Arrange
        person_id = uuid.uuid4()
        country_id = uuid.uuid4()
        address_create = PersonAddressCreate(
            country_id=country_id,
            start_date=date(2020, 1, 1),
            is_current=False,
        )

        service = PersonAddressService(mock_session)
        
        def return_address(address: PersonAddress) -> PersonAddress:
            return address

        with patch.object(service.address_repo, "create", side_effect=return_address):
            # Act
            result = service.create_address(person_id, address_create)

            # Assert
            assert result.person_id == person_id
            assert result.country_id == country_id
            assert result.is_current is False

    def test_create_current_address_clears_other_current(
        self, mock_session: MagicMock
    ) -> None:
        """Test creating current address clears other current addresses."""
        # Arrange
        person_id = uuid.uuid4()
        address_create = PersonAddressCreate(
            country_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )

        service = PersonAddressService(mock_session)
        mock_clear = MagicMock()
        
        def return_address(address: PersonAddress) -> PersonAddress:
            return address

        with patch.object(service.address_repo, "clear_current_addresses", mock_clear):
            with patch.object(service.address_repo, "create", side_effect=return_address):
                # Act
                service.create_address(person_id, address_create)

                # Assert
                mock_clear.assert_called_once_with(person_id)

    def test_create_non_current_address_does_not_clear_current(
        self, mock_session: MagicMock
    ) -> None:
        """Test creating non-current address doesn't clear current addresses."""
        # Arrange
        person_id = uuid.uuid4()
        address_create = PersonAddressCreate(
            country_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=False,
        )

        service = PersonAddressService(mock_session)
        mock_clear = MagicMock()
        
        def return_address(address: PersonAddress) -> PersonAddress:
            return address

        with patch.object(service.address_repo, "clear_current_addresses", mock_clear):
            with patch.object(service.address_repo, "create", side_effect=return_address):
                # Act
                service.create_address(person_id, address_create)

                # Assert
                mock_clear.assert_not_called()


@pytest.mark.unit
class TestPersonAddressServiceUpdate:
    """Tests for address update operations."""

    def test_update_address_fields(self, mock_session: MagicMock) -> None:
        """Test updating address fields."""
        # Arrange
        mock_address = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=False,
            address_line="Old Address",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        address_update = PersonAddressUpdate(address_line="New Address")

        service = PersonAddressService(mock_session)
        
        def return_address(address: PersonAddress) -> PersonAddress:
            return address

        with patch.object(service.address_repo, "update", side_effect=return_address):
            # Act
            result = service.update_address(mock_address, address_update)

            # Assert
            assert result.address_line == "New Address"

    def test_update_to_current_clears_other_current(
        self, mock_session: MagicMock
    ) -> None:
        """Test updating address to current clears other current addresses."""
        # Arrange
        person_id = uuid.uuid4()
        mock_address = PersonAddress(
            id=uuid.uuid4(),
            person_id=person_id,
            country_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        address_update = PersonAddressUpdate(is_current=True)

        service = PersonAddressService(mock_session)
        mock_clear = MagicMock()
        
        def return_address(address: PersonAddress) -> PersonAddress:
            return address

        with patch.object(service.address_repo, "clear_current_addresses", mock_clear):
            with patch.object(service.address_repo, "update", side_effect=return_address):
                # Act
                service.update_address(mock_address, address_update)

                # Assert
                mock_clear.assert_called_once_with(person_id)


@pytest.mark.unit
class TestPersonAddressServiceDelete:
    """Tests for address deletion."""

    def test_delete_address_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete_address calls the repository delete method."""
        # Arrange
        mock_address = PersonAddress(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            country_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )

        service = PersonAddressService(mock_session)
        mock_delete = MagicMock()
        
        with patch.object(service.address_repo, "delete", mock_delete):
            # Act
            service.delete_address(mock_address)

            # Assert
            mock_delete.assert_called_once_with(mock_address)
