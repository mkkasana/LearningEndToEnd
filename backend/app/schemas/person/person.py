"""Person schemas."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class PersonBase(SQLModel):
    """Base person properties."""

    first_name: str = Field(max_length=100, description="First name")
    middle_name: str | None = Field(
        default=None, max_length=100, description="Middle name"
    )
    last_name: str = Field(max_length=100, description="Last name")
    gender_id: uuid.UUID = Field(description="Gender reference")
    date_of_birth: date = Field(description="Date of birth")
    date_of_death: date | None = Field(default=None, description="Date of death")


class PersonCreate(PersonBase):
    """Schema for creating a new person."""

    user_id: uuid.UUID = Field(description="User account reference")


class PersonUpdate(SQLModel):
    """Schema for updating a person (all fields optional)."""

    first_name: str | None = Field(default=None, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    gender_id: uuid.UUID | None = None
    date_of_birth: date | None = None
    date_of_death: date | None = None


class PersonPublic(PersonBase):
    """Person response schema."""

    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
