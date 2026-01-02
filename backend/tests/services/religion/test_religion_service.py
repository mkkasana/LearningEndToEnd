"""Unit tests for ReligionService.

Tests cover:
- Religion retrieval
- Religion CRUD operations
- Code validation

Requirements: 2.17, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.religion.religion import Religion
from app.schemas.religion import ReligionCreate, ReligionUpdate
from app.services.religion.religion_service import ReligionService


@pytest.mark.unit
class TestReligionServiceQueries:
    """Tests for religion query operations."""

    def test_get_religions_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting all religions returns a list."""
        # Arrange
        mock_religions = [
            Religion(id=uuid.uuid4(), name="Hinduism", code="HIN", is_active=True),
            Religion(id=uuid.uuid4(), name="Christianity", code="CHR", is_active=True),
        ]

        service = ReligionService(mock_session)
        with patch.object(
            service.religion_repo, "get_active_religions", return_value=mock_religions
        ):
            # Act
            result = service.get_religions()

            # Assert
            assert len(result) == 2
            assert result[0].religionName == "Hinduism"
            assert result[1].religionName == "Christianity"

    def test_get_religion_by_id_returns_religion(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting religion by ID returns the religion."""
        # Arrange
        religion_id = uuid.uuid4()
        mock_religion = Religion(
            id=religion_id, name="Hinduism", code="HIN", is_active=True
        )

        service = ReligionService(mock_session)
        with patch.object(
            service.religion_repo, "get_by_id", return_value=mock_religion
        ):
            # Act
            result = service.get_religion_by_id(religion_id)

            # Assert
            assert result is not None
            assert result.id == religion_id
            assert result.name == "Hinduism"

    def test_get_religion_by_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent religion returns None."""
        # Arrange
        service = ReligionService(mock_session)
        with patch.object(service.religion_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_religion_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestReligionServiceCreate:
    """Tests for religion creation."""

    def test_create_religion_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating religion with valid data."""
        # Arrange
        religion_create = ReligionCreate(
            name="New Religion", code="nr", is_active=True
        )

        service = ReligionService(mock_session)

        def return_religion(religion: Religion) -> Religion:
            return religion

        with patch.object(
            service.religion_repo, "create", side_effect=return_religion
        ):
            # Act
            result = service.create_religion(religion_create)

            # Assert
            assert result.name == "New Religion"
            assert result.code == "NR"  # Should be uppercase
            assert result.is_active is True

    def test_create_religion_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that religion code is uppercased on creation."""
        # Arrange
        religion_create = ReligionCreate(name="Test", code="test", is_active=True)

        service = ReligionService(mock_session)

        def return_religion(religion: Religion) -> Religion:
            return religion

        with patch.object(
            service.religion_repo, "create", side_effect=return_religion
        ):
            # Act
            result = service.create_religion(religion_create)

            # Assert
            assert result.code == "TEST"


@pytest.mark.unit
class TestReligionServiceUpdate:
    """Tests for religion update operations."""

    def test_update_religion_name(self, mock_session: MagicMock) -> None:
        """Test updating religion name."""
        # Arrange
        mock_religion = Religion(
            id=uuid.uuid4(), name="Old Name", code="ON", is_active=True
        )
        religion_update = ReligionUpdate(name="New Name")

        service = ReligionService(mock_session)

        def return_religion(religion: Religion) -> Religion:
            return religion

        with patch.object(
            service.religion_repo, "update", side_effect=return_religion
        ):
            # Act
            result = service.update_religion(mock_religion, religion_update)

            # Assert
            assert result.name == "New Name"

    def test_update_religion_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating religion code uppercases it."""
        # Arrange
        mock_religion = Religion(
            id=uuid.uuid4(), name="Religion", code="OLD", is_active=True
        )
        religion_update = ReligionUpdate(code="new")

        service = ReligionService(mock_session)

        def return_religion(religion: Religion) -> Religion:
            return religion

        with patch.object(
            service.religion_repo, "update", side_effect=return_religion
        ):
            # Act
            result = service.update_religion(mock_religion, religion_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestReligionServiceDelete:
    """Tests for religion deletion."""

    def test_delete_religion_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_religion = Religion(
            id=uuid.uuid4(), name="Religion to Delete", code="RD", is_active=True
        )

        service = ReligionService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.religion_repo, "delete", mock_delete):
            # Act
            service.delete_religion(mock_religion)

            # Assert
            mock_delete.assert_called_once_with(mock_religion)


@pytest.mark.unit
class TestReligionServiceValidation:
    """Tests for religion validation."""

    def test_code_exists_returns_true_for_existing_code(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        service = ReligionService(mock_session)
        with patch.object(service.religion_repo, "code_exists", return_value=True):
            # Act
            result = service.code_exists("HIN")

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(
        self, mock_session: MagicMock
    ) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = ReligionService(mock_session)
        with patch.object(service.religion_repo, "code_exists", return_value=False):
            # Act
            result = service.code_exists("XXX")

            # Assert
            assert result is False
