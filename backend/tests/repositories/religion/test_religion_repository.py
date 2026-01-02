"""Unit tests for ReligionRepository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.religion.religion import Religion
from app.repositories.religion.religion_repository import ReligionRepository


@pytest.mark.unit
class TestGetActiveReligions:
    """Tests for get_active_religions method."""

    def test_get_active_religions_returns_list(self, mock_session: MagicMock) -> None:
        """Test get_active_religions returns list of active religions."""
        repo = ReligionRepository(mock_session)
        religions = [
            Religion(
                id=uuid.uuid4(),
                name="Christianity",
                code="CHRISTIANITY",
                is_active=True,
            ),
            Religion(
                id=uuid.uuid4(),
                name="Islam",
                code="ISLAM",
                is_active=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = religions

        result = repo.get_active_religions()

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_active_religions_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_active_religions returns empty list when no active religions."""
        repo = ReligionRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_active_religions()

        assert result == []


@pytest.mark.unit
class TestCodeExists:
    """Tests for code_exists method."""

    def test_code_exists_returns_true_when_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns True when code exists."""
        repo = ReligionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = Religion(
            id=uuid.uuid4(),
            name="Christianity",
            code="CHRISTIANITY",
            is_active=True,
        )

        result = repo.code_exists("CHRISTIANITY")

        assert result is True

    def test_code_exists_returns_false_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns False when code doesn't exist."""
        repo = ReligionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.code_exists("NONEXISTENT")

        assert result is False

    def test_code_exists_excludes_specified_id(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists excludes specified religion ID."""
        repo = ReligionRepository(mock_session)
        exclude_id = uuid.uuid4()
        mock_session.exec.return_value.first.return_value = None

        result = repo.code_exists("CHRISTIANITY", exclude_religion_id=exclude_id)

        assert result is False
        mock_session.exec.assert_called_once()
