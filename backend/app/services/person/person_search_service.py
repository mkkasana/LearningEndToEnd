"""Person search service for global person search functionality."""

import logging
import uuid

from rapidfuzz import fuzz
from sqlalchemy import extract
from sqlmodel import Session, col, select

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_religion import PersonReligion
from app.schemas.person.person_search import (
    PersonSearchFilterRequest,
    PersonSearchResponse,
    PersonSearchResult,
)

logger = logging.getLogger(__name__)


class PersonSearchService:
    """Service for global person search with filters and pagination."""

    # Name matching threshold (40% as per existing PersonMatchingService)
    NAME_MATCH_THRESHOLD = 40.0

    def __init__(self, session: Session):
        """Initialize the person search service.

        Args:
            session: Database session
        """
        self.session = session

    def calculate_name_match_score(
        self,
        search_first: str,
        search_last: str,
        person_first: str,
        person_last: str,
    ) -> float:
        """Calculate fuzzy match score for names (0-100).

        Uses rapidfuzz to calculate similarity between names.
        Weighted average: 40% first name, 60% last name.

        Args:
            search_first: First name from search criteria
            search_last: Last name from search criteria
            person_first: First name of person being compared
            person_last: Last name of person being compared

        Returns:
            Match score from 0-100, rounded to 2 decimal places
        """
        # Normalize names (lowercase, strip whitespace)
        search_first = search_first.lower().strip()
        search_last = search_last.lower().strip()
        person_first = person_first.lower().strip()
        person_last = person_last.lower().strip()

        # Calculate individual scores using rapidfuzz
        first_name_score = fuzz.ratio(search_first, person_first)
        last_name_score = fuzz.ratio(search_last, person_last)

        # Weighted average (last name more important)
        match_score = (first_name_score * 0.6) + (last_name_score * 0.4)

        return round(match_score, 2)

    def _find_persons_by_address(
        self,
        country_id: uuid.UUID,
        state_id: uuid.UUID,
        district_id: uuid.UUID,
        sub_district_id: uuid.UUID,
        locality_id: uuid.UUID | None = None,
    ) -> list[uuid.UUID]:
        """Find persons with matching address criteria.

        Required criteria (country, state, district, sub_district) must match exactly.
        Optional criteria (locality) is only applied if provided.

        Args:
            country_id: Country ID (required)
            state_id: State ID (required)
            district_id: District ID (required)
            sub_district_id: Sub-district ID (required)
            locality_id: Locality ID (optional, None = match any)

        Returns:
            List of person IDs matching the address criteria
        """
        logger.debug(
            f"Querying person_address: country={country_id}, state={state_id}, "
            f"district={district_id}, sub_district={sub_district_id}, locality={locality_id}"
        )

        # Start with required criteria
        statement = select(PersonAddress.person_id).where(
            PersonAddress.country_id == country_id,
            PersonAddress.state_id == state_id,
            PersonAddress.district_id == district_id,
            PersonAddress.sub_district_id == sub_district_id,
        )

        # Only apply locality filter if value is provided
        if locality_id is not None:
            statement = statement.where(PersonAddress.locality_id == locality_id)
            logger.debug(f"Applying locality filter: {locality_id}")
        else:
            logger.debug("Skipping locality filter (not provided)")

        # Execute query and return list of person IDs
        results = self.session.exec(statement).all()
        logger.debug(f"Address query returned {len(results)} person IDs")
        return list(results)

    def _find_persons_by_religion(
        self,
        religion_id: uuid.UUID,
        religion_category_id: uuid.UUID,
        religion_sub_category_id: uuid.UUID | None = None,
    ) -> list[uuid.UUID]:
        """Find persons with matching religion criteria.

        Required criteria (religion, category) must match exactly.
        Optional criteria (sub_category) is only applied if provided.

        Args:
            religion_id: Religion ID (required)
            religion_category_id: Religion category ID (required)
            religion_sub_category_id: Religion sub-category ID (optional, None = match any)

        Returns:
            List of person IDs matching the religion criteria
        """
        logger.debug(
            f"Querying person_religion: religion={religion_id}, "
            f"category={religion_category_id}, sub_category={religion_sub_category_id}"
        )

        # Start with required criteria
        statement = select(PersonReligion.person_id).where(
            PersonReligion.religion_id == religion_id,
            PersonReligion.religion_category_id == religion_category_id,
        )

        # Only apply sub_category filter if value is provided
        if religion_sub_category_id is not None:
            statement = statement.where(
                PersonReligion.religion_sub_category_id == religion_sub_category_id
            )
            logger.debug(
                f"Applying religion_sub_category filter: {religion_sub_category_id}"
            )
        else:
            logger.debug("Skipping religion_sub_category filter (not provided)")

        # Execute query and return list of person IDs
        results = self.session.exec(statement).all()
        logger.debug(f"Religion query returned {len(results)} person IDs")
        return list(results)

    def search_persons(
        self,
        request: PersonSearchFilterRequest,
    ) -> PersonSearchResponse:
        """Search for persons with filters and pagination.

        Steps:
        1. Find persons by address (required filters)
        2. Find persons by religion (required filters)
        3. Compute intersection
        4. Apply optional gender filter
        5. Apply optional birth year range filter
        6. Apply optional name fuzzy matching
        7. Apply pagination
        8. Return results with total count

        Args:
            request: Search filter request with all criteria and pagination

        Returns:
            PersonSearchResponse with paginated results and total count
        """
        logger.info("Starting global person search")

        # Step 1: Find persons by address
        logger.debug(
            f"Searching by address: country={request.country_id}, "
            f"state={request.state_id}, district={request.district_id}, "
            f"sub_district={request.sub_district_id}, locality={request.locality_id}"
        )
        address_person_ids = self._find_persons_by_address(
            country_id=request.country_id,
            state_id=request.state_id,
            district_id=request.district_id,
            sub_district_id=request.sub_district_id,
            locality_id=request.locality_id,
        )
        logger.info(
            f"Found {len(address_person_ids)} persons matching address criteria"
        )

        # Step 2: Find persons by religion
        logger.debug(
            f"Searching by religion: religion_id={request.religion_id}, "
            f"category={request.religion_category_id}, "
            f"sub_category={request.religion_sub_category_id}"
        )
        religion_person_ids = self._find_persons_by_religion(
            religion_id=request.religion_id,
            religion_category_id=request.religion_category_id,
            religion_sub_category_id=request.religion_sub_category_id,
        )
        logger.info(
            f"Found {len(religion_person_ids)} persons matching religion criteria"
        )

        # Step 3: Compute intersection of person IDs
        matching_person_ids = set(address_person_ids) & set(religion_person_ids)
        logger.info(
            f"Found {len(matching_person_ids)} persons matching both address and religion"
        )

        if not matching_person_ids:
            logger.info("No persons found matching both criteria, returning empty list")
            return PersonSearchResponse(
                results=[],
                total=0,
                skip=request.skip,
                limit=request.limit,
            )

        # Step 4: Build query with optional filters
        query = select(Person).where(col(Person.id).in_(matching_person_ids))

        # Apply optional gender filter
        if request.gender_id is not None:
            query = query.where(Person.gender_id == request.gender_id)
            logger.debug(f"Applying gender filter: {request.gender_id}")
        else:
            logger.debug("Skipping gender filter (not provided)")

        # Step 5: Apply birth year range filter
        if request.birth_year_from is not None:
            query = query.where(
                extract("year", col(Person.date_of_birth)) >= request.birth_year_from
            )
            logger.debug(f"Applying birth_year_from filter: {request.birth_year_from}")

        if request.birth_year_to is not None:
            query = query.where(
                extract("year", col(Person.date_of_birth)) <= request.birth_year_to
            )
            logger.debug(f"Applying birth_year_to filter: {request.birth_year_to}")

        # Execute query to get all matching persons
        persons = self.session.exec(query).all()
        logger.info(f"After demographic filters: {len(persons)} persons remain")

        # Step 6: Apply name fuzzy matching if name filters provided
        has_name_filter = (
            request.first_name is not None or request.last_name is not None
        )

        if has_name_filter:
            # Apply name matching with threshold
            search_first = request.first_name or ""
            search_last = request.last_name or ""

            scored_persons = []
            for person in persons:
                name_score = self.calculate_name_match_score(
                    search_first,
                    search_last,
                    person.first_name,
                    person.last_name,
                )

                # Filter by minimum score threshold (40%)
                if name_score >= self.NAME_MATCH_THRESHOLD:
                    scored_persons.append((person, name_score))

            logger.info(
                f"After name matching (threshold {self.NAME_MATCH_THRESHOLD}%): "
                f"{len(scored_persons)} matches found"
            )

            # Sort by name match score descending
            scored_persons.sort(key=lambda x: x[1], reverse=True)

            # Get total count before pagination
            total = len(scored_persons)

            # Apply pagination
            paginated = scored_persons[request.skip : request.skip + request.limit]

            # Build results with name_match_score
            results = [
                PersonSearchResult(
                    person_id=person.id,
                    first_name=person.first_name,
                    middle_name=person.middle_name,
                    last_name=person.last_name,
                    date_of_birth=person.date_of_birth,
                    gender_id=person.gender_id,
                    name_match_score=score,
                )
                for person, score in paginated
            ]
        else:
            # No name filter - return all matching persons sorted by last name
            persons_list: list[Person] = list(persons)
            persons_list.sort(key=lambda p: (p.last_name.lower(), p.first_name.lower()))

            # Get total count before pagination
            total = len(persons_list)

            # Apply pagination
            paginated_persons = persons_list[
                request.skip : request.skip + request.limit
            ]

            # Build results without name_match_score
            results = [
                PersonSearchResult(
                    person_id=person.id,
                    first_name=person.first_name,
                    middle_name=person.middle_name,
                    last_name=person.last_name,
                    date_of_birth=person.date_of_birth,
                    gender_id=person.gender_id,
                    name_match_score=None,
                )
                for person in paginated_persons
            ]

        logger.info(
            f"Returning {len(results)} results (skip={request.skip}, "
            f"limit={request.limit}, total={total})"
        )

        return PersonSearchResponse(
            results=results,
            total=total,
            skip=request.skip,
            limit=request.limit,
        )
