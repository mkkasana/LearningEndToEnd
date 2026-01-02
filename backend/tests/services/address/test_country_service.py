"""Unit tests for CountryService.

Tests cover:
- Country retrieval
- Country CRUD operations
- Code validation

Requirements: 2.16, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.address import Country
from app.schemas.address import CountryCreate, CountryUpdate
from app.services.address.country_service import CountryService


@pytest.mark.unit
class TestCountryServiceQueries:
    """Tests for country query operations."""

    def test_get_countries_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting all countries returns a list."""
        # Arrange
        mock_countries = [
            Country(id=uuid.uuid4(), name="India", code="IN", is_active=True),
            Country(id=uuid.uuid4(), name="United States", code="US", is_active=True),
        ]

        service = CountryService(mock_session)
        with patch.object(
            service.country_repo, "get_active_countries", return_value=mock_countries
        ):
            # Act
            result = service.get_countries()

            # Assert
            assert len(result) == 2
            assert result[0].countryName == "India"
            assert result[1].countryName == "United States"

    def test_get_country_by_id_returns_country(self, mock_session: MagicMock) -> None:
        """Test getting country by ID returns the country."""
        # Arrange
        country_id = uuid.uuid4()
        mock_country = Country(id=country_id, name="India", code="IN", is_active=True)

        service = CountryService(mock_session)
        with patch.object(
            service.country_repo, "get_by_id", return_value=mock_country
        ):
            # Act
            result = service.get_country_by_id(country_id)

            # Assert
            assert result is not None
            assert result.id == country_id
            assert result.name == "India"

    def test_get_country_by_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent country returns None."""
        # Arrange
        service = CountryService(mock_session)
        with patch.object(service.country_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_country_by_id(uuid.uuid4())

            # Assert
            assert result is None

    def test_get_country_by_code_returns_country(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting country by code returns the country."""
        # Arrange
        mock_country = Country(
            id=uuid.uuid4(), name="India", code="IN", is_active=True
        )

        service = CountryService(mock_session)
        with patch.object(
            service.country_repo, "get_by_code", return_value=mock_country
        ):
            # Act
            result = service.get_country_by_code("IN")

            # Assert
            assert result is not None
            assert result.code == "IN"

    def test_get_country_by_code_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting country by nonexistent code returns None."""
        # Arrange
        service = CountryService(mock_session)
        with patch.object(service.country_repo, "get_by_code", return_value=None):
            # Act
            result = service.get_country_by_code("XX")

            # Assert
            assert result is None


@pytest.mark.unit
class TestCountryServiceCreate:
    """Tests for country creation."""

    def test_create_country_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating country with valid data."""
        # Arrange
        country_create = CountryCreate(name="New Country", code="nc", is_active=True)

        service = CountryService(mock_session)

        def return_country(country: Country) -> Country:
            return country

        with patch.object(
            service.country_repo, "create", side_effect=return_country
        ):
            # Act
            result = service.create_country(country_create)

            # Assert
            assert result.name == "New Country"
            assert result.code == "NC"  # Should be uppercase
            assert result.is_active is True

    def test_create_country_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that country code is uppercased on creation."""
        # Arrange
        country_create = CountryCreate(name="Test", code="ts", is_active=True)

        service = CountryService(mock_session)

        def return_country(country: Country) -> Country:
            return country

        with patch.object(
            service.country_repo, "create", side_effect=return_country
        ):
            # Act
            result = service.create_country(country_create)

            # Assert
            assert result.code == "TS"


@pytest.mark.unit
class TestCountryServiceUpdate:
    """Tests for country update operations."""

    def test_update_country_name(self, mock_session: MagicMock) -> None:
        """Test updating country name."""
        # Arrange
        mock_country = Country(
            id=uuid.uuid4(), name="Old Name", code="ON", is_active=True
        )
        country_update = CountryUpdate(name="New Name")

        service = CountryService(mock_session)

        def return_country(country: Country) -> Country:
            return country

        with patch.object(
            service.country_repo, "update", side_effect=return_country
        ):
            # Act
            result = service.update_country(mock_country, country_update)

            # Assert
            assert result.name == "New Name"

    def test_update_country_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating country code uppercases it."""
        # Arrange
        mock_country = Country(
            id=uuid.uuid4(), name="Country", code="OLD", is_active=True
        )
        country_update = CountryUpdate(code="new")

        service = CountryService(mock_session)

        def return_country(country: Country) -> Country:
            return country

        with patch.object(
            service.country_repo, "update", side_effect=return_country
        ):
            # Act
            result = service.update_country(mock_country, country_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestCountryServiceDelete:
    """Tests for country deletion."""

    def test_delete_country_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_country = Country(
            id=uuid.uuid4(), name="Country to Delete", code="CD", is_active=True
        )

        service = CountryService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.country_repo, "delete", mock_delete):
            # Act
            service.delete_country(mock_country)

            # Assert
            mock_delete.assert_called_once_with(mock_country)


@pytest.mark.unit
class TestCountryServiceValidation:
    """Tests for country validation."""

    def test_code_exists_returns_true_for_existing_code(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        mock_country = Country(
            id=uuid.uuid4(), name="India", code="IN", is_active=True
        )

        service = CountryService(mock_session)
        with patch.object(
            service.country_repo, "get_by_code", return_value=mock_country
        ):
            # Act
            result = service.code_exists("IN")

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = CountryService(mock_session)
        with patch.object(service.country_repo, "get_by_code", return_value=None):
            # Act
            result = service.code_exists("XX")

            # Assert
            assert result is False

    def test_code_exists_with_exclude_returns_false(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        country_id = uuid.uuid4()
        mock_country = Country(id=country_id, name="India", code="IN", is_active=True)

        service = CountryService(mock_session)
        with patch.object(
            service.country_repo, "get_by_code", return_value=mock_country
        ):
            # Act
            result = service.code_exists("IN", exclude_country_id=country_id)

            # Assert
            assert result is False
