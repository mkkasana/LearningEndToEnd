"""Unit tests for ItemRepository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.item import Item
from app.repositories.item_repository import ItemRepository


@pytest.mark.unit
class TestGetByOwner:
    """Tests for get_by_owner method."""

    def test_get_by_owner_returns_items(self, mock_session: MagicMock) -> None:
        """Test get_by_owner returns list of items."""
        repo = ItemRepository(mock_session)
        owner_id = uuid.uuid4()
        items = [
            Item(
                id=uuid.uuid4(),
                title="Item 1",
                description="Description 1",
                owner_id=owner_id,
            ),
            Item(
                id=uuid.uuid4(),
                title="Item 2",
                description="Description 2",
                owner_id=owner_id,
            ),
        ]
        mock_session.exec.return_value.all.return_value = items

        result = repo.get_by_owner(owner_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_owner_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_by_owner returns empty list when no items."""
        repo = ItemRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_owner(uuid.uuid4())

        assert result == []

    def test_get_by_owner_with_pagination(self, mock_session: MagicMock) -> None:
        """Test get_by_owner respects skip and limit."""
        repo = ItemRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_by_owner(uuid.uuid4(), skip=10, limit=50)

        mock_session.exec.assert_called_once()


@pytest.mark.unit
class TestCountByOwner:
    """Tests for count_by_owner method."""

    def test_count_by_owner_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_by_owner returns correct count."""
        repo = ItemRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 5

        result = repo.count_by_owner(uuid.uuid4())

        assert result == 5

    def test_count_by_owner_returns_zero(self, mock_session: MagicMock) -> None:
        """Test count_by_owner returns 0 when no items."""
        repo = ItemRepository(mock_session)
        mock_session.exec.return_value.one.return_value = 0

        result = repo.count_by_owner(uuid.uuid4())

        assert result == 0


@pytest.mark.unit
class TestDeleteByOwner:
    """Tests for delete_by_owner method."""

    def test_delete_by_owner_executes_delete(self, mock_session: MagicMock) -> None:
        """Test delete_by_owner executes delete statement."""
        repo = ItemRepository(mock_session)
        owner_id = uuid.uuid4()

        repo.delete_by_owner(owner_id)

        mock_session.exec.assert_called_once()
        mock_session.commit.assert_called_once()
