"""Person Relationship service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_relationship import PersonRelationship
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.schemas.person import PersonRelationshipCreate, PersonRelationshipUpdate


class PersonRelationshipService:
    """Service for person relationship business logic."""

    def __init__(self, session: Session):
        self.relationship_repo = PersonRelationshipRepository(session)

    def get_relationships_by_person(
        self, person_id: uuid.UUID
    ) -> list[PersonRelationship]:
        """Get all relationships for a person."""
        return self.relationship_repo.get_by_person_id(person_id)

    def get_relationship_by_id(
        self, relationship_id: uuid.UUID
    ) -> PersonRelationship | None:
        """Get relationship by ID."""
        return self.relationship_repo.get_by_id(relationship_id)

    def create_relationship(
        self, person_id: uuid.UUID, relationship_create: PersonRelationshipCreate
    ) -> PersonRelationship:
        """Create a new relationship for a person."""
        relationship = PersonRelationship(
            person_id=person_id, **relationship_create.model_dump()
        )
        return self.relationship_repo.create(relationship)

    def update_relationship(
        self, relationship: PersonRelationship, relationship_update: PersonRelationshipUpdate
    ) -> PersonRelationship:
        """Update a relationship."""
        update_data = relationship_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(relationship, key, value)
        relationship.updated_at = datetime.utcnow()
        return self.relationship_repo.update(relationship)

    def delete_relationship(self, relationship: PersonRelationship) -> None:
        """Delete a relationship."""
        self.relationship_repo.delete(relationship)
