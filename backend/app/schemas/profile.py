"""Profile completion schemas."""

from sqlmodel import SQLModel


class ProfileCompletionStatus(SQLModel):
    """Profile completion status response."""

    is_complete: bool
    has_person: bool
    has_address: bool
    missing_fields: list[str]
