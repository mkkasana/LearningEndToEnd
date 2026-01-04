"""Life Event schemas."""

import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class LifeEventType(str, Enum):
    """Enum for life event types."""

    BIRTH = "birth"
    MARRIAGE = "marriage"
    DEATH = "death"
    PURCHASE = "purchase"
    SALE = "sale"
    ACHIEVEMENT = "achievement"
    EDUCATION = "education"
    CAREER = "career"
    HEALTH = "health"
    TRAVEL = "travel"
    OTHER = "other"


class LifeEventBase(SQLModel):
    """Base life event properties."""

    event_type: LifeEventType = Field(description="Type of life event")
    title: str = Field(
        min_length=1, max_length=100, description="Event title (max 100 characters)"
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Event description (max 500 characters)",
    )
    event_year: int = Field(description="Year when the event occurred")
    event_month: int | None = Field(
        default=None, ge=1, le=12, description="Month when the event occurred (1-12)"
    )
    event_date: int | None = Field(
        default=None, ge=1, le=31, description="Day when the event occurred (1-31)"
    )
    country_id: uuid.UUID | None = Field(default=None, description="Country reference")
    state_id: uuid.UUID | None = Field(default=None, description="State reference")
    district_id: uuid.UUID | None = Field(
        default=None, description="District reference"
    )
    sub_district_id: uuid.UUID | None = Field(
        default=None, description="Sub-district reference"
    )
    locality_id: uuid.UUID | None = Field(
        default=None, description="Locality reference"
    )
    address_details: str | None = Field(
        default=None,
        max_length=30,
        description="Additional address details (max 30 characters)",
    )


class LifeEventCreate(LifeEventBase):
    """Schema for creating a new life event."""

    pass


class LifeEventUpdate(SQLModel):
    """Schema for updating a life event (all fields optional)."""

    event_type: LifeEventType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    event_year: int | None = None
    event_month: int | None = Field(default=None, ge=1, le=12)
    event_date: int | None = Field(default=None, ge=1, le=31)
    country_id: uuid.UUID | None = None
    state_id: uuid.UUID | None = None
    district_id: uuid.UUID | None = None
    sub_district_id: uuid.UUID | None = None
    locality_id: uuid.UUID | None = None
    address_details: str | None = Field(default=None, max_length=30)


class LifeEventPublic(LifeEventBase):
    """Life event response schema."""

    id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class LifeEventsPublic(SQLModel):
    """List of life events response."""

    data: list[LifeEventPublic]
    count: int
