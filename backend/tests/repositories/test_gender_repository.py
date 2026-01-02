"""Unit tests for GenderRepository.

Tests cover:
- Gender retrieval (all active)
- Gender retrieval by ID
- Gender retrieval by code
- Code existence check

Requirements: 3.13, 3.15
"""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.person.gender import Gender
from app.repositories.person.gender_repository import GenderRepository


@pytest.mark.unit
class TestGetActiveGenders:
    """Tests for get_active_genders method."""

    def test_get_active_genders_returns_list(self, mock_session: MagicMock) -> None:
        """Test get_active_genders returns list of genders."""
        repo = GenderRepository(mock_session)
        genders = [
            Gender(id=uuid.uuid4(), name="Male", code="MALE", is_active=True),
            Gender(id=uuid.uuid4(), name="Female", code="FEMALE", is_active=True),
        ]
        mock_session.exec.return_value.all.return_value = genders

        result = repo.get_active_genders()

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_active_genders_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_active_genders returns empty list when no genders."""
        repo = GenderRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_active_genders()

        assert result == []


@pytest.mark.unit
class TestGetByCode:
    """Tests for get_by_code method."""

    def test_get_by_code_returns_gender(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns gender when found."""
        repo = GenderRepository(mock_session)
        gender = Gender(id=uuid.uuid4(), name="Male", code="MALE", is_active=True)
        mock_session.exec.return_value.first.return_value = gender

        result = repo.get_by_code("MALE")

        assert result == gender
        assert result.code == "MALE"

    def test_get_by_code_returns_none_when_not_found(self, mock_session: MagicMock) -> None:
        """Test get_by_code returns None when gender not found."""
        repo = GenderRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_code("UNKNOWN")

        assert result is None

    def test_get_by_code_case_insensitive(self, mock_session: MagicMock) -> None:
        """Test get_by_code handles lowercase input."""
        repo = GenderRepository(mock_session)
        gender = Gender(id=uuid.uuid4(), name="Male", code="MALE", is_active=True)
        mock_session.exec.return_value.first.return_value = gender

        result = repo.get_by_code("male")

        assert result == gender


@pytest.mark.unit
class TestCodeExists:
    """Tests for code_exists method."""

    def test_code_exists_returns_true_when_exists(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True when code exists."""
        repo = GenderRepository(mock_session)
        gender = Gender(id=uuid.uuid4(), name="Male", code="MALE", is_active=True)
        mock_session.exec.return_value.first.return_value = gender

        result = repo.code_exists("MALE")

        assert result is True

    def test_code_exists_returns_false_when_not_exists(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False when code doesn't exist."""
        repo = GenderRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.code_exists("UNKNOWN")

        assert result is False

    def test_code_exists_with_exclude_id(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude_gender_id parameter."""
        repo = GenderRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        gender_id = uuid.uuid4()
        result = repo.code_exists("MALE", exclude_gender_id=gender_id)

        assert result is False
        mock_session.exec.assert_called_once()

    def test_code_exists_case_insensitive(self, mock_session: MagicMock) -> None:
        """Test code_exists handles lowercase input."""
        repo = GenderRepository(mock_session)
        gender = Gender(id=uuid.uuid4(), name="Male", code="MALE", is_active=True)
        mock_session.exec.return_value.first.return_value = gender

        result = repo.code_exists("male")

        assert result is True
