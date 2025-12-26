"""Person matching service for finding duplicate persons."""

import uuid
from typing import List

from rapidfuzz import fuzz
from sqlmodel import Session

from app.repositories.person.person_address_repository import PersonAddressRepository
from app.repositories.person.person_relationship_repository import (
    PersonRelationshipRepository,
)
from app.repositories.person.person_religion_repository import PersonReligionRepository
from app.repositories.person.person_repository import PersonRepository


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
    ) -> List[uuid.UUID]:
        """Find persons with matching address criteria.
        
        Args:
            country_id: Country ID
            state_id: State ID
            district_id: District ID
            sub_district_id: Sub-district ID (optional)
            locality_id: Locality ID (optional)
            
        Returns:
            List of person IDs matching the address criteria
        """
        # TODO: Implement address matching logic
        # This will be implemented in a later task
        return []

    def _find_persons_by_religion(
        self,
        religion_id: uuid.UUID,
        religion_category_id: uuid.UUID | None = None,
        religion_sub_category_id: uuid.UUID | None = None,
    ) -> List[uuid.UUID]:
        """Find persons with matching religion criteria.
        
        Args:
            religion_id: Religion ID
            religion_category_id: Religion category ID (optional)
            religion_sub_category_id: Religion sub-category ID (optional)
            
        Returns:
            List of person IDs matching the religion criteria
        """
        # TODO: Implement religion matching logic
        # This will be implemented in a later task
        return []

    def _build_match_result(
        self, person_id: uuid.UUID, name_score: float
    ) -> dict:
        """Build a match result for a person.
        
        Args:
            person_id: Person ID
            name_score: Name match score
            
        Returns:
            Dictionary containing person details and match score
        """
        # TODO: Implement match result building logic
        # This will be implemented in a later task
        return {}

    def search_matching_persons(
        self,
        current_user_id: uuid.UUID,
        search_criteria: dict,
    ) -> List[dict]:
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
        # TODO: Implement full search logic
        # This will be implemented in a later task
        return []

