"""Person Life Event database model."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PersonLifeEvent(SQLModel, table=True):
    """Person Life Event model - Records significant life events for a person."""

    __tablename__ = "person_life_event"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        description="Unique life event identifier",
    )
    person_id: uuid.UUID = Field(
        foreign_key="person.id",
        index=True,
        description="Person reference",
    )
    event_type: str = Field(
        max_length=50,
        description="Type of life event (birth, marriage, death, purchase, sale, achievement, education, career, health, travel, other)",
    )
    title: str = Field(
        max_length=100,
        description="Event title",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Event description",
    )
    event_year: int = Field(
        description="Year when the event occurred",
    )
    event_month: int | None = Field(
        default=None,
        ge=1,
        le=12,
        description="Month when the event occurred (1-12)",
    )
    event_date: int | None = Field(
        default=None,
        ge=1,
        le=31,
        description="Day when the event occurred (1-31)",
    )
    country_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="address_country.id",
        description="Country reference",
    )
    state_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="address_state.id",
        description="State reference",
    )
    district_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="address_district.id",
        description="District reference",
    )
    sub_district_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="address_sub_district.id",
        description="Sub-district reference",
    )
    locality_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="address_locality.id",
        description="Locality reference",
    )
    address_details: str | None = Field(
        default=None,
        max_length=30,
        description="Additional address details",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp",
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp",
    )
