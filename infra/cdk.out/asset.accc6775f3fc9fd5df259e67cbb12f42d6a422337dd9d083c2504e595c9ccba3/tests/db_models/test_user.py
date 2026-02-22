"""Property-based tests for User model default role assignment.

**Feature: user-roles-permissions, Property 2: Default Role Assignment**
**Validates: Requirements 1.3**

Note: These tests verify the Python model behavior (defaults, properties) without
database interaction. Database schema changes require migration (Task 8).
"""

import uuid

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.db_models.user import User
from app.enums.user_role import UserRole


# Custom strategy for valid email addresses
def valid_email() -> st.SearchStrategy[str]:
    """Generate valid email addresses for testing."""
    return st.emails()


# Custom strategy for text without NUL bytes (PostgreSQL doesn't allow them)
def text_without_nul(min_size: int = 1, max_size: int = 100) -> st.SearchStrategy[str]:
    """Generate text without NUL bytes which PostgreSQL rejects."""
    return st.text(
        min_size=min_size,
        max_size=max_size,
        alphabet=st.characters(
            blacklist_categories=("Cs",),  # Surrogate characters
            blacklist_characters="\x00",  # NUL byte
        ),
    )


@pytest.mark.unit
class TestUserDefaultRole:
    """Tests for Property 2: Default Role Assignment.
    
    **Feature: user-roles-permissions, Property 2: Default Role Assignment**
    **Validates: Requirements 1.3**
    
    Tests that users created without role get UserRole.USER.
    """

    @settings(max_examples=100)
    @given(
        email=valid_email(),
        hashed_password=text_without_nul(min_size=8, max_size=128),
        full_name=st.one_of(st.none(), text_without_nul(min_size=1, max_size=255)),
        is_active=st.booleans(),
    )
    def test_user_created_without_role_gets_default_user_role(
        self,
        email: str,
        hashed_password: str,
        full_name: str | None,
        is_active: bool,
    ) -> None:
        """Property 2: For any user created without specifying a role,
        the resulting user must have role equal to UserRole.USER.
        """
        # Create user without specifying role
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_active=is_active,
        )
        
        # Verify default role is USER
        assert user.role == UserRole.USER, (
            f"User created without role should have UserRole.USER, got {user.role}"
        )

    def test_user_default_role_is_user(self) -> None:
        """Test that User model defaults to USER role."""
        user = User(
            email="test@example.com",
            hashed_password="hashed_password_123",
        )
        
        assert user.role == UserRole.USER

    def test_user_with_explicit_role_preserves_role(self) -> None:
        """Test that explicitly set roles are preserved."""
        for role in UserRole:
            user = User(
                email=f"test_{role.value}@example.com",
                hashed_password="hashed_password_123",
                role=role,
            )
            assert user.role == role, f"Expected {role}, got {user.role}"


@pytest.mark.unit
class TestUserBackwardCompatibility:
    """Tests for backward compatibility properties (is_superuser, is_admin).
    
    **Validates: Requirements 1.2, 1.4**
    """

    def test_is_superuser_true_for_superuser_role(self) -> None:
        """Test is_superuser returns True for SUPERUSER role."""
        user = User(
            email="superuser@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.SUPERUSER,
        )
        assert user.is_superuser is True

    def test_is_superuser_false_for_admin_role(self) -> None:
        """Test is_superuser returns False for ADMIN role."""
        user = User(
            email="admin@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.ADMIN,
        )
        assert user.is_superuser is False

    def test_is_superuser_false_for_user_role(self) -> None:
        """Test is_superuser returns False for USER role."""
        user = User(
            email="user@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.USER,
        )
        assert user.is_superuser is False

    def test_is_admin_true_only_for_admin_role(self) -> None:
        """Test is_admin returns True only for ADMIN role."""
        admin_user = User(
            email="admin@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.ADMIN,
        )
        superuser = User(
            email="superuser@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.SUPERUSER,
        )
        regular_user = User(
            email="user@example.com",
            hashed_password="hashed_password_123",
            role=UserRole.USER,
        )
        
        assert admin_user.is_admin is True
        assert superuser.is_admin is False
        assert regular_user.is_admin is False

    @settings(max_examples=100)
    @given(role=st.sampled_from(list(UserRole)))
    def test_is_superuser_matches_superuser_role(
        self, role: UserRole
    ) -> None:
        """Property: is_superuser should be True only for SUPERUSER role."""
        user = User(
            email=f"test_{uuid.uuid4()}@example.com",
            hashed_password="hashed_password_123",
            role=role,
        )
        
        expected_is_superuser = role == UserRole.SUPERUSER
        assert user.is_superuser == expected_is_superuser, (
            f"For role {role}, is_superuser should be {expected_is_superuser}, "
            f"got {user.is_superuser}"
        )

    @settings(max_examples=100)
    @given(role=st.sampled_from(list(UserRole)))
    def test_is_admin_matches_admin_role(
        self, role: UserRole
    ) -> None:
        """Property: is_admin should be True only for ADMIN role."""
        user = User(
            email=f"test_{uuid.uuid4()}@example.com",
            hashed_password="hashed_password_123",
            role=role,
        )
        
        expected_is_admin = role == UserRole.ADMIN
        assert user.is_admin == expected_is_admin, (
            f"For role {role}, is_admin should be {expected_is_admin}, "
            f"got {user.is_admin}"
        )
