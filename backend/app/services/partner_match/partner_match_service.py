"""Partner Match service for finding potential marriage matches."""

import logging
import uuid
from collections import deque
from dataclasses import dataclass

from fastapi import HTTPException
from sqlmodel import Session, col, select

from app.core.config import settings
from app.db_models.address.country import Country
from app.db_models.address.district import District
from app.db_models.address.locality import Locality
from app.db_models.address.state import State
from app.db_models.address.sub_district import SubDistrict
from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_relationship import PersonRelationship
from app.db_models.person.person_religion import PersonReligion
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.db_models.religion.religion_sub_category import ReligionSubCategory
from app.enums.gender import get_gender_by_code, get_gender_by_id
from app.enums.marital_status import MaritalStatus
from app.enums.relationship_type import RelationshipType
from app.schemas.partner_match import (
    MatchConnectionInfo,
    MatchGraphNode,
    PartnerMatchRequest,
    PartnerMatchResponse,
)

logger = logging.getLogger(__name__)


@dataclass
class PersonReligionIds:
    """Container for person's religion IDs."""

    religion_id: uuid.UUID | None = None
    category_id: uuid.UUID | None = None
    sub_category_id: uuid.UUID | None = None


class PartnerMatchService:
    """Service for finding potential marriage matches within a family network.

    Uses BFS traversal to explore family relationships and applies
    cultural/religious compatibility filters.
    """

    # Relationship types that indicate marriage
    SPOUSE_RELATIONSHIP_TYPES = {
        RelationshipType.WIFE,
        RelationshipType.HUSBAND,
        RelationshipType.SPOUSE,
    }

    # Relationship types that indicate having children
    CHILD_RELATIONSHIP_TYPES = {
        RelationshipType.SON,
        RelationshipType.DAUGHTER,
    }

    # Relationship types that indicate close family (excluded from matches)
    # Parents, children, and spouses are too close to be potential partners
    CLOSE_FAMILY_RELATIONSHIP_TYPES = {
        RelationshipType.FATHER,
        RelationshipType.MOTHER,
        RelationshipType.SON,
        RelationshipType.DAUGHTER,
        RelationshipType.WIFE,
        RelationshipType.HUSBAND,
        RelationshipType.SPOUSE,
    }

    def __init__(self, session: Session):
        """Initialize the partner match service.

        Args:
            session: Database session
        """
        self.session = session
        self.default_depth = settings.PARTNER_MATCH_DEFAULT_DEPTH
        self.max_allowed_depth = settings.PARTNER_MATCH_MAX_DEPTH

    def find_matches(self, request: PartnerMatchRequest) -> PartnerMatchResponse:
        """Find potential partner matches for a seeker.

        Args:
            request: Partner match request with filters

        Returns:
            PartnerMatchResponse with matches and exploration graph

        Raises:
            HTTPException: 404 if seeker not found, 400 for invalid parameters
        """
        logger.info(
            f"Finding partner matches for seeker={request.seeker_person_id}, "
            f"target_gender={request.target_gender_code}, max_depth={request.max_depth}"
        )

        # Validate seeker exists
        seeker = self._get_person(request.seeker_person_id)
        if not seeker:
            logger.warning(f"Seeker person not found: {request.seeker_person_id}")
            raise HTTPException(status_code=404, detail="Seeker person not found")

        # Validate gender code
        if not get_gender_by_code(request.target_gender_code):
            logger.warning(f"Invalid gender code: {request.target_gender_code}")
            raise HTTPException(
                status_code=400, detail="Invalid gender code. Use 'MALE' or 'FEMALE'"
            )

        # Validate and apply max_depth limit
        max_depth = min(request.max_depth, self.max_allowed_depth)
        if request.max_depth > self.max_allowed_depth:
            logger.warning(
                f"Requested max_depth {request.max_depth} exceeds limit "
                f"{self.max_allowed_depth}, using {max_depth}"
            )

        # Run BFS exploration
        parent_map, depth_map, matches = self._bfs_explore(
            seeker_id=request.seeker_person_id,
            max_depth=max_depth,
            request=request,
        )

        logger.info(
            f"BFS complete: visited={len(parent_map)} nodes, "
            f"found={len(matches)} matches"
        )

        # Build exploration tree
        exploration_graph = self._build_exploration_tree(
            parent_map=parent_map,
            depth_map=depth_map,
            matches=matches,
            seeker_id=request.seeker_person_id,
        )

        # Apply graph pruning if requested (default: True)
        if request.prune_graph:
            exploration_graph = self._prune_graph(
                graph=exploration_graph,
                matches=matches,
                seeker_id=request.seeker_person_id,
            )

        return PartnerMatchResponse(
            seeker_id=request.seeker_person_id,
            total_matches=len(matches),
            matches=matches,
            exploration_graph=exploration_graph,
        )

    def _bfs_explore(
        self,
        seeker_id: uuid.UUID,
        max_depth: int,
        request: PartnerMatchRequest,
    ) -> tuple[
        dict[uuid.UUID, uuid.UUID | None], dict[uuid.UUID, int], list[uuid.UUID]
    ]:
        """Perform BFS from seeker, tracking parent relationships and finding matches.

        Args:
            seeker_id: Starting person ID
            max_depth: Maximum traversal depth
            request: Partner match request with filters

        Returns:
            Tuple of:
            - parent_map: {person_id: parent_person_id} for tree reconstruction
            - depth_map: {person_id: depth} distance from seeker
            - matches: list of eligible match person_ids
        """
        parent_map: dict[uuid.UUID, uuid.UUID | None] = {seeker_id: None}
        depth_map: dict[uuid.UUID, int] = {seeker_id: 0}
        matches: list[uuid.UUID] = []

        # Get seeker's close family members to exclude from matches
        close_family_ids = self._get_close_family_ids(seeker_id)

        queue: deque[uuid.UUID] = deque([seeker_id])
        current_depth = 0

        while queue and current_depth < max_depth:
            level_size = len(queue)
            current_depth += 1

            for _ in range(level_size):
                current_id = queue.popleft()
                relationships = self._get_relationships(current_id)

                for related_id in relationships:
                    if related_id in parent_map:
                        continue  # Already visited

                    parent_map[related_id] = current_id
                    depth_map[related_id] = current_depth
                    queue.append(related_id)

                    # Check if eligible match (skip seeker and close family)
                    if (
                        related_id != seeker_id
                        and related_id not in close_family_ids
                        and self._is_eligible_match(related_id, request)
                    ):
                        matches.append(related_id)

        return parent_map, depth_map, matches

    def _get_close_family_ids(self, person_id: uuid.UUID) -> set[uuid.UUID]:
        """Get IDs of close family members who should be excluded from matches.

        Close family includes:
        - Parents (Father, Mother)
        - Children (Son, Daughter)
        - Spouses (Wife, Husband, Spouse)
        - Siblings (share at least one parent)

        Args:
            person_id: Person whose close family to find

        Returns:
            Set of person IDs who are close family members
        """
        close_family: set[uuid.UUID] = set()

        # Get direct relationships
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id,
            PersonRelationship.is_active == True,  # noqa: E712
        )
        relationships = self.session.exec(statement).all()

        # Collect parents for sibling detection
        parent_ids: set[uuid.UUID] = set()

        for rel in relationships:
            # Add all close family relationships
            if rel.relationship_type in self.CLOSE_FAMILY_RELATIONSHIP_TYPES:
                close_family.add(rel.related_person_id)

            # Track parents for sibling detection
            if rel.relationship_type in {
                RelationshipType.FATHER,
                RelationshipType.MOTHER,
            }:
                parent_ids.add(rel.related_person_id)

        # Find siblings (people who share at least one parent)
        for parent_id in parent_ids:
            # Get all children of this parent
            parent_children_stmt = select(PersonRelationship).where(
                PersonRelationship.person_id == parent_id,
                PersonRelationship.is_active == True,  # noqa: E712
                col(PersonRelationship.relationship_type).in_(
                    list(self.CHILD_RELATIONSHIP_TYPES)
                ),
            )
            parent_children = self.session.exec(parent_children_stmt).all()

            for child_rel in parent_children:
                if child_rel.related_person_id != person_id:
                    close_family.add(child_rel.related_person_id)

        logger.debug(
            f"Close family for person {person_id}: {len(close_family)} members"
        )

        return close_family

    def _is_eligible_match(
        self, person_id: uuid.UUID, request: PartnerMatchRequest
    ) -> bool:
        """Check if a person passes all eligibility filters.

        Args:
            person_id: Person to check
            request: Partner match request with filters

        Returns:
            True if person is an eligible match
        """
        person = self._get_person(person_id)
        if not person:
            return False

        # 1. Gender check
        if not self._matches_gender(person, request.target_gender_code):
            return False

        # 2. Living check - must not have date_of_death
        if person.date_of_death is not None:
            return False

        # 3. Age/birth year check
        birth_year = person.date_of_birth.year if person.date_of_birth else None
        if not self._in_birth_year_range(
            birth_year, request.birth_year_min, request.birth_year_max
        ):
            return False

        # 4-7. Religion filters (inclusion and exclusion)
        if not self._passes_religion_filters(person_id, request):
            return False

        # 8. Marital status check - use marital_status field with relationship fallback
        if self._is_ineligible_marital_status(person):
            return False

        return True

    def _matches_gender(self, person: Person, target_gender_code: str) -> bool:
        """Check if person's gender matches the target gender code.

        Args:
            person: Person to check
            target_gender_code: Target gender code (e.g., 'MALE', 'FEMALE')

        Returns:
            True if gender matches
        """
        person_gender = get_gender_by_id(person.gender_id)
        if not person_gender:
            return False
        return person_gender.code.upper() == target_gender_code.upper()

    def _in_birth_year_range(
        self,
        birth_year: int | None,
        birth_year_min: int | None,
        birth_year_max: int | None,
    ) -> bool:
        """Check if birth year is within the specified range.

        Args:
            birth_year: Person's birth year (None if unknown)
            birth_year_min: Minimum birth year (inclusive)
            birth_year_max: Maximum birth year (inclusive)

        Returns:
            True if birth year is within range or no range specified
        """
        if birth_year is None:
            # If birth year is unknown, exclude from matches
            return False

        if birth_year_min is not None and birth_year < birth_year_min:
            return False

        if birth_year_max is not None and birth_year > birth_year_max:
            return False

        return True

    def _passes_religion_filters(
        self, person_id: uuid.UUID, request: PartnerMatchRequest
    ) -> bool:
        """Check if person passes all religion inclusion and exclusion filters.

        Args:
            person_id: Person to check
            request: Partner match request with religion filters

        Returns:
            True if person passes all religion filters
        """
        religion_ids = self._get_person_religion_ids(person_id)

        # Inclusion filters (AND logic between different levels)
        # If include list is provided and non-empty, person must match

        if request.include_religion_ids:
            if (
                religion_ids.religion_id is None
                or religion_ids.religion_id not in request.include_religion_ids
            ):
                return False

        if request.include_category_ids:
            if (
                religion_ids.category_id is None
                or religion_ids.category_id not in request.include_category_ids
            ):
                return False

        if request.include_sub_category_ids:
            if (
                religion_ids.sub_category_id is None
                or religion_ids.sub_category_id not in request.include_sub_category_ids
            ):
                return False

        # Exclusion filter (gotra exclusion)
        if request.exclude_sub_category_ids:
            if (
                religion_ids.sub_category_id is not None
                and religion_ids.sub_category_id in request.exclude_sub_category_ids
            ):
                return False

        return True

    def _is_ineligible_marital_status(self, person: Person) -> bool:
        """Check if person is ineligible based on marital status.

        Uses the person's marital_status field as the primary check.
        Falls back to relationship-based check only if marital_status is UNKNOWN.

        Eligible statuses: SINGLE, DIVORCED, WIDOWED, SEPARATED
        Ineligible statuses: MARRIED
        Fallback (UNKNOWN): Check for spouse/child relationships

        Args:
            person: Person object (already fetched from DB)

        Returns:
            True if person is ineligible (married or has children)
        """
        # Use marital_status field if it's set (not UNKNOWN)
        if person.marital_status != MaritalStatus.UNKNOWN:
            # MARRIED means ineligible
            # SINGLE, DIVORCED, WIDOWED, SEPARATED are all eligible
            return person.marital_status == MaritalStatus.MARRIED

        # Fallback: marital_status is UNKNOWN, check relationships
        logger.debug(
            f"Person {person.id} has UNKNOWN marital status, "
            "falling back to relationship-based check"
        )

        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person.id,
            PersonRelationship.is_active == True,  # noqa: E712
        )
        relationships = self.session.exec(statement).all()

        for rel in relationships:
            # Check for spouse relationships
            if rel.relationship_type in self.SPOUSE_RELATIONSHIP_TYPES:
                return True
            # Check for child relationships (person has children)
            if rel.relationship_type in self.CHILD_RELATIONSHIP_TYPES:
                return True

        return False

    def _build_exploration_tree(
        self,
        parent_map: dict[uuid.UUID, uuid.UUID | None],
        depth_map: dict[uuid.UUID, int],
        matches: list[uuid.UUID],
        seeker_id: uuid.UUID,
    ) -> dict[uuid.UUID, MatchGraphNode]:
        """Build the exploration tree from BFS results.

        Args:
            parent_map: {person_id: parent_person_id} mapping
            depth_map: {person_id: depth} mapping
            matches: List of eligible match person_ids
            seeker_id: The seeker's person ID

        Returns:
            Dictionary mapping person_id -> MatchGraphNode
        """
        matches_set = set(matches)
        graph: dict[uuid.UUID, MatchGraphNode] = {}

        # First pass: create all nodes with enriched data
        for person_id in parent_map:
            node = self._enrich_node_data(person_id)
            node.depth = depth_map[person_id]
            node.is_match = person_id in matches_set
            graph[person_id] = node

        # Second pass: set from_person and to_persons connections
        for person_id, parent_id in parent_map.items():
            node = graph[person_id]

            # Set from_person (parent in BFS tree)
            if parent_id is not None:
                relationship_type = self._get_relationship_type(person_id, parent_id)
                node.set_from_person(
                    MatchConnectionInfo(
                        person_id=parent_id,
                        relationship=relationship_type,
                    )
                )

                # Add this node to parent's to_persons list
                parent_node = graph[parent_id]
                reverse_relationship = self._get_relationship_type(parent_id, person_id)
                parent_node.add_to_person(
                    MatchConnectionInfo(
                        person_id=person_id,
                        relationship=reverse_relationship,
                    )
                )

        return graph

    def _prune_graph(
        self,
        graph: dict[uuid.UUID, MatchGraphNode],
        matches: list[uuid.UUID],
        seeker_id: uuid.UUID,
    ) -> dict[uuid.UUID, MatchGraphNode]:
        """Prune the exploration graph to only include nodes on paths to matches.

        Algorithm:
        1. Start with empty set of nodes_to_keep
        2. For each match, trace back to seeker via from_person links
        3. Add all nodes on each path to nodes_to_keep
        4. Filter graph to only include nodes_to_keep
        5. Update to_persons lists to only reference kept nodes

        Args:
            graph: Full exploration graph from BFS
            matches: List of eligible match person_ids
            seeker_id: The seeker's person ID

        Returns:
            Pruned graph containing only nodes on paths from seeker to matches
        """
        logger.debug(
            f"Pruning graph: {len(graph)} nodes, {len(matches)} matches, seeker={seeker_id}"
        )

        # Handle edge case: no matches - return only seeker node
        if not matches:
            logger.debug("No matches found, returning only seeker node")
            seeker_node = graph[seeker_id]
            # Clear to_persons since no children lead to matches
            pruned_seeker = MatchGraphNode(
                person_id=seeker_node.person_id,
                first_name=seeker_node.first_name,
                last_name=seeker_node.last_name,
                birth_year=seeker_node.birth_year,
                death_year=seeker_node.death_year,
                address=seeker_node.address,
                religion=seeker_node.religion,
                is_match=seeker_node.is_match,
                depth=seeker_node.depth,
                from_person=seeker_node.from_person,
                to_persons=[],
            )
            return {seeker_id: pruned_seeker}

        # Collect all nodes on paths from matches back to seeker
        nodes_to_keep: set[uuid.UUID] = {seeker_id}

        for match_id in matches:
            current_id: uuid.UUID | None = match_id
            while current_id is not None:
                nodes_to_keep.add(current_id)
                node = graph.get(current_id)
                if node and node.from_person:
                    current_id = node.from_person.person_id
                else:
                    current_id = None

        logger.debug(
            f"Nodes to keep after tracing paths: {len(nodes_to_keep)} of {len(graph)}"
        )

        # Build pruned graph with filtered to_persons
        pruned_graph: dict[uuid.UUID, MatchGraphNode] = {}
        for person_id in nodes_to_keep:
            original_node = graph[person_id]
            # Filter to_persons to only include kept nodes
            filtered_to_persons = [
                conn
                for conn in original_node.to_persons
                if conn.person_id in nodes_to_keep
            ]
            # Create new node with filtered connections
            pruned_node = MatchGraphNode(
                person_id=original_node.person_id,
                first_name=original_node.first_name,
                last_name=original_node.last_name,
                birth_year=original_node.birth_year,
                death_year=original_node.death_year,
                address=original_node.address,
                religion=original_node.religion,
                is_match=original_node.is_match,
                depth=original_node.depth,
                from_person=original_node.from_person,
                to_persons=filtered_to_persons,
            )
            pruned_graph[person_id] = pruned_node

        logger.info(
            f"Graph pruned: {len(graph)} -> {len(pruned_graph)} nodes "
            f"({len(graph) - len(pruned_graph)} removed)"
        )

        return pruned_graph

    # ==================== Helper Methods ====================

    def _get_person(self, person_id: uuid.UUID) -> Person | None:
        """Get a person by ID.

        Args:
            person_id: Person's ID

        Returns:
            Person object or None if not found
        """
        statement = select(Person).where(Person.id == person_id)
        return self.session.exec(statement).first()

    def _get_relationships(self, person_id: uuid.UUID) -> list[uuid.UUID]:
        """Get all active relationships for a person.

        Args:
            person_id: Person's ID

        Returns:
            List of related_person_ids
        """
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id,
            PersonRelationship.is_active == True,  # noqa: E712
        )
        relationships = self.session.exec(statement).all()

        return [rel.related_person_id for rel in relationships]

    def _get_relationship_type(
        self, from_person_id: uuid.UUID, to_person_id: uuid.UUID
    ) -> str:
        """Get the relationship type label between two persons.

        Args:
            from_person_id: The person whose perspective we're looking from
            to_person_id: The related person

        Returns:
            Relationship type label (e.g., "Father", "Son") or "Related" if not found
        """
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == from_person_id,
            PersonRelationship.related_person_id == to_person_id,
            PersonRelationship.is_active == True,  # noqa: E712
        )
        relationship = self.session.exec(statement).first()

        if relationship:
            return relationship.relationship_type.label

        return "Related"

    def _get_person_religion_ids(self, person_id: uuid.UUID) -> PersonReligionIds:
        """Get religion IDs for a person.

        Args:
            person_id: Person's ID

        Returns:
            PersonReligionIds with religion, category, and sub-category IDs
        """
        statement = select(PersonReligion).where(PersonReligion.person_id == person_id)
        person_religion = self.session.exec(statement).first()

        if not person_religion:
            return PersonReligionIds()

        return PersonReligionIds(
            religion_id=person_religion.religion_id,
            category_id=person_religion.religion_category_id,
            sub_category_id=person_religion.religion_sub_category_id,
        )

    def _enrich_node_data(self, person_id: uuid.UUID) -> MatchGraphNode:
        """Fetch and format person details including address and religion.

        Args:
            person_id: Person's ID

        Returns:
            MatchGraphNode with enriched data (from_person and to_persons are set separately)
        """
        person = self._get_person(person_id)
        if not person:
            # Return minimal node if person not found (shouldn't happen)
            return MatchGraphNode(
                person_id=person_id,
                first_name="Unknown",
                last_name="Unknown",
                birth_year=None,
                death_year=None,
                address="",
                religion="",
                is_match=False,
                depth=0,
                from_person=None,
                to_persons=[],
            )

        # Extract birth and death years
        birth_year = person.date_of_birth.year if person.date_of_birth else None
        death_year = person.date_of_death.year if person.date_of_death else None

        # Get address string
        address = self._get_address_string(person_id)

        # Get religion string
        religion = self._get_religion_string(person_id)

        return MatchGraphNode(
            person_id=person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            birth_year=birth_year,
            death_year=death_year,
            address=address,
            religion=religion,
            is_match=False,
            depth=0,
            from_person=None,
            to_persons=[],
        )

    def _get_address_string(self, person_id: uuid.UUID) -> str:
        """Get comma-separated address string for a person.

        Args:
            person_id: Person's ID

        Returns:
            Comma-separated address string or empty string if not available
        """
        # Get current address
        statement = select(PersonAddress).where(
            PersonAddress.person_id == person_id,
            PersonAddress.is_current == True,  # noqa: E712
        )
        person_address = self.session.exec(statement).first()

        if not person_address:
            return ""

        parts: list[str] = []

        # Get locality name
        if person_address.locality_id:
            locality = self.session.exec(
                select(Locality).where(Locality.id == person_address.locality_id)
            ).first()
            if locality:
                parts.append(locality.name)

        # Get sub-district name
        if person_address.sub_district_id:
            sub_district = self.session.exec(
                select(SubDistrict).where(
                    SubDistrict.id == person_address.sub_district_id
                )
            ).first()
            if sub_district:
                parts.append(sub_district.name)

        # Get district name
        if person_address.district_id:
            district = self.session.exec(
                select(District).where(District.id == person_address.district_id)
            ).first()
            if district:
                parts.append(district.name)

        # Get state name
        if person_address.state_id:
            state = self.session.exec(
                select(State).where(State.id == person_address.state_id)
            ).first()
            if state:
                parts.append(state.name)

        # Get country name
        if person_address.country_id:
            country = self.session.exec(
                select(Country).where(Country.id == person_address.country_id)
            ).first()
            if country:
                parts.append(country.name)

        return ", ".join(parts)

    def _get_religion_string(self, person_id: uuid.UUID) -> str:
        """Get comma-separated religion string for a person.

        Args:
            person_id: Person's ID

        Returns:
            Comma-separated religion string or empty string if not available
        """
        statement = select(PersonReligion).where(PersonReligion.person_id == person_id)
        person_religion = self.session.exec(statement).first()

        if not person_religion:
            return ""

        parts: list[str] = []

        # Get religion name
        if person_religion.religion_id:
            religion = self.session.exec(
                select(Religion).where(Religion.id == person_religion.religion_id)
            ).first()
            if religion:
                parts.append(religion.name)

        # Get category name
        if person_religion.religion_category_id:
            category = self.session.exec(
                select(ReligionCategory).where(
                    ReligionCategory.id == person_religion.religion_category_id
                )
            ).first()
            if category:
                parts.append(category.name)

        # Get sub-category name
        if person_religion.religion_sub_category_id:
            sub_category = self.session.exec(
                select(ReligionSubCategory).where(
                    ReligionSubCategory.id == person_religion.religion_sub_category_id
                )
            ).first()
            if sub_category:
                parts.append(sub_category.name)

        return ", ".join(parts)
