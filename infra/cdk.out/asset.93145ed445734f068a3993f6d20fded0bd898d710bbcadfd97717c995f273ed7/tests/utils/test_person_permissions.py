"""Unit tests for person_permissions utility module.

This module tests the validate_person_access function which implements
the permission model for person-related API endpoints.
"""

import uuid
from datetime import date
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.db_models.user import User
from app.enums.user_role import UserRole
from app.utils.person_permissions import validate_person_access


def create_mock_person(
    person_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    created_by_user_id: uuid.UUID | None = None,
) -> MagicMock:
    """Create a mock Person object with the required attributes."""
    person = MagicMock()
    person.id = person_id
    person.user_id = user_id
    person.created_by_user_id = created_by_user_id
    person.first_name = "Test"
    person.last_name = "Person"
    return person


class TestValidatePersonAccess:
    """Test suite for validate_person_access() function."""

    @pytest.fixture
    def user_id(self) -> uuid.UUID:
        """Create a test user ID."""
        return uuid.uuid4()

    @pytest.fixture
    def other_user_id(self) -> uuid.UUID:
        """Create another test user ID."""
        return uuid.uuid4()

    @pytest.fixture
    def person_id(self) -> uuid.UUID:
        """Create a test person ID."""
        return uuid.uuid4()

    @pytest.fixture
    def gender_id(self) -> uuid.UUID:
        """Create a test gender ID."""
        return uuid.uuid4()

    @pytest.fixture
    def regular_user(self, user_id: uuid.UUID) -> User:
        """Create a regular user (USER role)."""
        user = User(
            id=user_id,
            email="regular@test.com",
            hashed_password="hashed",
            is_active=True,
            role=UserRole.USER,
        )
        return user

    @pytest.fixture
    def admin_user(self, user_id: uuid.UUID) -> User:
        """Create an admin user."""
        user = User(
            id=user_id,
            email="admin@test.com",
            hashed_password="hashed",
            is_active=True,
            role=UserRole.ADMIN,
        )
        return user

    @pytest.fixture
    def superuser(self, user_id: uuid.UUID) -> User:
        """Create a superuser."""
        user = User(
            id=user_id,
            email="super@test.com",
            hashed_password="hashed",
            is_active=True,
            role=UserRole.SUPERUSER,
        )
        return user

    # ========================================================================
    # Test: Person not found (404)
    # ========================================================================

    def test_person_not_found_raises_404(self, regular_user: User) -> None:
        """Test that None person raises 404 HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            validate_person_access(None, regular_user)

        assert exc_info.value.status_code == 404
        assert "not found" in exc_info.value.detail.lower()

    # ========================================================================
    # Test: User's own person (user_id matches)
    # ========================================================================

    def test_user_can_access_own_person(
        self, regular_user: User, person_id: uuid.UUID
    ) -> None:
        """Test that user can access their own person (user_id matches)."""
        person = create_mock_person(
            person_id=person_id,
            user_id=regular_user.id,  # User's own person
            created_by_user_id=regular_user.id,
        )

        result = validate_person_access(person, regular_user)
        assert result == person

    def test_user_can_access_own_person_even_if_created_by_other(
        self, regular_user: User, person_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> None:
        """Test that user can access their own person even if created by another user."""
        person = create_mock_person(
            person_id=person_id,
            user_id=regular_user.id,  # User's own person
            created_by_user_id=other_user_id,  # Created by someone else
        )

        result = validate_person_access(person, regular_user)
        assert result == person

    # ========================================================================
    # Test: Person created by user (created_by_user_id matches)
    # ========================================================================

    def test_user_can_access_person_they_created(
        self, regular_user: User, person_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> None:
        """Test that user can access a person they created."""
        person = create_mock_person(
            person_id=person_id,
            user_id=other_user_id,  # Not user's own person
            created_by_user_id=regular_user.id,  # Created by this user
        )

        result = validate_person_access(person, regular_user)
        assert result == person

    def test_user_can_access_family_member_without_user_id(
        self, regular_user: User, person_id: uuid.UUID
    ) -> None:
        """Test that user can access a family member (no user_id) they created."""
        person = create_mock_person(
            person_id=person_id,
            user_id=None,  # Family member without account
            created_by_user_id=regular_user.id,  # Created by this user
        )

        result = validate_person_access(person, regular_user)
        assert result == person

    def test_allow_created_by_false_denies_creator_access(
        self, regular_user: User, person_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> None:
        """Test that allow_created_by=False denies access to creator."""
        person = create_mock_person(
            person_id=person_id,
            user_id=other_user_id,  # Not user's own person
            created_by_user_id=regular_user.id,  # Created by this user
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_person_access(person, regular_user, allow_created_by=False)

        assert exc_info.value.status_code == 403
        assert "not authorized" in exc_info.value.detail.lower()

    # ========================================================================
    # Test: Admin access
    # ========================================================================

    def test_admin_can_access_any_person(
        self, admin_user: User, person_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> None:
        """Test that admin can access any person."""
        person = create_mock_person(
            person_id=person_id,
            user_id=other_user_id,  # Not admin's person
            created_by_user_id=other_user_id,  # Not created by admin
        )

        result = validate_person_access(person, admin_user)
        assert result == person

    def test_superuser_cannot_access_unrelated_person(
        self, superuser: User, person_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> None:
        """Test that superuser cannot access unrelated person (only ADMIN has override).
        
        Note: The validate_person_access function only grants admin override to ADMIN role,
        not SUPERUSER. SUPERUSER can only access persons they own or created.
        """
        person = create_mock_person(
            person_id=person_id,
            user_id=other_user_id,  # Not superuser's person
            created_by_user_id=other_user_id,  # Not created by superuser
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_person_access(person, superuser)

        assert exc_info.value.status_code == 403

    # ========================================================================
    # Test: Access denied (403)
    # ========================================================================

    def test_user_cannot_access_unrelated_person(
        self, regular_user: User, person_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> None:
        """Test that user cannot access a person they didn't create and don't own."""
        person = create_mock_person(
            person_id=person_id,
            user_id=other_user_id,  # Not user's person
            created_by_user_id=other_user_id,  # Not created by user
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_person_access(person, regular_user)

        assert exc_info.value.status_code == 403
        assert "not authorized" in exc_info.value.detail.lower()

    def test_user_cannot_access_person_with_no_creator(
        self, regular_user: User, person_id: uuid.UUID, other_user_id: uuid.UUID
    ) -> None:
        """Test that user cannot access a person with no creator set."""
        person = create_mock_person(
            person_id=person_id,
            user_id=other_user_id,  # Not user's person
            created_by_user_id=None,  # No creator
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_person_access(person, regular_user)

        assert exc_info.value.status_code == 403
        assert "not authorized" in exc_info.value.detail.lower()

    # ========================================================================
    # Test: Edge cases
    # ========================================================================

    def test_user_id_none_and_created_by_none_denies_access(
        self, regular_user: User, person_id: uuid.UUID
    ) -> None:
        """Test that person with no user_id and no creator denies access."""
        person = create_mock_person(
            person_id=person_id,
            user_id=None,  # No user
            created_by_user_id=None,  # No creator
        )

        with pytest.raises(HTTPException) as exc_info:
            validate_person_access(person, regular_user)

        assert exc_info.value.status_code == 403

    def test_admin_can_access_orphan_person(
        self, admin_user: User, person_id: uuid.UUID
    ) -> None:
        """Test that admin can access a person with no user_id and no creator."""
        person = create_mock_person(
            person_id=person_id,
            user_id=None,  # No user
            created_by_user_id=None,  # No creator
        )

        result = validate_person_access(person, admin_user)
        assert result == person
