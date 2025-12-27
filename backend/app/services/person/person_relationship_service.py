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
        """
        Update a bidirectional relationship.
        
        This method updates both the primary relationship and its inverse relationship,
        ensuring that changes to is_active, start_date, and end_date are synchronized
        across both directions. The relationship_type is NOT updated for the inverse.
        
        Args:
            relationship: The primary relationship to update
            relationship_update: The update data
            
        Returns:
            The updated primary relationship
            
        Raises:
            Exception: If the update fails (transaction will be rolled back)
        """
        try:
            logger.info(
                f"Updating relationship: id={relationship.id}, "
                f"person_id={relationship.person_id}, "
                f"related_person_id={relationship.related_person_id}"
            )
            
            # Update primary relationship
            update_data = relationship_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(relationship, key, value)
            relationship.updated_at = datetime.utcnow()
            updated_primary = self.relationship_repo.update(relationship)
            logger.info(f"Updated primary relationship with ID: {updated_primary.id}")
            
            # Find inverse relationship using repository
            inverse_relationship = self.relationship_repo.find_inverse_including_inactive(
                person_id=relationship.person_id,
                related_person_id=relationship.related_person_id,
            )
            
            # If inverse found, update matching fields
            if inverse_relationship:
                logger.info(
                    f"Found inverse relationship with ID: {inverse_relationship.id}, "
                    f"updating matching fields"
                )
                
                # Update only the fields that should be synchronized
                # Do NOT update relationship_type of inverse
                if "is_active" in update_data:
                    inverse_relationship.is_active = update_data["is_active"]
                if "start_date" in update_data:
                    inverse_relationship.start_date = update_data["start_date"]
                if "end_date" in update_data:
                    inverse_relationship.end_date = update_data["end_date"]
                
                # Update updated_at timestamp for inverse
                inverse_relationship.updated_at = datetime.utcnow()
                self.relationship_repo.update(inverse_relationship)
                logger.info(f"Updated inverse relationship with ID: {inverse_relationship.id}")
            else:
                # If inverse not found, log warning and continue
                logger.warning(
                    f"Inverse relationship not found for relationship ID: {relationship.id}. "
                    f"Continuing with primary update only."
                )
            
            # Commit transaction
            self.session.commit()
            logger.info(f"Successfully committed bidirectional relationship update")
            
            return updated_primary
            
        except Exception as e:
            # Rollback transaction on any error
            logger.error(f"Error updating relationship: {e}", exc_info=True)
            self.session.rollback()
            raise

    def delete_relationship(self, relationship: PersonRelationship, soft_delete: bool = False) -> None:
        """
        Delete a bidirectional relationship.
        
        This method deletes both the primary relationship and its inverse relationship,
        ensuring that both directions are removed from the system. Supports both
        soft delete (setting is_active=False) and hard delete (removing records).
        
        Args:
            relationship: The primary relationship to delete
            soft_delete: If True, performs soft delete (is_active=False), otherwise hard delete
            
        Raises:
            Exception: If the deletion fails (transaction will be rolled back)
        """
        try:
            logger.info(
                f"Deleting relationship: id={relationship.id}, "
                f"person_id={relationship.person_id}, "
                f"related_person_id={relationship.related_person_id}, "
                f"soft_delete={soft_delete}"
            )
            
            # Find inverse relationship using repository
            inverse_relationship = self.relationship_repo.find_inverse_including_inactive(
                person_id=relationship.person_id,
                related_person_id=relationship.related_person_id,
            )
            
            if soft_delete:
                # Soft delete: update is_active to False for both relationships
                logger.info(f"Performing soft delete for relationship ID: {relationship.id}")
                relationship.is_active = False
                relationship.updated_at = datetime.utcnow()
                self.relationship_repo.update_without_commit(relationship)
                logger.info(f"Soft deleted primary relationship with ID: {relationship.id}")
                
                if inverse_relationship:
                    logger.info(
                        f"Found inverse relationship with ID: {inverse_relationship.id}, "
                        f"performing soft delete"
                    )
                    inverse_relationship.is_active = False
                    inverse_relationship.updated_at = datetime.utcnow()
                    self.relationship_repo.update_without_commit(inverse_relationship)
                    logger.info(f"Soft deleted inverse relationship with ID: {inverse_relationship.id}")
                else:
                    logger.warning(
                        f"Inverse relationship not found for relationship ID: {relationship.id}. "
                        f"Continuing with primary soft delete only."
                    )
            else:
                # Hard delete: remove both records from database
                logger.info(f"Performing hard delete for relationship ID: {relationship.id}")
                self.relationship_repo.delete_without_commit(relationship)
                logger.info(f"Hard deleted primary relationship with ID: {relationship.id}")
                
                if inverse_relationship:
                    logger.info(
                        f"Found inverse relationship with ID: {inverse_relationship.id}, "
                        f"performing hard delete"
                    )
                    self.relationship_repo.delete_without_commit(inverse_relationship)
                    logger.info(f"Hard deleted inverse relationship with ID: {inverse_relationship.id}")
                else:
                    logger.warning(
                        f"Inverse relationship not found for relationship ID: {relationship.id}. "
                        f"Continuing with primary hard delete only."
                    )
            
            # Commit transaction
            self.session.commit()
            logger.info(f"Successfully committed bidirectional relationship deletion")
            
        except Exception as e:
            # Rollback transaction on any error
            logger.error(f"Error deleting relationship: {e}", exc_info=True)
            self.session.rollback()
            raise

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
