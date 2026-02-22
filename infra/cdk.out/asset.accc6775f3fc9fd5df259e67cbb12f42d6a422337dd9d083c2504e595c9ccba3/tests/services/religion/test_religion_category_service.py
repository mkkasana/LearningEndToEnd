"""Unit tests for ReligionCategoryService.

Tests cover:
- Religion category retrieval by religion
- Religion category retrieval by ID
- Religion category CRUD operations
- Code validation

Requirements: 2.17, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.religion.religion_category import ReligionCategory
from app.schemas.religion import ReligionCategoryCreate, ReligionCategoryUpdate
from app.services.religion.religion_category_service import ReligionCategoryService


@pytest.mark.unit
class TestReligionCategoryServiceQueries:
    """Tests for religion category query operations."""

    def test_get_categories_by_religion_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting categories by religion returns a list."""
        # Arrange
        religion_id = uuid.uuid4()
        mock_categories = [
            ReligionCategory(id=uuid.uuid4(), name="Shaivism", code="SHA", religion_id=religion_id, is_active=True),
            ReligionCategory(id=uuid.uuid4(), name="Vaishnavism", code="VAI", religion_id=religion_id, is_active=True),
        ]

        service = ReligionCategoryService(mock_session)
        with patch.object(service.category_repo, "get_categories_by_religion", return_value=mock_categories):
            # Act
            result = service.get_categories_by_religion(religion_id)

            # Assert
            assert len(result) == 2
            assert result[0].categoryName == "Shaivism"
            assert result[1].categoryName == "Vaishnavism"

    def test_get_categories_by_religion_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test getting categories for religion with no categories returns empty list."""
        # Arrange
        religion_id = uuid.uuid4()
        service = ReligionCategoryService(mock_session)
        with patch.object(service.category_repo, "get_categories_by_religion", return_value=[]):
            # Act
            result = service.get_categories_by_religion(religion_id)

            # Assert
            assert len(result) == 0

    def test_get_category_by_id_returns_category(self, mock_session: MagicMock) -> None:
        """Test getting category by ID returns the category."""
        # Arrange
        category_id = uuid.uuid4()
        mock_category = ReligionCategory(id=category_id, name="Shaivism", code="SHA", religion_id=uuid.uuid4(), is_active=True)

        service = ReligionCategoryService(mock_session)
        with patch.object(service.category_repo, "get_by_id", return_value=mock_category):
            # Act
            result = service.get_category_by_id(category_id)

            # Assert
            assert result is not None
            assert result.id == category_id
            assert result.name == "Shaivism"

    def test_get_category_by_id_returns_none_for_nonexistent(self, mock_session: MagicMock) -> None:
        """Test getting nonexistent category returns None."""
        # Arrange
        service = ReligionCategoryService(mock_session)
        with patch.object(service.category_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_category_by_id(uuid.uuid4())

            # Assert
            assert result is None


@pytest.mark.unit
class TestReligionCategoryServiceCreate:
    """Tests for religion category creation."""

    def test_create_category_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating category with valid data."""
        # Arrange
        religion_id = uuid.uuid4()
        category_create = ReligionCategoryCreate(name="New Category", code="nc", religion_id=religion_id, is_active=True)

        service = ReligionCategoryService(mock_session)

        def return_category(category: ReligionCategory) -> ReligionCategory:
            return category

        with patch.object(service.category_repo, "create", side_effect=return_category):
            # Act
            result = service.create_category(category_create)

            # Assert
            assert result.name == "New Category"
            assert result.code == "NC"  # Should be uppercase
            assert result.religion_id == religion_id
            assert result.is_active is True

    def test_create_category_uppercases_code(self, mock_session: MagicMock) -> None:
        """Test that category code is uppercased on creation."""
        # Arrange
        category_create = ReligionCategoryCreate(name="Test", code="ts", religion_id=uuid.uuid4(), is_active=True)

        service = ReligionCategoryService(mock_session)

        def return_category(category: ReligionCategory) -> ReligionCategory:
            return category

        with patch.object(service.category_repo, "create", side_effect=return_category):
            # Act
            result = service.create_category(category_create)

            # Assert
            assert result.code == "TS"

    def test_create_category_with_none_code(self, mock_session: MagicMock) -> None:
        """Test creating category with None code."""
        # Arrange
        category_create = ReligionCategoryCreate(name="Test", code=None, religion_id=uuid.uuid4(), is_active=True)

        service = ReligionCategoryService(mock_session)

        def return_category(category: ReligionCategory) -> ReligionCategory:
            return category

        with patch.object(service.category_repo, "create", side_effect=return_category):
            # Act
            result = service.create_category(category_create)

            # Assert
            assert result.code is None


@pytest.mark.unit
class TestReligionCategoryServiceUpdate:
    """Tests for religion category update operations."""

    def test_update_category_name(self, mock_session: MagicMock) -> None:
        """Test updating category name."""
        # Arrange
        mock_category = ReligionCategory(id=uuid.uuid4(), name="Old Name", code="ON", religion_id=uuid.uuid4(), is_active=True)
        category_update = ReligionCategoryUpdate(name="New Name")

        service = ReligionCategoryService(mock_session)

        def return_category(category: ReligionCategory) -> ReligionCategory:
            return category

        with patch.object(service.category_repo, "update", side_effect=return_category):
            # Act
            result = service.update_category(mock_category, category_update)

            # Assert
            assert result.name == "New Name"

    def test_update_category_code_uppercases(self, mock_session: MagicMock) -> None:
        """Test that updating category code uppercases it."""
        # Arrange
        mock_category = ReligionCategory(id=uuid.uuid4(), name="Category", code="OLD", religion_id=uuid.uuid4(), is_active=True)
        category_update = ReligionCategoryUpdate(code="new")

        service = ReligionCategoryService(mock_session)

        def return_category(category: ReligionCategory) -> ReligionCategory:
            return category

        with patch.object(service.category_repo, "update", side_effect=return_category):
            # Act
            result = service.update_category(mock_category, category_update)

            # Assert
            assert result.code == "NEW"


@pytest.mark.unit
class TestReligionCategoryServiceDelete:
    """Tests for religion category deletion."""

    def test_delete_category_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_category = ReligionCategory(id=uuid.uuid4(), name="Category to Delete", code="CD", religion_id=uuid.uuid4(), is_active=True)

        service = ReligionCategoryService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.category_repo, "delete", mock_delete):
            # Act
            service.delete_category(mock_category)

            # Assert
            mock_delete.assert_called_once_with(mock_category)


@pytest.mark.unit
class TestReligionCategoryServiceValidation:
    """Tests for religion category validation."""

    def test_code_exists_returns_true_for_existing_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns True for existing code."""
        # Arrange
        religion_id = uuid.uuid4()
        service = ReligionCategoryService(mock_session)
        with patch.object(service.category_repo, "code_exists", return_value=True):
            # Act
            result = service.code_exists("SHA", religion_id)

            # Assert
            assert result is True

    def test_code_exists_returns_false_for_nonexistent_code(self, mock_session: MagicMock) -> None:
        """Test code_exists returns False for nonexistent code."""
        # Arrange
        service = ReligionCategoryService(mock_session)
        with patch.object(service.category_repo, "code_exists", return_value=False):
            # Act
            result = service.code_exists("XX", uuid.uuid4())

            # Assert
            assert result is False

    def test_code_exists_with_exclude_returns_false(self, mock_session: MagicMock) -> None:
        """Test code_exists with exclude returns False when excluding the match."""
        # Arrange
        category_id = uuid.uuid4()
        religion_id = uuid.uuid4()
        service = ReligionCategoryService(mock_session)
        with patch.object(service.category_repo, "code_exists", return_value=False):
            # Act
            result = service.code_exists("SHA", religion_id, exclude_category_id=category_id)

            # Assert
            assert result is False
