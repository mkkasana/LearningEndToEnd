"""Property-based tests for UserRole enum.

**Feature: user-roles-permissions, Property 3: Role Hierarchy Permission**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.enums.user_role import UserRole


@pytest.mark.unit
class TestUserRoleHierarchy:
    """Tests for Property 3: Role Hierarchy Permission.
    
    **Feature: user-roles-permissions, Property 3: Role Hierarchy Permission**
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    
    Tests that has_permission correctly enforces admin > superuser > user.
    """

    @settings(max_examples=100)
    @given(
        role_a=st.sampled_from(list(UserRole)),
        role_b=st.sampled_from(list(UserRole)),
    )
    def test_has_permission_respects_hierarchy_levels(
        self, role_a: UserRole, role_b: UserRole
    ) -> None:
        """Property 3: For any two roles A and B, A.has_permission(B) returns True
        if and only if the hierarchy level of A >= hierarchy level of B.
        """
        level_a = UserRole.get_hierarchy_level(role_a)
        level_b = UserRole.get_hierarchy_level(role_b)
        
        expected = level_a >= level_b
        actual = role_a.has_permission(role_b)
        
        assert actual == expected, (
            f"{role_a.value}.has_permission({role_b.value}) should be {expected}, "
            f"got {actual}. Levels: {level_a} vs {level_b}"
        )

    def test_admin_has_permission_for_all_roles(self) -> None:
        """Admin should have permission for all role levels."""
        admin = UserRole.ADMIN
        
        assert admin.has_permission(UserRole.USER) is True
        assert admin.has_permission(UserRole.SUPERUSER) is True
        assert admin.has_permission(UserRole.ADMIN) is True

    def test_superuser_has_permission_for_user_and_self(self) -> None:
        """Superuser should have permission for user and superuser, but not admin."""
        superuser = UserRole.SUPERUSER
        
        assert superuser.has_permission(UserRole.USER) is True
        assert superuser.has_permission(UserRole.SUPERUSER) is True
        assert superuser.has_permission(UserRole.ADMIN) is False

    def test_user_has_permission_only_for_self(self) -> None:
        """User should only have permission for user role."""
        user = UserRole.USER
        
        assert user.has_permission(UserRole.USER) is True
        assert user.has_permission(UserRole.SUPERUSER) is False
        assert user.has_permission(UserRole.ADMIN) is False

    def test_hierarchy_levels_are_correct(self) -> None:
        """Verify hierarchy levels: USER=0, SUPERUSER=1, ADMIN=10."""
        assert UserRole.get_hierarchy_level(UserRole.USER) == 0
        assert UserRole.get_hierarchy_level(UserRole.SUPERUSER) == 1
        assert UserRole.get_hierarchy_level(UserRole.ADMIN) == 10

    def test_enum_values_are_correct(self) -> None:
        """Verify enum string values are lowercase."""
        assert UserRole.USER.value == "user"
        assert UserRole.SUPERUSER.value == "superuser"
        assert UserRole.ADMIN.value == "admin"

    def test_enum_has_exactly_three_values(self) -> None:
        """Verify enum contains exactly three roles."""
        all_roles = list(UserRole)
        assert len(all_roles) == 3
        assert set(all_roles) == {UserRole.USER, UserRole.SUPERUSER, UserRole.ADMIN}
