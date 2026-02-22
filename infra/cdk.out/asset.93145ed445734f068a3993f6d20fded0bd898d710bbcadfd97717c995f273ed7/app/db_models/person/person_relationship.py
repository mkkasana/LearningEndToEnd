"""Person Relationship database model."""

import uuid
from datetime import date, datetime

from sqlmodel import Field, SQLModel

from app.enums import RelationshipType


class PersonRelationship(SQLModel, table=True):
    """Person Relationship model - Tracks relationships between persons."""

    __tablename__ = "person_relationship"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    person_id: uuid.UUID = Field(
        foreign_key="person.id", index=True, description="Person reference"
    )
    related_person_id: uuid.UUID = Field(
        foreign_key="person.id", description="Related person reference"
    )
    relationship_type: RelationshipType = Field(description="Relationship type")
    start_date: date | None = Field(default=None, description="Relationship start date")
    end_date: date | None = Field(default=None, description="Relationship end date")
    is_active: bool = Field(default=True, description="Is relationship active")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
