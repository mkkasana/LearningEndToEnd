"""Unit tests for AuthService.

Tests cover:
- Login with valid/invalid credentials
- Token generation and validation
- Password hashing and verification
- User active status checking

Requirements: 2.1, 2.18
"""

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from app.core.security import get_password_hash
from app.db_models.user import User
from app.services.auth_service import AuthService


@pytest.mark.unit
class TestAuthServiceAuthentication:
    """Tests for user authentication."""

    def test_authenticate_user_with_valid_credentials(
        self, mock_session: MagicMock
    ) -> None:
        """Test successful authentication with valid email and password."""
        # Arrange
        password = "correct_password"
        hashed_password = get_password_hash(password)
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True,
        )

        service = AuthService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=mock_user):
            # Act
            result = service.authenticate_user("test@example.com", password)

            # Assert
            assert result is not None
            assert result.email == "test@example.com"
            assert result.id == mock_user.id

    def test_authenticate_user_with_invalid_password(
        self, mock_session: MagicMock
    ) -> None:
        """Test authentication fails with wrong password."""
        # Arrange
        correct_password = "correct_password"
        wrong_password = "wrong_password"
        hashed_password = get_password_hash(correct_password)
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password=hashed_password,
            is_active=True,
        )

        service = AuthService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=mock_user):
            # Act
            result = service.authenticate_user("test@example.com", wrong_password)

            # Assert
            assert result is None

    def test_authenticate_user_with_nonexistent_email(
        self, mock_session: MagicMock
    ) -> None:
        """Test authentication fails when user doesn't exist."""
        # Arrange
        service = AuthService(mock_session)
        with patch.object(service.user_repo, "get_by_email", return_value=None):
            # Act
            result = service.authenticate_user("nonexistent@example.com", "any_password")

            # Assert
            assert result is None

    def test_authenticate_user_calls_repository(
        self, mock_session: MagicMock
    ) -> None:
        """Test that authenticate_user calls the repository with correct email."""
        # Arrange
        service = AuthService(mock_session)
        mock_get_by_email = MagicMock(return_value=None)
        
        with patch.object(service.user_repo, "get_by_email", mock_get_by_email):
            # Act
            service.authenticate_user("test@example.com", "password")

            # Assert
            mock_get_by_email.assert_called_once_with("test@example.com")


@pytest.mark.unit
class TestAuthServiceTokenGeneration:
    """Tests for access token generation."""

    def test_create_access_token_for_user_returns_token(
        self, mock_session: MagicMock
    ) -> None:
        """Test that token generation returns a Token object."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        expires_delta = timedelta(minutes=30)

        service = AuthService(mock_session)

        # Act
        result = service.create_access_token_for_user(mock_user, expires_delta)

        # Assert
        assert result is not None
        assert hasattr(result, "access_token")
        assert result.access_token is not None
        assert len(result.access_token) > 0

    def test_create_access_token_with_different_expiry(
        self, mock_session: MagicMock
    ) -> None:
        """Test token generation with different expiry times."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            is_active=True,
        )
        short_expiry = timedelta(minutes=5)
        long_expiry = timedelta(hours=24)

        service = AuthService(mock_session)

        # Act
        short_token = service.create_access_token_for_user(mock_user, short_expiry)
        long_token = service.create_access_token_for_user(mock_user, long_expiry)

        # Assert - both should return valid tokens (different due to different expiry)
        assert short_token.access_token is not None
        assert long_token.access_token is not None
        # Tokens should be different due to different expiry times
        assert short_token.access_token != long_token.access_token


@pytest.mark.unit
class TestAuthServiceUserStatus:
    """Tests for user active status checking."""

    def test_is_user_active_returns_true_for_active_user(
        self, mock_session: MagicMock
    ) -> None:
        """Test that is_user_active returns True for active users."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="active@example.com",
            hashed_password="hashed",
            is_active=True,
        )

        service = AuthService(mock_session)

        # Act
        result = service.is_user_active(mock_user)

        # Assert
        assert result is True

    def test_is_user_active_returns_false_for_inactive_user(
        self, mock_session: MagicMock
    ) -> None:
        """Test that is_user_active returns False for inactive users."""
        # Arrange
        mock_user = User(
            id=uuid.uuid4(),
            email="inactive@example.com",
            hashed_password="hashed",
            is_active=False,
        )

        service = AuthService(mock_session)

        # Act
        result = service.is_user_active(mock_user)

        # Assert
        assert result is False
