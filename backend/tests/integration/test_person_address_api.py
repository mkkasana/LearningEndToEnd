"""Integration tests for Person Address API routes.

This module tests the Person Address API endpoints including:
- Address CRUD operations for /me/addresses (Task 32.1)
- Address CRUD operations for /{person_id}/addresses (Task 32.1)

Tests use dynamically created test data.
"""

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.address.country import Country
from app.db_models.address.state import State
from app.db_models.person.person import Person
from app.db_models.person.gender import Gender
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


def get_address_hierarchy(db: Session) -> dict[str, uuid.UUID]:
    """Get address hierarchy IDs from seeded data."""
    country = db.exec(select(Country)).first()
    if not country:
        pytest.skip("No countries found in database")
    
    state = db.exec(select(State).where(State.country_id == country.id)).first()
    
    return {
        "country_id": country.id,
        "state_id": state.id if state else None,
    }


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


# ============================================================================
# Integration Tests - /me/addresses Endpoints (Task 32.1)
# ============================================================================


@pytest.mark.integration
class TestGetMyAddresses:
    """Integration tests for GET /person/me/addresses endpoint."""

    def test_get_my_addresses_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's addresses."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me/addresses",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_my_addresses_without_auth(self, client: TestClient) -> None:
        """Test getting addresses without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/me/addresses")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreateMyAddress:
    """Integration tests for POST /person/me/addresses endpoint."""

    def test_create_my_address_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating an address for current user."""
        headers, _ = create_test_user_with_person(client, db)
        address_hierarchy = get_address_hierarchy(db)
        
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "state_id": str(address_hierarchy["state_id"]) if address_hierarchy["state_id"] else None,
            "address_line": "123 Test Street",
            "start_date": "2020-01-01",
            "is_current": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/addresses",
            headers=headers,
            json=address_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["country_id"] == str(address_hierarchy["country_id"])
        assert data["address_line"] == "123 Test Street"
        assert data["is_current"] is True

    def test_create_my_address_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating address without authentication returns 401."""
        address_hierarchy = get_address_hierarchy(db)
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/addresses",
            json=address_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestGetMyAddressById:
    """Integration tests for GET /person/me/addresses/{address_id} endpoint."""

    def test_get_my_address_by_id_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting a specific address by ID."""
        headers, _ = create_test_user_with_person(client, db)
        address_hierarchy = get_address_hierarchy(db)
        
        # Create an address first
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/addresses",
            headers=headers,
            json=address_data,
        )
        assert r.status_code == 200
        created_address = r.json()
        
        # Get the address by ID
        r = client.get(
            f"{settings.API_V1_STR}/person/me/addresses/{created_address['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == created_address["id"]

    def test_get_my_address_by_id_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting non-existent address returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me/addresses/{non_existent_uuid}",
            headers=headers,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestUpdateMyAddress:
    """Integration tests for PATCH /person/me/addresses/{address_id} endpoint."""

    def test_update_my_address_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating an address."""
        headers, _ = create_test_user_with_person(client, db)
        address_hierarchy = get_address_hierarchy(db)
        
        # Create an address first
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "start_date": "2020-01-01",
            "address_line": "Original Address",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/addresses",
            headers=headers,
            json=address_data,
        )
        assert r.status_code == 200
        created_address = r.json()
        
        # Update the address
        update_data = {"address_line": "Updated Address"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me/addresses/{created_address['id']}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["address_line"] == "Updated Address"

    def test_update_my_address_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating non-existent address returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        update_data = {"address_line": "Updated Address"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me/addresses/{non_existent_uuid}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestDeleteMyAddress:
    """Integration tests for DELETE /person/me/addresses/{address_id} endpoint."""

    def test_delete_my_address_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting an address."""
        headers, _ = create_test_user_with_person(client, db)
        address_hierarchy = get_address_hierarchy(db)
        
        # Create an address first
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/addresses",
            headers=headers,
            json=address_data,
        )
        assert r.status_code == 200
        created_address = r.json()
        
        # Delete the address
        r = client.delete(
            f"{settings.API_V1_STR}/person/me/addresses/{created_address['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()
        
        # Verify it's deleted
        r = client.get(
            f"{settings.API_V1_STR}/person/me/addresses/{created_address['id']}",
            headers=headers,
        )
        assert r.status_code == 404

    def test_delete_my_address_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting non-existent address returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/me/addresses/{non_existent_uuid}",
            headers=headers,
        )
        assert r.status_code == 404


# ============================================================================
# Integration Tests - /{person_id}/addresses Endpoints (Task 32.1)
# ============================================================================


@pytest.mark.integration
class TestGetPersonAddresses:
    """Integration tests for GET /person/{person_id}/addresses endpoint."""

    def test_get_person_addresses_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting addresses for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/addresses",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_person_addresses_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting addresses without authentication returns 401."""
        _, person = create_test_user_with_person(client, db)
        
        r = client.get(f"{settings.API_V1_STR}/person/{person.id}/addresses")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreatePersonAddress:
    """Integration tests for POST /person/{person_id}/addresses endpoint."""

    def test_create_person_address_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating an address for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        address_hierarchy = get_address_hierarchy(db)
        
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "start_date": "2020-01-01",
            "address_line": "Person Address",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/addresses",
            headers=headers,
            json=address_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["person_id"] == str(person.id)
        assert data["address_line"] == "Person Address"


@pytest.mark.integration
class TestUpdatePersonAddress:
    """Integration tests for PATCH /person/{person_id}/addresses/{address_id} endpoint."""

    def test_update_person_address_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating an address for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        address_hierarchy = get_address_hierarchy(db)
        
        # Create an address first
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/addresses",
            headers=headers,
            json=address_data,
        )
        assert r.status_code == 200
        created_address = r.json()
        
        # Update the address
        update_data = {"address_line": "Updated Person Address"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/{person.id}/addresses/{created_address['id']}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["address_line"] == "Updated Person Address"

    def test_update_person_address_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating non-existent address returns 404."""
        headers, person = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        update_data = {"address_line": "Updated Address"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/{person.id}/addresses/{non_existent_uuid}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestDeletePersonAddress:
    """Integration tests for DELETE /person/{person_id}/addresses/{address_id} endpoint."""

    def test_delete_person_address_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting an address for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        address_hierarchy = get_address_hierarchy(db)
        
        # Create an address first
        address_data = {
            "country_id": str(address_hierarchy["country_id"]),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/addresses",
            headers=headers,
            json=address_data,
        )
        assert r.status_code == 200
        created_address = r.json()
        
        # Delete the address
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/addresses/{created_address['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()

    def test_delete_person_address_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting non-existent address returns 404."""
        headers, person = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/addresses/{non_existent_uuid}",
            headers=headers,
        )
        assert r.status_code == 404
