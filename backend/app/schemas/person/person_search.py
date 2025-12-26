"""Person search schemas for matching existing persons."""

import uuid
from datetime import date

from sqlmodel import Field, SQLModel


class PersonSearchRequest(SQLModel):
    """Request schema for person matching search."""

    # Basic details
    first_name: str = Field(max_length=100, description="First name to search")
    last_name: str = Field(max_length=100, description="Last name to search")
    middle_name: str | None = Field(
        default=None, max_length=100, description="Middle name (optional)"
    )
    gender_id: uuid.UUID = Field(description="Gender ID")
    date_of_birth: date = Field(description="Date of birth")

    # Address criteria
    country_id: uuid.UUID = Field(description="Country reference")
    state_id: uuid.UUID = Field(description="State reference")
    district_id: uuid.UUID = Field(description="District reference")
    sub_district_id: uuid.UUID | None = Field(
        default=None, description="Sub-district reference"
    )
    locality_id: uuid.UUID | None = Field(default=None, description="Locality reference")

    # Religion criteria
    religion_id: uuid.UUID = Field(description="Religion reference")
    religion_category_id: uuid.UUID | None = Field(
        default=None, description="Religion category reference"
    )
    religion_sub_category_id: uuid.UUID | None = Field(
        default=None, description="Religion sub-category reference"
    )


class PersonMatchResult(SQLModel):
    """Result schema for person match."""

    # Person identification
    person_id: uuid.UUID = Field(description="Person ID")

    # Person details
    first_name: str = Field(description="First name")
    middle_name: str | None = Field(default=None, description="Middle name")
    last_name: str = Field(description="Last name")
    date_of_birth: date = Field(description="Date of birth")
    date_of_death: date | None = Field(default=None, description="Date of death")

    # Display strings
    address_display: str = Field(description="Comma-separated address display")
    religion_display: str = Field(description="Comma-separated religion display")

    # Match scoring
    match_score: float = Field(description="Overall match score 0-100")
    name_match_score: float = Field(description="Name similarity score 0-100")
