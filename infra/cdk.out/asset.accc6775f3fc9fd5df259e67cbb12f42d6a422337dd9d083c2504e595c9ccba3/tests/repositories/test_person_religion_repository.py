"""Unit tests for PersonReligionRepository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.person.person_religion import PersonReligion
from app.repositories.person.person_religion_repository import PersonReligionRepository


@pytest.mark.unit
class TestGetByPersonId:
    """Tests for get_by_person_id method."""

    def test_get_by_person_id_returns_religion(self, mock_session: MagicMock) -> None:
        """Test get_by_person_id returns religion when exists."""
        repo = PersonReligionRepository(mock_session)
        person_id = uuid.uuid4()
        religion = PersonReligion(
            id=uuid.uuid4(),
            person_id=person_id,
            religion_id=uuid.uuid4(),
        )
        mock_session.exec.return_value.first.return_value = religion

        result = repo.get_by_person_id(person_id)

        assert result == religion
        mock_session.exec.assert_called_once()

    def test_get_by_person_id_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_person_id returns None when no religion."""
        repo = PersonReligionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_person_id(uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestPersonHasReligion:
    """Tests for person_has_religion method."""

    def test_person_has_religion_returns_true_when_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test person_has_religion returns True when person has religion."""
        repo = PersonReligionRepository(mock_session)
        person_id = uuid.uuid4()
        mock_session.exec.return_value.first.return_value = PersonReligion(
            id=uuid.uuid4(),
            person_id=person_id,
            religion_id=uuid.uuid4(),
        )

        result = repo.person_has_religion(person_id)

        assert result is True

    def test_person_has_religion_returns_false_when_not_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test person_has_religion returns False when person has no religion."""
        repo = PersonReligionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.person_has_religion(uuid.uuid4())

        assert result is False
