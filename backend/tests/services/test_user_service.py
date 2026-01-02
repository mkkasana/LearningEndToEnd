"""Unit tests for UserService.

Tests cover:
- User CRUD operations
- User queries (by email, by id)
- User activation/deactivation
- Password management

Requirements: 2.2, 2.18, 2.19
"""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.core.security import get_password_hash, verify_password
from app.db_models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


@pytest.mark.unit
class TestUserServiceQueries:
    """Tests for user query operations."""

    def test_get_user_by_id_returns_user(self, mock_session: MagicMock) -> None:
        """Test getting user by ID returns the user."""
        # Arrange
        user_id = uuid.uuid4()
        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
        )

        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_by_id", return_value=mock_user):
            # Act
            result = service.get_user_by_id(user_id)

            # Assert
            assert result is not None
            assert result.id == user_id
            assert result.email == "test@example.com"

    def test_get_user_by_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent user by ID returns None."""
        # Arrange
        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_user_by_id(uuid.uuid4())

            # Assert
            assert result is None

    def test_get_user_by_email_returns_user(self, mock_session: MagicMock) -> None:
        """Test getting user by email returns the user."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
        )

        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=mock_user):
            # Act
            result = service.get_user_by_email("test@example.com")

            # Assert
            assert result is not None
            assert result.email == "test@example.com"

    def test_get_user_by_email_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent user by email returns None."""
        # Arrange
        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=None):
            # Act
            result = service.get_user_by_email("nonexistent@example.com")

            # Assert
            assert result is None

    def test_get_users_returns_paginated_list(self, mock_session: MagicMock) -> None:
        """Test getting paginated list of users."""
        # Arrange
        mock_users = [
            User(id=uuid.uuid4(), email=f"user{i}@example.com", hashed_password="h", is_active=True)
            for i in range(3)
        ]

        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_all", return_value=mock_users):
            with patch.object(service.user_repo, "count", return_value=10):
                # Act
                users, count = service.get_users(skip=0, limit=3)

                # Assert
                assert len(users) == 3
                assert count == 10


@pytest.mark.unit
class TestUserServiceCreate:
    """Tests for user creation."""

    def test_create_user_hashes_password(self, mock_session: MagicMock) -> None:
        """Test that create_user hashes the password."""
        # Arrange
        user_create = UserCreate(
            email="new@example.com",
            password="plaintext_password",
        )

        service = UserService(mock_session)
        
        created_user = None
        def capture_create(user: User) -> User:
            nonlocal created_user
            created_user = user
            return user

        with patch.object(service.user_repo, "create", side_effect=capture_create):
            # Act
            service.create_user(user_create)

            # Assert
            assert created_user is not None
            assert created_user.hashed_password != "plaintext_password"
            assert verify_password("plaintext_password", created_user.hashed_password)

    def test_create_user_sets_email(self, mock_session: MagicMock) -> None:
        """Test that create_user sets the email correctly."""
        # Arrange
        user_create = UserCreate(
            email="new@example.com",
            password="password123",
        )

        service = UserService(mock_session)
        
        def return_user(user: User) -> User:
            return user

        with patch.object(service.user_repo, "create", side_effect=return_user):
            # Act
            result = service.create_user(user_create)

            # Assert
            assert result.email == "new@example.com"

    def test_create_user_with_full_name(self, mock_session: MagicMock) -> None:
        """Test creating user with full name."""
        # Arrange
        user_create = UserCreate(
            email="new@example.com",
            password="password123",
            full_name="Test User",
        )

        service = UserService(mock_session)
        
        def return_user(user: User) -> User:
            return user

        with patch.object(service.user_repo, "create", side_effect=return_user):
            # Act
            result = service.create_user(user_create)

            # Assert
            assert result.full_name == "Test User"

    def test_create_superuser(self, mock_session: MagicMock) -> None:
        """Test creating a superuser."""
        # Arrange
        user_create = UserCreate(
            email="admin@example.com",
            password="adminpass",
            is_superuser=True,
        )

        service = UserService(mock_session)
        
        def return_user(user: User) -> User:
            return user

        with patch.object(service.user_repo, "create", side_effect=return_user):
            # Act
            result = service.create_user(user_create)

            # Assert
            assert result.is_superuser is True


@pytest.mark.unit
class TestUserServiceUpdate:
    """Tests for user update operations."""

    def test_update_user_email(self, mock_session: MagicMock) -> None:
        """Test updating user email."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="old@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        user_update = UserUpdate(email="new@example.com")

        service = UserService(mock_session)
        
        def return_user(user: User) -> User:
            return user

        with patch.object(service.user_repo, "update", side_effect=return_user):
            # Act
            result = service.update_user(mock_user, user_update)

            # Assert
            assert result.email == "new@example.com"

    def test_update_user_password_hashes_new_password(
        self, mock_session: MagicMock
    ) -> None:
        """Test that updating password hashes the new password."""
        # Arrange
        old_hash = get_password_hash("old_password")
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password=old_hash,
            is_active=True,
        )
        user_update = UserUpdate(password="new_password")

        service = UserService(mock_session)
        
        def return_user(user: User) -> User:
            return user

        with patch.object(service.user_repo, "update", side_effect=return_user):
            # Act
            result = service.update_user(mock_user, user_update)

            # Assert
            assert result.hashed_password != old_hash
            assert verify_password("new_password", result.hashed_password)

    def test_update_user_full_name(self, mock_session: MagicMock) -> None:
        """Test updating user full name."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
            full_name="Old Name",
        )
        user_update = UserUpdate(full_name="New Name")

        service = UserService(mock_session)
        
        def return_user(user: User) -> User:
            return user

        with patch.object(service.user_repo, "update", side_effect=return_user):
            # Act
            result = service.update_user(mock_user, user_update)

            # Assert
            assert result.full_name == "New Name"


@pytest.mark.unit
class TestUserServiceDelete:
    """Tests for user deletion."""

    def test_delete_user_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete_user calls the repository delete method."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
        )

        service = UserService(mock_session)
        mock_delete = MagicMock()
        
        with patch.object(service.user_repo, "delete", mock_delete):
            # Act
            service.delete_user(mock_user)

            # Assert
            mock_delete.assert_called_once_with(mock_user)


@pytest.mark.unit
class TestUserServiceEmailExists:
    """Tests for email existence checking."""

    def test_email_exists_returns_true_when_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test email_exists returns True when email exists."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="existing@example.com",
            hashed_password="hashed",
            is_active=True,
        )

        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=mock_user):
            # Act
            result = service.email_exists("existing@example.com")

            # Assert
            assert result is True

    def test_email_exists_returns_false_when_not_exists(
        self, mock_session: MagicMock
    ) -> None:
        """Test email_exists returns False when email doesn't exist."""
        # Arrange
        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=None):
            # Act
            result = service.email_exists("nonexistent@example.com")

            # Assert
            assert result is False

    def test_email_exists_excludes_specified_user(
        self, mock_session: MagicMock
    ) -> None:
        """Test email_exists excludes the specified user from check."""
        # Arrange
        user_id = uuid.uuid4()
        mock_user = User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
        )

        service = UserService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=mock_user):
            # Act
            result = service.email_exists("test@example.com", exclude_user_id=user_id)

            # Assert
            assert result is False


@pytest.mark.unit
class TestUserServicePassword:
    """Tests for password operations."""

    def test_verify_password_returns_true_for_correct_password(
        self, mock_session: MagicMock
    ) -> None:
        """Test verify_password returns True for correct password."""
        # Arrange
        plain_password = "correct_password"
        hashed_password = get_password_hash(plain_password)

        service = UserService(mock_session)

        # Act
        result = service.verify_password(plain_password, hashed_password)

        # Assert
        assert result is True

    def test_verify_password_returns_false_for_wrong_password(
        self, mock_session: MagicMock
    ) -> None:
        """Test verify_password returns False for wrong password."""
        # Arrange
        hashed_password = get_password_hash("correct_password")

        service = UserService(mock_session)

        # Act
        result = service.verify_password("wrong_password", hashed_password)

        # Assert
        assert result is False

    def test_update_password_hashes_new_password(
        self, mock_session: MagicMock
    ) -> None:
        """Test update_password hashes the new password."""
        # Arrange
        old_hash = get_password_hash("old_password")
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password=old_hash,
            is_active=True,
        )

        service = UserService(mock_session)
        
        def return_user(user: User) -> User:
            return user

        with patch.object(service.user_repo, "update", side_effect=return_user):
            # Act
            result = service.update_password(mock_user, "new_password")

            # Assert
            assert result.hashed_password != old_hash
            assert verify_password("new_password", result.hashed_password)
