"""Partner Match schemas for finding potential marriage matches."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field, model_validator


class PartnerMatchRequest(BaseModel):
    """Request body for partner match search."""

    seeker_person_id: uuid.UUID = Field(description="The person looking for matches")
    target_gender_code: str = Field(
        description="Gender code to search for ('M' or 'F')"
    )

    # Age filters
    birth_year_min: int | None = Field(
        default=None, description="Minimum birth year (inclusive)"
    )
    birth_year_max: int | None = Field(
        default=None, description="Maximum birth year (inclusive)"
    )

    # Religion inclusion filters (AND logic between different levels)
    include_religion_ids: list[uuid.UUID] | None = Field(
        default=None, description="Include only candidates with these religion IDs"
    )
    include_category_ids: list[uuid.UUID] | None = Field(
        default=None, description="Include only candidates with these category IDs"
    )
    include_sub_category_ids: list[uuid.UUID] | None = Field(
        default=None, description="Include only candidates with these sub-category IDs"
    )

    # Gotra/sub-category exclusion
    exclude_sub_category_ids: list[uuid.UUID] = Field(
        default_factory=list,
        description="Exclude candidates with these sub-category IDs (gotras)",
    )

    # Search depth
    max_depth: int = Field(
        default=5, description="Maximum BFS traversal depth (relationship hops)"
    )

    # Graph pruning
    prune_graph: bool = Field(
        default=True,
        description="If True, only include nodes on paths to matches. If False, return full exploration graph.",
    )

    @model_validator(mode="after")
    def validate_birth_year_range(self) -> PartnerMatchRequest:
        """Validate that birth_year_min is not greater than birth_year_max."""
        if (
            self.birth_year_min is not None
            and self.birth_year_max is not None
            and self.birth_year_min > self.birth_year_max
        ):
            raise ValueError("birth_year_min cannot be greater than birth_year_max")
        return self


class MatchConnectionInfo(BaseModel):
    """Represents a connection/edge between two persons in the exploration graph.

    Note: The full MatchGraphNode details can be looked up from the graph
    using the person_id.
    """

    person_id: uuid.UUID = Field(description="Connected person ID")
    relationship: str = Field(
        description="Relationship type (e.g., Father, Mother, Son, Daughter, Wife, Husband)"
    )


class MatchGraphNode(BaseModel):
    """A node in the partner match exploration graph."""

    person_id: uuid.UUID = Field(description="Person ID")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    birth_year: int | None = Field(default=None, description="Birth year")
    death_year: int | None = Field(
        default=None, description="Death year (if applicable)"
    )
    address: str = Field(
        default="",
        description="Comma-separated address: Village, District, State, Country",
    )
    religion: str = Field(
        default="",
        description="Comma-separated religion: Religion, Category, SubCategory",
    )
    is_match: bool = Field(
        default=False, description="True if this person is an eligible match"
    )
    depth: int = Field(description="Number of relationship hops from seeker")
    from_person: MatchConnectionInfo | None = Field(
        default=None,
        description="Parent node in BFS tree (person from whom this node was reached)",
    )
    to_persons: list[MatchConnectionInfo] = Field(
        default_factory=list,
        description="Child nodes explored from this node",
    )

    def set_from_person(self, from_person: MatchConnectionInfo | None) -> None:
        """Set the parent connection info."""
        self.from_person = from_person

    def add_to_person(self, to_person: MatchConnectionInfo) -> None:
        """Add a child connection info."""
        self.to_persons.append(to_person)


class PartnerMatchResponse(BaseModel):
    """Response for partner match search."""

    seeker_id: uuid.UUID = Field(description="The seeker person ID from the request")
    total_matches: int = Field(description="Total number of eligible matches found")
    matches: list[uuid.UUID] = Field(
        default_factory=list, description="Person IDs of eligible match candidates"
    )
    exploration_graph: dict[uuid.UUID, MatchGraphNode] = Field(
        default_factory=dict,
        description="Graph of all visited persons keyed by person_id for O(1) lookup",
    )
