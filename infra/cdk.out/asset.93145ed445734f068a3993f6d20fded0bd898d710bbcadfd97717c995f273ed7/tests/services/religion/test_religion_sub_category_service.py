"""Unit tests for ReligionSubCategoryService.

Tests cover:
- Religion sub-category retrieval by category
- Religion sub-category retrieval by ID
- Religion sub-category CRUD operations
- Code validation

Requirements: 2.17, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.schemas.religion import ReligionSubCategoryCreate, ReligionSubCategoryUpdate
from app.services.religion.religion_sub_category_service import ReligionSubCategoryService


@pytest.mark.unit
class TestReligionSubCategoryServiceQueries:
    """Tests for religion sub-category query operations."""

    def test_get_sub_categories_by_category_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting sub-categories by category returns a list."""
        # Arrange
        category_id = uuid.uuid4()
        mock_sub_categories = [
            ReligionSubCategory(id=uuid.uuid4(), name="Lingayat", code="LIN", category_id=category_id, is_active=True),
            ReligionSubCategory(id=uuid.uuid4(), name="Nath", code="NAT", category_id=category_id, is_active=True),
        ]

        service = ReligionSubCategoryService(mock_session)
        with patch.object(service.sub_category_repo, "get_sub_categories_by_category", return_value=mock_sub_categories):
            # Act
            result = service.get_sub_categories_by_category(category_id)

            # Assert
            assert len(result) == 2
            assert result[0].subCategoryName == "Lingayat"
            assert result[1].subCategoryName == "Nath"

    def test_get_sub_categories_by_category_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test getting sub-categories for category with no sub-categories returns empty list."""
        # Arrange
        category_id = uuid.uuid4()
        service = ReligionSubCategoryService(mock_session)
        with patch.object(service.sub_category_repo, "get_sub_categories_by_category", return_value=[]):
            # Act
            result = service.get_sub_categories_by_category(category_id)

            # Assert
            assert len(result) == 0

    def test_get_sub_category_by_id_returns_sub_category(self, mock_session: MagicMock) -> None:
        """Test getting sub-category by ID returns the sub-category."""
        # Arrange
        sub_category_id = uuid.uuid4()
        mock_sub_category = ReligionSubCategory(id=sub_category_id, name="Lingayat", code="LIN", category_id=uuid.uuid4(), is_active=True)

        service = ReligionSubCategoryService(mock_session)
        with patch.object(service.sub_category_repo, "get_by_id", return_value=mock_sub_category):
            # Act
            result = service.get_sub_category_by_id(sub_category_id)

            # Assert
            assert result is not None
            assert result.id == sub_category_id
            assert result.name == "Lingayat"

    def test_get_sub_category_by_id_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting nonexistent sub-category returns None."""
        # Arrange
        service = ReligionSubCategoryService(mock_session)
        with patch.object(service.sub_category_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_sub_category_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestReligionSubCategoryServiceCreate:
    """Tests for religion sub-category creation."""

    def test_create_sub_category_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating sub-category with valid data."""
        # Arrange
        category_id = uuid.uuid4()
        sub_category_create = ReligionSubCategoryCreate(name="New SubCategory", code="nsc", category_id=category_id, is_active=True)

        service = ReligionSubCategoryService(mock_session)

        def return_sub_category(sub_category: ReligionSubCategory) -> ReligionSubCategory:
            return sub_category

        with patch.object(service.sub_category_repo, "create", side_effect=return_sub_category):
            # Act
            result = service.create_sub_category(sub_category_create)

            # Assert
            assert result.name == "New SubCategory"
            assert result.code == "NSC"  # Should be uppercase
            assert result.category_id == category_id
            assert result.is_active is True

    def test_create_sub_category_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that sub-category code is uppercased on creation."""
        # Arrange
        sub_category_create = ReligionSubCategoryCreate(name="Test", code="ts", category_id=uuid.uuid4(), is_active=True)

        service = ReligionSubCategoryService(mock_session)

        def return_sub_category(sub_category: ReligionSubCategory) -> ReligionSubCategory:
            return sub_category

        with patch.object(service.sub_category_repo, "create", side_effect=return_sub_category):
            # Act
            result = service.create_sub_category(sub_category_create)

            # Assert
            assert result.code == "TS"

    def test_create_sub_category_with_none_code(self, mock_session: MagicMock) -> None:
        """Test creating sub-category with None code."""
        # Arrange
        sub_category_create = ReligionSubCategoryCreate(name="Test", code=None, category_id=uuid.uuid4(), is_active=True)

        service = ReligionSubCategoryService(mock_session)

        def return_sub_category(sub_category: ReligionSubCategory) -> ReligionSubCategory:
            return sub_category

        with patch.object(service.sub_category_repo, "create", side_effect=return_sub_category):
            # Act
            result = service.create_sub_category(sub_category_create)

            # Assert
            assert result.code is None


@pytest.mark.unit
class TestReligionSubCategoryServiceUpdate:
    """Tests for religion sub-category update operations."""

    def test_update_sub_category_name(self, mock_session: MagicMock) -> None:
        """Test updating sub-category name."""
        # Arrange
        mock_sub_category = ReligionSubCategory(id=uuid.uuid4(), name="Old Name", code="ON", category_id=uuid.uuid4(), is_active=True)
        sub_category_update = ReligionSubCategoryUpdate(name="New Name")

        service = ReligionSubCategoryService(mock_session)

        def return_sub_category(sub_category: ReligionSubCategory) -> ReligionSubCategory:
            return sub_category

        with patch.object(service.sub_category_repo, "update", side_effect=return_sub_category):
            # Act
            result = service.update_sub_category(mock_sub_category, sub_category_update)

            # Assert
            assert result.name == "New Name"

    def test_update_sub_category_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating sub-category code uppercases it."""
        # Arrange
        mock_sub_category = ReligionSubCategory(id=uuid.uuid4(), name="SubCategory", code="OLD", category_id=uuid.uuid4(), is_active=True)
        sub_category_update = ReligionSubCategoryUpdate(code="new")

        service = ReligionSubCategoryService(mock_session)

        def return_sub_category(sub_category: ReligionSubCategory) -> ReligionSubCategory:
            return sub_category

        with patch.object(service.sub_category_repo, "update", side_effect=return_sub_category):
            # Act
            result = service.update_sub_category(mock_sub_category, sub_category_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestReligionSubCategoryServiceDelete:
    """Tests for religion sub-category deletion."""

    def test_delete_sub_category_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_sub_category = ReligionSubCategory(id=uuid.uuid4(), name="SubCategory to Delete", code="SD", category_id=uuid.uuid4(), is_active=True)

        service = ReligionSubCategoryService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.sub_category_repo, "delete", mock_delete):
            # Act
            service.delete_sub_category(mock_sub_category)

            # Assert
            mock_delete.assert_called_once_with(mock_sub_category)


@pytest.mark.unit
class TestReligionSubCategoryServiceValidation:
    """Tests for religion sub-category validation."""

    def test_code_exists_returns_true_for_existing_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        category_id = uuid.uuid4()
        service = ReligionSubCategoryService(mock_session)
        with patch.object(service.sub_category_repo, "code_exists", return_value=True):
            # Act
            result = service.code_exists("LIN", category_id)

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = ReligionSubCategoryService(mock_session)
        with patch.object(service.sub_category_repo, "code_exists", return_value=False):
            # Act
            result = service.code_exists("XX", uuid.uuid4())

            # Assert
            assert result is False

    def test_code_exists_with_exclude_returns_false(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        sub_category_id = uuid.uuid4()
        category_id = uuid.uuid4()
        service = ReligionSubCategoryService(mock_session)
        with patch.object(service.sub_category_repo, "code_exists", return_value=False):
            # Act
            result = service.code_exists("LIN", category_id, exclude_sub_category_id=sub_category_id)

            # Assert
            assert result is False
