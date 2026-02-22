"""Person Profession association schemas."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class PersonProfessionBase(SQLModel):
    """Base person profession properties."""

    profession_id: uuid.UUID = Field(description="Profession reference")
    start_date: date = Field(description="Profession start date")
    end_date: date | None = Field(default=None, description="Profession end date")
    is_current: bool = Field(
        default=False, description="Is this the current profession"
    )


class PersonProfessionCreate(PersonProfessionBase):
    """Schema for creating a new person profession."""

    pass


class PersonProfessionUpdate(SQLModel):
    """Schema for updating a person profession (all fields optional)."""

    profession_id: uuid.UUID | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None


class PersonProfessionPublic(PersonProfessionBase):
    """Person profession response schema."""

    id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
