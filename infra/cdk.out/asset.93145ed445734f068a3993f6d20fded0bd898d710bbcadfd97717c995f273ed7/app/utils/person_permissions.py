"""Person permission validation utilities.

This module provides reusable permission checking functions for person-related
API endpoints. It implements the permission model defined in Requirements 6.1-6.5.
"""

from fastapi import HTTPException, status

from app.db_models.person.person import Person
from app.db_models.user import User


def validate_person_access(
    person: Person | None,
    current_user: User,
    allow_created_by: bool = True,
) -> Person:
    """Validate that the current user has permission to access/modify a person.

    Permission is granted if any of the following conditions are met:
    1. The person's user_id matches the current user's id (user's own person)
       - Requirements: 6.1
    2. The person's created_by_user_id matches the current user's id (person created by user)
       - Requirements: 6.2
    3. The current user has ADMIN role (admin override)
       - Requirements: 6.3

    Args:
        person: The person to validate access for (or None if not found)
        current_user: The currently authenticated user
        allow_created_by: Whether to allow access if user created the person.
                         Defaults to True. Set to False for stricter access control.

    Returns:
        The person if access is allowed

    Raises:
        HTTPException: 404 if person not found, 403 if access denied
            - Requirements: 6.4, 6.5
    """
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )

    # Check if user owns this person (their primary person)
    # Requirements: 6.1
    if person.user_id == current_user.id:
        return person

    # Check if user created this person
    # Requirements: 6.2
    if allow_created_by and person.created_by_user_id == current_user.id:
        return person

    # Check if user is admin
    # Requirements: 6.3
    if current_user.is_admin:
        return person

    # None of the conditions met - deny access
    # Requirements: 6.4
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized to access this person",
    )
