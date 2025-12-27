"""SupportTicket database model."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class SupportTicket(SQLModel, table=True):
    """SupportTicket model - User-submitted bug reports and feature requests."""

    __tablename__ = "support_ticket"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", index=True, description="User who created the ticket"
    )
    issue_type: str = Field(
        max_length=20, description="Type of issue: bug or feature_request"
    )
    title: str = Field(max_length=100, description="Ticket title")
    description: str = Field(description="Detailed description of the issue")
    status: str = Field(
        default="open", max_length=20, index=True, description="Ticket status: open or closed"
    )
    resolved_by_user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", description="Admin who resolved the ticket"
    )
    resolved_at: datetime | None = Field(
        default=None, description="Timestamp when ticket was resolved"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, index=True, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
