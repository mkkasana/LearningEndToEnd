"""Unit tests for PersonContributionPublic schema."""

import uuid
from datetime import date, datetime

import pytest

from app.schemas.person import PersonContributionPublic


def test_person_contribution_public_with_valid_data():
    """Test PersonContributionPublic schema validation with valid data."""
    # Arrange
    person_id = uuid.uuid4()
    now = datetime.utcnow()
    birth_date = date(1990, 1, 1)
    death_date = date(2020, 12, 31)

    # Act
    contribution = PersonContributionPublic(
        id=person_id,
        first_name="John",
        last_name="Doe",
        date_of_birth=birth_date,
        date_of_death=death_date,
        is_active=True,
        address="123 Main St, Springfield, IL, USA",
        total_views=42,
        created_at=now,
    )

    # Assert
    assert contribution.id == person_id
    assert contribution.first_name == "John"
    assert contribution.last_name == "Doe"
    assert contribution.date_of_birth == birth_date
    assert contribution.date_of_death == death_date
    assert contribution.is_active is True
    assert contribution.address == "123 Main St, Springfield, IL, USA"
    assert contribution.total_views == 42
    assert contribution.created_at == now


def test_person_contribution_public_with_null_death_date():
    """Test PersonContributionPublic schema with null death date (living person)."""
    # Arrange
    person_id = uuid.uuid4()
    now = datetime.utcnow()
    birth_date = date(1990, 1, 1)

    # Act
    contribution = PersonContributionPublic(
        id=person_id,
        first_name="Jane",
        last_name="Smith",
        date_of_birth=birth_date,
        date_of_death=None,
        is_active=True,
        address="456 Oak Ave, Portland, OR, USA",
        total_views=15,
        created_at=now,
    )

    # Assert
    assert contribution.date_of_death is None
    assert contribution.first_name == "Jane"
    assert contribution.last_name == "Smith"


def test_person_contribution_public_with_empty_address():
    """Test PersonContributionPublic schema with empty address string."""
    # Arrange
    person_id = uuid.uuid4()
    now = datetime.utcnow()
    birth_date = date(1985, 5, 15)

    # Act
    contribution = PersonContributionPublic(
        id=person_id,
        first_name="Bob",
        last_name="Johnson",
        date_of_birth=birth_date,
        date_of_death=None,
        is_active=False,
        address="",
        total_views=0,
        created_at=now,
    )

    # Assert
    assert contribution.address == ""
    assert contribution.total_views == 0
    assert contribution.is_active is False


def test_person_contribution_public_serialization():
    """Test PersonContributionPublic schema serialization to dict."""
    # Arrange
    person_id = uuid.uuid4()
    now = datetime.utcnow()
    birth_date = date(1975, 3, 20)
    death_date = date(2015, 8, 10)

    contribution = PersonContributionPublic(
        id=person_id,
        first_name="Alice",
        last_name="Williams",
        date_of_birth=birth_date,
        date_of_death=death_date,
        is_active=True,
        address="789 Pine Rd, Seattle, WA, USA",
        total_views=100,
        created_at=now,
    )

    # Act
    data = contribution.model_dump()

    # Assert
    assert isinstance(data, dict)
    assert data["id"] == person_id
    assert data["first_name"] == "Alice"
    assert data["last_name"] == "Williams"
    assert data["date_of_birth"] == birth_date
    assert data["date_of_death"] == death_date
    assert data["is_active"] is True
    assert data["address"] == "789 Pine Rd, Seattle, WA, USA"
    assert data["total_views"] == 100
    assert data["created_at"] == now


def test_person_contribution_public_json_serialization():
    """Test PersonContributionPublic schema JSON serialization."""
    # Arrange
    person_id = uuid.uuid4()
    now = datetime.utcnow()
    birth_date = date(1980, 7, 4)

    contribution = PersonContributionPublic(
        id=person_id,
        first_name="Charlie",
        last_name="Brown",
        date_of_birth=birth_date,
        date_of_death=None,
        is_active=True,
        address="321 Elm St, Boston, MA, USA",
        total_views=25,
        created_at=now,
    )

    # Act
    json_str = contribution.model_dump_json()

    # Assert
    assert isinstance(json_str, str)
    assert str(person_id) in json_str
    assert "Charlie" in json_str
    assert "Brown" in json_str
    assert "321 Elm St, Boston, MA, USA" in json_str


def test_person_contribution_public_with_zero_views():
    """Test PersonContributionPublic schema with zero views."""
    # Arrange
    person_id = uuid.uuid4()
    now = datetime.utcnow()
    birth_date = date(2000, 1, 1)

    # Act
    contribution = PersonContributionPublic(
        id=person_id,
        first_name="David",
        last_name="Miller",
        date_of_birth=birth_date,
        date_of_death=None,
        is_active=True,
        address="555 Maple Dr, Austin, TX, USA",
        total_views=0,
        created_at=now,
    )

    # Assert
    assert contribution.total_views == 0
