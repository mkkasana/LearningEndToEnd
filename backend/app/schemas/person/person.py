"""Person schemas."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.enums.marital_status import MaritalStatus


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
    marital_status: MaritalStatus = Field(
        default=MaritalStatus.UNKNOWN,
        description="Person's marital status",
    )


class PersonCreate(PersonBase):
    """Schema for creating a new person."""

    user_id: uuid.UUID | None = Field(
        default=None, description="User account reference (optional for family members)"
    )
    is_primary: bool = Field(
        default=False, description="Is this the primary person for the user"
    )


class PersonUpdate(SQLModel):
    """Schema for updating a person (all fields optional)."""

    first_name: str | None = Field(default=None, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    gender_id: uuid.UUID | None = None
    date_of_birth: date | None = None
    date_of_death: date | None = None
    religion_id: uuid.UUID | None = None
    religion_category_id: uuid.UUID | None = None
    religion_sub_category_id: uuid.UUID | None = None
    marital_status: MaritalStatus | None = None


class PersonPublic(PersonBase):
    """Person response schema."""

    id: uuid.UUID
    user_id: uuid.UUID | None
    created_by_user_id: uuid.UUID
    is_primary: bool
    created_at: datetime
    updated_at: datetime
