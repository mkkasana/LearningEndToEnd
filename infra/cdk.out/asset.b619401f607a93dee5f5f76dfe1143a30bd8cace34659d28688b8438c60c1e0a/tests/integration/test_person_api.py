"""Integration tests for Person API routes.

This module tests the Person API endpoints including:
- Person CRUD operations (Task 15.1)
- Person queries (Task 15.2)

Tests use a combination of seeded data and dynamically created test data.
"""

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.gender import Gender
from app.enums import GENDER_DATA, GenderEnum
from app import crud
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


def get_gender_id(db: Session, gender_code: str = "MALE") -> uuid.UUID:
    """Get gender ID by code."""
    gender = db.exec(select(Gender).where(Gender.code == gender_code)).first()
    if gender:
        return gender.id
    # Fallback to enum data
    return GENDER_DATA[GenderEnum.MALE].id


def create_test_user_with_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], Person]:
    """Create a test user with a person profile and return auth headers and person."""
    # Create user
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
    
    # Login to get auth headers
    login_data = {"username": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    if r.status_code != 200:
        pytest.skip(f"Could not login test user: {r.json()}")
    
    tokens = r.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    
    # Get the person
    r = client.get(f"{settings.API_V1_STR}/person/me", headers=headers)
    if r.status_code != 200:
        pytest.skip(f"Could not get person: {r.json()}")
    
    person_data = r.json()
    person = db.exec(select(Person).where(Person.id == uuid.UUID(person_data["id"]))).first()
    
    return headers, person


# ============================================================================
# Integration Tests - Person CRUD (Task 15.1)
# ============================================================================


@pytest.mark.integration
class TestGetMyPerson:
    """Integration tests for GET /person/me endpoint."""

    def test_get_my_person_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's person profile."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(person.id)
        assert data["first_name"] == person.first_name
        assert data["last_name"] == person.last_name

    def test_get_my_person_without_auth(self, client: TestClient) -> None:
        """Test getting person without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/me")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreateMyPerson:
    """Integration tests for POST /person/me endpoint."""

    def test_create_my_person_already_exists(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating person when one already exists returns 400."""
        headers, person = create_test_user_with_person(client, db)
        gender_id = get_gender_id(db)
        
        person_data = {
            "first_name": "Test",
            "last_name": "Person",
            "gender_id": str(gender_id),
            "date_of_birth": "1990-01-01",
            "user_id": str(person.user_id),
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me",
            headers=headers,
            json=person_data,
        )
        assert r.status_code == 400
        assert "already exists" in r.json()["detail"]

    def test_create_my_person_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating person without authentication returns 401."""
        gender_id = get_gender_id(db)
        person_data = {
            "first_name": "Test",
            "last_name": "Person",
            "gender_id": str(gender_id),
            "date_of_birth": "1990-01-01",
        }
        r = client.post(f"{settings.API_V1_STR}/person/me", json=person_data)
        assert r.status_code == 401


@pytest.mark.integration
class TestUpdateMyPerson:
    """Integration tests for PATCH /person/me endpoint."""

    def test_update_my_person_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating current user's person profile."""
        headers, person = create_test_user_with_person(client, db)
        original_first_name = person.first_name
        
        update_data = {"first_name": "UpdatedFirstName"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["first_name"] == "UpdatedFirstName"

        # Revert the change
        revert_data = {"first_name": original_first_name}
        client.patch(
            f"{settings.API_V1_STR}/person/me",
            headers=headers,
            json=revert_data,
        )

    def test_update_my_person_partial_update(
        self, client: TestClient, db: Session
    ) -> None:
        """Test partial update only changes specified fields."""
        headers, person = create_test_user_with_person(client, db)
        original_last_name = person.last_name
        
        update_data = {"middle_name": "MiddleTest"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["middle_name"] == "MiddleTest"
        assert data["last_name"] == original_last_name

    def test_update_my_person_without_auth(self, client: TestClient) -> None:
        """Test updating person without authentication returns 401."""
        update_data = {"first_name": "Hacked"}
        r = client.patch(f"{settings.API_V1_STR}/person/me", json=update_data)
        assert r.status_code == 401


@pytest.mark.integration
class TestDeleteMyPerson:
    """Integration tests for DELETE /person/me endpoint."""

    def test_delete_my_person_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting current user's person profile."""
        headers, person = create_test_user_with_person(client, db)
        person_id = person.id
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/me",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()
        
        # Verify person is deleted
        deleted_person = db.exec(select(Person).where(Person.id == person_id)).first()
        assert deleted_person is None

    def test_delete_my_person_without_auth(self, client: TestClient) -> None:
        """Test deleting person without authentication returns 401."""
        r = client.delete(f"{settings.API_V1_STR}/person/me")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreateFamilyMember:
    """Integration tests for POST /person/family-member endpoint."""

    def test_create_family_member_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a family member (person without user account)."""
        headers, _ = create_test_user_with_person(client, db)
        gender_id = get_gender_id(db)
        
        person_data = {
            "first_name": "FamilyMember",
            "last_name": "Test",
            "gender_id": str(gender_id),
            "date_of_birth": "1960-05-15",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/family-member",
            headers=headers,
            json=person_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["first_name"] == "FamilyMember"
        assert data["last_name"] == "Test"
        assert data["user_id"] is None  # Family members don't have user accounts

    def test_create_family_member_with_user_id_fails(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating family member with user_id returns 400."""
        headers, _ = create_test_user_with_person(client, db)
        gender_id = get_gender_id(db)
        
        person_data = {
            "first_name": "FamilyMember",
            "last_name": "Test",
            "gender_id": str(gender_id),
            "date_of_birth": "1960-05-15",
            "user_id": str(uuid.uuid4()),
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/family-member",
            headers=headers,
            json=person_data,
        )
        assert r.status_code == 400
        assert "cannot have a user account" in r.json()["detail"]

    def test_create_family_member_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating family member without authentication returns 401."""
        gender_id = get_gender_id(db)
        person_data = {
            "first_name": "FamilyMember",
            "last_name": "Test",
            "gender_id": str(gender_id),
            "date_of_birth": "1960-05-15",
        }
        r = client.post(f"{settings.API_V1_STR}/person/family-member", json=person_data)
        assert r.status_code == 401


@pytest.mark.integration
class TestGetPersonByUserId:
    """Integration tests for GET /person/{user_id} endpoint (admin only)."""

    def test_get_person_by_user_id_as_admin(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test admin can get person by user ID."""
        # Create a test user with person
        _, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.user_id}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(person.id)

    def test_get_person_by_user_id_not_found(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test getting non-existent person returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(
            f"{settings.API_V1_STR}/person/{non_existent_uuid}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 404

    def test_get_person_by_user_id_as_normal_user(
        self, client: TestClient, db: Session
    ) -> None:
        """Test normal user cannot access admin endpoint."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{uuid.uuid4()}",
            headers=headers,
        )
        assert r.status_code == 403


@pytest.mark.integration
class TestDeletePersonByUserId:
    """Integration tests for DELETE /person/{user_id} endpoint (admin only)."""

    def test_delete_person_by_user_id_not_found(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test deleting non-existent person returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.delete(
            f"{settings.API_V1_STR}/person/{non_existent_uuid}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 404

    def test_delete_person_by_user_id_as_normal_user(
        self, client: TestClient, db: Session
    ) -> None:
        """Test normal user cannot access admin delete endpoint."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/{uuid.uuid4()}",
            headers=headers,
        )
        assert r.status_code == 403



# ============================================================================
# Integration Tests - Person Queries (Task 15.2)
# ============================================================================


@pytest.mark.integration
class TestGetMyContributions:
    """Integration tests for GET /person/my-contributions endpoint."""

    def test_get_my_contributions_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's contributions."""
        headers, person = create_test_user_with_person(client, db)
        
        # Create a family member to have a contribution
        gender_id = get_gender_id(db)
        family_member_data = {
            "first_name": "Contribution",
            "last_name": "Test",
            "gender_id": str(gender_id),
            "date_of_birth": "1960-05-15",
        }
        client.post(
            f"{settings.API_V1_STR}/person/family-member",
            headers=headers,
            json=family_member_data,
        )
        
        r = client.get(
            f"{settings.API_V1_STR}/person/my-contributions",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # Should have at least the family member we created
        assert len(data) >= 1
        # Verify the response structure
        contribution = data[0]
        assert "id" in contribution
        assert "first_name" in contribution
        assert "last_name" in contribution
        assert "total_views" in contribution

    def test_get_my_contributions_without_auth(self, client: TestClient) -> None:
        """Test getting contributions without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/my-contributions")
        assert r.status_code == 401


@pytest.mark.integration
class TestGetPersonCompleteDetails:
    """Integration tests for GET /person/{person_id}/complete-details endpoint."""

    def test_get_person_complete_details_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting complete details for a person."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/complete-details",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(person.id)
        assert data["first_name"] == person.first_name
        assert data["last_name"] == person.last_name
        assert "gender_name" in data

    def test_get_person_complete_details_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting complete details for non-existent person returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{non_existent_uuid}/complete-details",
            headers=headers,
        )
        assert r.status_code == 404

    def test_get_person_complete_details_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting complete details without authentication returns 401."""
        _, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/complete-details"
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestSearchMatchingPersons:
    """Integration tests for POST /person/search-matches endpoint."""

    def test_search_matching_persons_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test searching for matching persons."""
        headers, _ = create_test_user_with_person(client, db)
        
        # Get reference data for search
        from app.db_models.address.country import Country
        from app.db_models.address.state import State
        from app.db_models.address.district import District
        from app.db_models.religion.religion import Religion

        # Get first available country, state, district, religion
        country = db.exec(select(Country)).first()
        if not country:
            pytest.skip("No countries found in database")
        
        state = db.exec(
            select(State).where(State.country_id == country.id)
        ).first()
        if not state:
            pytest.skip("No states found in database")
        
        district = db.exec(
            select(District).where(District.state_id == state.id)
        ).first()
        if not district:
            pytest.skip("No districts found in database")
        
        religion = db.exec(select(Religion)).first()
        if not religion:
            pytest.skip("No religions found in database")

        search_data = {
            "first_name": "Test",
            "last_name": "Person",
            "country_id": str(country.id),
            "state_id": str(state.id),
            "district_id": str(district.id),
            "religion_id": str(religion.id),
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/search-matches",
            headers=headers,
            json=search_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # Results may be empty if no matches found
        if len(data) > 0:
            match = data[0]
            assert "person_id" in match
            assert "first_name" in match
            assert "match_score" in match

    def test_search_matching_persons_without_auth(
        self, client: TestClient
    ) -> None:
        """Test searching without authentication returns 401."""
        search_data = {
            "first_name": "Test",
            "last_name": "Person",
            "country_id": str(uuid.uuid4()),
            "state_id": str(uuid.uuid4()),
            "district_id": str(uuid.uuid4()),
            "religion_id": str(uuid.uuid4()),
        }
        r = client.post(f"{settings.API_V1_STR}/person/search-matches", json=search_data)
        assert r.status_code == 401


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
        # Results may be empty if no discoveries found

    def test_discover_family_members_without_auth(self, client: TestClient) -> None:
        """Test discovering family members without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/discover-family-members")
        assert r.status_code == 401


@pytest.mark.integration
class TestGetPersonRelationshipsWithDetails:
    """Integration tests for GET /person/{person_id}/relationships/with-details endpoint."""

    def test_get_person_relationships_with_details_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting relationships with details for a person."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/relationships/with-details",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "selected_person" in data
        assert "relationships" in data
        assert data["selected_person"]["id"] == str(person.id)

    def test_get_person_relationships_with_details_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting relationships for non-existent person returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{non_existent_uuid}/relationships/with-details",
            headers=headers,
        )
        assert r.status_code == 404

    def test_get_person_relationships_with_details_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting relationships without authentication returns 401."""
        _, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/relationships/with-details"
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestGetMyRelationshipsWithDetails:
    """Integration tests for GET /person/me/relationships/with-details endpoint."""

    def test_get_my_relationships_with_details_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's relationships with details."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me/relationships/with-details",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert "selected_person" in data
        assert "relationships" in data
        assert data["selected_person"]["id"] == str(person.id)

    def test_get_my_relationships_with_details_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting relationships without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/me/relationships/with-details")
        assert r.status_code == 401


@pytest.mark.integration
class TestGetMyRelationships:
    """Integration tests for GET /person/me/relationships endpoint."""

    def test_get_my_relationships_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's relationships."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me/relationships",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_my_relationships_without_auth(self, client: TestClient) -> None:
        """Test getting relationships without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/me/relationships")
        assert r.status_code == 401
