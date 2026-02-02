"""Person search schemas for matching existing persons."""

import uuid
from datetime import date
from typing import Any

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel

# =============================================================================
# Global Person Search Schemas (for Search Page)
# =============================================================================


class PersonSearchFilterRequest(SQLModel):
    """Request schema for global person search with filters and pagination.

    Used by the Search page to browse and filter persons in the system.
    """

    # Name filters (optional - for fuzzy matching)
    first_name: str | None = Field(
        default=None, max_length=100, description="First name to search (optional)"
    )
    last_name: str | None = Field(
        default=None, max_length=100, description="Last name to search (optional)"
    )

    # Address filters (required for filtering)
    country_id: uuid.UUID = Field(description="Country reference (required)")
    state_id: uuid.UUID = Field(description="State reference (required)")
    district_id: uuid.UUID = Field(description="District reference (required)")
    sub_district_id: uuid.UUID = Field(description="Sub-district reference (required)")
    locality_id: uuid.UUID | None = Field(
        default=None, description="Locality reference (optional)"
    )

    # Religion filters (required for filtering)
    religion_id: uuid.UUID = Field(description="Religion reference (required)")
    religion_category_id: uuid.UUID = Field(
        description="Religion category reference (required)"
    )
    religion_sub_category_id: uuid.UUID | None = Field(
        default=None, description="Religion sub-category reference (optional)"
    )

    # Demographics filters (optional)
    gender_id: uuid.UUID | None = Field(
        default=None, description="Gender ID (optional)"
    )
    birth_year_from: int | None = Field(
        default=None, ge=1900, le=2100, description="Birth year range start (optional)"
    )
    birth_year_to: int | None = Field(
        default=None, ge=1900, le=2100, description="Birth year range end (optional)"
    )

    # Pagination
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=20, ge=1, le=100, description="Maximum number of records to return"
    )

    @field_validator(
        "gender_id", "locality_id", "religion_sub_category_id", mode="before"
    )
    @classmethod
    def empty_string_to_none(cls, v: Any) -> Any:
        """Convert empty string to None for optional UUID fields."""
        if v == "" or v is None:
            return None
        return v

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def empty_string_name_to_none(cls, v: Any) -> Any:
        """Convert empty string to None for optional name fields."""
        if v == "" or v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            return v if v else None
        return v

    @field_validator("birth_year_from", "birth_year_to", mode="before")
    @classmethod
    def empty_string_year_to_none(cls, v: Any) -> Any:
        """Convert empty string to None for optional year fields."""
        if v == "" or v is None:
            return None
        return v

    @model_validator(mode="after")
    def validate_birth_year_range(self) -> "PersonSearchFilterRequest":
        """Validate that birth_year_from <= birth_year_to when both are provided."""
        if (
            self.birth_year_from is not None
            and self.birth_year_to is not None
            and self.birth_year_from > self.birth_year_to
        ):
            raise ValueError(
                "birth_year_from must be less than or equal to birth_year_to"
            )
        return self


class PersonSearchResult(SQLModel):
    """Individual person result in global search.

    Contains person details for display in search results.
    """

    person_id: uuid.UUID = Field(description="Person ID")
    first_name: str = Field(description="First name")
    middle_name: str | None = Field(default=None, description="Middle name")
    last_name: str = Field(description="Last name")
    date_of_birth: date = Field(description="Date of birth")
    gender_id: uuid.UUID | None = Field(
        default=None, description="Gender ID for avatar styling (optional)"
    )
    name_match_score: float | None = Field(
        default=None,
        description="Name similarity score (only present when name filter used)",
    )


class PersonSearchResponse(SQLModel):
    """Response schema for global person search.

    Contains paginated results with total count for pagination UI.
    """

    results: list[PersonSearchResult] = Field(description="List of matching persons")
    total: int = Field(description="Total count of matching persons")
    skip: int = Field(description="Number of records skipped")
    limit: int = Field(description="Maximum records per page")


# =============================================================================
# Person Matching Schemas (for Add Family Member)
# =============================================================================


class PersonSearchRequest(SQLModel):
    """Request schema for person matching search."""

    # Basic details
    first_name: str = Field(max_length=100, description="First name to search")
    last_name: str = Field(max_length=100, description="Last name to search")
    middle_name: str | None = Field(
        default=None, max_length=100, description="Middle name (optional)"
    )
    gender_id: uuid.UUID | None = Field(
        default=None, description="Gender ID (optional)"
    )
    date_of_birth: date | None = Field(
        default=None, description="Date of birth (optional)"
    )

    @field_validator("gender_id", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: Any) -> Any:
        """Convert empty string to None for optional UUID fields."""
        if v == "" or v is None:
            return None
        return v

    # Address criteria
    country_id: uuid.UUID = Field(description="Country reference")
    state_id: uuid.UUID = Field(description="State reference")
    district_id: uuid.UUID = Field(description="District reference")
    sub_district_id: uuid.UUID | None = Field(
        default=None, description="Sub-district reference (optional)"
    )
    locality_id: uuid.UUID | None = Field(
        default=None, description="Locality reference (optional)"
    )

    # Religion criteria
    religion_id: uuid.UUID = Field(description="Religion reference")
    religion_category_id: uuid.UUID | None = Field(
        default=None, description="Religion category reference (optional)"
    )
    religion_sub_category_id: uuid.UUID | None = Field(
        default=None, description="Religion sub-category reference (optional)"
    )

    # Address display string (passed from frontend to avoid duplicate queries)
    address_display: str | None = Field(
        default=None, description="Comma-separated address display string (optional)"
    )
    # Religion display string (passed from frontend to avoid duplicate queries)
    religion_display: str | None = Field(
        default=None, description="Comma-separated religion display string (optional)"
    )

    @field_validator("address_display", "religion_display", mode="before")
    @classmethod
    def empty_string_display_to_none(cls, v: Any) -> Any:
        """Convert empty string to None for optional display fields."""
        if v == "" or v is None:
            return None
        return v


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

    # Relationship flags
    is_current_user: bool = Field(
        default=False, description="True if this is the current user's person record"
    )
    is_already_connected: bool = Field(
        default=False,
        description="True if this person is already connected to the current user",
    )
