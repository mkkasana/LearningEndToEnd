"""Unit tests for UserRepository."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.db_models.user import User
from app.repositories.user_repository import UserRepository


@pytest.mark.unit
class TestUserRepositoryGetByEmail:
    """Tests for get_by_email method."""

    def test_get_by_email_returns_user_when_found(self, mock_session: MagicMock) -> None:
        """Test get_by_email returns user when email exists."""
        repo = UserRepository(mock_session)
        expected_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            is_superuser=False,
        )
        mock_session.exec.return_value.first.return_value = expected_user

        result = repo.get_by_email("test@example.com")

        assert result == expected_user
        mock_session.exec.assert_called_once()

    def test_get_by_email_returns_none_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_by_email returns None when email doesn't exist."""
        repo = UserRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.get_by_email("nonexistent@example.com")

        assert result is None


@pytest.mark.unit
class TestUserRepositoryGetActiveUsers:
    """Tests for get_active_users method."""

    def test_get_active_users_returns_list(self, mock_session: MagicMock) -> None:
        """Test get_active_users returns list of active users."""
        repo = UserRepository(mock_session)
        users = [
            User(
                id=uuid.uuid4(),
                email="user1@example.com",
                hashed_password="hashed",
                is_active=True,
                is_superuser=False,
            ),
            User(
                id=uuid.uuid4(),
                email="user2@example.com",
                hashed_password="hashed",
                is_active=True,
                is_superuser=False,
            ),
        ]
        mock_session.exec.return_value.all.return_value = users

        result = repo.get_active_users(skip=0, limit=100)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_active_users_returns_empty_list(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_active_users returns empty list when no active users."""
        repo = UserRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_active_users()

        assert result == []

    def test_get_active_users_with_pagination(self, mock_session: MagicMock) -> None:
        """Test get_active_users respects skip and limit parameters."""
        repo = UserRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_active_users(skip=10, limit=50)

        mock_session.exec.assert_called_once()


@pytest.mark.unit
class TestUserRepositoryEmailExists:
    """Tests for email_exists method."""

    def test_email_exists_returns_true_when_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test email_exists returns True when email exists."""
        repo = UserRepository(mock_session)
        mock_session.exec.return_value.first.return_value = User(
            id=uuid.uuid4(),
            email="existing@example.com",
            hashed_password="hashed",
            is_active=True,
            is_superuser=False,
        )

        result = repo.email_exists("existing@example.com")

        assert result is True

    def test_email_exists_returns_false_when_not_found(
        self, mock_session: MagicMock
    ) -> None:
        """Test email_exists returns False when email doesn't exist."""
        repo = UserRepository(mock_session)
        mock_session.exec.return_value.first.return_value = None

        result = repo.email_exists("nonexistent@example.com")

        assert result is False
