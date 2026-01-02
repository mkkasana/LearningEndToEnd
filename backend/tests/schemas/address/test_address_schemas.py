"""Unit tests for Address schemas."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.address.country import (
    CountryBase,
    CountryCreate,
    CountryUpdate,
    CountryPublic,
    CountryDetailPublic,
    CountriesPublic,
)


@pytest.mark.unit
class TestCountryBase:
    """Tests for CountryBase schema."""

    def test_valid_country_base(self) -> None:
        """Test CountryBase with valid data."""
        country = CountryBase(name="United States", code="USA")
        assert country.name == "United States"
        assert country.code == "USA"
        assert country.is_active is True

    def test_country_base_with_inactive(self) -> None:
        """Test CountryBase with is_active=False."""
        country = CountryBase(name="Test Country", code="TST", is_active=False)
        assert country.is_active is False

    def test_country_base_name_required(self) -> None:
        """Test CountryBase requires name."""
        with pytest.raises(ValidationError) as exc_info:
            CountryBase(code="USA")
        assert "name" in str(exc_info.value)

    def test_country_base_code_required(self) -> None:
        """Test CountryBase requires code."""
        with pytest.raises(ValidationError) as exc_info:
            CountryBase(name="United States")
        assert "code" in str(exc_info.value)

    def test_country_base_code_max_length(self) -> None:
        """Test CountryBase code max length (3 chars)."""
        with pytest.raises(ValidationError) as exc_info:
            CountryBase(name="Test Country", code="TOOLONG")
        assert "code" in str(exc_info.value)

    def test_country_base_name_max_length(self) -> None:
        """Test CountryBase name max length."""
        with pytest.raises(ValidationError) as exc_info:
            CountryBase(name="A" * 256, code="TST")
        assert "name" in str(exc_info.value)


@pytest.mark.unit
class TestCountryCreate:
    """Tests for CountryCreate schema."""

    def test_valid_country_create(self) -> None:
        """Test CountryCreate with valid data."""
        country = CountryCreate(name="Canada", code="CAN")
        assert country.name == "Canada"
        assert country.code == "CAN"


@pytest.mark.unit
class TestCountryUpdate:
    """Tests for CountryUpdate schema."""

    def test_country_update_all_optional(self) -> None:
        """Test CountryUpdate with no fields."""
        country = CountryUpdate()
        assert country.name is None
        assert country.code is None
        assert country.is_active is None

    def test_country_update_partial(self) -> None:
        """Test CountryUpdate with partial fields."""
        country = CountryUpdate(name="New Name")
        assert country.name == "New Name"
        assert country.code is None

    def test_country_update_code_max_length(self) -> None:
        """Test CountryUpdate code max length."""
        with pytest.raises(ValidationError) as exc_info:
            CountryUpdate(code="TOOLONG")
        assert "code" in str(exc_info.value)


@pytest.mark.unit
class TestCountryPublic:
    """Tests for CountryPublic schema."""

    def test_valid_country_public(self) -> None:
        """Test CountryPublic with valid data."""
        country = CountryPublic(
            countryId=uuid.uuid4(),
            countryName="United States",
        )
        assert country.countryName == "United States"

    def test_country_public_requires_id(self) -> None:
        """Test CountryPublic requires countryId."""
        with pytest.raises(ValidationError) as exc_info:
            CountryPublic(countryName="United States")
        assert "countryId" in str(exc_info.value)

    def test_country_public_requires_name(self) -> None:
        """Test CountryPublic requires countryName."""
        with pytest.raises(ValidationError) as exc_info:
            CountryPublic(countryId=uuid.uuid4())
        assert "countryName" in str(exc_info.value)


@pytest.mark.unit
class TestCountryDetailPublic:
    """Tests for CountryDetailPublic schema."""

    def test_valid_country_detail_public(self) -> None:
        """Test CountryDetailPublic with valid data."""
        country = CountryDetailPublic(
            id=uuid.uuid4(),
            name="United States",
            code="USA",
            is_active=True,
        )
        assert country.name == "United States"
        assert country.code == "USA"

    def test_country_detail_public_requires_id(self) -> None:
        """Test CountryDetailPublic requires id."""
        with pytest.raises(ValidationError) as exc_info:
            CountryDetailPublic(name="United States", code="USA")
        assert "id" in str(exc_info.value)


@pytest.mark.unit
class TestCountriesPublic:
    """Tests for CountriesPublic schema."""

    def test_valid_countries_public(self) -> None:
        """Test CountriesPublic with valid data."""
        countries = CountriesPublic(
            data=[
                CountryPublic(countryId=uuid.uuid4(), countryName="USA"),
                CountryPublic(countryId=uuid.uuid4(), countryName="Canada"),
            ]
        )
        assert len(countries.data) == 2

    def test_countries_public_empty_list(self) -> None:
        """Test CountriesPublic with empty list."""
        countries = CountriesPublic(data=[])
        assert len(countries.data) == 0
