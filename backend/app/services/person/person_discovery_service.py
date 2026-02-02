"""Person Discovery service for finding potential family member connections."""

import logging
import uuid

from sqlmodel import Session

from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums.relationship_type import RelationshipType
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository
from app.schemas.person.person_discovery import PersonDiscoveryResult
from app.utils.cache import cached

logger = logging.getLogger(__name__)

# Static gender code constants
GENDER_CODE_MALE = "male"
GENDER_CODE_FEMALE = "female"

# Hardcoded gender ID to code mapping
# These are the only two genders in the database
# TODO: Move to enum in the future
GENDER_ID_TO_CODE = {
    uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83"): GENDER_CODE_MALE,
    uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95"): GENDER_CODE_FEMALE,
}


class PersonDiscoveryService:
    """Service for discovering potential family member connections.

    This service implements three discovery patterns:
    1. Spouse's children → Suggest as user's Son/Daughter
    2. Parent's spouse → Suggest as user's Father/Mother
    3. Child's parent → Suggest as user's Spouse
    """

    def __init__(self, session: Session):
        """Initialize the discovery service.

        Args:
            session: Database session
        """
        self.session = session
        self.person_repo = PersonRepository(session)
        self.relationship_repo = PersonRelationshipRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)

    @cached(ttl_seconds=60, key_prefix="discovery")
    def discover_family_members(
        self, current_user_id: uuid.UUID, person_id: uuid.UUID | None = None
    ) -> list[PersonDiscoveryResult]:
        """Discover potential family member connections.

        Implements three discovery patterns:
        1. Spouse's children → User's children
        2. Parent's spouse → User's parent
        3. Child's parent → User's spouse

        Results are cached for 1 minute to improve performance.
        Cache is invalidated when relationships are created, updated, or deleted.

        Args:
            current_user_id: Current user's ID (used for cache key and logging)
            person_id: Optional person ID to discover for. When provided, discovers
                      for this specific person instead of looking up by user_id.
                      This enables the "assume person role" feature where elevated
                      users can discover family members for persons they created.

        Returns:
            List of discovered persons with inferred relationships,
            sorted by proximity and relationship priority, limited to 20 results

        Raises:
            Exception: Re-raises any database or unexpected errors for API layer to handle
        """
        if person_id:
            logger.info(
                f"Starting family member discovery for person: {person_id} "
                f"(requested by user: {current_user_id})"
            )
        else:
            logger.info(f"Starting family member discovery for user: {current_user_id}")

        try:
            # Get person record - either by person_id or user_id
            if person_id:
                person = self.person_repo.get_by_id(person_id)
                if not person:
                    logger.warning(
                        f"No person record found for person_id: {person_id}."
                    )
                    return []
            else:
                person = self.person_repo.get_by_user_id(current_user_id)
                if not person:
                    logger.warning(
                        f"No person record found for user: {current_user_id}. "
                        "User may not have completed profile setup."
                    )
                    return []

            logger.debug(
                f"Found person record: {person.first_name} {person.last_name} (ID: {person.id})"
            )

            # Fetch all active relationships for the user ONCE
            try:
                user_relationships = self.relationship_repo.get_active_relationships(
                    person.id
                )
                logger.debug(
                    f"Fetched {len(user_relationships)} active relationships for user"
                )
            except Exception as e:
                logger.error(
                    f"Database error fetching relationships for person {person.id}: {str(e)}",
                    exc_info=True,
                )
                raise

            # Get all connected person IDs to filter out existing connections
            connected_person_ids = self._get_connected_person_ids_from_relationships(
                person.id, user_relationships
            )
            logger.debug(f"User has {len(connected_person_ids)} existing connections")

            # Discover from all three patterns
            discoveries: list[PersonDiscoveryResult] = []

            # Pattern 1: Spouse's children
            try:
                spouses_children = self._discover_spouses_children(
                    person.id, user_relationships, connected_person_ids
                )
                logger.debug(
                    f"Found {len(spouses_children)} potential children from spouse(s)"
                )
                discoveries.extend(spouses_children)
            except Exception as e:
                logger.error(
                    f"Error discovering spouse's children for person {person.id}: {str(e)}",
                    exc_info=True,
                )
                # Continue with other patterns even if this one fails

            # Pattern 2: Parent's spouse
            try:
                parents_spouse = self._discover_parents_spouse(
                    person.id, user_relationships, connected_person_ids
                )
                logger.debug(
                    f"Found {len(parents_spouse)} potential parents from parent's spouse"
                )
                discoveries.extend(parents_spouse)
            except Exception as e:
                logger.error(
                    f"Error discovering parent's spouse for person {person.id}: {str(e)}",
                    exc_info=True,
                )
                # Continue with other patterns even if this one fails

            # Pattern 3: Child's parent
            try:
                childs_parent = self._discover_childs_parent(
                    person.id, user_relationships, connected_person_ids
                )
                logger.debug(
                    f"Found {len(childs_parent)} potential spouses from child's parent"
                )
                discoveries.extend(childs_parent)
            except Exception as e:
                logger.error(
                    f"Error discovering child's parent for person {person.id}: {str(e)}",
                    exc_info=True,
                )
                # Continue even if this pattern fails

            # Sort and filter results
            try:
                sorted_discoveries = self._sort_and_limit_discoveries(discoveries)
            except Exception as e:
                logger.error(
                    f"Error sorting discoveries for person {person.id}: {str(e)}",
                    exc_info=True,
                )
                # Return unsorted results rather than failing completely
                sorted_discoveries = discoveries[:20]

            logger.info(
                f"Discovery complete for user {current_user_id}: "
                f"Found {len(sorted_discoveries)} suggestions"
            )

            return sorted_discoveries

        except Exception as e:
            # Log the error and re-raise for API layer to handle
            logger.exception(
                f"Unexpected error in family member discovery for user {current_user_id}: {str(e)}"
            )
            raise

    def _get_connected_person_ids_from_relationships(
        self, person_id: uuid.UUID, relationships: list[PersonRelationship]
    ) -> set[uuid.UUID]:
        """Get all person IDs that are already connected to the user.

        Args:
            person_id: User's person ID
            relationships: List of active relationships

        Returns:
            Set of connected person IDs (including the user's own person ID)
        """
        # Extract related person IDs from the provided relationships
        connected_ids = {rel.related_person_id for rel in relationships}

        # Add the person's own ID to avoid suggesting themselves
        connected_ids.add(person_id)

        return connected_ids

    def _get_gender_code(self, gender_id: uuid.UUID) -> str:
        """Get gender code for a gender_id using hardcoded mapping.

        Args:
            gender_id: Gender ID

        Returns:
            Gender code ('male', 'female') or 'unknown'
        """
        return GENDER_ID_TO_CODE.get(gender_id, "unknown")

    def _infer_child_relationship(self, gender_id: uuid.UUID) -> RelationshipType:
        """Infer Son or Daughter based on gender_id.

        Args:
            gender_id: Gender ID of the child

        Returns:
            Relationship type (Son or Daughter)
        """
        from app.enums.relationship_type import RelationshipType

        gender_code = self._get_gender_code(gender_id)

        # Infer based on gender code
        if gender_code == GENDER_CODE_FEMALE:
            return RelationshipType.DAUGHTER
        else:
            # Default to Son for male or unknown
            return RelationshipType.SON

    def _infer_parent_relationship(self, gender_id: uuid.UUID) -> RelationshipType:
        """Infer Father or Mother based on gender_id.

        Args:
            gender_id: Gender ID of the parent

        Returns:
            Relationship type (Father or Mother)
        """
        from app.enums.relationship_type import RelationshipType

        gender_code = self._get_gender_code(gender_id)

        # Infer based on gender code
        if gender_code == GENDER_CODE_FEMALE:
            return RelationshipType.MOTHER
        else:
            # Default to Father for male or unknown
            return RelationshipType.FATHER

    def _build_discovery_result(
        self,
        person: Person,
        inferred_relationship_type: RelationshipType,
        connection_path: str,
        proximity_score: int,
        relationship_priority: int,
    ) -> PersonDiscoveryResult | None:
        """Build a discovery result with person details.

        Args:
            person: Person object (already fetched)
            inferred_relationship_type: Inferred relationship type
            connection_path: Human-readable connection path
            proximity_score: Relationship proximity (1 = direct, 2 = 2 degrees, etc.)
            relationship_priority: Relationship type priority (1 = children, 2 = parents, 3 = spouses)

        Returns:
            PersonDiscoveryResult or None if person data is invalid or person is inactive
        """
        try:
            # Skip inactive persons (e.g., temporary persons pending approval)
            if hasattr(person, "is_active") and not person.is_active:
                logger.debug(
                    f"Person {person.id} is inactive, skipping from discovery results"
                )
                return None

            # Validate required fields
            if (
                not person.first_name
                or not person.last_name
                or not person.date_of_birth
            ):
                logger.warning(
                    f"Person {person.id} missing required fields "
                    f"(first_name: {person.first_name}, last_name: {person.last_name}, "
                    f"date_of_birth: {person.date_of_birth}). Skipping."
                )
                return None

            # Get relationship label
            inferred_relationship_label = inferred_relationship_type.label

            # Build and return discovery result
            # Note: address_display and religion_display are set to None for performance
            # These fields are optional and can be populated later if needed
            return PersonDiscoveryResult(
                person_id=person.id,
                first_name=person.first_name,
                middle_name=person.middle_name,
                last_name=person.last_name,
                date_of_birth=person.date_of_birth,
                date_of_death=person.date_of_death,
                gender_id=person.gender_id,
                address_display=None,  # Optional - not populated for performance
                religion_display=None,  # Optional - not populated for performance
                inferred_relationship_type=inferred_relationship_type.value,
                inferred_relationship_label=inferred_relationship_label,
                connection_path=connection_path,
                proximity_score=proximity_score,
                relationship_priority=relationship_priority,
            )
        except Exception as e:
            logger.error(
                f"Error building discovery result for person {person.id}: {str(e)}",
                exc_info=True,
            )
            return None

    def _discover_spouses_children(
        self,
        person_id: uuid.UUID,
        user_relationships: list[PersonRelationship],
        connected_person_ids: set[uuid.UUID],
    ) -> list[PersonDiscoveryResult]:
        """Discover children of user's spouse.

        Logic:
        1. Filter user's spouses from provided relationships (Wife/Husband/Spouse)
        2. For each spouse, find their children (Son/Daughter relationships)
        3. Filter out children already connected to user
        4. Infer relationship type based on child's gender

        Args:
            person_id: User's person ID
            user_relationships: Pre-fetched list of user's active relationships
            connected_person_ids: Set of already-connected person IDs

        Returns:
            List of discovered children
        """
        from app.enums.relationship_type import RelationshipType

        discoveries: list[PersonDiscoveryResult] = []

        # Filter user's spouses from the provided relationships
        spouse_relationships = [
            r
            for r in user_relationships
            if r.relationship_type
            in [
                RelationshipType.WIFE,
                RelationshipType.HUSBAND,
                RelationshipType.SPOUSE,
            ]
        ]

        logger.debug(
            f"Found {len(spouse_relationships)} spouse(s) for person {person_id}"
        )

        # For each spouse, find their children
        for spouse_rel in spouse_relationships:
            spouse_id = spouse_rel.related_person_id
            spouse = self.person_repo.get_by_id(spouse_id)

            if not spouse:
                logger.warning(f"Spouse person not found: {spouse_id}")
                continue

            spouse_name = f"{spouse.first_name} {spouse.last_name}"
            logger.debug(
                f"Checking children of spouse: {spouse_name} (ID: {spouse_id})"
            )

            # Find spouse's children
            child_relationships = self.relationship_repo.get_by_relationship_types(
                spouse_id, [RelationshipType.SON, RelationshipType.DAUGHTER]
            )

            # Filter to active relationships only
            child_relationships = [r for r in child_relationships if r.is_active]

            logger.debug(
                f"Spouse {spouse_name} has {len(child_relationships)} child(ren)"
            )

            # Check each child
            for child_rel in child_relationships:
                child_id = child_rel.related_person_id

                # Skip if already connected to user
                if child_id in connected_person_ids:
                    logger.debug(
                        f"Child {child_id} already connected to user, skipping"
                    )
                    continue

                # Fetch child person details ONCE
                child = self.person_repo.get_by_id(child_id)
                if not child:
                    logger.warning(f"Child person not found: {child_id}")
                    continue

                # Infer relationship type based on child's gender
                inferred_relationship_type = self._infer_child_relationship(
                    child.gender_id
                )

                # Build connection path
                connection_path = f"Connected to your spouse {spouse_name}"

                # Build discovery result (pass Person object, not ID)
                discovery = self._build_discovery_result(
                    person=child,
                    inferred_relationship_type=inferred_relationship_type,
                    connection_path=connection_path,
                    proximity_score=2,  # 2 degrees of separation
                    relationship_priority=1,  # Children have priority 1
                )

                if discovery:
                    discoveries.append(discovery)
                    logger.debug(
                        f"Added discovery: {discovery.first_name} {discovery.last_name} "
                        f"as {discovery.inferred_relationship_label}"
                    )
                else:
                    logger.warning(
                        f"Failed to build discovery result for child {child_id}"
                    )

        return discoveries

    def _discover_parents_spouse(
        self,
        person_id: uuid.UUID,
        user_relationships: list[PersonRelationship],
        connected_person_ids: set[uuid.UUID],
    ) -> list[PersonDiscoveryResult]:
        """Discover spouse of user's parent.

        Logic:
        1. Filter user's parents from provided relationships (Father/Mother)
        2. For each parent, find their spouse (Spouse/Wife/Husband relationships)
        3. Filter out spouses already connected to user
        4. Infer relationship type based on spouse's gender

        Args:
            person_id: User's person ID
            user_relationships: Pre-fetched list of user's active relationships
            connected_person_ids: Set of already-connected person IDs

        Returns:
            List of discovered parents
        """
        from app.enums.relationship_type import RelationshipType

        discoveries: list[PersonDiscoveryResult] = []

        # Filter user's parents from the provided relationships
        parent_relationships = [
            r
            for r in user_relationships
            if r.relationship_type in [RelationshipType.FATHER, RelationshipType.MOTHER]
        ]

        logger.debug(
            f"Found {len(parent_relationships)} parent(s) for person {person_id}"
        )

        # For each parent, find their spouse
        for parent_rel in parent_relationships:
            parent_id = parent_rel.related_person_id
            parent = self.person_repo.get_by_id(parent_id)

            if not parent:
                logger.warning(f"Parent person not found: {parent_id}")
                continue

            parent_name = f"{parent.first_name} {parent.last_name}"
            logger.debug(f"Checking spouse of parent: {parent_name} (ID: {parent_id})")

            # Find parent's spouse
            spouse_relationships = self.relationship_repo.get_by_relationship_types(
                parent_id,
                [
                    RelationshipType.WIFE,
                    RelationshipType.HUSBAND,
                    RelationshipType.SPOUSE,
                ],
            )

            # Filter to active relationships only
            spouse_relationships = [r for r in spouse_relationships if r.is_active]

            logger.debug(
                f"Parent {parent_name} has {len(spouse_relationships)} spouse(s)"
            )

            # Check each spouse
            for spouse_rel in spouse_relationships:
                spouse_id = spouse_rel.related_person_id

                # Skip if already connected to user
                if spouse_id in connected_person_ids:
                    logger.debug(
                        f"Spouse {spouse_id} already connected to user, skipping"
                    )
                    continue

                # Fetch spouse person details ONCE
                spouse = self.person_repo.get_by_id(spouse_id)
                if not spouse:
                    logger.warning(f"Spouse person not found: {spouse_id}")
                    continue

                # Infer relationship type based on spouse's gender
                inferred_relationship_type = self._infer_parent_relationship(
                    spouse.gender_id
                )

                # Build connection path
                connection_path = f"Connected to your parent {parent_name}"

                # Build discovery result (pass Person object, not ID)
                discovery = self._build_discovery_result(
                    person=spouse,
                    inferred_relationship_type=inferred_relationship_type,
                    connection_path=connection_path,
                    proximity_score=2,  # 2 degrees of separation
                    relationship_priority=2,  # Parents have priority 2
                )

                if discovery:
                    discoveries.append(discovery)
                    logger.debug(
                        f"Added discovery: {discovery.first_name} {discovery.last_name} "
                        f"as {discovery.inferred_relationship_label}"
                    )
                else:
                    logger.warning(
                        f"Failed to build discovery result for spouse {spouse_id}"
                    )

        return discoveries

    def _discover_childs_parent(
        self,
        person_id: uuid.UUID,
        user_relationships: list[PersonRelationship],
        connected_person_ids: set[uuid.UUID],
    ) -> list[PersonDiscoveryResult]:
        """Discover parent of user's child.

        Logic:
        1. Filter user's children from provided relationships (Son/Daughter)
        2. For each child, find their parents (Father/Mother relationships)
        3. Filter out parents already connected to user
        4. Infer relationship type as "Spouse" (gender-neutral)

        Args:
            person_id: User's person ID
            user_relationships: Pre-fetched list of user's active relationships
            connected_person_ids: Set of already-connected person IDs

        Returns:
            List of discovered spouses
        """
        from app.enums.relationship_type import RelationshipType

        discoveries: list[PersonDiscoveryResult] = []

        # Filter user's children from the provided relationships
        child_relationships = [
            r
            for r in user_relationships
            if r.relationship_type in [RelationshipType.SON, RelationshipType.DAUGHTER]
        ]

        logger.debug(
            f"Found {len(child_relationships)} child(ren) for person {person_id}"
        )

        # For each child, find their parents
        for child_rel in child_relationships:
            child_id = child_rel.related_person_id
            child = self.person_repo.get_by_id(child_id)

            if not child:
                logger.warning(f"Child person not found: {child_id}")
                continue

            child_name = f"{child.first_name} {child.last_name}"
            logger.debug(f"Checking parents of child: {child_name} (ID: {child_id})")

            # Find child's parents
            parent_relationships = self.relationship_repo.get_by_relationship_types(
                child_id, [RelationshipType.FATHER, RelationshipType.MOTHER]
            )

            # Filter to active relationships only
            parent_relationships = [r for r in parent_relationships if r.is_active]

            logger.debug(
                f"Child {child_name} has {len(parent_relationships)} parent(s)"
            )

            # Check each parent
            for parent_rel in parent_relationships:
                parent_id = parent_rel.related_person_id

                # Skip if already connected to user
                if parent_id in connected_person_ids:
                    logger.debug(
                        f"Parent {parent_id} already connected to user, skipping"
                    )
                    continue

                # Fetch parent person details ONCE
                parent = self.person_repo.get_by_id(parent_id)
                if not parent:
                    logger.warning(f"Parent person not found: {parent_id}")
                    continue

                # Infer relationship type as "Spouse" (gender-neutral)
                inferred_relationship_type = RelationshipType.SPOUSE

                # Build connection path
                connection_path = f"Connected to your child {child_name}"

                # Build discovery result (pass Person object, not ID)
                discovery = self._build_discovery_result(
                    person=parent,
                    inferred_relationship_type=inferred_relationship_type,
                    connection_path=connection_path,
                    proximity_score=2,  # 2 degrees of separation
                    relationship_priority=3,  # Spouses have priority 3
                )

                if discovery:
                    discoveries.append(discovery)
                    logger.debug(
                        f"Added discovery: {discovery.first_name} {discovery.last_name} "
                        f"as {discovery.inferred_relationship_label}"
                    )
                else:
                    logger.warning(
                        f"Failed to build discovery result for parent {parent_id}"
                    )

        return discoveries

    def _sort_and_limit_discoveries(
        self, discoveries: list[PersonDiscoveryResult]
    ) -> list[PersonDiscoveryResult]:
        """Sort discoveries and limit to top 20 results.

        Sorting order:
        1. proximity_score (ascending) - direct connections first
        2. relationship_priority (ascending) - children, then parents, then spouses
        3. first_name (alphabetical)

        Also deduplicates persons appearing through multiple paths,
        keeping the most direct connection.

        Args:
            discoveries: List of discovery results

        Returns:
            Sorted and limited list (max 20 results)
        """
        if not discoveries:
            return []

        # Deduplicate by person_id, keeping the best result for each person
        person_map: dict[uuid.UUID, PersonDiscoveryResult] = {}

        for discovery in discoveries:
            person_id = discovery.person_id

            if person_id not in person_map:
                # First time seeing this person
                person_map[person_id] = discovery
            else:
                # Person already exists, keep the better one
                existing = person_map[person_id]

                # Compare by proximity first
                if discovery.proximity_score < existing.proximity_score:
                    person_map[person_id] = discovery
                elif discovery.proximity_score == existing.proximity_score:
                    # Same proximity, compare by relationship priority
                    if discovery.relationship_priority < existing.relationship_priority:
                        person_map[person_id] = discovery

        # Get deduplicated list
        deduplicated = list(person_map.values())

        logger.debug(
            f"Deduplicated {len(discoveries)} discoveries to {len(deduplicated)} unique persons"
        )

        # Sort by proximity_score, relationship_priority, then first_name
        sorted_discoveries = sorted(
            deduplicated,
            key=lambda d: (
                d.proximity_score,
                d.relationship_priority,
                d.first_name.lower(),
            ),
        )

        # Limit to top 20
        limited = sorted_discoveries[:20]

        if len(sorted_discoveries) > 20:
            logger.debug(f"Limited results from {len(sorted_discoveries)} to 20")

        return limited
