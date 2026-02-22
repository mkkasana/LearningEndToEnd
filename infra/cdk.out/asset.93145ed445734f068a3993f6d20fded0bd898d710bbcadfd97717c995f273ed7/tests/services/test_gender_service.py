"""Unit tests for GenderService.

Tests cover:
- Gender retrieval
- Gender validation

Requirements: 2.15, 2.18
"""

import uuid

import pytest

from app.services.person.gender_service import GenderService


@pytest.mark.unit
class TestGenderServiceQueries:
    """Tests for gender query operations."""

    def test_get_genders_returns_list(self) -> None:
        """Test getting all genders returns a list."""
        # Arrange
        service = GenderService()

        # Act
        result = service.get_genders()

        # Assert
        assert isinstance(result, list)
        assert len(result) >= 2  # At least male and female

    def test_get_genders_contains_male_and_female(self) -> None:
        """Test that genders list contains male and female."""
        # Arrange
        service = GenderService()

        # Act
        result = service.get_genders()
        gender_codes = [g.genderCode for g in result]

        # Assert
        assert "MALE" in gender_codes
        assert "FEMALE" in gender_codes

    def test_get_gender_by_id_returns_gender(self) -> None:
        """Test getting gender by valid ID returns the gender."""
        # Arrange
        service = GenderService()
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")

        # Act
        result = service.get_gender_by_id(male_gender_id)

        # Assert
        assert result is not None
        assert result.code == "MALE"
        assert result.name == "Male"

    def test_get_gender_by_id_returns_none_for_nonexistent(self) -> None:
        """Test getting nonexistent gender returns None."""
        # Arrange
        service = GenderService()
        nonexistent_id = uuid.uuid4()

        # Act
        result = service.get_gender_by_id(nonexistent_id)

        # Assert
        assert result is None

    def test_get_gender_by_code_male(self) -> None:
        """Test getting gender by code 'male'."""
        # Arrange
        service = GenderService()

        # Act
        result = service.get_gender_by_code("male")

        # Assert
        assert result is not None
        assert result.code == "MALE"

    def test_get_gender_by_code_female(self) -> None:
        """Test getting gender by code 'female'."""
        # Arrange
        service = GenderService()

        # Act
        result = service.get_gender_by_code("female")

        # Assert
        assert result is not None
        assert result.code == "FEMALE"

    def test_get_gender_by_code_returns_none_for_invalid(self) -> None:
        """Test getting gender by invalid code returns None."""
        # Arrange
        service = GenderService()

        # Act
        result = service.get_gender_by_code("invalid_code")

        # Assert
        assert result is None


@pytest.mark.unit
class TestGenderServiceValidation:
    """Tests for gender validation."""

    def test_code_exists_returns_true_for_existing_code(self) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        service = GenderService()

        # Act
        result = service.code_exists("male")

        # Assert
        assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(self) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = GenderService()

        # Act
        result = service.code_exists("nonexistent")

        # Assert
        assert result is False

    def test_code_exists_with_exclude_returns_false(self) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        service = GenderService()
        male_gender_id = uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83")

        # Act
        result = service.code_exists("male", exclude_gender_id=male_gender_id)

        # Assert
        assert result is False

    def test_code_exists_with_exclude_returns_true_for_different_id(self) -> None:
        """Test code_exists with exclude returns True when excluding different ID."""
        # Arrange
        service = GenderService()
        different_id = uuid.uuid4()

        # Act
        result = service.code_exists("male", exclude_gender_id=different_id)

        # Assert
        assert result is True
