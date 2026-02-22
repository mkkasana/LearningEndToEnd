"""Integration tests for Person Discovery API routes.

This module tests the Person Discovery API endpoints including:
- GET /person/discover-family-members (Task 32.4)
- GET /person/{person_id}/discover-family-members (Task 32.4)
- POST /person/search-matches (Task 32.4)

Tests use dynamically created test data.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.gender import Gender
from app.db_models.address.country import Country
from app.db_models.address.state import State
from app.db_models.address.district import District
from app.db_models.religion.religion import Religion
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


def get_gender_id(db: Session, gender_code: str = "MALE") -> uuid.UUID:
    """Get gender ID by code."""
    gender = db.exec(select(Gender).where(Gender.code == gender_code)).first()
    if gender:
        return gender.id
    pytest.skip("No genders found in database")


def create_test_user_with_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], Person]:
    """Create a test user with a person profile and return auth headers and person."""
    email = random_email()
    password = random_lower_string() + "Aa1!"
    first_name = random_lower_string()[:10]
    last_name = random_lower_string()[:10]
    
    signup_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "gender": "MALE",
        "date_of_birth": "1990-01-01",
    }
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=signup_data)
    if r.status_code != 200:
        pytest.skip(f"Could not create test user: {r.json()}")
    
    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    if r.status_code != 200:
        pytest.skip(f"Could not login test user: {r.json()}")
    
    tokens = r.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    r = client.get(f"{settings.API_V1_STR}/person/me", headers=headers)
    if r.status_code != 200:
        pytest.skip(f"Could not get person: {r.json()}")
    
    person_data = r.json()
    person = db.exec(select(Person).where(Person.id == uuid.UUID(person_data["id"]))).first()
    
    return headers, person


def get_search_criteria(db: Session) -> dict:
    """Get search criteria from seeded data.
    
    Returns all required fields for PersonSearchRequest:
    - country_id (required)
    - state_id (required)
    - district_id (required)
    - religion_id (required)
    
    Finds a valid hierarchy: country -> state -> district
    """
    # Find a district first, then work backwards to get state and country
    district = db.exec(select(District)).first()
    if not district:
        pytest.skip("No districts found in database")
    
    state = db.exec(select(State).where(State.id == district.state_id)).first()
    if not state:
        pytest.skip("No state found for district")
    
    country = db.exec(select(Country).where(Country.id == state.country_id)).first()
    if not country:
        pytest.skip("No country found for state")
    
    religion = db.exec(select(Religion)).first()
    if not religion:
        pytest.skip("No religions found in database")
    
    return {
        "country_id": str(country.id),
        "state_id": str(state.id),
        "district_id": str(district.id),
        "religion_id": str(religion.id),
    }


# ============================================================================
# Integration Tests - GET /person/discover-family-members (Task 32.4)
# ============================================================================


@pytest.mark.integration
class TestDiscoverFamilyMembers:
    """Integration tests for GET /person/discover-family-members endpoint."""

    def test_discover_family_members_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test discovering potential family member connections."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/discover-family-members",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_discover_family_members_without_auth(self, client: TestClient) -> None:
        """Test discovering family members without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/discover-family-members")
        assert r.status_code == 401

    def test_discover_family_members_response_structure(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that discovery response has correct structure when results exist."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/discover-family-members",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        
        # If there are results, verify structure
        if len(data) > 0:
            discovery = data[0]
            assert "person_id" in discovery or "id" in discovery
            assert "first_name" in discovery
            assert "last_name" in discovery


# ============================================================================
# Integration Tests - GET /person/{person_id}/discover-family-members (Task 32.4)
# ============================================================================


@pytest.mark.integration
class TestDiscoverPersonFamilyMembers:
    """Integration tests for GET /person/{person_id}/discover-family-members endpoint."""

    def test_discover_for_own_person_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test discovering family members for user's own person."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/discover-family-members",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_discover_for_non_existent_person(
        self, client: TestClient, db: Session
    ) -> None:
        """Test discovering for non-existent person returns 403 or 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_id = uuid.uuid4()
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{non_existent_id}/discover-family-members",
            headers=headers,
        )
        # Should return 403 (not authorized) or 404 (not found)
        assert r.status_code in [403, 404]

    def test_discover_without_auth(self, client: TestClient) -> None:
        """Test discover without authentication returns 401."""
        r = client.get(
            f"{settings.API_V1_STR}/person/{uuid.uuid4()}/discover-family-members"
        )
        assert r.status_code == 401


# ============================================================================
# Integration Tests - POST /person/search-matches (Task 32.4)
# ============================================================================


@pytest.mark.integration
class TestSearchMatchingPersons:
    """Integration tests for POST /person/search-matches endpoint."""

    def test_search_matching_persons_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test searching for matching persons."""
        headers, _ = create_test_user_with_person(client, db)
        criteria = get_search_criteria(db)
        
        search_data = {
            "first_name": "Test",
            "last_name": "Person",
            **{k: v for k, v in criteria.items() if v is not None},
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/search-matches",
            headers=headers,
            json=search_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_search_matching_persons_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test searching without authentication returns 401."""
        criteria = get_search_criteria(db)
        search_data = {
            "first_name": "Test",
            "last_name": "Person",
            **{k: v for k, v in criteria.items() if v is not None},
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/search-matches",
            json=search_data,
        )
        assert r.status_code == 401

    def test_search_matching_persons_all_required_fields(
        self, client: TestClient, db: Session
    ) -> None:
        """Test searching with all required fields (country, state, district, religion)."""
        headers, _ = create_test_user_with_person(client, db)
        criteria = get_search_criteria(db)
        
        # Provide all required fields
        search_data = {
            "first_name": "Test",
            "last_name": "Person",
            "country_id": criteria["country_id"],
            "state_id": criteria["state_id"],
            "district_id": criteria["district_id"],
            "religion_id": criteria["religion_id"],
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/search-matches",
            headers=headers,
            json=search_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_search_matching_persons_missing_required_field(
        self, client: TestClient, db: Session
    ) -> None:
        """Test searching with missing required field returns 422."""
        headers, _ = create_test_user_with_person(client, db)
        criteria = get_search_criteria(db)
        
        # Missing state_id, district_id, religion_id (required fields)
        search_data = {
            "first_name": "Test",
            "last_name": "Person",
            "country_id": criteria["country_id"],
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/search-matches",
            headers=headers,
            json=search_data,
        )
        # Should return 422 for missing required fields
        assert r.status_code == 422

    def test_search_matching_persons_response_structure(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that search response has correct structure when results exist."""
        headers, _ = create_test_user_with_person(client, db)
        criteria = get_search_criteria(db)
        
        search_data = {
            "first_name": "Test",
            "last_name": "Person",
            **{k: v for k, v in criteria.items() if v is not None},
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/search-matches",
            headers=headers,
            json=search_data,
        )
        assert r.status_code == 200
        data = r.json()
        
        # If there are results, verify structure
        if len(data) > 0:
            match = data[0]
            assert "person_id" in match
            assert "first_name" in match
            assert "match_score" in match

    def test_search_matching_persons_empty_name(
        self, client: TestClient, db: Session
    ) -> None:
        """Test searching with empty name fields."""
        headers, _ = create_test_user_with_person(client, db)
        criteria = get_search_criteria(db)
        
        search_data = {
            "first_name": "",
            "last_name": "",
            "country_id": criteria["country_id"],
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/search-matches",
            headers=headers,
            json=search_data,
        )
        # Should return 200 with empty results or 422 for validation error
        assert r.status_code in [200, 422]
