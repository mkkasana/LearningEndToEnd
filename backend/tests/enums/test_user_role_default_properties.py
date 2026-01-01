"""Property-based tests for default role assignment.

**Feature: user-roles-permissions, Property 2: Default Role Assignment**
**Validates: Requirements 1.3**

Note: These tests do not require database access as they test in-memory object creation.
The User model import is done inside test functions to avoid triggering the db fixture.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from app.enums.user_role import UserRole
from app.schemas.user import UserBase


# Custom strategy for valid email addresses
def valid_emails() -> st.SearchStrategy[str]:
    """Generate valid email addresses."""
    return st.emails()


# Custom strategy for text without NUL bytes (PostgreSQL doesn't allow them)
def text_without_nul(min_size: int = 0, max_size: int | None = None) -> st.SearchStrategy[str]:
    """Generate text without NUL bytes which PostgreSQL/UTF-8 rejects."""
    return st.text(
        min_size=min_size,
        max_size=max_size,
        alphabet=st.characters(
            blacklist_categories=("Cs",),  # Surrogate characters
            blacklist_characters="\x00",  # NUL byte
        ),
    )


class TestDefaultRoleAssignment:
    """Tests for Property 2: Default Role Assignment.
    
    **Feature: user-roles-permissions, Property 2: Default Role Assignment**
    **Validates: Requirements 1.3**
    
    Tests that users created without role get UserRole.USER.
    """

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_user_model_default_role_is_user(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Property 2: User model created without role defaults to USER.
        
        For any user creation where no role is specified, the resulting
        user must have role equal to UserRole.USER.
        """
        # Import inside function to avoid triggering db fixture at module load
        from app.db_models.user import User
        
        # Create user without specifying role
        user = User(
            email=email,
            hashed_password=hashed_password,
        )
        
        assert user.role == UserRole.USER, (
            f"User created without role should default to USER, got {user.role}"
        )

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_user_model_default_is_not_superuser(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Default user should not be a superuser."""
        # Import inside function to avoid triggering db fixture at module load
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
        )
        
        assert user.is_superuser is False, (
            "User created without role should not be a superuser"
        )

    @settings(max_examples=100)
    @given(
        email=valid_emails(),
        hashed_password=text_without_nul(min_size=1, max_size=100),
    )
    def test_user_model_default_is_not_admin(
        self,
        email: str,
        hashed_password: str,
    ) -> None:
        """Default user should not be an admin."""
        # Import inside function to avoid triggering db fixture at module load
        from app.db_models.user import User
        
        user = User(
            email=email,
            hashed_password=hashed_password,
        )
        
        assert user.is_admin is False, (
            "User created without role should not be an admin"
        )

    @settings(max_examples=100)
    @given(email=valid_emails())
    def test_user_schema_default_role_is_user(
        self,
        email: str,
    ) -> None:
        """Property 2: UserBase schema created without role defaults to USER.
        
        For any user schema creation where no role is specified, the resulting
        schema must have role equal to UserRole.USER.
        """
        # Create schema without specifying role
        user_base = UserBase(email=email)
        
        assert user_base.role == UserRole.USER, (
            f"UserBase created without role should default to USER, got {user_base.role}"
        )
