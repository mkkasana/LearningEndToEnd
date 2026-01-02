"""Relationship Type Helper utility for bidirectional relationship management."""

import logging
import uuid

from app.enums import RelationshipType, get_gender_mapping

logger = logging.getLogger(__name__)


class RelationshipTypeHelper:
    """Helper class for relationship type operations and inverse determination."""

    @classmethod
    def get_gender_mapping(cls, session: object = None) -> dict[uuid.UUID, str]:
        """
        Get gender mapping from hardcoded enum values.

        Args:
            session: Database session (kept for API compatibility but not used)

        Returns:
            Dictionary mapping gender_id to gender code (e.g., 'MALE', 'FEMALE')
        """
        return get_gender_mapping()

    @staticmethod
    def get_inverse_type(
        relationship_type: RelationshipType,
        person_gender_id: uuid.UUID,
        related_person_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str],
    ) -> RelationshipType | None:
        """
        Determine the inverse relationship type based on the primary relationship and genders.

        SEMANTICS:
        - When A → B with relationship_type, we need to create B → A with inverse_type
        - relationship_type describes who B is to A
        - inverse_type describes who A is to B
        - For parent-child relationships, we use person_gender (A's gender) to determine inverse

        Args:
            relationship_type: The primary relationship type (describes B to A)
            person_gender_id: Gender ID of person A (who creates the relationship)
            related_person_gender_id: Gender ID of person B (the related person)
            gender_mapping: Mapping of gender_id to gender code (male/female)

        Returns:
            The inverse relationship type, or None if cannot be determined

        Examples:
            - A → B as Father (B is A's father) + A is male → B → A as Son (A is B's son)
            - A → B as Father (B is A's father) + A is female → B → A as Daughter (A is B's daughter)
            - A → B as Mother (B is A's mother) + A is male → B → A as Son (A is B's son)
            - A → B as Mother (B is A's mother) + A is female → B → A as Daughter (A is B's daughter)
            - A → B as Son (B is A's son) + A is male → B → A as Father (A is B's father)
            - A → B as Son (B is A's son) + A is female → B → A as Mother (A is B's mother)
            - A → B as Daughter (B is A's daughter) + A is male → B → A as Father (A is B's father)
            - A → B as Daughter (B is A's daughter) + A is female → B → A as Mother (A is B's mother)
            - A → B as Husband (B is A's husband) → B → A as Wife (A is B's wife)
            - A → B as Wife (B is A's wife) → B → A as Husband (A is B's husband)
            - A → B as Spouse (B is A's spouse) → B → A as Spouse (A is B's spouse)
        """
        # Get gender codes from mapping
        person_gender = gender_mapping.get(person_gender_id, "").lower()
        gender_mapping.get(related_person_gender_id, "").lower()

        # Parent → Child relationships
        # When A → B as Father (B is A's father), check A's gender to determine inverse
        if relationship_type == RelationshipType.FATHER:
            if person_gender == "male":
                return RelationshipType.SON  # A is male, so A is B's son
            elif person_gender == "female":
                return RelationshipType.DAUGHTER  # A is female, so A is B's daughter
            else:
                logger.warning(
                    f"Cannot determine inverse for FATHER relationship: "
                    f"person gender '{person_gender}' not recognized"
                )
                return None

        # When A → B as Mother (B is A's mother), check A's gender to determine inverse
        if relationship_type == RelationshipType.MOTHER:
            if person_gender == "male":
                return RelationshipType.SON  # A is male, so A is B's son
            elif person_gender == "female":
                return RelationshipType.DAUGHTER  # A is female, so A is B's daughter
            else:
                logger.warning(
                    f"Cannot determine inverse for MOTHER relationship: "
                    f"person gender '{person_gender}' not recognized"
                )
                return None

        # Child → Parent relationships
        # When A → B as Son (B is A's son), check A's gender to determine inverse
        if relationship_type == RelationshipType.SON:
            if person_gender == "male":
                return RelationshipType.FATHER  # A is male, so A is B's father
            elif person_gender == "female":
                return RelationshipType.MOTHER  # A is female, so A is B's mother
            else:
                logger.warning(
                    f"Cannot determine inverse for SON relationship: "
                    f"person gender '{person_gender}' not recognized"
                )
                return None

        # When A → B as Daughter (B is A's daughter), check A's gender to determine inverse
        if relationship_type == RelationshipType.DAUGHTER:
            if person_gender == "male":
                return RelationshipType.FATHER  # A is male, so A is B's father
            elif person_gender == "female":
                return RelationshipType.MOTHER  # A is female, so A is B's mother
            else:
                logger.warning(
                    f"Cannot determine inverse for DAUGHTER relationship: "
                    f"person gender '{person_gender}' not recognized"
                )
                return None

        # Spouse relationships (gender-independent)
        if relationship_type == RelationshipType.HUSBAND:
            return RelationshipType.WIFE

        if relationship_type == RelationshipType.WIFE:
            return RelationshipType.HUSBAND

        if relationship_type == RelationshipType.SPOUSE:
            return RelationshipType.SPOUSE

        # Unknown relationship type
        logger.warning(f"Unknown relationship type: {relationship_type}")
        return None

    @staticmethod
    def requires_gender_context(relationship_type: RelationshipType) -> bool:
        """
        Check if a relationship type requires gender information to determine its inverse.

        Args:
            relationship_type: The relationship type to check

        Returns:
            True if gender context is required, False otherwise

        Examples:
            - Parent-child relationships (Father, Mother, Son, Daughter) → True
            - Spouse relationships (Husband, Wife, Spouse) → False
        """
        # Parent-child relationships require gender context
        if relationship_type in (
            RelationshipType.FATHER,
            RelationshipType.MOTHER,
            RelationshipType.SON,
            RelationshipType.DAUGHTER,
        ):
            return True

        # Spouse relationships don't require gender context
        if relationship_type in (
            RelationshipType.HUSBAND,
            RelationshipType.WIFE,
            RelationshipType.SPOUSE,
        ):
            return False

        # Unknown types - assume they need gender context to be safe
        logger.warning(
            f"Unknown relationship type '{relationship_type}' in requires_gender_context check"
        )
        return True
