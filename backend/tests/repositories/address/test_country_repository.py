"""Unit tests for CountryRepository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.address import Country
from app.repositories.address.country_repository import CountryRepository


@pytest.mark.unit
class TestGetActiveCountries:
    """Tests for get_active_countries method."""

    def test_get_active_countries_returns_list(self, mock_session: MagicMock) -> None:
        """Test get_active_countries returns list of active countries."""
        repo = CountryRepository(mock_session)
        countries = [
            Country(
                id=uuid.uuid4(),
                name="United States",
                code="USA",
                is_active=True,
            ),
            Country(
                id=uuid.uuid4(),
                name="Canada",
                code="CAN",
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = countries

        result = repo.get_active_countries()

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_active_countries_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_active_countries returns empty list when no active countries."""
        repo = CountryRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_active_countries()

        assert result == []


@pytest.mark.unit
class TestGetByCode:
    """Tests for get_by_code method."""

    def test_get_by_code_returns_country(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns country when found."""
        repo = CountryRepository(mock_session)
        country = Country(
            id=uuid.uuid4(),
            name="United States",
            code="USA",
            is_active=True,
        )
        mock_session.exec.return_value.first.return_value = country

        result = repo.get_by_code("USA")

        assert result == country
        assert result.code == "USA"

    def test_get_by_code_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_code returns None when country not found."""
        repo = CountryRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_code("XXX")

        assert result is None
