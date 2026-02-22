"""Relatives Network service for finding relatives within a family network."""

import logging
import uuid
from collections import deque

from fastapi import HTTPException
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.address.district import District
from app.db_models.address.locality import Locality
from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_relationship import PersonRelationship
from app.schemas.relatives_network import (
    RelativeInfo,
    RelativesNetworkRequest,
    RelativesNetworkResponse,
)

logger = logging.getLogger(__name__)

# Maximum number of results to return
MAX_RESULTS = 100


class RelativesNetworkService:
    """Service for finding relatives within a family network using BFS.

    Uses BFS traversal to explore family relationships up to a specified depth
    and applies filters for living status, gender, and address.
    """

    def __init__(self, session: Session):
        """Initialize the relatives network service.

        Args:
            session: Database session
        """
        self.session = session
        self.max_depth = settings.RELATIVES_NETWORK_MAX_DEPTH

    def find_relatives(
        self, request: RelativesNetworkRequest
    ) -> RelativesNetworkResponse:
        """Find relatives up to or at specified depth.

        Args:
            request: Relatives network request with filters

        Returns:
            RelativesNetworkResponse with relatives list

        Raises:
            HTTPException: 404 if person not found, 400 for invalid parameters
        """
        logger.info(
            f"Finding relatives for person={request.person_id}, "
            f"depth={request.depth}, depth_mode={request.depth_mode}"
        )

        # 1. Validate person exists
        person = self._get_person(request.person_id)
        if not person:
            logger.warning(f"Person not found: {request.person_id}")
            raise HTTPException(status_code=404, detail="Person not found")

        # 2. Validate and cap depth
        effective_depth = min(request.depth, self.max_depth)
        if request.depth > self.max_depth:
            logger.warning(
                f"Requested depth {request.depth} exceeds limit "
                f"{self.max_depth}, using {effective_depth}"
            )

        # 3. Run BFS traversal
        depth_map = self._bfs_traverse(request.person_id, effective_depth)

        # 4. Filter by depth mode
        filtered_person_ids = self._filter_by_depth_mode(
            depth_map, effective_depth, request.depth_mode
        )

        # 5. Exclude self from results
        filtered_person_ids = [
            pid for pid in filtered_person_ids if pid != request.person_id
        ]

        # 6. Apply filters (living, gender, address)
        filtered_person_ids = self._apply_filters(filtered_person_ids, request)

        # 7. Limit results
        if len(filtered_person_ids) > MAX_RESULTS:
            logger.info(
                f"Limiting results from {len(filtered_person_ids)} to {MAX_RESULTS}"
            )
            filtered_person_ids = filtered_person_ids[:MAX_RESULTS]

        # 8. Build response with relative info
        relatives = [
            self._enrich_relative_info(pid, depth_map[pid])
            for pid in filtered_person_ids
        ]

        logger.info(f"Found {len(relatives)} relatives for person {request.person_id}")

        return RelativesNetworkResponse(
            person_id=request.person_id,
            total_count=len(relatives),
            depth=effective_depth,
            depth_mode=request.depth_mode,
            relatives=relatives,
        )

    def _bfs_traverse(
        self, person_id: uuid.UUID, max_depth: int
    ) -> dict[uuid.UUID, int]:
        """BFS traversal returning {person_id: depth} mapping.

        Uses deque for level-by-level traversal and tracks visited nodes
        to avoid cycles.

        Args:
            person_id: Starting person ID
            max_depth: Maximum traversal depth

        Returns:
            Dictionary mapping person_id to their depth from the starting person
        """
        visited: dict[uuid.UUID, int] = {person_id: 0}
        queue: deque[uuid.UUID] = deque([person_id])
        current_depth = 0

        while queue and current_depth < max_depth:
            level_size = len(queue)
            current_depth += 1

            for _ in range(level_size):
                current_id = queue.popleft()
                relationships = self._get_relationships(current_id)

                for related_id in relationships:
                    if related_id not in visited:
                        visited[related_id] = current_depth
                        queue.append(related_id)

        logger.debug(
            f"BFS traversal complete: visited {len(visited)} persons "
            f"up to depth {max_depth}"
        )

        return visited

    def _filter_by_depth_mode(
        self, depth_map: dict[uuid.UUID, int], depth: int, mode: str
    ) -> list[uuid.UUID]:
        """Filter persons by depth mode (up_to or only_at).

        Args:
            depth_map: Dictionary mapping person_id to depth
            depth: Target depth value
            mode: 'up_to' returns all with depth <= N, 'only_at' returns depth == N

        Returns:
            List of person IDs matching the depth criteria
        """
        if mode == "up_to":
            # Return all persons with depth from 1 to N (inclusive)
            return [pid for pid, d in depth_map.items() if 1 <= d <= depth]
        else:  # mode == "only_at"
            # Return only persons exactly at depth N
            return [pid for pid, d in depth_map.items() if d == depth]

    def _apply_filters(
        self, person_ids: list[uuid.UUID], request: RelativesNetworkRequest
    ) -> list[uuid.UUID]:
        """Apply living, gender, and address filters.

        Args:
            person_ids: List of person IDs to filter
            request: Request containing filter criteria

        Returns:
            Filtered list of person IDs
        """
        filtered_ids: list[uuid.UUID] = []

        for person_id in person_ids:
            person = self._get_person(person_id)
            if not person:
                continue

            # Living filter: exclude persons with date_of_death
            if request.living_only and person.date_of_death is not None:
                continue

            # Gender filter: match gender_id
            if request.gender_id is not None and person.gender_id != request.gender_id:
                continue

            # Address filters: match address hierarchy
            if not self._matches_address_filters(person_id, request):
                continue

            filtered_ids.append(person_id)

        return filtered_ids

    def _matches_address_filters(
        self, person_id: uuid.UUID, request: RelativesNetworkRequest
    ) -> bool:
        """Check if person's address matches the address filters.

        Args:
            person_id: Person ID to check
            request: Request containing address filter criteria

        Returns:
            True if address matches all specified filters
        """
        # If no address filters specified, match all
        if not any(
            [
                request.country_id,
                request.state_id,
                request.district_id,
                request.sub_district_id,
                request.locality_id,
            ]
        ):
            return True

        # Get person's current address
        statement = select(PersonAddress).where(
            PersonAddress.person_id == person_id,
            PersonAddress.is_current == True,  # noqa: E712
        )
        person_address = self.session.exec(statement).first()

        if not person_address:
            return False

        # Check each address filter
        if request.country_id and person_address.country_id != request.country_id:
            return False
        if request.state_id and person_address.state_id != request.state_id:
            return False
        if request.district_id and person_address.district_id != request.district_id:
            return False
        if (
            request.sub_district_id
            and person_address.sub_district_id != request.sub_district_id
        ):
            return False
        if request.locality_id and person_address.locality_id != request.locality_id:
            return False

        return True

    def _enrich_relative_info(self, person_id: uuid.UUID, depth: int) -> RelativeInfo:
        """Fetch person details and build RelativeInfo.

        Args:
            person_id: Person ID to enrich
            depth: Relationship depth from the requesting person

        Returns:
            RelativeInfo with person details and address
        """
        person = self._get_person(person_id)
        if not person:
            # Return minimal info if person not found (shouldn't happen)
            return RelativeInfo(
                person_id=person_id,
                first_name="Unknown",
                last_name="Unknown",
                gender_id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
                birth_year=None,
                death_year=None,
                district_name=None,
                locality_name=None,
                depth=depth,
            )

        # Extract birth and death years
        birth_year = person.date_of_birth.year if person.date_of_birth else None
        death_year = person.date_of_death.year if person.date_of_death else None

        # Get district and locality names
        district_name, locality_name = self._get_address_names(person_id)

        return RelativeInfo(
            person_id=person_id,
            first_name=person.first_name,
            last_name=person.last_name,
            gender_id=person.gender_id,
            birth_year=birth_year,
            death_year=death_year,
            district_name=district_name,
            locality_name=locality_name,
            depth=depth,
        )

    def _get_address_names(self, person_id: uuid.UUID) -> tuple[str | None, str | None]:
        """Get district and locality names for a person.

        Args:
            person_id: Person ID

        Returns:
            Tuple of (district_name, locality_name)
        """
        # Get current address
        statement = select(PersonAddress).where(
            PersonAddress.person_id == person_id,
            PersonAddress.is_current == True,  # noqa: E712
        )
        person_address = self.session.exec(statement).first()

        if not person_address:
            return None, None

        district_name = None
        locality_name = None

        # Get district name
        if person_address.district_id:
            district = self.session.exec(
                select(District).where(District.id == person_address.district_id)
            ).first()
            if district:
                district_name = district.name

        # Get locality name
        if person_address.locality_id:
            locality = self.session.exec(
                select(Locality).where(Locality.id == person_address.locality_id)
            ).first()
            if locality:
                locality_name = locality.name

        return district_name, locality_name

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
