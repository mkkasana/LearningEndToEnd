"""Person matching service for finding duplicate persons."""

import logging
import uuid

from rapidfuzz import fuzz
from sqlmodel import Session, col, select

from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_religion import PersonReligion
from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository
from app.schemas.person.person_search import PersonMatchResult, PersonSearchRequest

logger = logging.getLogger(__name__)


class PersonMatchingService:
    """Service for finding and scoring person matches."""

    def __init__(self, session: Session):
        """Initialize the person matching service.

        Args:
            session: Database session
        """
        self.session = session
        self.person_repo = PersonRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)
        self.relationship_repo = PersonRelationshipRepository(session)

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
        match_score = (first_name_score * 0.4) + (last_name_score * 0.6)

        return round(match_score, 2)

    def _find_persons_by_address(
        self,
        country_id: uuid.UUID,
        state_id: uuid.UUID,
        district_id: uuid.UUID,
        sub_district_id: uuid.UUID | None = None,
        locality_id: uuid.UUID | None = None,
    ) -> list[uuid.UUID]:
        """Find persons with matching address criteria.

        Required criteria (country, state, district) must match exactly.
        Optional criteria (sub_district, locality) are only applied if provided:
        - If provided: must match exactly
        - If None: matches any value (including None)

        This supports two use cases:
        1. "Update Family" flow: All fields provided → exact match
        2. "Search Person" flow: Optional fields None → broader match

        Args:
            country_id: Country ID (required)
            state_id: State ID (required)
            district_id: District ID (required)
            sub_district_id: Sub-district ID (optional, None = match any)
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
        )

        # Only apply optional filters if values are provided
        if sub_district_id is not None:
            statement = statement.where(
                PersonAddress.sub_district_id == sub_district_id
            )
            logger.debug(f"Applying sub_district filter: {sub_district_id}")
        else:
            logger.debug("Skipping sub_district filter (not provided)")

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
        religion_category_id: uuid.UUID | None = None,
        religion_sub_category_id: uuid.UUID | None = None,
    ) -> list[uuid.UUID]:
        """Find persons with matching religion criteria.

        Required criteria (religion) must match exactly.
        Optional criteria (category, sub_category) are only applied if provided:
        - If provided: must match exactly
        - If None: matches any value (including None)

        This supports two use cases:
        1. "Update Family" flow: All fields provided → exact match
        2. "Search Person" flow: Optional fields None → broader match

        Args:
            religion_id: Religion ID (required)
            religion_category_id: Religion category ID (optional, None = match any)
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
        )

        # Only apply optional filters if values are provided
        if religion_category_id is not None:
            statement = statement.where(
                PersonReligion.religion_category_id == religion_category_id
            )
            logger.debug(f"Applying religion_category filter: {religion_category_id}")
        else:
            logger.debug("Skipping religion_category filter (not provided)")

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

    def _build_match_result(
        self,
        person_id: uuid.UUID,
        name_score: float,
        address_display: str,
        religion_display: str,
        is_current_user: bool = False,
        is_already_connected: bool = False,
    ) -> PersonMatchResult | None:
        """Build a match result for a person.

        Args:
            person_id: Person ID
            name_score: Name match score
            address_display: Pre-built address display string
            religion_display: Pre-built religion display string
            is_current_user: Whether this is the current user's person record
            is_already_connected: Whether this person is already connected

        Returns:
            PersonMatchResult object or None if person not found
        """
        # Fetch person details
        person = self.session.exec(select(Person).where(Person.id == person_id)).first()

        if not person:
            return None

        # Get gender display name
        gender_display = None
        if person.gender_id:
            from app.enums import get_gender_by_id

            gender = get_gender_by_id(person.gender_id)
            if gender:
                gender_display = gender.name

        # Construct PersonMatchResult
        match_result = PersonMatchResult(
            person_id=person.id,
            first_name=person.first_name,
            middle_name=person.middle_name,
            last_name=person.last_name,
            date_of_birth=person.date_of_birth,
            date_of_death=person.date_of_death,
            gender=gender_display,
            address_display=address_display,
            religion_display=religion_display,
            match_score=name_score,  # For now, match_score equals name_score
            name_match_score=name_score,
            is_current_user=is_current_user,
            is_already_connected=is_already_connected,
        )

        return match_result

    def _get_person_address_display(self, person_id: uuid.UUID) -> str:
        """Get formatted address display string for a person.

        Args:
            person_id: The person's ID

        Returns:
            Formatted address string or empty string if no address
        """
        from app.services.person.person_address_service import PersonAddressService

        address_service = PersonAddressService(self.session)
        address = address_service.get_formatted_current_address(person_id)
        return address or ""

    def _get_person_religion_display(self, person_id: uuid.UUID) -> str:
        """Get formatted religion display string for a person.

        Args:
            person_id: The person's ID

        Returns:
            Formatted religion string or empty string if no religion
        """
        from app.services.person.person_religion_service import PersonReligionService

        religion_service = PersonReligionService(self.session)
        religion = religion_service.get_formatted_religion(person_id)
        return religion or ""

    def search_matching_persons(
        self,
        current_user_id: uuid.UUID,
        search_criteria: PersonSearchRequest,
    ) -> list[PersonMatchResult]:
        """Search for persons matching the provided criteria.

        Steps:
        1. Find persons with matching address
        2. Find persons with matching religion
        3. Compute intersection
        4. Filter by gender
        5. Apply fuzzy name matching and score
        6. Exclude already-connected persons
        7. Sort by match score

        Args:
            current_user_id: Current user's ID
            search_criteria: Dictionary containing search parameters

        Returns:
            List of matching persons with scores, sorted by match score
        """
        logger.info(f"Starting person search for user {current_user_id}")

        # Use display strings from search criteria (passed from frontend)
        # If not provided, use empty strings as placeholders
        # address_display = search_criteria.address_display or ""
        # religion_display = search_criteria.religion_display or ""

        # Step 1: Find persons by address
        logger.debug(
            f"Searching by address: country={search_criteria.country_id}, "
            f"state={search_criteria.state_id}, district={search_criteria.district_id}"
        )
        address_person_ids = self._find_persons_by_address(
            country_id=search_criteria.country_id,
            state_id=search_criteria.state_id,
            district_id=search_criteria.district_id,
            sub_district_id=search_criteria.sub_district_id,
            locality_id=search_criteria.locality_id,
        )
        logger.info(
            f"Found {len(address_person_ids)} persons matching address criteria"
        )

        # Step 2: Find persons by religion
        logger.debug(
            f"Searching by religion: religion_id={search_criteria.religion_id}"
        )
        religion_person_ids = self._find_persons_by_religion(
            religion_id=search_criteria.religion_id,
            religion_category_id=search_criteria.religion_category_id,
            religion_sub_category_id=search_criteria.religion_sub_category_id,
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
            return []

        # Step 4: Filter by gender (only if provided) and exclude inactive persons
        query = select(Person).where(
            col(Person.id).in_(matching_person_ids),
            Person.is_active == True,  # noqa: E712 - Exclude inactive persons from search
        )

        # Only apply gender filter if gender_id is provided and not empty
        if search_criteria.gender_id:
            query = query.where(Person.gender_id == search_criteria.gender_id)
            logger.debug(f"Applying gender filter: {search_criteria.gender_id}")
        else:
            logger.debug("Skipping gender filter (not provided)")

        persons = self.session.exec(query).all()
        logger.info(f"After gender filter: {len(persons)} persons remain")

        # Step 5: Get current user's person and connected person IDs
        current_person = self.person_repo.get_by_user_id(current_user_id)

        if not current_person:
            # If current user doesn't have a person record, return empty
            logger.warning(f"User {current_user_id} does not have a person record")
            return []

        # Get all related person IDs (already connected)
        relationships = self.relationship_repo.get_by_person_id(current_person.id)
        connected_person_ids = {rel.related_person_id for rel in relationships}
        logger.info(f"User has {len(connected_person_ids)} existing relationships")

        # Step 6: Calculate name match scores for all persons (no exclusion)
        # Instead, we'll mark them with flags
        results = []
        for person in persons:
            # Determine flags
            is_current_user = person.id == current_person.id
            is_already_connected = person.id in connected_person_ids

            name_score = self.calculate_name_match_score(
                search_criteria.first_name,
                search_criteria.last_name,
                person.first_name,
                person.last_name,
            )

            # Filter by minimum score threshold (40%)
            if name_score >= 40:
                # Build display strings for THIS matched person (not the searcher)
                person_address_display = self._get_person_address_display(person.id)
                person_religion_display = self._get_person_religion_display(person.id)

                match_result = self._build_match_result(
                    person.id,
                    name_score,
                    person_address_display,
                    person_religion_display,
                    is_current_user=is_current_user,
                    is_already_connected=is_already_connected,
                )
                if match_result:  # Only add if result was successfully built
                    results.append(match_result)

        logger.info(
            f"After name matching (threshold 40%): {len(results)} matches found"
        )

        # Step 8: Sort by match score descending
        results.sort(key=lambda x: x.match_score, reverse=True)

        # Step 9: Limit to top 100 results
        final_results = results[:100]
        logger.info(f"Returning {len(final_results)} matches (top 100)")

        return final_results
