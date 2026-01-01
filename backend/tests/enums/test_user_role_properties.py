"""Property-based tests for UserRole enum.

**Feature: user-roles-permissions, Property 3: Role Hierarchy Permission**
**Validates: Requirements 2.1, 2.2, 2.3, 2.4**
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from app.enums.user_role import UserRole


class TestRoleHierarchyPermission:
    """Tests for Property 3: Role Hierarchy Permission.
    
    **Feature: user-roles-permissions, Property 3: Role Hierarchy Permission**
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4**
    
    Tests that has_permission correctly enforces admin > superuser > user hierarchy.
    """

    @settings(max_examples=100)
    @given(
        role_a=st.sampled_from(list(UserRole)),
        role_b=st.sampled_from(list(UserRole)),
    )
    def test_has_permission_matches_hierarchy_levels(
        self,
        role_a: UserRole,
        role_b: UserRole,
    ) -> None:
        """Property 3: has_permission returns True iff role_a level >= role_b level.
        
        For any two roles A and B, A.has_permission(B) should return True
        if and only if the hierarchy level of A is >= the hierarchy level of B.
        """
        level_a = UserRole.get_hierarchy_level(role_a)
        level_b = UserRole.get_hierarchy_level(role_b)
        
        expected = level_a >= level_b
        actual = role_a.has_permission(role_b)
        
        assert actual == expected, (
            f"{role_a.value} (level {level_a}) has_permission({role_b.value}) "
            f"(level {level_b}) should be {expected}, got {actual}"
        )

    def test_admin_has_all_permissions(self) -> None:
        """Admin role should have permission for all roles."""
        assert UserRole.ADMIN.has_permission(UserRole.USER) is True
        assert UserRole.ADMIN.has_permission(UserRole.SUPERUSER) is True
        assert UserRole.ADMIN.has_permission(UserRole.ADMIN) is True

    def test_superuser_permissions(self) -> None:
        """Superuser should have permission for user and superuser, not admin."""
        assert UserRole.SUPERUSER.has_permission(UserRole.USER) is True
        assert UserRole.SUPERUSER.has_permission(UserRole.SUPERUSER) is True
        assert UserRole.SUPERUSER.has_permission(UserRole.ADMIN) is False

    def test_user_permissions(self) -> None:
        """User should only have permission for user role."""
        assert UserRole.USER.has_permission(UserRole.USER) is True
        assert UserRole.USER.has_permission(UserRole.SUPERUSER) is False
        assert UserRole.USER.has_permission(UserRole.ADMIN) is False

    def test_hierarchy_levels_are_correct(self) -> None:
        """Verify the hierarchy levels match the design spec."""
        assert UserRole.get_hierarchy_level(UserRole.USER) == 0
        assert UserRole.get_hierarchy_level(UserRole.SUPERUSER) == 1
        assert UserRole.get_hierarchy_level(UserRole.ADMIN) == 10

    @settings(max_examples=100)
    @given(role=st.sampled_from(list(UserRole)))
    def test_role_has_permission_for_itself(self, role: UserRole) -> None:
        """Every role should have permission for itself (reflexive property)."""
        assert role.has_permission(role) is True, (
            f"{role.value} should have permission for itself"
        )

    @settings(max_examples=100)
    @given(
        role_a=st.sampled_from(list(UserRole)),
        role_b=st.sampled_from(list(UserRole)),
        role_c=st.sampled_from(list(UserRole)),
    )
    def test_permission_transitivity(
        self,
        role_a: UserRole,
        role_b: UserRole,
        role_c: UserRole,
    ) -> None:
        """If A has permission for B and B has permission for C, then A has permission for C.
        
        This tests the transitive property of the permission hierarchy.
        """
        if role_a.has_permission(role_b) and role_b.has_permission(role_c):
            assert role_a.has_permission(role_c) is True, (
                f"Transitivity violated: {role_a.value} has permission for {role_b.value}, "
                f"{role_b.value} has permission for {role_c.value}, "
                f"but {role_a.value} does not have permission for {role_c.value}"
            )
