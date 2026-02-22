"""Person Religion schemas."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PersonReligionBase(SQLModel):
    """Base person religion properties."""

    religion_id: uuid.UUID = Field(description="Religion reference")
    religion_category_id: uuid.UUID | None = Field(
        default=None, description="Religion category reference"
    )
    religion_sub_category_id: uuid.UUID | None = Field(
        default=None, description="Religion sub-category reference"
    )


class PersonReligionCreate(PersonReligionBase):
    """Schema for creating person religion."""

    pass


class PersonReligionUpdate(SQLModel):
    """Schema for updating person religion (all fields optional)."""

    religion_id: uuid.UUID | None = None
    religion_category_id: uuid.UUID | None = None
    religion_sub_category_id: uuid.UUID | None = None


class PersonReligionPublic(PersonReligionBase):
    """Person religion response schema."""

    id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
