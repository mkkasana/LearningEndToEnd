"""Unit tests for PersonProfessionRepository."""

import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest

from app.db_models.person.person_profession import PersonProfession
from app.repositories.person.person_profession_repository import (
    PersonProfessionRepository,
)


@pytest.mark.unit
class TestGetByPersonId:
    """Tests for get_by_person_id method."""

    def test_get_by_person_id_returns_professions(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_person_id returns list of professions."""
        repo = PersonProfessionRepository(mock_session)
        person_id = uuid.uuid4()
        professions = [
            PersonProfession(
                id=uuid.uuid4(),
                person_id=person_id,
                profession_id=uuid.uuid4(),
                start_date=date(2020, 1, 1),
                is_current=True,
            ),
            PersonProfession(
                id=uuid.uuid4(),
                person_id=person_id,
                profession_id=uuid.uuid4(),
                start_date=date(2015, 1, 1),
                end_date=date(2019, 12, 31),
                is_current=False,
            ),
        ]
        mock_session.exec.return_value.all.return_value = professions

        result = repo.get_by_person_id(person_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_person_id_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_person_id returns empty list when no professions."""
        repo = PersonProfessionRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_person_id(uuid.uuid4())

        assert result == []


@pytest.mark.unit
class TestGetCurrentProfession:
    """Tests for get_current_profession method."""

    def test_get_current_profession_returns_current(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_current_profession returns current profession."""
        repo = PersonProfessionRepository(mock_session)
        person_id = uuid.uuid4()
        current_profession = PersonProfession(
            id=uuid.uuid4(),
            person_id=person_id,
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )
        mock_session.exec.return_value.first.return_value = current_profession

        result = repo.get_current_profession(person_id)

        assert result == current_profession
        assert result.is_current is True

    def test_get_current_profession_returns_none_when_no_current(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_current_profession returns None when no current profession."""
        repo = PersonProfessionRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_current_profession(uuid.uuid4())

        assert result is None


@pytest.mark.unit
class TestClearCurrentProfessions:
    """Tests for clear_current_professions method."""

    def test_clear_current_professions_clears_all(
        self, mock_session: MagicMock
    ) -> None:
        """Test clear_current_professions clears is_current flag for all."""
        repo = PersonProfessionRepository(mock_session)
        person_id = uuid.uuid4()
        professions = [
            PersonProfession(
                id=uuid.uuid4(),
                person_id=person_id,
                profession_id=uuid.uuid4(),
                start_date=date(2020, 1, 1),
                is_current=True,
            ),
            PersonProfession(
                id=uuid.uuid4(),
                person_id=person_id,
                profession_id=uuid.uuid4(),
                start_date=date(2018, 1, 1),
                is_current=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = professions

        repo.clear_current_professions(person_id)

        # Verify all professions had is_current set to False
        for prof in professions:
            assert prof.is_current is False
        # Verify session.add was called for each profession
        assert mock_session.add.call_count == 2
        mock_session.commit.assert_called_once()

    def test_clear_current_professions_handles_no_professions(
        self, mock_session: MagicMock
    ) -> None:
        """Test clear_current_professions handles case with no professions."""
        repo = PersonProfessionRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.clear_current_professions(uuid.uuid4())

        mock_session.add.assert_not_called()
        mock_session.commit.assert_called_once()
