"""Relationship factory for creating test PersonRelationship entities."""

import uuid
from datetime import date, datetime
from typing import Any

from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType


class RelationshipFactory:
    """Factory for creating PersonRelationship test entities."""

    # Mapping of relationship types to their inverse
    INVERSE_RELATIONSHIPS: dict[RelationshipType, RelationshipType] = {
        RelationshipType.FATHER: RelationshipType.SON,  # Father's inverse is Son/Daughter
        RelationshipType.MOTHER: RelationshipType.SON,  # Mother's inverse is Son/Daughter
        RelationshipType.SON: RelationshipType.FATHER,  # Son's inverse is Father/Mother
        RelationshipType.DAUGHTER: RelationshipType.FATHER,  # Daughter's inverse is Father/Mother
        RelationshipType.HUSBAND: RelationshipType.WIFE,
        RelationshipType.WIFE: RelationshipType.HUSBAND,
        RelationshipType.SPOUSE: RelationshipType.SPOUSE,
    }

    @classmethod
    def create(
        cls,
        session: Session,
        *,
        person: Person,
        related_person: Person,
        relationship_type: RelationshipType = RelationshipType.FATHER,
        start_date: date | None = None,
        end_date: date | None = None,
        is_active: bool = True,
        commit: bool = True,
    ) -> PersonRelationship:
        """Create a PersonRelationship entity.

        Args:
            session: Database session
            person: The person who has the relationship
            related_person: The related person
            relationship_type: Type of relationship
            start_date: When the relationship started
            end_date: When the relationship ended
            is_active: Whether the relationship is active
            commit: Whether to commit the transaction

        Returns:
            Created PersonRelationship entity
        """
        relationship = PersonRelationship(
            person_id=person.id,
            related_person_id=related_person.id,
            relationship_type=relationship_type,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )

        session.add(relationship)
        if commit:
            session.commit()
            session.refresh(relationship)

        return relationship

    @classmethod
    def create_bidirectional(
        cls,
        session: Session,
        *,
        person: Person,
        related_person: Person,
        relationship_type: RelationshipType,
        inverse_relationship_type: RelationshipType | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        is_active: bool = True,
        commit: bool = True,
    ) -> tuple[PersonRelationship, PersonRelationship]:
        """Create bidirectional relationships between two persons.

        Args:
            session: Database session
            person: The first person
            related_person: The second person
            relationship_type: Type of relationship from person to related_person
            inverse_relationship_type: Type of inverse relationship (auto-determined if not provided)
            start_date: When the relationship started
            end_date: When the relationship ended
            is_active: Whether the relationship is active
            commit: Whether to commit the transaction

        Returns:
            Tuple of (forward_relationship, inverse_relationship)
        """
        if inverse_relationship_type is None:
            inverse_relationship_type = cls.INVERSE_RELATIONSHIPS.get(
                relationship_type, relationship_type
            )

        forward = PersonRelationship(
            person_id=person.id,
            related_person_id=related_person.id,
            relationship_type=relationship_type,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )

        inverse = PersonRelationship(
            person_id=related_person.id,
            related_person_id=person.id,
            relationship_type=inverse_relationship_type,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )

        session.add(forward)
        session.add(inverse)

        if commit:
            session.commit()
            session.refresh(forward)
            session.refresh(inverse)

        return forward, inverse

    @classmethod
    def build(
        cls,
        *,
        person_id: uuid.UUID,
        related_person_id: uuid.UUID,
        relationship_type: RelationshipType = RelationshipType.FATHER,
        start_date: date | None = None,
        end_date: date | None = None,
        is_active: bool = True,
    ) -> PersonRelationship:
        """Build a PersonRelationship entity without persisting to database.

        Useful for unit tests with mocked sessions.

        Args:
            person_id: UUID of the person
            related_person_id: UUID of the related person
            relationship_type: Type of relationship
            start_date: When the relationship started
            end_date: When the relationship ended
            is_active: Whether the relationship is active

        Returns:
            PersonRelationship entity (not persisted)
        """
        return PersonRelationship(
            id=uuid.uuid4(),
            person_id=person_id,
            related_person_id=related_person_id,
            relationship_type=relationship_type,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    @classmethod
    def create_parent_child(
        cls,
        session: Session,
        *,
        parent: Person,
        child: Person,
        parent_is_father: bool = True,
        commit: bool = True,
    ) -> tuple[PersonRelationship, PersonRelationship]:
        """Create parent-child bidirectional relationships.

        Args:
            session: Database session
            parent: The parent person
            child: The child person
            parent_is_father: Whether the parent is father (True) or mother (False)
            commit: Whether to commit the transaction

        Returns:
            Tuple of (parent_to_child_relationship, child_to_parent_relationship)
        """
        parent_type = RelationshipType.FATHER if parent_is_father else RelationshipType.MOTHER
        # Child type depends on child's gender - simplified to SON for now
        child_type = RelationshipType.SON

        return cls.create_bidirectional(
            session,
            person=parent,
            related_person=child,
            relationship_type=parent_type,
            inverse_relationship_type=child_type,
            commit=commit,
        )

    @classmethod
    def create_spouse(
        cls,
        session: Session,
        *,
        person1: Person,
        person2: Person,
        person1_is_husband: bool = True,
        start_date: date | None = None,
        commit: bool = True,
    ) -> tuple[PersonRelationship, PersonRelationship]:
        """Create spouse bidirectional relationships.

        Args:
            session: Database session
            person1: First spouse
            person2: Second spouse
            person1_is_husband: Whether person1 is husband (True) or wife (False)
            start_date: Marriage date
            commit: Whether to commit the transaction

        Returns:
            Tuple of (person1_to_person2_relationship, person2_to_person1_relationship)
        """
        type1 = RelationshipType.HUSBAND if person1_is_husband else RelationshipType.WIFE
        type2 = RelationshipType.WIFE if person1_is_husband else RelationshipType.HUSBAND

        return cls.create_bidirectional(
            session,
            person=person1,
            related_person=person2,
            relationship_type=type1,
            inverse_relationship_type=type2,
            start_date=start_date,
            commit=commit,
        )
