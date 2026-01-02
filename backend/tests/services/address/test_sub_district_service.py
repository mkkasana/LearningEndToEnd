"""Unit tests for SubDistrictService.

Tests cover:
- Sub-district retrieval by district
- Sub-district retrieval by ID
- Sub-district CRUD operations
- Code validation

Requirements: 2.16, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.address import SubDistrict
from app.schemas.address.sub_district import SubDistrictCreate, SubDistrictUpdate
from app.services.address.sub_district_service import SubDistrictService


@pytest.mark.unit
class TestSubDistrictServiceQueries:
    """Tests for sub-district query operations."""

    def test_get_sub_districts_by_district_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting sub-districts by district returns a list."""
        # Arrange
        district_id = uuid.uuid4()
        mock_sub_districts = [
            SubDistrict(id=uuid.uuid4(), name="Andheri", code="AND", district_id=district_id, is_active=True),
            SubDistrict(id=uuid.uuid4(), name="Bandra", code="BAN", district_id=district_id, is_active=True),
        ]

        service = SubDistrictService(mock_session)
        with patch.object(service.sub_district_repo, "get_by_district", return_value=mock_sub_districts):
            # Act
            result = service.get_sub_districts_by_district(district_id)

            # Assert
            assert len(result) == 2
            assert result[0].tehsilName == "Andheri"
            assert result[1].tehsilName == "Bandra"

    def test_get_sub_districts_by_district_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test getting sub-districts for district with no sub-districts returns empty list."""
        # Arrange
        district_id = uuid.uuid4()
        service = SubDistrictService(mock_session)
        with patch.object(service.sub_district_repo, "get_by_district", return_value=[]):
            # Act
            result = service.get_sub_districts_by_district(district_id)

            # Assert
            assert len(result) == 0

    def test_get_sub_district_by_id_returns_sub_district(self, mock_session: MagicMock) -> None:
        """Test getting sub-district by ID returns the sub-district."""
        # Arrange
        sub_district_id = uuid.uuid4()
        mock_sub_district = SubDistrict(id=sub_district_id, name="Andheri", code="AND", district_id=uuid.uuid4(), is_active=True)

        service = SubDistrictService(mock_session)
        with patch.object(service.sub_district_repo, "get_by_id", return_value=mock_sub_district):
            # Act
            result = service.get_sub_district_by_id(sub_district_id)

            # Assert
            assert result is not None
            assert result.id == sub_district_id
            assert result.name == "Andheri"

    def test_get_sub_district_by_id_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting nonexistent sub-district returns None."""
        # Arrange
        service = SubDistrictService(mock_session)
        with patch.object(service.sub_district_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_sub_district_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestSubDistrictServiceCreate:
    """Tests for sub-district creation."""

    def test_create_sub_district_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating sub-district with valid data."""
        # Arrange
        district_id = uuid.uuid4()
        sub_district_create = SubDistrictCreate(name="New SubDistrict", code="nsd", district_id=district_id, is_active=True)

        service = SubDistrictService(mock_session)

        def return_sub_district(sub_district: SubDistrict) -> SubDistrict:
            return sub_district

        with patch.object(service.sub_district_repo, "create", side_effect=return_sub_district):
            # Act
            result = service.create_sub_district(sub_district_create)

            # Assert
            assert result.name == "New SubDistrict"
            assert result.code == "NSD"  # Should be uppercase
            assert result.district_id == district_id
            assert result.is_active is True

    def test_create_sub_district_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that sub-district code is uppercased on creation."""
        # Arrange
        sub_district_create = SubDistrictCreate(name="Test", code="ts", district_id=uuid.uuid4(), is_active=True)

        service = SubDistrictService(mock_session)

        def return_sub_district(sub_district: SubDistrict) -> SubDistrict:
            return sub_district

        with patch.object(service.sub_district_repo, "create", side_effect=return_sub_district):
            # Act
            result = service.create_sub_district(sub_district_create)

            # Assert
            assert result.code == "TS"

    def test_create_sub_district_with_none_code(self, mock_session: MagicMock) -> None:
        """Test creating sub-district with None code."""
        # Arrange
        sub_district_create = SubDistrictCreate(name="Test", code=None, district_id=uuid.uuid4(), is_active=True)

        service = SubDistrictService(mock_session)

        def return_sub_district(sub_district: SubDistrict) -> SubDistrict:
            return sub_district

        with patch.object(service.sub_district_repo, "create", side_effect=return_sub_district):
            # Act
            result = service.create_sub_district(sub_district_create)

            # Assert
            assert result.code is None


@pytest.mark.unit
class TestSubDistrictServiceUpdate:
    """Tests for sub-district update operations."""

    def test_update_sub_district_name(self, mock_session: MagicMock) -> None:
        """Test updating sub-district name."""
        # Arrange
        mock_sub_district = SubDistrict(id=uuid.uuid4(), name="Old Name", code="ON", district_id=uuid.uuid4(), is_active=True)
        sub_district_update = SubDistrictUpdate(name="New Name")

        service = SubDistrictService(mock_session)

        def return_sub_district(sub_district: SubDistrict) -> SubDistrict:
            return sub_district

        with patch.object(service.sub_district_repo, "update", side_effect=return_sub_district):
            # Act
            result = service.update_sub_district(mock_sub_district, sub_district_update)

            # Assert
            assert result.name == "New Name"

    def test_update_sub_district_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating sub-district code uppercases it."""
        # Arrange
        mock_sub_district = SubDistrict(id=uuid.uuid4(), name="SubDistrict", code="OLD", district_id=uuid.uuid4(), is_active=True)
        sub_district_update = SubDistrictUpdate(code="new")

        service = SubDistrictService(mock_session)

        def return_sub_district(sub_district: SubDistrict) -> SubDistrict:
            return sub_district

        with patch.object(service.sub_district_repo, "update", side_effect=return_sub_district):
            # Act
            result = service.update_sub_district(mock_sub_district, sub_district_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestSubDistrictServiceDelete:
    """Tests for sub-district deletion."""

    def test_delete_sub_district_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_sub_district = SubDistrict(id=uuid.uuid4(), name="SubDistrict to Delete", code="SD", district_id=uuid.uuid4(), is_active=True)

        service = SubDistrictService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.sub_district_repo, "delete", mock_delete):
            # Act
            service.delete_sub_district(mock_sub_district)

            # Assert
            mock_delete.assert_called_once_with(mock_sub_district)


@pytest.mark.unit
class TestSubDistrictServiceValidation:
    """Tests for sub-district validation."""

    def test_code_exists_returns_true_for_existing_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        district_id = uuid.uuid4()
        mock_sub_district = SubDistrict(id=uuid.uuid4(), name="Andheri", code="AND", district_id=district_id, is_active=True)

        service = SubDistrictService(mock_session)
        with patch.object(service.sub_district_repo, "get_by_code", return_value=mock_sub_district):
            # Act
            result = service.code_exists("AND", district_id)

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = SubDistrictService(mock_session)
        with patch.object(service.sub_district_repo, "get_by_code", return_value=None):
            # Act
            result = service.code_exists("XX", uuid.uuid4())

            # Assert
            assert result is False

    def test_code_exists_with_exclude_returns_false(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        sub_district_id = uuid.uuid4()
        district_id = uuid.uuid4()
        mock_sub_district = SubDistrict(id=sub_district_id, name="Andheri", code="AND", district_id=district_id, is_active=True)

        service = SubDistrictService(mock_session)
        with patch.object(service.sub_district_repo, "get_by_code", return_value=mock_sub_district):
            # Act
            result = service.code_exists("AND", district_id, exclude_sub_district_id=sub_district_id)

            # Assert
            assert result is False

    def test_code_exists_returns_false_for_empty_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for empty code."""
        # Arrange
        service = SubDistrictService(mock_session)

        # Act
        result = service.code_exists("", uuid.uuid4())

        # Assert
        assert result is False
