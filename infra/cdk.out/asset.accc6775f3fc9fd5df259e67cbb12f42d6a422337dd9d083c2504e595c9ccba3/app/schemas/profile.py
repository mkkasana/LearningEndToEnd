"""Profile completion schemas."""

import uuid

from sqlmodel import SQLModel


class ProfileCompletionStatus(SQLModel):
    """Profile completion status response."""

    is_complete: bool
    has_person: bool
    has_address: bool
    has_religion: bool
    has_marital_status: bool
    has_duplicate_check: bool
    has_pending_attachment_request: bool
    pending_request_id: uuid.UUID | None
    missing_fields: list[str]
