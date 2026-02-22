"""User factory for creating test User entities."""

import uuid
from typing import Any

from sqlmodel import Session

from app.core.security import get_password_hash
from app.db_models.user import User
from app.enums.user_role import UserRole


class UserFactory:
    """Factory for creating User test entities."""

    _counter = 0

    @classmethod
    def _get_unique_suffix(cls) -> str:
        """Generate a unique suffix for test data."""
        cls._counter += 1
        return f"{cls._counter}_{uuid.uuid4().hex[:8]}"

    @classmethod
    def create(
        cls,
        session: Session,
        *,
        email: str | None = None,
        password: str = "testpassword123",
        is_active: bool = True,
        is_superuser: bool = False,
        role: UserRole | None = None,
        full_name: str | None = None,
        commit: bool = True,
    ) -> User:
        """Create a User entity with sensible defaults.

        Args:
            session: Database session
            email: User email (auto-generated if not provided)
            password: Plain text password (will be hashed)
            is_active: Whether user is active
            is_superuser: Whether user is a superuser (deprecated, use role instead)
            role: User role (USER, SUPERUSER, or ADMIN)
            full_name: User's full name
            commit: Whether to commit the transaction

        Returns:
            Created User entity
        """
        if email is None:
            suffix = cls._get_unique_suffix()
            email = f"test_user_{suffix}@example.com"

        # Determine role: explicit role takes precedence, then is_superuser for backward compatibility
        if role is None:
            role = UserRole.SUPERUSER if is_superuser else UserRole.USER

        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=is_active,
            role=role,
            full_name=full_name,
        )

        session.add(user)
        if commit:
            session.commit()
            session.refresh(user)

        return user

    @classmethod
    def create_superuser(
        cls,
        session: Session,
        *,
        email: str | None = None,
        password: str = "superpassword123",
        commit: bool = True,
    ) -> User:
        """Create a superuser for testing elevated functionality.

        Args:
            session: Database session
            email: User email (auto-generated if not provided)
            password: Plain text password
            commit: Whether to commit the transaction

        Returns:
            Created superuser entity
        """
        return cls.create(
            session,
            email=email,
            password=password,
            role=UserRole.SUPERUSER,
            full_name="Test Superuser",
            commit=commit,
        )

    @classmethod
    def create_admin(
        cls,
        session: Session,
        *,
        email: str | None = None,
        password: str = "adminpassword123",
        commit: bool = True,
    ) -> User:
        """Create an admin user for testing admin functionality.

        Args:
            session: Database session
            email: User email (auto-generated if not provided)
            password: Plain text password
            commit: Whether to commit the transaction

        Returns:
            Created admin entity
        """
        return cls.create(
            session,
            email=email,
            password=password,
            role=UserRole.ADMIN,
            full_name="Test Admin",
            commit=commit,
        )

    @classmethod
    def build(
        cls,
        *,
        email: str | None = None,
        password: str = "testpassword123",
        is_active: bool = True,
        is_superuser: bool = False,
        role: UserRole | None = None,
        full_name: str | None = None,
    ) -> User:
        """Build a User entity without persisting to database.

        Useful for unit tests with mocked sessions.

        Args:
            email: User email (auto-generated if not provided)
            password: Plain text password (will be hashed)
            is_active: Whether user is active
            is_superuser: Whether user is a superuser (deprecated, use role instead)
            role: User role (USER, SUPERUSER, or ADMIN)
            full_name: User's full name

        Returns:
            User entity (not persisted)
        """
        if email is None:
            suffix = cls._get_unique_suffix()
            email = f"test_user_{suffix}@example.com"

        # Determine role: explicit role takes precedence, then is_superuser for backward compatibility
        if role is None:
            role = UserRole.SUPERUSER if is_superuser else UserRole.USER

        return User(
            id=uuid.uuid4(),
            email=email,
            hashed_password=get_password_hash(password),
            is_active=is_active,
            role=role,
            full_name=full_name,
        )

    @classmethod
    def create_batch(
        cls,
        session: Session,
        count: int,
        *,
        commit: bool = True,
        **kwargs: Any,
    ) -> list[User]:
        """Create multiple User entities.

        Args:
            session: Database session
            count: Number of users to create
            commit: Whether to commit after all users are created
            **kwargs: Additional arguments passed to create()

        Returns:
            List of created User entities
        """
        users = []
        for _ in range(count):
            user = cls.create(session, commit=False, **kwargs)
            users.append(user)

        if commit:
            session.commit()
            for user in users:
                session.refresh(user)

        return users
