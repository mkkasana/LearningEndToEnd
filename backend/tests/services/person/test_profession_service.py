"""Unit tests for ProfessionService.

Tests cover:
- Profession retrieval (all active)
- Profession retrieval by ID
- Profession CRUD operations
- Name existence check

Requirements: 2.7, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.person.profession import Profession
from app.schemas.person import ProfessionCreate, ProfessionUpdate
from app.services.person.profession_service import ProfessionService


@pytest.mark.unit
class TestProfessionServiceQueries:
    """Tests for profession query operations."""

    def test_get_professions_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting all professions returns a list."""
        # Arrange
        mock_professions = [
            Profession(id=uuid.uuid4(), name="Engineer", description="Engineering", weight=1, is_active=True),
            Profession(id=uuid.uuid4(), name="Doctor", description="Medical", weight=2, is_active=True),
        ]

        service = ProfessionService(mock_session)
        with patch.object(service.profession_repo, "get_active_professions", return_value=mock_professions):
            # Act
            result = service.get_professions()

            # Assert
            assert len(result) == 2
            assert result[0].professionName == "Engineer"
            assert result[1].professionName == "Doctor"

    def test_get_professions_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test getting professions returns empty list when none exist."""
        # Arrange
        service = ProfessionService(mock_session)
        with patch.object(service.profession_repo, "get_active_professions", return_value=[]):
            # Act
            result = service.get_professions()

            # Assert
            assert len(result) == 0

    def test_get_profession_by_id_returns_profession(self, mock_session: MagicMock) -> None:
        """Test getting profession by ID returns the profession."""
        # Arrange
        profession_id = uuid.uuid4()
        mock_profession = Profession(id=profession_id, name="Engineer", description="Engineering", weight=1, is_active=True)

        service = ProfessionService(mock_session)
        with patch.object(service.profession_repo, "get_by_id", return_value=mock_profession):
            # Act
            result = service.get_profession_by_id(profession_id)

            # Assert
            assert result is not None
            assert result.id == profession_id
            assert result.name == "Engineer"

    def test_get_profession_by_id_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting nonexistent profession returns None."""
        # Arrange
        service = ProfessionService(mock_session)
        with patch.object(service.profession_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_profession_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestProfessionServiceCreate:
    """Tests for profession creation."""

    def test_create_profession_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating profession with valid data."""
        # Arrange
        profession_create = ProfessionCreate(name="New Profession", description="Description", weight=1, is_active=True)

        service = ProfessionService(mock_session)

        def return_profession(profession: Profession) -> Profession:
            profession.id = uuid.uuid4()
            return profession

        with patch.object(service.profession_repo, "create", side_effect=return_profession):
            # Act
            result = service.create_profession(profession_create)

            # Assert
            assert result.name == "New Profession"
            assert result.description == "Description"


@pytest.mark.unit
class TestProfessionServiceUpdate:
    """Tests for profession update operations."""

    def test_update_profession_name(self, mock_session: MagicMock) -> None:
        """Test updating profession name."""
        # Arrange
        mock_profession = Profession(id=uuid.uuid4(), name="Old Name", description="Desc", weight=1, is_active=True)
        profession_update = ProfessionUpdate(name="New Name")

        service = ProfessionService(mock_session)

        def return_profession(profession: Profession) -> Profession:
            return profession

        with patch.object(service.profession_repo, "update", side_effect=return_profession):
            # Act
            result = service.update_profession(mock_profession, profession_update)

            # Assert
            assert result.name == "New Name"

    def test_update_profession_description(self, mock_session: MagicMock) -> None:
        """Test updating profession description."""
        # Arrange
        mock_profession = Profession(id=uuid.uuid4(), name="Name", description="Old Desc", weight=1, is_active=True)
        profession_update = ProfessionUpdate(description="New Desc")

        service = ProfessionService(mock_session)

        def return_profession(profession: Profession) -> Profession:
            return profession

        with patch.object(service.profession_repo, "update", side_effect=return_profession):
            # Act
            result = service.update_profession(mock_profession, profession_update)

            # Assert
            assert result.description == "New Desc"


@pytest.mark.unit
class TestProfessionServiceDelete:
    """Tests for profession deletion."""

    def test_delete_profession_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_profession = Profession(id=uuid.uuid4(), name="To Delete", description="Desc", weight=1, is_active=True)

        service = ProfessionService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.profession_repo, "delete", mock_delete):
            # Act
            service.delete_profession(mock_profession)

            # Assert
            mock_delete.assert_called_once_with(mock_profession)


@pytest.mark.unit
class TestProfessionServiceValidation:
    """Tests for profession validation."""

    def test_name_exists_returns_true_for_existing_name(self, mock_session: MagicMock) -> None:
        """Test name_exists returns True for existing name."""
        # Arrange
        service = ProfessionService(mock_session)
        with patch.object(service.profession_repo, "name_exists", return_value=True):
            # Act
            result = service.name_exists("Engineer")

            # Assert
            assert result is True

    def test_name_exists_returns_false_for_nonexistent_name(self, mock_session: MagicMock) -> None:
        """Test name_exists returns False for nonexistent name."""
        # Arrange
        service = ProfessionService(mock_session)
        with patch.object(service.profession_repo, "name_exists", return_value=False):
            # Act
            result = service.name_exists("Unknown")

            # Assert
            assert result is False

    def test_name_exists_with_exclude_id(self, mock_session: MagicMock) -> None:
        """Test name_exists with exclude_profession_id parameter."""
        # Arrange
        profession_id = uuid.uuid4()
        service = ProfessionService(mock_session)
        with patch.object(service.profession_repo, "name_exists", return_value=False):
            # Act
            result = service.name_exists("Engineer", exclude_profession_id=profession_id)

            # Assert
            assert result is False
