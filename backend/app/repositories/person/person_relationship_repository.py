"""Person Relationship repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType
from app.repositories.base import BaseRepository


class PersonRelationshipRepository(BaseRepository[PersonRelationship]):
    """Repository for person relationship data access."""

    def __init__(self, session: Session):
        super().__init__(PersonRelationship, session)

    def get_by_person_id(self, person_id: uuid.UUID) -> list[PersonRelationship]:
        """Get all relationships for a person."""
        statement = (
            select(PersonRelationship)
            .where(PersonRelationship.person_id == person_id)
            .order_by(PersonRelationship.created_at.desc())
        )
        return list(self.session.exec(statement).all())

    def get_active_relationships(self, person_id: uuid.UUID) -> list[PersonRelationship]:
        """Get active relationships for a person."""
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id, PersonRelationship.is_active == True
        )
        return list(self.session.exec(statement).all())

    def get_by_relationship_type(
        self, person_id: uuid.UUID, relationship_type: RelationshipType
    ) -> list[PersonRelationship]:
        """Get relationships of a specific type for a person."""
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id,
            PersonRelationship.relationship_type == relationship_type,
        )
        return list(self.session.exec(statement).all())

    def get_by_relationship_types(
        self, person_id: uuid.UUID, relationship_types: list[RelationshipType]
    ) -> list[PersonRelationship]:
        """Get relationships of multiple types for a person."""
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id,
            PersonRelationship.relationship_type.in_(relationship_types),
        )
        return list(self.session.exec(statement).all())
