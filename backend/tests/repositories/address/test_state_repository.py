"""Unit tests for StateRepository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.address import State
from app.repositories.address.state_repository import StateRepository


@pytest.mark.unit
class TestGetByCountry:
    """Tests for get_by_country method."""

    def test_get_by_country_returns_states(self, mock_session: MagicMock) -> None:
        """Test get_by_country returns list of states."""
        repo = StateRepository(mock_session)
        country_id = uuid.uuid4()
        states = [
            State(
                id=uuid.uuid4(),
                name="California",
                code="CA",
                country_id=country_id,
                is_active=True,
            ),
            State(
                id=uuid.uuid4(),
                name="Texas",
                code="TX",
                country_id=country_id,
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = states

        result = repo.get_by_country(country_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_country_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_country returns empty list when no states."""
        repo = StateRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_country(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetByCode:
    """Tests for get_by_code method."""

    def test_get_by_code_returns_state(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns state when found."""
        repo = StateRepository(mock_session)
        country_id = uuid.uuid4()
        state = State(
            id=uuid.uuid4(),
            name="California",
            code="CA",
            country_id=country_id,
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = state

        result = repo.get_by_code("CA", country_id)

        assert result == state
        assert result.code == "CA"

    def test_get_by_code_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_code returns None when state not found."""
        repo = StateRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_code("XX", uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestCountByCountry:
    """Tests for count_by_country method."""

    def test_count_by_country_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_by_country returns correct count."""
        repo = StateRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 5

        result = repo.count_by_country(uuid.uuid4())

        assert result == 5

    def test_count_by_country_returns_zero(self, mock_session: MagicMock) -> None:
        """Test count_by_country returns 0 when no states."""
        repo = StateRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 0

        result = repo.count_by_country(uuid.uuid4())

        assert result == 0
