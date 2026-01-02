"""Unit tests for LocalityService.

Tests cover:
- Locality retrieval by sub-district
- Locality retrieval by ID
- Locality CRUD operations
- Code validation

Requirements: 2.16, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.address import Locality
from app.schemas.address.locality import LocalityCreate, LocalityUpdate
from app.services.address.locality_service import LocalityService


@pytest.mark.unit
class TestLocalityServiceQueries:
    """Tests for locality query operations."""

    def test_get_localities_by_sub_district_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting localities by sub-district returns a list."""
        # Arrange
        sub_district_id = uuid.uuid4()
        mock_localities = [
            Locality(id=uuid.uuid4(), name="Versova", code="VER", sub_district_id=sub_district_id, is_active=True),
            Locality(id=uuid.uuid4(), name="Lokhandwala", code="LOK", sub_district_id=sub_district_id, is_active=True),
        ]

        service = LocalityService(mock_session)
        with patch.object(service.locality_repo, "get_by_sub_district", return_value=mock_localities):
            # Act
            result = service.get_localities_by_sub_district(sub_district_id)

            # Assert
            assert len(result) == 2
            assert result[0].localityName == "Versova"
            assert result[1].localityName == "Lokhandwala"

    def test_get_localities_by_sub_district_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test getting localities for sub-district with no localities returns empty list."""
        # Arrange
        sub_district_id = uuid.uuid4()
        service = LocalityService(mock_session)
        with patch.object(service.locality_repo, "get_by_sub_district", return_value=[]):
            # Act
            result = service.get_localities_by_sub_district(sub_district_id)

            # Assert
            assert len(result) == 0

    def test_get_locality_by_id_returns_locality(self, mock_session: MagicMock) -> None:
        """Test getting locality by ID returns the locality."""
        # Arrange
        locality_id = uuid.uuid4()
        mock_locality = Locality(id=locality_id, name="Versova", code="VER", sub_district_id=uuid.uuid4(), is_active=True)

        service = LocalityService(mock_session)
        with patch.object(service.locality_repo, "get_by_id", return_value=mock_locality):
            # Act
            result = service.get_locality_by_id(locality_id)

            # Assert
            assert result is not None
            assert result.id == locality_id
            assert result.name == "Versova"

    def test_get_locality_by_id_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting nonexistent locality returns None."""
        # Arrange
        service = LocalityService(mock_session)
        with patch.object(service.locality_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_locality_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestLocalityServiceCreate:
    """Tests for locality creation."""

    def test_create_locality_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating locality with valid data."""
        # Arrange
        sub_district_id = uuid.uuid4()
        locality_create = LocalityCreate(name="New Locality", code="nl", sub_district_id=sub_district_id, is_active=True)

        service = LocalityService(mock_session)

        def return_locality(locality: Locality) -> Locality:
            return locality

        with patch.object(service.locality_repo, "create", side_effect=return_locality):
            # Act
            result = service.create_locality(locality_create)

            # Assert
            assert result.name == "New Locality"
            assert result.code == "NL"  # Should be uppercase
            assert result.sub_district_id == sub_district_id
            assert result.is_active is True

    def test_create_locality_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that locality code is uppercased on creation."""
        # Arrange
        locality_create = LocalityCreate(name="Test", code="ts", sub_district_id=uuid.uuid4(), is_active=True)

        service = LocalityService(mock_session)

        def return_locality(locality: Locality) -> Locality:
            return locality

        with patch.object(service.locality_repo, "create", side_effect=return_locality):
            # Act
            result = service.create_locality(locality_create)

            # Assert
            assert result.code == "TS"

    def test_create_locality_with_none_code(self, mock_session: MagicMock) -> None:
        """Test creating locality with None code."""
        # Arrange
        locality_create = LocalityCreate(name="Test", code=None, sub_district_id=uuid.uuid4(), is_active=True)

        service = LocalityService(mock_session)

        def return_locality(locality: Locality) -> Locality:
            return locality

        with patch.object(service.locality_repo, "create", side_effect=return_locality):
            # Act
            result = service.create_locality(locality_create)

            # Assert
            assert result.code is None


@pytest.mark.unit
class TestLocalityServiceUpdate:
    """Tests for locality update operations."""

    def test_update_locality_name(self, mock_session: MagicMock) -> None:
        """Test updating locality name."""
        # Arrange
        mock_locality = Locality(id=uuid.uuid4(), name="Old Name", code="ON", sub_district_id=uuid.uuid4(), is_active=True)
        locality_update = LocalityUpdate(name="New Name")

        service = LocalityService(mock_session)

        def return_locality(locality: Locality) -> Locality:
            return locality

        with patch.object(service.locality_repo, "update", side_effect=return_locality):
            # Act
            result = service.update_locality(mock_locality, locality_update)

            # Assert
            assert result.name == "New Name"

    def test_update_locality_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating locality code uppercases it."""
        # Arrange
        mock_locality = Locality(id=uuid.uuid4(), name="Locality", code="OLD", sub_district_id=uuid.uuid4(), is_active=True)
        locality_update = LocalityUpdate(code="new")

        service = LocalityService(mock_session)

        def return_locality(locality: Locality) -> Locality:
            return locality

        with patch.object(service.locality_repo, "update", side_effect=return_locality):
            # Act
            result = service.update_locality(mock_locality, locality_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestLocalityServiceDelete:
    """Tests for locality deletion."""

    def test_delete_locality_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_locality = Locality(id=uuid.uuid4(), name="Locality to Delete", code="LD", sub_district_id=uuid.uuid4(), is_active=True)

        service = LocalityService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.locality_repo, "delete", mock_delete):
            # Act
            service.delete_locality(mock_locality)

            # Assert
            mock_delete.assert_called_once_with(mock_locality)


@pytest.mark.unit
class TestLocalityServiceValidation:
    """Tests for locality validation."""

    def test_code_exists_returns_true_for_existing_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        sub_district_id = uuid.uuid4()
        mock_locality = Locality(id=uuid.uuid4(), name="Versova", code="VER", sub_district_id=sub_district_id, is_active=True)

        service = LocalityService(mock_session)
        with patch.object(service.locality_repo, "get_by_code", return_value=mock_locality):
            # Act
            result = service.code_exists("VER", sub_district_id)

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = LocalityService(mock_session)
        with patch.object(service.locality_repo, "get_by_code", return_value=None):
            # Act
            result = service.code_exists("XX", uuid.uuid4())

            # Assert
            assert result is False

    def test_code_exists_with_exclude_returns_false(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        locality_id = uuid.uuid4()
        sub_district_id = uuid.uuid4()
        mock_locality = Locality(id=locality_id, name="Versova", code="VER", sub_district_id=sub_district_id, is_active=True)

        service = LocalityService(mock_session)
        with patch.object(service.locality_repo, "get_by_code", return_value=mock_locality):
            # Act
            result = service.code_exists("VER", sub_district_id, exclude_locality_id=locality_id)

            # Assert
            assert result is False

    def test_code_exists_returns_false_for_empty_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for empty code."""
        # Arrange
        service = LocalityService(mock_session)

        # Act
        result = service.code_exists("", uuid.uuid4())

        # Assert
        assert result is False
