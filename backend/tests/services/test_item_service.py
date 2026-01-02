"""Unit tests for ItemService.

Tests cover:
- Item CRUD operations
- Owner validation
- Permission checks

Requirements: 2.13, 2.18
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.item import Item
from app.db_models.user import User
from app.schemas.item import ItemCreate, ItemUpdate
from app.services.item_service import ItemService


@pytest.mark.unit
class TestItemServiceQueries:
    """Tests for item query operations."""

    def test_get_item_by_id_returns_item(self, mock_session: MagicMock) -> None:
        """Test getting item by ID returns the item."""
        # Arrange
        item_id = uuid.uuid4()
        mock_item = Item(
            id=item_id,
            title="Test Item",
            description="Test Description",
            owner_id=uuid.uuid4(),
        )

        service = ItemService(mock_session)
        with patch.object(service.item_repo, "get_by_id", return_value=mock_item):
            # Act
            result = service.get_item_by_id(item_id)

            # Assert
            assert result is not None
            assert result.id == item_id
            assert result.title == "Test Item"

    def test_get_item_by_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent item returns None."""
        # Arrange
        service = ItemService(mock_session)
        with patch.object(service.item_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_item_by_id(uuid.uuid4())

            # Assert
            assert result is None

    def test_get_items_for_superuser_returns_all(
        self, mock_session: MagicMock
    ) -> None:
        """Test that superuser gets all items."""
        # Arrange
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid.uuid4()
        mock_user.email = "admin@example.com"
        mock_user.is_superuser = True

        mock_items = [
            Item(id=uuid.uuid4(), title="Item 1", owner_id=uuid.uuid4()),
            Item(id=uuid.uuid4(), title="Item 2", owner_id=uuid.uuid4()),
        ]

        service = ItemService(mock_session)
        with patch.object(
            service.item_repo, "get_all", return_value=mock_items
        ), patch.object(service.item_repo, "count", return_value=2):
            # Act
            items, count = service.get_items(mock_user, skip=0, limit=100)

            # Assert
            assert len(items) == 2
            assert count == 2

    def test_get_items_for_regular_user_returns_owned_only(
        self, mock_session: MagicMock
    ) -> None:
        """Test that regular user gets only their own items."""
        # Arrange
        user_id = uuid.uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id
        mock_user.email = "user@example.com"
        mock_user.is_superuser = False

        mock_items = [
            Item(id=uuid.uuid4(), title="My Item", owner_id=user_id),
        ]

        service = ItemService(mock_session)
        with patch.object(
            service.item_repo, "get_by_owner", return_value=mock_items
        ), patch.object(service.item_repo, "count_by_owner", return_value=1):
            # Act
            items, count = service.get_items(mock_user, skip=0, limit=100)

            # Assert
            assert len(items) == 1
            assert count == 1


@pytest.mark.unit
class TestItemServiceCreate:
    """Tests for item creation."""

    def test_create_item_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating item with valid data."""
        # Arrange
        owner_id = uuid.uuid4()
        item_create = ItemCreate(title="New Item", description="New Description")

        service = ItemService(mock_session)

        def return_item(item: Item) -> Item:
            return item

        with patch.object(service.item_repo, "create", side_effect=return_item):
            # Act
            result = service.create_item(item_create, owner_id)

            # Assert
            assert result.title == "New Item"
            assert result.description == "New Description"
            assert result.owner_id == owner_id


@pytest.mark.unit
class TestItemServiceUpdate:
    """Tests for item update operations."""

    def test_update_item_title(self, mock_session: MagicMock) -> None:
        """Test updating item title."""
        # Arrange
        mock_item = Item(
            id=uuid.uuid4(),
            title="Old Title",
            description="Description",
            owner_id=uuid.uuid4(),
        )
        item_update = ItemUpdate(title="New Title")

        service = ItemService(mock_session)

        def return_item(item: Item) -> Item:
            return item

        with patch.object(service.item_repo, "update", side_effect=return_item):
            # Act
            result = service.update_item(mock_item, item_update)

            # Assert
            assert result.title == "New Title"


@pytest.mark.unit
class TestItemServiceDelete:
    """Tests for item deletion."""

    def test_delete_item_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_item = Item(
            id=uuid.uuid4(),
            title="Item to Delete",
            owner_id=uuid.uuid4(),
        )

        service = ItemService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.item_repo, "delete", mock_delete):
            # Act
            service.delete_item(mock_item)

            # Assert
            mock_delete.assert_called_once_with(mock_item)

    def test_delete_items_by_owner(self, mock_session: MagicMock) -> None:
        """Test deleting all items for an owner."""
        # Arrange
        owner_id = uuid.uuid4()

        service = ItemService(mock_session)
        mock_delete_by_owner = MagicMock()

        with patch.object(
            service.item_repo, "delete_by_owner", mock_delete_by_owner
        ):
            # Act
            service.delete_items_by_owner(owner_id)

            # Assert
            mock_delete_by_owner.assert_called_once_with(owner_id)


@pytest.mark.unit
class TestItemServicePermissions:
    """Tests for item permission checks."""

    def test_user_can_access_own_item(self, mock_session: MagicMock) -> None:
        """Test that user can access their own item."""
        # Arrange
        user_id = uuid.uuid4()
        mock_user = MagicMock(spec=User)
        mock_user.id = user_id
        mock_user.email = "user@example.com"
        mock_user.is_superuser = False

        mock_item = Item(id=uuid.uuid4(), title="My Item", owner_id=user_id)

        service = ItemService(mock_session)

        # Act
        result = service.user_can_access_item(mock_user, mock_item)

        # Assert
        assert result is True

    def test_user_cannot_access_other_user_item(
        self, mock_session: MagicMock
    ) -> None:
        """Test that user cannot access another user's item."""
        # Arrange
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid.uuid4()
        mock_user.email = "user@example.com"
        mock_user.is_superuser = False

        mock_item = Item(
            id=uuid.uuid4(), title="Other Item", owner_id=uuid.uuid4()
        )

        service = ItemService(mock_session)

        # Act
        result = service.user_can_access_item(mock_user, mock_item)

        # Assert
        assert result is False

    def test_superuser_can_access_any_item(self, mock_session: MagicMock) -> None:
        """Test that superuser can access any item."""
        # Arrange
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid.uuid4()
        mock_user.email = "admin@example.com"
        mock_user.is_superuser = True

        mock_item = Item(
            id=uuid.uuid4(), title="Any Item", owner_id=uuid.uuid4()
        )

        service = ItemService(mock_session)

        # Act
        result = service.user_can_access_item(mock_user, mock_item)

        # Assert
        assert result is True
