"""Person assume role schemas.

Schemas for the "Assume Person Role" feature that allows elevated users
(SuperUser/Admin) to act on behalf of persons they created.

_Requirements: 2.1, 2.4_
"""

import uuid

from sqlmodel import Field, SQLModel


class CanAssumeResponse(SQLModel):
    """Response for can-assume permission check.
    
    Returns whether the current user can assume the role of a specific person,
    along with the reason if denied and the person's name if allowed.
    
    _Requirements: 2.1, 2.4_
    """

    can_assume: bool = Field(
        description="Whether the user can assume this person's role"
    )
    reason: str | None = Field(
        default=None,
        description="Reason if assumption is denied (not_elevated_user, not_creator, person_not_found)",
    )
    person_name: str | None = Field(
        default=None,
        description="Full name of the person if assumption is allowed",
    )


class AssumedPersonContext(SQLModel):
    """Context information for an assumed person.
    
    Contains the essential information about a person being assumed,
    used for frontend display and validation.
    """

    person_id: uuid.UUID = Field(description="ID of the assumed person")
    first_name: str = Field(description="First name of the assumed person")
    last_name: str = Field(description="Last name of the assumed person")
    created_by_user_id: uuid.UUID = Field(
        description="ID of the user who created this person"
    )
