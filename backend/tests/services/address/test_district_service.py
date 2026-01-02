"""Unit tests for DistrictService.

Tests cover:
- District retrieval by state
- District retrieval by ID
- District CRUD operations
- Code validation

Requirements: 2.16, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.address import District
from app.schemas.address.district import DistrictCreate, DistrictUpdate
from app.services.address.district_service import DistrictService


@pytest.mark.unit
class TestDistrictServiceQueries:
    """Tests for district query operations."""

    def test_get_districts_by_state_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting districts by state returns a list."""
        # Arrange
        state_id = uuid.uuid4()
        mock_districts = [
            District(id=uuid.uuid4(), name="Mumbai", code="MUM", state_id=state_id, is_active=True),
            District(id=uuid.uuid4(), name="Pune", code="PUN", state_id=state_id, is_active=True),
        ]

        service = DistrictService(mock_session)
        with patch.object(service.district_repo, "get_by_state", return_value=mock_districts):
            # Act
            result = service.get_districts_by_state(state_id)

            # Assert
            assert len(result) == 2
            assert result[0].districtName == "Mumbai"
            assert result[1].districtName == "Pune"

    def test_get_districts_by_state_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test getting districts for state with no districts returns empty list."""
        # Arrange
        state_id = uuid.uuid4()
        service = DistrictService(mock_session)
        with patch.object(service.district_repo, "get_by_state", return_value=[]):
            # Act
            result = service.get_districts_by_state(state_id)

            # Assert
            assert len(result) == 0

    def test_get_district_by_id_returns_district(self, mock_session: MagicMock) -> None:
        """Test getting district by ID returns the district."""
        # Arrange
        district_id = uuid.uuid4()
        mock_district = District(id=district_id, name="Mumbai", code="MUM", state_id=uuid.uuid4(), is_active=True)

        service = DistrictService(mock_session)
        with patch.object(service.district_repo, "get_by_id", return_value=mock_district):
            # Act
            result = service.get_district_by_id(district_id)

            # Assert
            assert result is not None
            assert result.id == district_id
            assert result.name == "Mumbai"

    def test_get_district_by_id_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting nonexistent district returns None."""
        # Arrange
        service = DistrictService(mock_session)
        with patch.object(service.district_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_district_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestDistrictServiceCreate:
    """Tests for district creation."""

    def test_create_district_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating district with valid data."""
        # Arrange
        state_id = uuid.uuid4()
        district_create = DistrictCreate(name="New District", code="nd", state_id=state_id, is_active=True)

        service = DistrictService(mock_session)

        def return_district(district: District) -> District:
            return district

        with patch.object(service.district_repo, "create", side_effect=return_district):
            # Act
            result = service.create_district(district_create)

            # Assert
            assert result.name == "New District"
            assert result.code == "ND"  # Should be uppercase
            assert result.state_id == state_id
            assert result.is_active is True

    def test_create_district_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that district code is uppercased on creation."""
        # Arrange
        district_create = DistrictCreate(name="Test", code="ts", state_id=uuid.uuid4(), is_active=True)

        service = DistrictService(mock_session)

        def return_district(district: District) -> District:
            return district

        with patch.object(service.district_repo, "create", side_effect=return_district):
            # Act
            result = service.create_district(district_create)

            # Assert
            assert result.code == "TS"

    def test_create_district_with_none_code(self, mock_session: MagicMock) -> None:
        """Test creating district with None code."""
        # Arrange
        district_create = DistrictCreate(name="Test", code=None, state_id=uuid.uuid4(), is_active=True)

        service = DistrictService(mock_session)

        def return_district(district: District) -> District:
            return district

        with patch.object(service.district_repo, "create", side_effect=return_district):
            # Act
            result = service.create_district(district_create)

            # Assert
            assert result.code is None


@pytest.mark.unit
class TestDistrictServiceUpdate:
    """Tests for district update operations."""

    def test_update_district_name(self, mock_session: MagicMock) -> None:
        """Test updating district name."""
        # Arrange
        mock_district = District(id=uuid.uuid4(), name="Old Name", code="ON", state_id=uuid.uuid4(), is_active=True)
        district_update = DistrictUpdate(name="New Name")

        service = DistrictService(mock_session)

        def return_district(district: District) -> District:
            return district

        with patch.object(service.district_repo, "update", side_effect=return_district):
            # Act
            result = service.update_district(mock_district, district_update)

            # Assert
            assert result.name == "New Name"

    def test_update_district_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating district code uppercases it."""
        # Arrange
        mock_district = District(id=uuid.uuid4(), name="District", code="OLD", state_id=uuid.uuid4(), is_active=True)
        district_update = DistrictUpdate(code="new")

        service = DistrictService(mock_session)

        def return_district(district: District) -> District:
            return district

        with patch.object(service.district_repo, "update", side_effect=return_district):
            # Act
            result = service.update_district(mock_district, district_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestDistrictServiceDelete:
    """Tests for district deletion."""

    def test_delete_district_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_district = District(id=uuid.uuid4(), name="District to Delete", code="DD", state_id=uuid.uuid4(), is_active=True)

        service = DistrictService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.district_repo, "delete", mock_delete):
            # Act
            service.delete_district(mock_district)

            # Assert
            mock_delete.assert_called_once_with(mock_district)


@pytest.mark.unit
class TestDistrictServiceValidation:
    """Tests for district validation."""

    def test_code_exists_returns_true_for_existing_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        state_id = uuid.uuid4()
        mock_district = District(id=uuid.uuid4(), name="Mumbai", code="MUM", state_id=state_id, is_active=True)

        service = DistrictService(mock_session)
        with patch.object(service.district_repo, "get_by_code", return_value=mock_district):
            # Act
            result = service.code_exists("MUM", state_id)

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = DistrictService(mock_session)
        with patch.object(service.district_repo, "get_by_code", return_value=None):
            # Act
            result = service.code_exists("XX", uuid.uuid4())

            # Assert
            assert result is False

    def test_code_exists_with_exclude_returns_false(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        district_id = uuid.uuid4()
        state_id = uuid.uuid4()
        mock_district = District(id=district_id, name="Mumbai", code="MUM", state_id=state_id, is_active=True)

        service = DistrictService(mock_session)
        with patch.object(service.district_repo, "get_by_code", return_value=mock_district):
            # Act
            result = service.code_exists("MUM", state_id, exclude_district_id=district_id)

            # Assert
            assert result is False

    def test_code_exists_returns_false_for_empty_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for empty code."""
        # Arrange
        service = DistrictService(mock_session)

        # Act
        result = service.code_exists("", uuid.uuid4())

        # Assert
        assert result is False
