"""Lineage Path service for finding relationship paths between persons."""

import logging
import uuid
from collections import deque

from fastapi import HTTPException
from sqlmodel import Session, select

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
from app.schemas.lineage_path import (
    ConnectionInfo,
    LineagePathResponse,
    PersonNode,
)

logger = logging.getLogger(__name__)


class LineagePathService:
    """Service for finding lineage paths between two persons in a family tree.

    Uses Bidirectional BFS to find the shortest path through family relationships.
    """

    def __init__(self, session: Session):
        """Initialize the lineage path service.

        Args:
            session: Database session
        """
        self.session = session
        self.max_depth = settings.LINEAGE_PATH_MAX_DEPTH

    def find_path(
        self, person_a_id: uuid.UUID, person_b_id: uuid.UUID
    ) -> LineagePathResponse:
        """Find the lineage path between two persons.

        Args:
            person_a_id: First person's ID
            person_b_id: Second person's ID

        Returns:
            LineagePathResponse with connection details and graph

        Raises:
            HTTPException: 404 if either person is not found
        """
        logger.info(
            f"Finding lineage path between person_a={person_a_id} and person_b={person_b_id}"
        )

        # Validate both persons exist
        person_a = self._get_person(person_a_id)
        if not person_a:
            logger.warning(f"Person A not found: {person_a_id}")
            raise HTTPException(status_code=404, detail="Person A not found")

        person_b = self._get_person(person_b_id)
        if not person_b:
            logger.warning(f"Person B not found: {person_b_id}")
            raise HTTPException(status_code=404, detail="Person B not found")

        # Handle same person edge case
        if person_a_id == person_b_id:
            logger.info(f"Same person provided: {person_a_id}")
            person_node = self._enrich_person_data(person_a_id)
            return LineagePathResponse(
                connection_found=True,
                message="Same person provided for both inputs",
                common_ancestor_id=person_a_id,
                graph={person_a_id: person_node},
            )

        # Run BFS to find common ancestor
        common_person_id, visited_map_a_to_common, visited_map_b_to_common = (
            self._bfs_find_common_ancestor(person_a_id, person_b_id)
        )

        if common_person_id is None:
            # No connection found
            logger.info(
                f"No connection found between {person_a_id} and {person_b_id} "
                f"within {self.max_depth} levels"
            )
            # Build graph with just the two persons (no connections)
            graph = {
                person_a_id: self._enrich_person_data(person_a_id),
                person_b_id: self._enrich_person_data(person_b_id),
            }
            return LineagePathResponse(
                connection_found=False,
                message=f"No relation found up to {self.max_depth}th connection",
                common_ancestor_id=None,
                graph=graph,
            )

        # Build the ordered path from person A to person B
        ordered_path = self._build_final_ordered_list(
            common_person_id, visited_map_a_to_common, visited_map_b_to_common
        )
        logger.info(
            f"Connection found via common point: {common_person_id}, "
            f"path length={len(ordered_path)}"
        )

        # Build the bidirectional linked list graph
        graph = self._build_bidirectional_linked_list(ordered_path)

        return LineagePathResponse(
            connection_found=True,
            message="Connection found",
            common_ancestor_id=common_person_id,
            graph=graph,
        )

    def _build_final_ordered_list(
        self,
        common_person_id: uuid.UUID,
        visited_map_a_to_common: dict[uuid.UUID, uuid.UUID | None],
        visited_map_b_to_common: dict[uuid.UUID, uuid.UUID | None],
    ) -> list[uuid.UUID]:
        """Build a ordered path from person A to person B through common point.

        Given two visited maps from BFS:
        - visited_map_a_to_common: A -> B -> C -> D (child -> parent mapping)
        - visited_map_b_to_common: M -> N -> O -> D (child -> parent mapping)

        Returns a combined path: [A, B, C, D, O, N, M]

        Args:
            common_person_id: The common person where both paths meet
            visited_map_a_to_common: Map from person A's BFS (person_id -> parent_id)
            visited_map_b_to_common: Map from person B's BFS (person_id -> parent_id)

        Returns:
            List of person IDs representing the full path from A to B
        """
        # Build path from A to common (by walking backwards through visited_map_a)
        path_a_to_common: list[uuid.UUID] = []
        current: uuid.UUID | None = common_person_id
        while current is not None:
            path_a_to_common.append(current)
            current = visited_map_a_to_common.get(current)
        path_a_to_common.reverse()  # Now: [A, B, C, D]

        # Build path from common to B (by walking backwards through visited_map_b, excluding common)
        path_common_to_b: list[uuid.UUID] = []
        current = visited_map_b_to_common.get(
            common_person_id
        )  # Start from parent of common in B's map
        while current is not None:
            path_common_to_b.append(current)
            current = visited_map_b_to_common.get(current)
        # path_common_to_b is now: [O, N, M] (already in correct order)

        # Combine: [A, B, C, D] + [O, N, M] = [A, B, C, D, O, N, M]
        return path_a_to_common + path_common_to_b

    def _build_bidirectional_linked_list(
        self, ordered_person_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, PersonNode]:
        """Build a bidirectional linked list of PersonNodes from ordered person IDs.

        Each PersonNode will have from_person and to_person connections set up
        to form a linked list structure.

        Args:
            ordered_person_ids: List of person IDs in order from person A to person B

        Returns:
            Dictionary mapping person_id -> PersonNode with linked connections
        """
        if not ordered_person_ids:
            return {}

        # First, enrich all person data
        enriched_nodes: dict[uuid.UUID, PersonNode] = {}
        for person_id in ordered_person_ids:
            enriched_nodes[person_id] = self._enrich_person_data(person_id)

        # If only one person, return as-is (no connections to set)
        if len(ordered_person_ids) == 1:
            return enriched_nodes

        # Build the bidirectional linked list
        for index in range(len(ordered_person_ids)):
            current_id = ordered_person_ids[index]
            current_node = enriched_nodes[current_id]

            # Set from_person (previous node in the list)
            if index > 0:
                prev_id = ordered_person_ids[index - 1]
                relationship_type = self._get_relationship_type(current_id, prev_id)
                current_node.set_from_person(
                    ConnectionInfo(
                        person_id=prev_id,
                        relationship=relationship_type,
                    )
                )

            # Set to_person (next node in the list)
            if index < len(ordered_person_ids) - 1:
                next_id = ordered_person_ids[index + 1]
                relationship_type = self._get_relationship_type(current_id, next_id)
                current_node.set_to_person(
                    ConnectionInfo(
                        person_id=next_id,
                        relationship=relationship_type,
                    )
                )

        return enriched_nodes

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
            List of related_person_id
        """
        statement = select(PersonRelationship).where(
            PersonRelationship.person_id == person_id,
            PersonRelationship.is_active == True,  # noqa: E712
        )
        relationships = self.session.exec(statement).all()

        return [rel.related_person_id for rel in relationships]

    def _bfs_find_common_ancestor(
        self, person_a_id: uuid.UUID, person_b_id: uuid.UUID
    ) -> tuple[
        uuid.UUID | None,
        dict[uuid.UUID, uuid.UUID | None],
        dict[uuid.UUID, uuid.UUID | None],
    ]:
        """Find common ancestor using bidirectional BFS.

        Args:
            person_a_id: First person's ID
            person_b_id: Second person's ID

        Returns:
            Tuple of (common_person_id, visited_map_a, visited_map_b)
            common_person_id is None if no connection found within max_depth
        """
        # Track visited nodes and their parents for path reconstruction
        # visited_a[person_id] = parent_person_id (or None for start)
        visited_a: dict[uuid.UUID, uuid.UUID | None] = {person_a_id: None}
        visited_b: dict[uuid.UUID, uuid.UUID | None] = {person_b_id: None}

        # BFS queues
        queue_a: deque[uuid.UUID] = deque([person_a_id])
        queue_b: deque[uuid.UUID] = deque([person_b_id])

        depth = 0

        while depth < self.max_depth and (queue_a or queue_b):
            # Expand from A
            if queue_a:
                next_queue_a: deque[uuid.UUID] = deque()
                while queue_a:
                    current = queue_a.popleft()
                    relationships = self._get_relationships(current)

                    for related_id in relationships:
                        # Check if we found a connection
                        if related_id in visited_b:
                            # Found common point
                            visited_a[related_id] = current
                            return (related_id, visited_a, visited_b)

                        if related_id not in visited_a:
                            visited_a[related_id] = current
                            next_queue_a.append(related_id)

                queue_a = next_queue_a

            # Expand from B
            if queue_b:
                next_queue_b: deque[uuid.UUID] = deque()
                while queue_b:
                    current = queue_b.popleft()
                    relationships = self._get_relationships(current)

                    for related_id in relationships:
                        # Check if we found a connection
                        if related_id in visited_a:
                            visited_b[related_id] = current
                            return (related_id, visited_a, visited_b)

                        if related_id not in visited_b:
                            visited_b[related_id] = current
                            next_queue_b.append(related_id)

                queue_b = next_queue_b

            depth += 1
            logger.debug(
                f"BFS depth {depth}: visited_a={len(visited_a)}, visited_b={len(visited_b)}"
            )

        return (None, visited_a, visited_b)

    def _enrich_person_data(self, person_id: uuid.UUID) -> PersonNode:
        """Fetch and format person details including address and religion.

        Args:
            person_id: Person's ID

        Returns:
            PersonNode with enriched data (from_person and to_person are set separately)
        """
        person = self._get_person(person_id)
        if not person:
            # Return minimal node if person not found (shouldn't happen)
            return PersonNode(
                person_id=person_id,
                first_name="Unknown",
                last_name="Unknown",
                birth_year=None,
                death_year=None,
                address="",
                religion="",
                from_person=None,
                to_person=None,
            )

        # Extract birth and death years
        birth_year = person.date_of_birth.year if person.date_of_birth else None
        death_year = person.date_of_death.year if person.date_of_death else None

        # Get address string
        address = self._get_address_string(person_id)

        # Get religion string
        religion = self._get_religion_string(person_id)

        return PersonNode(
            person_id=person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            birth_year=birth_year,
            death_year=death_year,
            address=address,
            religion=religion,
            from_person=None,
            to_person=None,
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
