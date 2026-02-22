"""Unit tests for PersonAddressRepository."""

import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest

from app.db_models.person.person_address import PersonAddress
from app.repositories.person.person_address_repository import PersonAddressRepository


@pytest.mark.unit
class TestGetByPersonId:
    """Tests for get_by_person_id method."""

    def test_get_by_person_id_returns_addresses(self, mock_session: MagicMock) -> None:
        """Test get_by_person_id returns list of addresses."""
        repo = PersonAddressRepository(mock_session)
        person_id = uuid.uuid4()
        addresses = [
            PersonAddress(
                id=uuid.uuid4(),
                person_id=person_id,
                locality_id=uuid.uuid4(),
                start_date=date(2020, 1, 1),
                is_current=True,
            ),
            PersonAddress(
                id=uuid.uuid4(),
                person_id=person_id,
                locality_id=uuid.uuid4(),
                start_date=date(2015, 1, 1),
                end_date=date(2019, 12, 31),
                is_current=False,
            ),
        ]
        mock_session.exec.return_value.all.return_value = addresses

        result = repo.get_by_person_id(person_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_person_id_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_person_id returns empty list when no addresses."""
        repo = PersonAddressRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_person_id(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetCurrentAddress:
    """Tests for get_current_address method."""

    def test_get_current_address_returns_current(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_current_address returns current address."""
        repo = PersonAddressRepository(mock_session)
        person_id = uuid.uuid4()
        current_address = PersonAddress(
            id=uuid.uuid4(),
            person_id=person_id,
            locality_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )
        mock_session.exec.return_value.first.return_value = current_address

        result = repo.get_current_address(person_id)

        assert result == current_address
        assert result.is_current is True

    def test_get_current_address_returns_none_when_no_current(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_current_address returns None when no current address."""
        repo = PersonAddressRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_current_address(uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestClearCurrentAddresses:
    """Tests for clear_current_addresses method."""

    def test_clear_current_addresses_clears_all(
        self, mock_session: MagicMock
    ) -> None:
        """Test clear_current_addresses clears is_current flag for all addresses."""
        repo = PersonAddressRepository(mock_session)
        person_id = uuid.uuid4()
        addresses = [
            PersonAddress(
                id=uuid.uuid4(),
                person_id=person_id,
                locality_id=uuid.uuid4(),
                start_date=date(2020, 1, 1),
                is_current=True,
            ),
            PersonAddress(
                id=uuid.uuid4(),
                person_id=person_id,
                locality_id=uuid.uuid4(),
                start_date=date(2015, 1, 1),
                is_current=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = addresses

        repo.clear_current_addresses(person_id)

        # Verify all addresses had is_current set to False
        for addr in addresses:
            assert addr.is_current is False
        # Verify session.add was called for each address
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()

    def test_clear_current_addresses_handles_no_addresses(
        self, mock_session: MagicMock
    ) -> None:
        """Test clear_current_addresses handles case with no addresses."""
        repo = PersonAddressRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.clear_current_addresses(uuid.uuid4())

        mock_session.add.assert_not_called()
        mock_session.commit.assert_called_once()
