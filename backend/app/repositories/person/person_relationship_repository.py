"""Person Relationship repository."""

import logging
import uuid

from sqlmodel import Session, col, desc, select

from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PersonRelationshipRepository(BaseRepository[PersonRelationship]):
    """Repository for person relationship data access."""

    def __init__(self, session: Session):
        super().__init__(PersonRelationship, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> list[PersonRelationship]:
        """Get all relationships for a person."""
        logger.debug(f"Querying relationships for person: {person_id}")
        statement = (
            select(PersonRelationship)
            .where(PersonRelationship.person_id == person_id)
            .order_by(desc(PersonRelationship.created_at))
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} relationships for person {person_id}")
        return results

    def get_active_relationships(
        self, person_id: uuid.UUID
    ) -> list[PersonRelationship]:
        """Get active relationships for a person."""
        logger.debug(f"Querying active relationships for person: {person_id}")
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id, PersonRelationship.is_active
        )
        results = list(self.session.exec(statement).all())
        logger.debug(
            f"Retrieved {len(results)} active relationships for person {person_id}"
        )
        return results

    def get_by_relationship_type(
        self, person_id: uuid.UUID, relationship_type: RelationshipType
    ) -> list[PersonRelationship]:
        """Get relationships of a specific type for a person."""
        logger.debug(
            f"Querying relationships for person {person_id} with type: {relationship_type}"
        )
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id,
            PersonRelationship.relationship_type == relationship_type,
        )
        results = list(self.session.exec(statement).all())
        logger.debug(
            f"Retrieved {len(results)} relationships of type {relationship_type} for person {person_id}"
        )
        return results

    def get_by_relationship_types(
        self, person_id: uuid.UUID, relationship_types: list[RelationshipType]
    ) -> list[PersonRelationship]:
        """Get relationships of multiple types for a person."""
        logger.debug(
            f"Querying relationships for person {person_id} with types: {relationship_types}"
        )
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id,
            col(PersonRelationship.relationship_type).in_(relationship_types),
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} relationships for person {person_id}")
        return results

    def find_inverse(
        self, person_id: uuid.UUID, related_person_id: uuid.UUID
    ) -> PersonRelationship | None:
        """
        Find the inverse relationship between two persons.

        Query person_relationship where person_id and related_person_id are swapped
        and filter by is_active = True.

        Args:
            person_id: The person_id from the primary relationship
            related_person_id: The related_person_id from the primary relationship

        Returns:
            The inverse relationship if found, None otherwise
        """
        logger.debug(
            f"Finding inverse relationship: person={related_person_id}, related={person_id}"
        )
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == related_person_id,
            PersonRelationship.related_person_id == person_id,
            PersonRelationship.is_active,
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"Inverse relationship found (ID: {result.id})")
        else:
            logger.debug("No inverse relationship found")
        return result

    def find_inverse_including_inactive(
        self, person_id: uuid.UUID, related_person_id: uuid.UUID
    ) -> PersonRelationship | None:
        """
        Find the inverse relationship between two persons, including inactive ones.

        Same as find_inverse but doesn't filter by is_active.
        Used for update/delete operations where we need to find the inverse
        regardless of its active status.

        Args:
            person_id: The person_id from the primary relationship
            related_person_id: The related_person_id from the primary relationship

        Returns:
            The inverse relationship if found, None otherwise
        """
        logger.debug(
            f"Finding inverse relationship (including inactive): person={related_person_id}, related={person_id}"
        )
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == related_person_id,
            PersonRelationship.related_person_id == person_id,
        )
        result = self.session.exec(statement).first()
        if result:
            logger.debug(
                f"Inverse relationship found (ID: {result.id}, active: {result.is_active})"
            )
        else:
            logger.debug("No inverse relationship found")
        return result

    def delete_without_commit(self, obj: PersonRelationship) -> None:
        """
        Delete a record without committing.

        Used for transactional operations where multiple deletes
        need to be committed together.
        """
        logger.debug(f"Deleting relationship without commit (ID: {obj.id})")
        self.session.delete(obj)

    def update_without_commit(self, obj: PersonRelationship) -> PersonRelationship:
        """
        Update a record without committing.

        Used for transactional operations where multiple updates
        need to be committed together.
        """
        logger.debug(f"Updating relationship without commit (ID: {obj.id})")
        self.session.add(obj)
        return obj
