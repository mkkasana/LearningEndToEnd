"""Person Relationship schemas."""

import uuid
from datetime import date, datetime
from typing import Any

from pydantic import computed_field
from sqlmodel import Field, SQLModel

from app.enums import RelationshipType


class PersonRelationshipBase(SQLModel):
    """Base person relationship properties."""

    related_person_id: uuid.UUID = Field(description="Related person reference")
    relationship_type: RelationshipType = Field(description="Relationship type")
    start_date: date | None = Field(default=None, description="Relationship start date")
    end_date: date | None = Field(default=None, description="Relationship end date")
    is_active: bool = Field(default=True, description="Is relationship active")


class PersonRelationshipCreate(PersonRelationshipBase):
    """Schema for creating a new person relationship."""

    pass


class PersonRelationshipUpdate(SQLModel):
    """Schema for updating a person relationship (all fields optional)."""

    related_person_id: uuid.UUID | None = None
    relationship_type: RelationshipType | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class PersonRelationshipPublic(PersonRelationshipBase):
    """Person relationship response schema."""

    id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def relationship_type_label(self) -> str:
        """Get human-readable label for the relationship type."""
        return self.relationship_type.label


# Inline person details to avoid circular import
class PersonDetails(SQLModel):
    """Person details for relationship response."""

    id: uuid.UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    gender_id: uuid.UUID
    date_of_birth: date
    date_of_death: date | None = None
    user_id: uuid.UUID | None = None
    created_by_user_id: uuid.UUID
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class PersonRelationshipWithDetails(SQLModel):
    """Person relationship with full person details."""

    relationship: PersonRelationshipPublic
    person: PersonDetails


class PersonRelationshipsWithDetailsResponse(SQLModel):
    """Response containing selected person and their relationships."""

    selected_person: PersonDetails
    relationships: list[PersonRelationshipWithDetails]

