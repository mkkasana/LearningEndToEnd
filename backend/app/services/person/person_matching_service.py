"""Person matching service for finding duplicate persons."""

import uuid
from typing import List

from rapidfuzz import fuzz
from sqlmodel import Session, select

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
        
        All provided criteria must match exactly. If sub_district_id or locality_id
        are provided, they must match. If they are None, only persons with None
        for those fields will match.
        
        Args:
            country_id: Country ID
            state_id: State ID
            district_id: District ID
            sub_district_id: Sub-district ID (optional)
            locality_id: Locality ID (optional)
            
        Returns:
            List of person IDs matching the address criteria exactly
        """
        # Build query with all criteria for exact match
        statement = select(PersonAddress.person_id).where(
            PersonAddress.country_id == country_id,
            PersonAddress.state_id == state_id,
            PersonAddress.district_id == district_id,
            PersonAddress.sub_district_id == sub_district_id,
            PersonAddress.locality_id == locality_id,
        )
        
        # Execute query and return list of person IDs
        results = self.session.exec(statement).all()
        return list(results)

    def _find_persons_by_religion(
        self,
        religion_id: uuid.UUID,
        religion_category_id: uuid.UUID | None = None,
        religion_sub_category_id: uuid.UUID | None = None,
    ) -> List[uuid.UUID]:
        """Find persons with matching religion criteria.
        
        All provided criteria must match exactly. If religion_category_id or 
        religion_sub_category_id are provided, they must match. If they are None,
        only persons with None for those fields will match.
        
        Args:
            religion_id: Religion ID
            religion_category_id: Religion category ID (optional)
            religion_sub_category_id: Religion sub-category ID (optional)
            
        Returns:
            List of person IDs matching the religion criteria exactly
        """
        # Build query with all criteria for exact match
        statement = select(PersonReligion.person_id).where(
            PersonReligion.religion_id == religion_id,
            PersonReligion.religion_category_id == religion_category_id,
            PersonReligion.religion_sub_category_id == religion_sub_category_id,
        )
        
        # Execute query and return list of person IDs
        results = self.session.exec(statement).all()
        return list(results)

    def _build_match_result(
        self,
        person_id: uuid.UUID,
        name_score: float,
        address_display: str,
        religion_display: str,
    ) -> PersonMatchResult | None:
        """Build a match result for a person.
        
        Args:
            person_id: Person ID
            name_score: Name match score
            address_display: Pre-built address display string
            religion_display: Pre-built religion display string
            
        Returns:
            PersonMatchResult object or None if person not found
        """
        # Fetch person details
        person = self.session.exec(
            select(Person).where(Person.id == person_id)
        ).first()
        
        if not person:
            return None
        
        # Construct PersonMatchResult
        match_result = PersonMatchResult(
            person_id=person.id,
            first_name=person.first_name,
            middle_name=person.middle_name,
            last_name=person.last_name,
            date_of_birth=person.date_of_birth,
            date_of_death=person.date_of_death,
            address_display=address_display,
            religion_display=religion_display,
            match_score=name_score,  # For now, match_score equals name_score
            name_match_score=name_score,
        )
        
        return match_result

    def search_matching_persons(
        self,
        current_user_id: uuid.UUID,
        search_criteria: dict,
    ) -> List[PersonMatchResult]:
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
        # Convert dict to PersonSearchRequest if needed
        if isinstance(search_criteria, dict):
            search_criteria = PersonSearchRequest(**search_criteria)
        
        # Use display strings from search criteria (passed from frontend)
        address_display = search_criteria.address_display
        religion_display = search_criteria.religion_display
        
        # Step 1: Find persons by address
        address_person_ids = self._find_persons_by_address(
            country_id=search_criteria.country_id,
            state_id=search_criteria.state_id,
            district_id=search_criteria.district_id,
            sub_district_id=search_criteria.sub_district_id,
            locality_id=search_criteria.locality_id,
        )
        
        # Step 2: Find persons by religion
        religion_person_ids = self._find_persons_by_religion(
            religion_id=search_criteria.religion_id,
            religion_category_id=search_criteria.religion_category_id,
            religion_sub_category_id=search_criteria.religion_sub_category_id,
        )
        
        # Step 3: Compute intersection of person IDs
        matching_person_ids = set(address_person_ids) & set(religion_person_ids)
        
        if not matching_person_ids:
            return []
        
        # Step 4: Filter by gender
        persons = self.session.exec(
            select(Person).where(
                Person.id.in_(matching_person_ids),
                Person.gender_id == search_criteria.gender_id
            )
        ).all()
        
        # Step 5: Get current user's person and connected person IDs
        current_person = self.person_repo.get_by_user_id(current_user_id)
        
        if not current_person:
            # If current user doesn't have a person record, return empty
            return []
        
        # Get all related person IDs (already connected)
        relationships = self.relationship_repo.get_by_person_id(current_person.id)
        connected_person_ids = {rel.related_person_id for rel in relationships}
        
        # Step 6: Exclude current user and already-connected persons
        persons = [
            p for p in persons
            if p.id != current_person.id and p.id not in connected_person_ids
        ]
        
        if not persons:
            return []
        
        # Step 7: Calculate name match scores for remaining persons
        results = []
        for person in persons:
            name_score = self.calculate_name_match_score(
                search_criteria.first_name,
                search_criteria.last_name,
                person.first_name,
                person.last_name,
            )
            
            # Filter by minimum score threshold (60%)
            if name_score >= 40:
                match_result = self._build_match_result(
                    person.id,
                    name_score,
                    address_display,
                    religion_display,
                )
                if match_result:  # Only add if result was successfully built
                    results.append(match_result)
        
        # Step 8: Sort by match score descending
        results.sort(key=lambda x: x.match_score, reverse=True)
        
        # Step 9: Limit to top 100 results
        return results[:100]

