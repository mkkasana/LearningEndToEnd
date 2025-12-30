"""Profile View Tracking database model."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class ProfileViewTracking(SQLModel, table=True):
    """Track profile view events for analytics."""

    __tablename__ = "profile_view_tracking"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique identifier for the view record",
    )

    viewed_person_id: uuid.UUID = Field(
        foreign_key="person.id",
        index=True,
        description="Person whose profile was viewed",
    )

    viewer_person_id: uuid.UUID = Field(
        foreign_key="person.id",
        index=True,
        description="Person who viewed the profile",
    )

    view_count: int = Field(
        default=1,
        description="Number of times viewed (for aggregated records)",
    )

    last_viewed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of most recent view",
    )

    is_aggregated: bool = Field(
        default=False,
        description="Whether this is an aggregated record",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Record creation timestamp",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Record last update timestamp",
    )
