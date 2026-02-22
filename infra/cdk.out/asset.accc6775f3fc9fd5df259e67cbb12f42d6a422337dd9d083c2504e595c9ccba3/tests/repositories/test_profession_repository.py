"""Unit tests for ProfessionRepository.

Tests cover:
- Profession retrieval (all active)
- Name existence check

Requirements: 3.14, 3.15
"""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.person.profession import Profession
from app.repositories.person.profession_repository import ProfessionRepository


@pytest.mark.unit
class TestGetActiveProfessions:
    """Tests for get_active_professions method."""

    def test_get_active_professions_returns_list(self, mock_session: MagicMock) -> None:
        """Test get_active_professions returns list of professions."""
        repo = ProfessionRepository(mock_session)
        professions = [
            Profession(id=uuid.uuid4(), name="Engineer", description="Engineering", weight=1, is_active=True),
            Profession(id=uuid.uuid4(), name="Doctor", description="Medical", weight=2, is_active=True),
        ]
        mock_session.exec.return_value.all.return_value = professions

        result = repo.get_active_professions()

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_active_professions_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_active_professions returns empty list when no professions."""
        repo = ProfessionRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_active_professions()

        assert result == []


@pytest.mark.unit
class TestNameExists:
    """Tests for name_exists method."""

    def test_name_exists_returns_true_when_exists(self, mock_session: MagicMock) -> None:
        """Test name_exists returns True when name exists."""
        repo = ProfessionRepository(mock_session)
        profession = Profession(id=uuid.uuid4(), name="Engineer", description="Engineering", weight=1, is_active=True)
        mock_session.exec.return_value.first.return_value = profession

        result = repo.name_exists("Engineer")

        assert result is True

    def test_name_exists_returns_false_when_not_exists(self, mock_session: MagicMock) -> None:
        """Test name_exists returns False when name doesn't exist."""
        repo = ProfessionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.name_exists("Unknown")

        assert result is False

    def test_name_exists_with_exclude_id(self, mock_session: MagicMock) -> None:
        """Test name_exists with exclude_profession_id parameter."""
        repo = ProfessionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        profession_id = uuid.uuid4()
        result = repo.name_exists("Engineer", exclude_profession_id=profession_id)

        assert result is False
        mock_session.exec.assert_called_once()

    def test_name_exists_case_sensitive(self, mock_session: MagicMock) -> None:
        """Test name_exists is case sensitive."""
        repo = ProfessionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.name_exists("engineer")

        assert result is False
