"""Person Address schemas."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class PersonAddressBase(SQLModel):
    """Base person address properties."""

    country_id: uuid.UUID = Field(description="Country reference")
    state_id: uuid.UUID | None = Field(default=None, description="State reference")
    district_id: uuid.UUID | None = Field(default=None, description="District reference")
    sub_district_id: uuid.UUID | None = Field(
        default=None, description="Sub-district reference"
    )
    locality_id: uuid.UUID | None = Field(default=None, description="Locality reference")
    address_line: str | None = Field(default=None, description="Additional address details")
    start_date: date = Field(description="Address start date")
    end_date: date | None = Field(default=None, description="Address end date")
    is_current: bool = Field(default=False, description="Is this the current address")


class PersonAddressCreate(PersonAddressBase):
    """Schema for creating a new person address."""

    pass


class PersonAddressUpdate(SQLModel):
    """Schema for updating a person address (all fields optional)."""

    country_id: uuid.UUID | None = None
    state_id: uuid.UUID | None = None
    district_id: uuid.UUID | None = None
    sub_district_id: uuid.UUID | None = None
    locality_id: uuid.UUID | None = None
    address_line: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None


class PersonAddressPublic(PersonAddressBase):
    """Person address response schema."""

    id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
