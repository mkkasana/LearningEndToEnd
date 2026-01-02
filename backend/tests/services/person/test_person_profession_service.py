"""Unit tests for PersonProfessionService.

Tests cover:
- Profession queries (by person, by id)
- Profession creation with is_current handling
- Profession updates
- Profession deletion

Requirements: 2.7, 2.18
"""

import uuid
from datetime import date, datetime
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.person.person_profession import PersonProfession
from app.schemas.person.person_profession import (
    PersonProfessionCreate,
    PersonProfessionUpdate,
)
from app.services.person.person_profession_service import PersonProfessionService


@pytest.mark.unit
class TestPersonProfessionServiceQueries:
    """Tests for profession query operations."""

    def test_get_professions_by_person_returns_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting professions by person ID returns a list."""
        # Arrange
        person_id = uuid.uuid4()
        mock_professions = [
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

        service = PersonProfessionService(mock_session)
        with patch.object(
            service.profession_repo, "get_by_person_id", return_value=mock_professions
        ):
            # Act
            result = service.get_professions_by_person(person_id)

            # Assert
            assert len(result) == 2
            assert all(p.person_id == person_id for p in result)

    def test_get_professions_by_person_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting professions for person without professions returns empty list."""
        # Arrange
        service = PersonProfessionService(mock_session)
        with patch.object(
            service.profession_repo, "get_by_person_id", return_value=[]
        ):
            # Act
            result = service.get_professions_by_person(uuid.uuid4())

            # Assert
            assert result == []

    def test_get_profession_by_id_returns_profession(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting profession by ID returns the profession."""
        # Arrange
        profession_id = uuid.uuid4()
        mock_profession = PersonProfession(
            id=profession_id,
            person_id=uuid.uuid4(),
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )

        service = PersonProfessionService(mock_session)
        with patch.object(
            service.profession_repo, "get_by_id", return_value=mock_profession
        ):
            # Act
            result = service.get_profession_by_id(profession_id)

            # Assert
            assert result is not None
            assert result.id == profession_id

    def test_get_profession_by_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent profession returns None."""
        # Arrange
        service = PersonProfessionService(mock_session)
        with patch.object(service.profession_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_profession_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestPersonProfessionServiceCreate:
    """Tests for profession creation."""

    def test_create_profession_basic(self, mock_session: MagicMock) -> None:
        """Test creating a basic profession."""
        # Arrange
        person_id = uuid.uuid4()
        profession_id = uuid.uuid4()
        profession_create = PersonProfessionCreate(
            profession_id=profession_id,
            start_date=date(2020, 1, 1),
            is_current=False,
        )

        service = PersonProfessionService(mock_session)

        def return_profession(profession: PersonProfession) -> PersonProfession:
            return profession

        with patch.object(
            service.profession_repo, "create", side_effect=return_profession
        ):
            # Act
            result = service.create_profession(person_id, profession_create)

            # Assert
            assert result.person_id == person_id
            assert result.profession_id == profession_id
            assert result.is_current is False

    def test_create_profession_with_is_current_clears_others(
        self, mock_session: MagicMock
    ) -> None:
        """Test creating profession with is_current=True clears other current professions."""
        # Arrange
        person_id = uuid.uuid4()
        profession_create = PersonProfessionCreate(
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )

        service = PersonProfessionService(mock_session)
        mock_clear = MagicMock()

        def return_profession(profession: PersonProfession) -> PersonProfession:
            return profession

        with patch.object(
            service.profession_repo, "clear_current_professions", mock_clear
        ), patch.object(
            service.profession_repo, "create", side_effect=return_profession
        ):
            # Act
            result = service.create_profession(person_id, profession_create)

            # Assert
            mock_clear.assert_called_once_with(person_id)
            assert result.is_current is True

    def test_create_profession_without_is_current_does_not_clear(
        self, mock_session: MagicMock
    ) -> None:
        """Test creating profession with is_current=False does not clear others."""
        # Arrange
        person_id = uuid.uuid4()
        profession_create = PersonProfessionCreate(
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=False,
        )

        service = PersonProfessionService(mock_session)
        mock_clear = MagicMock()

        def return_profession(profession: PersonProfession) -> PersonProfession:
            return profession

        with patch.object(
            service.profession_repo, "clear_current_professions", mock_clear
        ), patch.object(
            service.profession_repo, "create", side_effect=return_profession
        ):
            # Act
            service.create_profession(person_id, profession_create)

            # Assert
            mock_clear.assert_not_called()

    def test_create_profession_with_end_date(self, mock_session: MagicMock) -> None:
        """Test creating profession with end date."""
        # Arrange
        person_id = uuid.uuid4()
        profession_create = PersonProfessionCreate(
            profession_id=uuid.uuid4(),
            start_date=date(2015, 1, 1),
            end_date=date(2019, 12, 31),
            is_current=False,
        )

        service = PersonProfessionService(mock_session)

        def return_profession(profession: PersonProfession) -> PersonProfession:
            return profession

        with patch.object(
            service.profession_repo, "create", side_effect=return_profession
        ):
            # Act
            result = service.create_profession(person_id, profession_create)

            # Assert
            assert result.end_date == date(2019, 12, 31)


@pytest.mark.unit
class TestPersonProfessionServiceUpdate:
    """Tests for profession update operations."""

    def test_update_profession_basic_fields(self, mock_session: MagicMock) -> None:
        """Test updating profession basic fields."""
        # Arrange
        new_end_date = date(2024, 12, 31)
        mock_profession = PersonProfession(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        profession_update = PersonProfessionUpdate(end_date=new_end_date)

        service = PersonProfessionService(mock_session)

        def return_profession(profession: PersonProfession) -> PersonProfession:
            return profession

        with patch.object(
            service.profession_repo, "update", side_effect=return_profession
        ):
            # Act
            result = service.update_profession(mock_profession, profession_update)

            # Assert
            assert result.end_date == new_end_date

    def test_update_profession_to_current_clears_others(
        self, mock_session: MagicMock
    ) -> None:
        """Test updating profession to is_current=True clears other current professions."""
        # Arrange
        mock_profession = PersonProfession(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        profession_update = PersonProfessionUpdate(is_current=True)

        service = PersonProfessionService(mock_session)
        mock_clear = MagicMock()

        def return_profession(profession: PersonProfession) -> PersonProfession:
            return profession

        with patch.object(
            service.profession_repo, "clear_current_professions", mock_clear
        ), patch.object(
            service.profession_repo, "update", side_effect=return_profession
        ):
            # Act
            result = service.update_profession(mock_profession, profession_update)

            # Assert
            mock_clear.assert_called_once_with(mock_profession.person_id)
            assert result.is_current is True

    def test_update_profession_updates_timestamp(self, mock_session: MagicMock) -> None:
        """Test that updating profession updates the timestamp."""
        # Arrange
        old_timestamp = datetime(2020, 1, 1, 0, 0, 0)
        mock_profession = PersonProfession(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
            created_at=old_timestamp,
            updated_at=old_timestamp,
        )
        profession_update = PersonProfessionUpdate(end_date=date(2024, 12, 31))

        service = PersonProfessionService(mock_session)

        def return_profession(profession: PersonProfession) -> PersonProfession:
            return profession

        with patch.object(
            service.profession_repo, "update", side_effect=return_profession
        ):
            # Act
            result = service.update_profession(mock_profession, profession_update)

            # Assert
            assert result.updated_at > old_timestamp


@pytest.mark.unit
class TestPersonProfessionServiceDelete:
    """Tests for profession deletion."""

    def test_delete_profession_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_profession = PersonProfession(
            id=uuid.uuid4(),
            person_id=uuid.uuid4(),
            profession_id=uuid.uuid4(),
            start_date=date(2020, 1, 1),
            is_current=True,
        )

        service = PersonProfessionService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.profession_repo, "delete", mock_delete):
            # Act
            service.delete_profession(mock_profession)

            # Assert
            mock_delete.assert_called_once_with(mock_profession)
