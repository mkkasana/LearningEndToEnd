"""Lineage Path schemas for finding relationship paths between persons."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class LineagePathRequest(BaseModel):
    """Request body for lineage path query."""

    person_a_id: uuid.UUID = Field(description="First person ID")
    person_b_id: uuid.UUID = Field(description="Second person ID")


class ConnectionInfo(BaseModel):
    """Represents a connection to another person.

    Note: The full PersonNode details can be looked up from the graph
    using the person_id.
    """

    person_id: uuid.UUID = Field(description="Connected person ID")
    relationship: str = Field(
        description="Relationship type (e.g., Father, Mother, Son, Daughter, Wife, Husband)"
    )


class PersonNode(BaseModel):
    """A node in the lineage path graph."""

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
    from_person: ConnectionInfo | None = Field(
        default=None, description="Person from whom I was reached."
    )
    to_person: ConnectionInfo | None = Field(
        default=None, description="Person reached via me."
    )

    def set_from_person(self, from_person: ConnectionInfo | None) -> None:
        self.from_person = from_person

    def set_to_person(self, to_person: ConnectionInfo | None) -> None:
        self.to_person = to_person


class LineagePathResponse(BaseModel):
    """Response for lineage path query."""

    connection_found: bool = Field(description="Whether a connection was found")
    message: str = Field(description="Result description message")
    common_ancestor_id: uuid.UUID | None = Field(
        default=None, description="Common ancestor person ID (if found)"
    )
    graph: dict[uuid.UUID, PersonNode] = Field(
        default_factory=dict, description="Graph of person nodes keyed by person_id"
    )
