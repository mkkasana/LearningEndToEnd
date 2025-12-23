"""Person Relationship service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType
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

    def get_parents(self, person_id: uuid.UUID) -> list[PersonRelationship]:
        """Get all parents (father and mother) for a person."""
        parent_types = [RelationshipType.FATHER, RelationshipType.MOTHER]
        return self.relationship_repo.get_by_relationship_types(person_id, parent_types)

    def get_children(self, person_id: uuid.UUID) -> list[PersonRelationship]:
        """Get all children (sons and daughters) for a person."""
        children_types = [RelationshipType.SON, RelationshipType.DAUGHTER]
        return self.relationship_repo.get_by_relationship_types(person_id, children_types)

    def get_spouses(self, person_id: uuid.UUID) -> list[PersonRelationship]:
        """Get all spouses for a person."""
        spouse_types = [
            RelationshipType.SPOUSE,
            RelationshipType.HUSBAND,
            RelationshipType.WIFE,
        ]
        return self.relationship_repo.get_by_relationship_types(person_id, spouse_types)

    def get_siblings(self, person_id: uuid.UUID) -> list[PersonRelationship]:
        """
        Get all siblings for a person.
        
        Logic:
        1. Get all parents of the person
        2. For each parent, get all their children
        3. Exclude the person themselves from the results
        4. Remove duplicates (same sibling from both parents)
        """
        # Get all parents
        parents = self.get_parents(person_id)
        
        if not parents:
            return []
        
        # Collect all siblings from all parents
        siblings_dict = {}  # Use dict to avoid duplicates
        
        for parent in parents:
            parent_person_id = parent.related_person_id
            # Get all children of this parent
            children = self.get_children(parent_person_id)
            
            for child in children:
                # Exclude self and avoid duplicates
                if child.related_person_id != person_id:
                    siblings_dict[child.related_person_id] = child
        
        return list(siblings_dict.values())
