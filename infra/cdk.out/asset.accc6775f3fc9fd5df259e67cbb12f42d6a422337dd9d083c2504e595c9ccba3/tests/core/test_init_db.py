"""Property-based tests for init_db function.

**Feature: user-roles-permissions, Property 5: Init DB Idempotence**
**Validates: Requirements 4.3**
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from sqlmodel import Session, select

from app.core.config import settings as app_settings
from app.core.db import init_db
from app.db_models.user import User
from app.enums.user_role import UserRole
from tests.test_db import test_engine


@pytest.mark.unit
class TestInitDbIdempotence:
    """Tests for Property 5: Init DB Idempotence.
    
    **Feature: user-roles-permissions, Property 5: Init DB Idempotence**
    **Validates: Requirements 4.3**
    
    Tests that calling init_db multiple times creates exactly one admin user
    with the configured email, never creating duplicates.
    """

    @settings(max_examples=100)
    @given(call_count=st.integers(min_value=1, max_value=10))
    def test_init_db_creates_exactly_one_admin_user(self, call_count: int) -> None:
        """Property 5: For any number of init_db calls, exactly one admin user
        with the configured email should exist.
        
        This tests idempotence - calling init_db multiple times should not
        create duplicate admin users.
        """
        with Session(test_engine) as session:
            # Call init_db multiple times
            for _ in range(call_count):
                init_db(session)
            
            # Query for users with the first superuser email
            admin_users = session.exec(
                select(User).where(User.email == app_settings.FIRST_SUPERUSER)
            ).all()
            
            # Should have exactly one user with this email
            assert len(admin_users) == 1, (
                f"Expected exactly 1 admin user with email {app_settings.FIRST_SUPERUSER}, "
                f"found {len(admin_users)} after {call_count} init_db calls"
            )
            
            # The user should have admin role
            admin_user = admin_users[0]
            assert admin_user.role == UserRole.ADMIN, (
                f"First user should have ADMIN role, got {admin_user.role}"
            )

    def test_init_db_creates_admin_with_correct_email(self, db: Session) -> None:
        """Test that init_db creates admin user with configured email.
        
        **Validates: Requirements 4.1, 4.2**
        """
        # init_db is already called in the db fixture
        admin_user = db.exec(
            select(User).where(User.email == app_settings.FIRST_SUPERUSER)
        ).first()
        
        assert admin_user is not None, "Admin user should exist after init_db"
        assert admin_user.email == app_settings.FIRST_SUPERUSER
        assert admin_user.role == UserRole.ADMIN

    def test_init_db_does_not_create_duplicate_on_second_call(self, db: Session) -> None:
        """Test that calling init_db again does not create a duplicate admin.
        
        **Validates: Requirements 4.3**
        """
        # Count admin users before second init_db call
        initial_count = len(db.exec(
            select(User).where(User.email == app_settings.FIRST_SUPERUSER)
        ).all())
        
        # Call init_db again
        init_db(db)
        
        # Count admin users after
        final_count = len(db.exec(
            select(User).where(User.email == app_settings.FIRST_SUPERUSER)
        ).all())
        
        assert initial_count == final_count == 1, (
            f"Admin user count should remain 1, was {initial_count} before, "
            f"{final_count} after second init_db call"
        )
