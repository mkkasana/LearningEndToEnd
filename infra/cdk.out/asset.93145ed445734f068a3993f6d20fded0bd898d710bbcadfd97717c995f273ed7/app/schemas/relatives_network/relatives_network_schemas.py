"""Relatives Network schemas for finding relatives within a family network."""

from __future__ import annotations

import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class RelativesNetworkRequest(BaseModel):
    """Request body for relatives network search."""

    person_id: uuid.UUID = Field(description="The person to find relatives for")
    depth: int = Field(
        default=3,
        ge=1,
        description="Search depth (number of relationship hops)",
    )
    depth_mode: Literal["up_to", "only_at"] = Field(
        default="up_to",
        description="'up_to' returns all relatives from depth 1 to N, 'only_at' returns only relatives at exactly depth N",
    )
    living_only: bool = Field(
        default=True,
        description="If True, exclude deceased relatives (those with date_of_death)",
    )
    gender_id: uuid.UUID | None = Field(
        default=None,
        description="Filter by gender ID",
    )
    # Address filters (all optional)
    country_id: uuid.UUID | None = Field(
        default=None,
        description="Filter by country ID",
    )
    state_id: uuid.UUID | None = Field(
        default=None,
        description="Filter by state ID",
    )
    district_id: uuid.UUID | None = Field(
        default=None,
        description="Filter by district ID",
    )
    sub_district_id: uuid.UUID | None = Field(
        default=None,
        description="Filter by sub-district ID",
    )
    locality_id: uuid.UUID | None = Field(
        default=None,
        description="Filter by locality ID",
    )

    @field_validator("depth_mode")
    @classmethod
    def validate_depth_mode(cls, v: str) -> str:
        """Validate that depth_mode is either 'up_to' or 'only_at'."""
        if v not in ("up_to", "only_at"):
            raise ValueError("Invalid depth mode. Use 'up_to' or 'only_at'")
        return v


class RelativeInfo(BaseModel):
    """Information about a single relative."""

    person_id: uuid.UUID = Field(description="Person ID")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    gender_id: uuid.UUID = Field(description="Gender ID")
    birth_year: int | None = Field(
        default=None,
        description="Birth year",
    )
    death_year: int | None = Field(
        default=None,
        description="Death year (if deceased)",
    )
    district_name: str | None = Field(
        default=None,
        description="District name from address",
    )
    locality_name: str | None = Field(
        default=None,
        description="Locality/village name from address",
    )
    depth: int = Field(
        description="Number of relationship hops from the requesting person",
    )


class RelativesNetworkResponse(BaseModel):
    """Response for relatives network search."""

    person_id: uuid.UUID = Field(
        description="The person ID from the request",
    )
    total_count: int = Field(
        description="Total number of relatives found",
    )
    depth: int = Field(
        description="The depth value used in the search",
    )
    depth_mode: str = Field(
        description="The depth mode used ('up_to' or 'only_at')",
    )
    relatives: list[RelativeInfo] = Field(
        default_factory=list,
        description="List of relatives found",
    )
