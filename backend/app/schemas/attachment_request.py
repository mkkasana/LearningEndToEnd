"""Attachment request schemas."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.enums.attachment_request_status import AttachmentRequestStatus


class AttachmentRequestCreate(SQLModel):
    """Schema for creating an attachment request."""

    target_person_id: uuid.UUID = Field(
        description="The existing person record to attach to"
    )


class AttachmentRequestPublic(SQLModel):
    """Schema for public attachment request response."""

    id: uuid.UUID
    requester_user_id: uuid.UUID
    requester_person_id: uuid.UUID
    target_person_id: uuid.UUID
    approver_user_id: uuid.UUID
    status: AttachmentRequestStatus
    created_at: datetime
    resolved_at: datetime | None
    resolved_by_user_id: uuid.UUID | None


class AttachmentRequestWithDetails(SQLModel):
    """Schema for attachment request with requester and target details.

    Used for the approver's view of pending requests.
    """

    id: uuid.UUID
    status: AttachmentRequestStatus
    created_at: datetime

    # Requester details
    requester_first_name: str = Field(description="Requester's first name")
    requester_middle_name: str | None = Field(
        default=None, description="Requester's middle name"
    )
    requester_last_name: str = Field(description="Requester's last name")
    requester_date_of_birth: date = Field(description="Requester's date of birth")
    requester_gender: str = Field(description="Requester's gender display name")
    requester_address_display: str | None = Field(
        default=None, description="Requester's formatted address"
    )
    requester_religion_display: str | None = Field(
        default=None, description="Requester's formatted religion"
    )

    # Target person details
    target_first_name: str = Field(description="Target person's first name")
    target_middle_name: str | None = Field(
        default=None, description="Target person's middle name"
    )
    target_last_name: str = Field(description="Target person's last name")
    target_date_of_birth: date = Field(description="Target person's date of birth")


class MyPendingRequestResponse(SQLModel):
    """Schema for requester's pending request view."""

    id: uuid.UUID
    status: AttachmentRequestStatus
    created_at: datetime

    # Target person details
    target_first_name: str = Field(description="Target person's first name")
    target_middle_name: str | None = Field(
        default=None, description="Target person's middle name"
    )
    target_last_name: str = Field(description="Target person's last name")
    target_date_of_birth: date = Field(description="Target person's date of birth")
    target_gender: str = Field(description="Target person's gender display name")


class PendingCountResponse(SQLModel):
    """Schema for pending request count response."""

    count: int = Field(description="Number of pending requests for the user to approve")
