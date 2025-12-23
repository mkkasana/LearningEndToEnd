"""Person Address association database model."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel


class PersonAddress(SQLModel, table=True):
    """Person Address model - Associates persons with addresses over time."""

    __tablename__ = "person_address"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    person_id: uuid.UUID = Field(
        foreign_key="person.user_id", index=True, description="Person reference"
    )
    country_id: uuid.UUID = Field(
        foreign_key="address_country.id", description="Country reference"
    )
    state_id: uuid.UUID | None = Field(
        default=None, foreign_key="address_state.id", description="State reference"
    )
    district_id: uuid.UUID | None = Field(
        default=None, foreign_key="address_district.id", description="District reference"
    )
    sub_district_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="address_sub_district.id",
        description="Sub-district reference",
    )
    locality_id: uuid.UUID | None = Field(
        default=None, foreign_key="address_locality.id", description="Locality reference"
    )
    address_line: str | None = Field(
        default=None, description="Additional address details"
    )
    start_date: date = Field(description="Address start date")
    end_date: date | None = Field(default=None, description="Address end date")
    is_current: bool = Field(default=False, description="Is this the current address")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
