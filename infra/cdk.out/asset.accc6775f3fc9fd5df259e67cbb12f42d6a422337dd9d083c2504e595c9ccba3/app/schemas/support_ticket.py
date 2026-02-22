"""SupportTicket schemas."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class IssueType(str, Enum):
    """Enum for ticket types."""

    BUG = "bug"
    FEATURE_REQUEST = "feature_request"


class IssueStatus(str, Enum):
    """Enum for ticket status."""

    OPEN = "open"
    CLOSED = "closed"


class SupportTicketCreate(SQLModel):
    """Schema for creating a new support ticket."""

    issue_type: IssueType = Field(description="Type of issue: bug or feature_request")
    title: str = Field(
        min_length=1, max_length=100, description="Ticket title (max 100 characters)"
    )
    description: str = Field(
        min_length=1,
        max_length=2000,
        description="Detailed description (max 2000 characters)",
    )


class SupportTicketUpdate(SQLModel):
    """Schema for updating a support ticket (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=2000)


class SupportTicketPublic(SQLModel):
    """Support ticket response schema."""

    id: uuid.UUID
    user_id: uuid.UUID
    issue_type: IssueType
    title: str
    description: str
    status: IssueStatus
    resolved_by_user_id: uuid.UUID | None
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SupportTicketPublicWithUser(SupportTicketPublic):
    """Support ticket response schema with user details (for admin view)."""

    user_email: str = Field(description="Email of the user who created the ticket")
    user_full_name: str | None = Field(
        default=None, description="Full name of the user who created the ticket"
    )
    resolved_by_email: str | None = Field(
        default=None, description="Email of the admin who resolved the ticket"
    )


class SupportTicketsPublic(SQLModel):
    """List of support tickets response."""

    data: list[SupportTicketPublic]
    count: int
