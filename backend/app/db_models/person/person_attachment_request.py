"""Person attachment request database model."""

import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlmodel import Field, SQLModel

from app.enums.attachment_request_status import AttachmentRequestStatus


class PersonAttachmentRequest(SQLModel, table=True):
    """Person attachment request model - Tracks requests from new users to attach to existing Person records."""

    __tablename__ = "person_attachment_request"

    # Primary key
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique attachment request identifier",
    )

    # The user requesting to attach to an existing person
    # Nullable because it gets cleared when the user is deleted on deny
    requester_user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="user.id",
        index=True,
        description="User requesting attachment",
    )

    # The temporary person record created during signup for the requester
    # Nullable because it gets cleared when the person is deleted on approve/deny
    requester_person_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="person.id",
        index=True,
        description="Requester's temporary person record",
    )

    # The existing person record the requester wants to attach to
    target_person_id: uuid.UUID = Field(
        foreign_key="person.id",
        index=True,
        description="Target person to attach to",
    )

    # The user who created the target person and must approve/deny
    approver_user_id: uuid.UUID = Field(
        foreign_key="user.id",
        index=True,
        description="User who must approve/deny the request",
    )

    # Request status
    status: AttachmentRequestStatus = Field(
        default=AttachmentRequestStatus.PENDING,
        sa_column=sa.Column(
            sa.String(20),
            nullable=False,
            default="pending",
        ),
        description="Current status of the attachment request",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the request was created",
    )

    resolved_at: datetime | None = Field(
        default=None,
        description="When the request was resolved (approved/denied/cancelled)",
    )

    # Who resolved the request
    resolved_by_user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="user.id",
        description="User who resolved the request",
    )
