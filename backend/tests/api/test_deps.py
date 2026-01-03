"""Property-based tests for API dependencies role validation.

**Feature: user-roles-permissions, Property 4: Dependency Role Validation**
**Validates: Requirements 3.2, 3.3, 3.4**

Note: These tests verify the dependency functions' role checking logic.
Database tests will run after migration is applied.
"""

import uuid

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st
from unittest.mock import MagicMock

from app.api.deps import get_current_active_superuser, get_current_active_admin
from app.db_models.user import User
from app.enums.user_role import UserRole


def create_mock_user(role: UserRole, is_active: bool = True) -> User:
    """Create a mock user with the specified role."""
    user = MagicMock(spec=User)
    user.id = uuid.uuid4()
    user.email = f"test_{role.value}@example.com"
    user.is_active = is_active
    user.role = role
    return user


@pytest.mark.unit
class TestGetCurrentActiveSuperuser:
    """Tests for get_current_active_superuser dependency.
    
    **Feature: user-roles-permissions, Property 4: Dependency Role Validation**
    **Validates: Requirements 3.2**
    """

    def test_allows_superuser_role(self) -> None:
        """Test that SUPERUSER role is allowed."""
        user = create_mock_user(UserRole.SUPERUSER)
        result = get_current_active_superuser(user)
        assert result == user

    def test_allows_admin_role(self) -> None:
        """Test that ADMIN role is allowed (has superuser permission)."""
        user = create_mock_user(UserRole.ADMIN)
        result = get_current_active_superuser(user)
        assert result == user

    def test_denies_user_role(self) -> None:
        """Test that USER role is denied with 403."""
        user = create_mock_user(UserRole.USER)
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_superuser(user)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"

    @settings(max_examples=100)
    @given(role=st.sampled_from(list(UserRole)))
    def test_superuser_dependency_respects_hierarchy(self, role: UserRole) -> None:
        """Property 4: get_current_active_superuser allows user iff role has superuser permission."""
        user = create_mock_user(role)
        
        if role.has_permission(UserRole.SUPERUSER):
            # Should allow
            result = get_current_active_superuser(user)
            assert result == user
        else:
            # Should deny with 403
            with pytest.raises(HTTPException) as exc_info:
                get_current_active_superuser(user)
            assert exc_info.value.status_code == 403


@pytest.mark.unit
class TestGetCurrentActiveAdmin:
    """Tests for get_current_active_admin dependency.
    
    **Feature: user-roles-permissions, Property 4: Dependency Role Validation**
    **Validates: Requirements 3.3, 3.4**
    """

    def test_allows_admin_role(self) -> None:
        """Test that ADMIN role is allowed."""
        user = create_mock_user(UserRole.ADMIN)
        result = get_current_active_admin(user)
        assert result == user

    def test_denies_superuser_role(self) -> None:
        """Test that SUPERUSER role is denied with 403."""
        user = create_mock_user(UserRole.SUPERUSER)
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(user)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"

    def test_denies_user_role(self) -> None:
        """Test that USER role is denied with 403."""
        user = create_mock_user(UserRole.USER)
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(user)
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"

    @settings(max_examples=100)
    @given(role=st.sampled_from(list(UserRole)))
    def test_admin_dependency_respects_hierarchy(self, role: UserRole) -> None:
        """Property 4: get_current_active_admin allows user iff role has admin permission."""
        user = create_mock_user(role)
        
        if role.has_permission(UserRole.ADMIN):
            # Should allow
            result = get_current_active_admin(user)
            assert result == user
        else:
            # Should deny with 403
            with pytest.raises(HTTPException) as exc_info:
                get_current_active_admin(user)
            assert exc_info.value.status_code == 403
