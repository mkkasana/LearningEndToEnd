"""Profile completion schemas."""

from sqlmodel import SQLModel


class ProfileCompletionStatus(SQLModel):
    """Profile completion status response."""

    is_complete: bool
    has_person: bool
    has_address: bool
    has_religion: bool
    has_marital_status: bool
    missing_fields: list[str]
