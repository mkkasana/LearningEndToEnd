"""Person Relationship schemas."""

import uuid
from datetime import date, datetime

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
