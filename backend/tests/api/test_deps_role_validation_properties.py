"""Property-based tests for dependency role validation.

**Feature: user-roles-permissions, Property 4: Dependency Role Validation**
**Validates: Requirements 3.2, 3.3, 3.4**
"""

import pytest
from fastapi import HTTPException
from hypothesis import given, settings
from hypothesis import strategies as st

from app.enums.user_role import UserRole


# Custom strategy for valid email addresses
def valid_emails() -> st.SearchStrategy[str]:
    """Generate valid email addresses."""
    return st.emails()


# Custom strategy for text without NUL bytes
def text_without_nul(min_size: int = 0, max_size: int | None = None) -> st.SearchStrategy[str]:
    """Generate text without NUL bytes which PostgreSQL/UTF-8 rejects."""
    return st.text(
        min_size=min_size,
        max_size=max_size,
        alphabet=st.characters(
            blacklist_categories=("Cs",),
            blacklist_characters="\x00",
        ),
    )


class TestDependencyRoleValidation:
    """Tests for Property 4: Dependency Role Validation.
    
    **Feature: user-roles-permissions, Property 4: Dependency Role Validation**
    **Validates: Requirements 3.2, 3.3, 3.4**
    
    Tests that:
    - get_current_active_superuser allows superuser and admin, denies user
    - get_current_active_admin allows only admin
    - When denied, HTTP status code is 403 with message "The user doesn't have enough privileges"
    """

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_superuser_dependency_allows_admin(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Admin users should pass the superuser dependency check."""
        from app.api.deps import get_current_active_superuser
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
        )
        
        # Should not raise an exception
        result = get_current_active_superuser(user)
        assert result == user

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_superuser_dependency_allows_superuser(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Superuser users should pass the superuser dependency check."""
        from app.api.deps import get_current_active_superuser
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.SUPERUSER,
        )
        
        # Should not raise an exception
        result = get_current_active_superuser(user)
        assert result == user

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_superuser_dependency_denies_user(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Regular users should be denied by the superuser dependency check."""
        from app.api.deps import get_current_active_superuser
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.USER,
        )
        
        # Should raise HTTPException with 403 status
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_superuser(user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_admin_dependency_allows_admin(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Admin users should pass the admin dependency check."""
        from app.api.deps import get_current_active_admin
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
        )
        
        # Should not raise an exception
        result = get_current_active_admin(user)
        assert result == user

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_admin_dependency_denies_superuser(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Superuser users should be denied by the admin dependency check."""
        from app.api.deps import get_current_active_admin
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.SUPERUSER,
        )
        
        # Should raise HTTPException with 403 status
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_admin_dependency_denies_user(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Regular users should be denied by the admin dependency check."""
        from app.api.deps import get_current_active_admin
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
            role=UserRole.USER,
        )
        
        # Should raise HTTPException with 403 status
        with pytest.raises(HTTPException) as exc_info:
            get_current_active_admin(user)
        
        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "The user doesn't have enough privileges"

    @settings(max_examples=100)
    @given(role=st.sampled_from(list(UserRole)))
    def test_superuser_dependency_matches_role_hierarchy(
        self,
        role: UserRole,
    ) -> None:
        """Property 4: Superuser dependency allows iff role has superuser permission."""
        from app.api.deps import get_current_active_superuser
        from app.db_models.user import User
        
        user = User(
            email="test@example.com",
            hashed_password="test_password",
            role=role,
        )
        
        should_allow = role.has_permission(UserRole.SUPERUSER)
        
        if should_allow:
            result = get_current_active_superuser(user)
            assert result == user
        else:
            with pytest.raises(HTTPException) as exc_info:
                get_current_active_superuser(user)
            assert exc_info.value.status_code == 403

    @settings(max_examples=100)
    @given(role=st.sampled_from(list(UserRole)))
    def test_admin_dependency_matches_role_hierarchy(
        self,
        role: UserRole,
    ) -> None:
        """Property 4: Admin dependency allows iff role has admin permission."""
        from app.api.deps import get_current_active_admin
        from app.db_models.user import User
        
        user = User(
            email="test@example.com",
            hashed_password="test_password",
            role=role,
        )
        
        should_allow = role.has_permission(UserRole.ADMIN)
        
        if should_allow:
            result = get_current_active_admin(user)
            assert result == user
        else:
            with pytest.raises(HTTPException) as exc_info:
                get_current_active_admin(user)
            assert exc_info.value.status_code == 403
