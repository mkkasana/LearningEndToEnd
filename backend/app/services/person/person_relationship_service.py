"""Person Relationship service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.repositories.person.person_repository import PersonRepository
from app.schemas.person import PersonRelationshipCreate, PersonRelationshipUpdate
from app.utils.relationship_helper import RelationshipTypeHelper

logger = logging.getLogger(__name__)


class PersonRelationshipService:
    """Service for person relationship business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.relationship_repo = PersonRelationshipRepository(session)
        self.person_repo = PersonRepository(session)

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
        """
        Create a bidirectional relationship between two persons.
        
        This method creates both the primary relationship (A → B) and the inverse
        relationship (B → A) with the appropriate inverse type based on the
        relationship type and genders of both persons.
        
        Args:
            person_id: The ID of the person creating the relationship (person A)
            relationship_create: The relationship data including related_person_id and type
            
        Returns:
            The created primary relationship
            
        Raises:
            Exception: If the relationship creation fails (transaction will be rolled back)
        """
        try:
            # Start transaction
            logger.info(
                f"Creating relationship: person_id={person_id}, "
                f"related_person_id={relationship_create.related_person_id}, "
                f"type={relationship_create.relationship_type}"
            )
            
            # Fetch person and related_person records to get gender information
            person = self.person_repo.get_by_id(person_id)
            related_person = self.person_repo.get_by_id(relationship_create.related_person_id)
            
            if not person:
                logger.error(f"Person not found: {person_id}")
                raise ValueError(f"Person not found: {person_id}")
            
            if not related_person:
                logger.error(f"Related person not found: {relationship_create.related_person_id}")
                raise ValueError(f"Related person not found: {relationship_create.related_person_id}")
            
            # Create primary relationship (A → B)
            primary_relationship = PersonRelationship(
                person_id=person_id, **relationship_create.model_dump()
            )
            primary_relationship = self.relationship_repo.create(primary_relationship)
            logger.info(f"Created primary relationship with ID: {primary_relationship.id}")
            
            # Check if both persons have gender information
            if not person.gender_id or not related_person.gender_id:
                logger.warning(
                    f"Gender information missing for relationship {primary_relationship.id}. "
                    f"person.gender_id={person.gender_id}, "
                    f"related_person.gender_id={related_person.gender_id}. "
                    f"Creating primary relationship only."
                )
                self.session.commit()
                return primary_relationship
            
            # Get gender mapping
            gender_mapping = RelationshipTypeHelper.get_gender_mapping(self.session)
            
            # Determine inverse relationship type using RelationshipTypeHelper
            inverse_type = RelationshipTypeHelper.get_inverse_type(
                relationship_type=relationship_create.relationship_type,
                person_gender_id=person.gender_id,
                related_person_gender_id=related_person.gender_id,
                gender_mapping=gender_mapping,
            )
            
            # Create inverse relationship if type was determined
            if inverse_type:
                inverse_relationship = PersonRelationship(
                    person_id=relationship_create.related_person_id,
                    related_person_id=person_id,
                    relationship_type=inverse_type,
                    is_active=relationship_create.is_active,
                    start_date=relationship_create.start_date,
                    end_date=relationship_create.end_date,
                )
                inverse_relationship = self.relationship_repo.create(inverse_relationship)
                logger.info(
                    f"Created inverse relationship with ID: {inverse_relationship.id}, "
                    f"type: {inverse_type}"
                )
            else:
                logger.warning(
                    f"Could not determine inverse relationship type for "
                    f"relationship {primary_relationship.id} "
                    f"(type={relationship_create.relationship_type}). "
                    f"Creating primary relationship only."
                )
            
            # Commit transaction
            self.session.commit()
            logger.info(f"Successfully committed bidirectional relationship creation")
            
            return primary_relationship
            
        except Exception as e:
            # Rollback transaction on any error
            logger.error(f"Error creating relationship: {e}", exc_info=True)
            self.session.rollback()
            raise

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
