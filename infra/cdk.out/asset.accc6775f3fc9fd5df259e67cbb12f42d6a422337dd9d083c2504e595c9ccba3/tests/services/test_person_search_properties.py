"""Property-based tests for Person Search Services.

**Feature: person-attachment-approval, Property 2: Inactive Person Search Exclusion**
**Validates: Requirements 1.3**
"""

import uuid
from datetime import date

import pytest
from hypothesis import HealthCheck, given, settings, Phase
from hypothesis import strategies as st
from sqlmodel import Session, select, delete

from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_religion import PersonReligion
from app.db_models.address.country import Country
from app.db_models.address.state import State
from app.db_models.address.district import District
from app.db_models.address.sub_district import SubDistrict
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.models import User
from app.schemas.person.person_search import PersonSearchRequest, PersonSearchFilterRequest
from app.services.person.person_matching_service import PersonMatchingService
from app.services.person.person_search_service import PersonSearchService


class TestInactivePersonSearchExclusion:
    """Tests for Property 2: Inactive Person Search Exclusion.
    
    **Feature: person-attachment-approval, Property 2: Inactive Person Search Exclusion**
    **Validates: Requirements 1.3**
    
    Property: For any search query, persons with is_active=False should NEVER
    appear in search results, regardless of how well they match other criteria.
    """

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self, db: Session):
        """Setup and teardown for each test."""
        # Rollback any pending transaction
        db.rollback()
        yield
        # Cleanup after test
        db.rollback()

    def _get_fixtures(self, db: Session) -> dict:
        """Get existing fixtures from database."""
        gender = db.exec(select(Gender).where(Gender.code == "MALE")).first()
        country = db.exec(select(Country).limit(1)).first()
        state = db.exec(select(State).limit(1)).first() if country else None
        district = db.exec(select(District).limit(1)).first() if state else None
        sub_district = db.exec(select(SubDistrict).limit(1)).first() if district else None
        religion = db.exec(select(Religion).limit(1)).first()
        religion_category = db.exec(select(ReligionCategory).limit(1)).first() if religion else None
        
        return {
            "gender": gender,
            "country": country,
            "state": state,
            "district": district,
            "sub_district": sub_district,
            "religion": religion,
            "religion_category": religion_category,
        }

    def _create_test_user(self, db: Session) -> User:
        """Create a test user."""
        user = User(
            email=f"test_{uuid.uuid4()}@example.com",
            hashed_password="test_password",
            is_active=True,
            is_superuser=False,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def _create_person_with_data(
        self,
        db: Session,
        fixtures: dict,
        creator_user: User,
        first_name: str,
        last_name: str,
        is_active: bool,
    ) -> Person:
        """Create a person with address and religion records."""
        person = Person(
            user_id=None,
            created_by_user_id=creator_user.id,
            is_primary=False,
            first_name=first_name,
            last_name=last_name,
            gender_id=fixtures["gender"].id,
            date_of_birth=date(1990, 1, 1),
            is_active=is_active,
        )
        db.add(person)
        db.commit()
        db.refresh(person)
        
        # Create address
        address = PersonAddress(
            person_id=person.id,
            country_id=fixtures["country"].id,
            state_id=fixtures["state"].id,
            district_id=fixtures["district"].id,
            sub_district_id=fixtures["sub_district"].id,
            start_date=date(2020, 1, 1),
            is_current=True,
        )
        db.add(address)
        
        # Create religion
        religion = PersonReligion(
            person_id=person.id,
            religion_id=fixtures["religion"].id,
            religion_category_id=fixtures["religion_category"].id,
        )
        db.add(religion)
        db.commit()
        
        return person

    def _cleanup_person(self, db: Session, person: Person) -> None:
        """Clean up a person and related records."""
        # Delete address
        db.execute(delete(PersonAddress).where(PersonAddress.person_id == person.id))
        # Delete religion
        db.execute(delete(PersonReligion).where(PersonReligion.person_id == person.id))
        # Delete person
        db.execute(delete(Person).where(Person.id == person.id))
        db.commit()

    def _cleanup_user(self, db: Session, user: User) -> None:
        """Clean up a user."""
        db.execute(delete(User).where(User.id == user.id))
        db.commit()

    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target],
        database=None,  # Disable hypothesis database to avoid state issues
    )
    @given(
        active_count=st.integers(min_value=1, max_value=3),
        inactive_count=st.integers(min_value=1, max_value=3),
    )
    def test_inactive_persons_excluded_from_matching_service(
        self,
        db: Session,
        active_count: int,
        inactive_count: int,
    ) -> None:
        """Property 2: PersonMatchingService excludes inactive persons from results."""
        # Ensure clean state
        db.rollback()
        
        fixtures = self._get_fixtures(db)
        
        # Skip if fixtures not available
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available in database")
        
        # Create users
        searcher_user = self._create_test_user(db)
        creator_user = self._create_test_user(db)
        
        # Create searcher's person record
        searcher_person = Person(
            user_id=searcher_user.id,
            created_by_user_id=searcher_user.id,
            is_primary=True,
            first_name="Searcher",
            last_name="User",
            gender_id=fixtures["gender"].id,
            date_of_birth=date(1990, 1, 1),
            is_active=True,
        )
        db.add(searcher_person)
        db.commit()
        db.refresh(searcher_person)
        
        # Create active and inactive persons
        active_persons = []
        inactive_persons = []
        
        try:
            for i in range(active_count):
                person = self._create_person_with_data(
                    db, fixtures, creator_user,
                    first_name="John",
                    last_name="Doe",
                    is_active=True,
                )
                active_persons.append(person)
            
            for i in range(inactive_count):
                person = self._create_person_with_data(
                    db, fixtures, creator_user,
                    first_name="John",
                    last_name="Doe",
                    is_active=False,
                )
                inactive_persons.append(person)
            
            # Search using PersonMatchingService
            service = PersonMatchingService(db)
            search_request = PersonSearchRequest(
                first_name="John",
                last_name="Doe",
                gender_id=fixtures["gender"].id,
                country_id=fixtures["country"].id,
                state_id=fixtures["state"].id,
                district_id=fixtures["district"].id,
                sub_district_id=fixtures["sub_district"].id,
                religion_id=fixtures["religion"].id,
                religion_category_id=fixtures["religion_category"].id,
            )
            
            results = service.search_matching_persons(searcher_user.id, search_request)
            
            # Property: No inactive persons should appear in results
            result_ids = {r.person_id for r in results}
            inactive_ids = {p.id for p in inactive_persons}
            active_ids = {p.id for p in active_persons}
            
            assert result_ids.isdisjoint(inactive_ids), (
                f"PROPERTY VIOLATION: Inactive persons found in search results! "
                f"Inactive IDs in results: {result_ids & inactive_ids}"
            )
            
            # All active persons should be in results
            assert active_ids.issubset(result_ids), (
                f"Not all active persons found. Missing: {active_ids - result_ids}"
            )
        
        finally:
            # Cleanup
            for person in active_persons + inactive_persons:
                self._cleanup_person(db, person)
            self._cleanup_person(db, searcher_person)
            self._cleanup_user(db, searcher_user)
            self._cleanup_user(db, creator_user)

    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        phases=[Phase.generate, Phase.target],
        database=None,
    )
    @given(
        active_count=st.integers(min_value=1, max_value=3),
        inactive_count=st.integers(min_value=1, max_value=3),
    )
    def test_inactive_persons_excluded_from_search_service(
        self,
        db: Session,
        active_count: int,
        inactive_count: int,
    ) -> None:
        """Property 2: PersonSearchService excludes inactive persons from results."""
        # Ensure clean state
        db.rollback()
        
        fixtures = self._get_fixtures(db)
        
        # Skip if fixtures not available
        if not all(fixtures.values()):
            pytest.skip("Required fixtures not available in database")
        
        # Create creator user
        creator_user = self._create_test_user(db)
        
        # Create active and inactive persons
        active_persons = []
        inactive_persons = []
        
        try:
            for i in range(active_count):
                person = self._create_person_with_data(
                    db, fixtures, creator_user,
                    first_name="Jane",
                    last_name="Smith",
                    is_active=True,
                )
                active_persons.append(person)
            
            for i in range(inactive_count):
                person = self._create_person_with_data(
                    db, fixtures, creator_user,
                    first_name="Jane",
                    last_name="Smith",
                    is_active=False,
                )
                inactive_persons.append(person)
            
            # Search using PersonSearchService
            service = PersonSearchService(db)
            search_request = PersonSearchFilterRequest(
                first_name="Jane",
                last_name="Smith",
                gender_id=fixtures["gender"].id,
                country_id=fixtures["country"].id,
                state_id=fixtures["state"].id,
                district_id=fixtures["district"].id,
                sub_district_id=fixtures["sub_district"].id,
                religion_id=fixtures["religion"].id,
                religion_category_id=fixtures["religion_category"].id,
                skip=0,
                limit=100,
            )
            
            response = service.search_persons(search_request)
            
            # Property: No inactive persons should appear in results
            result_ids = {r.person_id for r in response.results}
            inactive_ids = {p.id for p in inactive_persons}
            active_ids = {p.id for p in active_persons}
            
            assert result_ids.isdisjoint(inactive_ids), (
                f"PROPERTY VIOLATION: Inactive persons found in search results! "
                f"Inactive IDs in results: {result_ids & inactive_ids}"
            )
            
            # All active persons should be in results
            assert active_ids.issubset(result_ids), (
                f"Not all active persons found. Missing: {active_ids - result_ids}"
            )
        
        finally:
            # Cleanup
            for person in active_persons + inactive_persons:
                self._cleanup_person(db, person)
            self._cleanup_user(db, creator_user)
