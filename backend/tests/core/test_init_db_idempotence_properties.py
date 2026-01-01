"""Property-based tests for init_db idempotence.

**Feature: user-roles-permissions, Property 5: Init DB Idempotence**
**Validates: Requirements 4.3**

Note: These tests verify the init_db logic creates exactly one admin user.
The tests use in-memory SQLite to avoid dependency on PostgreSQL schema migrations.
"""

from hypothesis import HealthCheck, given, settings as hypothesis_settings
from hypothesis import strategies as st
from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings
from app.core.db import init_db
from app.db_models.user import User
from app.enums.user_role import UserRole


def create_fresh_session() -> Session:
    """Create a fresh in-memory SQLite session for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    SQLModel.metadata.create_all(engine)
    return Session(engine)


class TestInitDbIdempotence:
    """Tests for Property 5: Init DB Idempotence.
    
    **Feature: user-roles-permissions, Property 5: Init DB Idempotence**
    **Validates: Requirements 4.3**
    
    Tests that calling init_db multiple times creates exactly one admin user.
    """

    @hypothesis_settings(
        max_examples=100,
        deadline=None,  # Disable deadline due to bcrypt hashing time
    )
    @given(call_count=st.integers(min_value=1, max_value=10))
    def test_init_db_creates_exactly_one_admin(
        self,
        call_count: int,
    ) -> None:
        """Property 5: Calling init_db multiple times creates exactly one admin user.
        
        For any number of init_db calls, there should be exactly one user
        with the configured FIRST_SUPERUSER email and admin role.
        """
        # Create a fresh session for each hypothesis iteration
        session = create_fresh_session()
        
        try:
            # Call init_db multiple times
            for _ in range(call_count):
                init_db(session)
            
            # Query for admin users with the configured email
            admin_users = session.exec(
                select(User).where(
                    User.email == settings.FIRST_SUPERUSER,
                    User.role == UserRole.ADMIN,
                )
            ).all()
            
            assert len(admin_users) == 1, (
                f"Expected exactly 1 admin user with email {settings.FIRST_SUPERUSER}, "
                f"found {len(admin_users)} after {call_count} init_db calls"
            )
        finally:
            session.close()

    def test_init_db_creates_admin_with_correct_email(
        self,
        sqlite_session: Session,
    ) -> None:
        """The admin user should have the configured FIRST_SUPERUSER email."""
        init_db(sqlite_session)
        
        admin_user = sqlite_session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).first()
        
        assert admin_user is not None, (
            f"Admin user with email {settings.FIRST_SUPERUSER} should exist"
        )
        assert admin_user.role == UserRole.ADMIN, (
            f"First superuser should have ADMIN role, got {admin_user.role}"
        )

    def test_init_db_does_not_create_duplicate_on_second_call(
        self,
        sqlite_session: Session,
    ) -> None:
        """Calling init_db twice should not create a duplicate admin user."""
        # First call
        init_db(sqlite_session)
        count_after_first = sqlite_session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).all()
        
        # Second call
        init_db(sqlite_session)
        count_after_second = sqlite_session.exec(
            select(User).where(User.email == settings.FIRST_SUPERUSER)
        ).all()
        
        assert len(count_after_first) == len(count_after_second) == 1, (
            f"Expected 1 admin user after both calls, "
            f"got {len(count_after_first)} after first, {len(count_after_second)} after second"
        )
