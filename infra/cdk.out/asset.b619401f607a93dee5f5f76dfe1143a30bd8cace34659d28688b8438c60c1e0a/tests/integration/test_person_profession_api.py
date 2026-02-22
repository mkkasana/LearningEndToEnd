"""Integration tests for Person Profession API routes.

This module tests the Person Profession API endpoints including:
- Profession CRUD operations for /me/professions (Task 32.2)
- Profession CRUD operations for /{person_id}/professions (Task 32.2)

Tests use dynamically created test data.
"""

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from app.db_models.person.profession import Profession
from app.db_models.person.gender import Gender
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


def get_profession_id(db: Session) -> uuid.UUID:
    """Get a profession ID from seeded data."""
    profession = db.exec(select(Profession)).first()
    if profession:
        return profession.id
    pytest.skip("No professions found in database")


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
# Integration Tests - /me/professions Endpoints (Task 32.2)
# ============================================================================


@pytest.mark.integration
class TestGetMyProfessions:
    """Integration tests for GET /person/me/professions endpoint."""

    def test_get_my_professions_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's professions."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me/professions",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_my_professions_without_auth(self, client: TestClient) -> None:
        """Test getting professions without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/me/professions")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreateMyProfession:
    """Integration tests for POST /person/me/professions endpoint."""

    def test_create_my_profession_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a profession for current user."""
        headers, _ = create_test_user_with_person(client, db)
        profession_id = get_profession_id(db)
        
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
            "is_current": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/professions",
            headers=headers,
            json=profession_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["profession_id"] == str(profession_id)
        assert data["is_current"] is True

    def test_create_my_profession_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating profession without authentication returns 401."""
        profession_id = get_profession_id(db)
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/professions",
            json=profession_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestGetMyProfessionById:
    """Integration tests for GET /person/me/professions/{profession_id} endpoint."""

    def test_get_my_profession_by_id_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting a specific profession by ID."""
        headers, _ = create_test_user_with_person(client, db)
        profession_id = get_profession_id(db)
        
        # Create a profession first
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/professions",
            headers=headers,
            json=profession_data,
        )
        assert r.status_code == 200
        created_profession = r.json()
        
        # Get the profession by ID
        r = client.get(
            f"{settings.API_V1_STR}/person/me/professions/{created_profession['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == created_profession["id"]

    def test_get_my_profession_by_id_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting non-existent profession returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me/professions/{non_existent_uuid}",
            headers=headers,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestUpdateMyProfession:
    """Integration tests for PATCH /person/me/professions/{profession_id} endpoint."""

    def test_update_my_profession_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating a profession."""
        headers, _ = create_test_user_with_person(client, db)
        profession_id = get_profession_id(db)
        
        # Create a profession first
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
            "is_current": False,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/professions",
            headers=headers,
            json=profession_data,
        )
        assert r.status_code == 200
        created_profession = r.json()
        
        # Update the profession
        update_data = {"is_current": True}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me/professions/{created_profession['id']}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["is_current"] is True

    def test_update_my_profession_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating non-existent profession returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        update_data = {"is_current": True}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me/professions/{non_existent_uuid}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestDeleteMyProfession:
    """Integration tests for DELETE /person/me/professions/{profession_id} endpoint."""

    def test_delete_my_profession_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting a profession."""
        headers, _ = create_test_user_with_person(client, db)
        profession_id = get_profession_id(db)
        
        # Create a profession first
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/professions",
            headers=headers,
            json=profession_data,
        )
        assert r.status_code == 200
        created_profession = r.json()
        
        # Delete the profession
        r = client.delete(
            f"{settings.API_V1_STR}/person/me/professions/{created_profession['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()
        
        # Verify it's deleted
        r = client.get(
            f"{settings.API_V1_STR}/person/me/professions/{created_profession['id']}",
            headers=headers,
        )
        assert r.status_code == 404

    def test_delete_my_profession_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting non-existent profession returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/me/professions/{non_existent_uuid}",
            headers=headers,
        )
        assert r.status_code == 404


# ============================================================================
# Integration Tests - /{person_id}/professions Endpoints (Task 32.2)
# ============================================================================


@pytest.mark.integration
class TestGetPersonProfessions:
    """Integration tests for GET /person/{person_id}/professions endpoint."""

    def test_get_person_professions_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting professions for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/professions",
            headers=headers,
        )
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_person_professions_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting professions without authentication returns 401."""
        _, person = create_test_user_with_person(client, db)
        
        r = client.get(f"{settings.API_V1_STR}/person/{person.id}/professions")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreatePersonProfession:
    """Integration tests for POST /person/{person_id}/professions endpoint."""

    def test_create_person_profession_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a profession for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        profession_id = get_profession_id(db)
        
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
            "is_current": True,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/professions",
            headers=headers,
            json=profession_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["person_id"] == str(person.id)
        assert data["profession_id"] == str(profession_id)


@pytest.mark.integration
class TestUpdatePersonProfession:
    """Integration tests for PATCH /person/{person_id}/professions/{profession_id} endpoint."""

    def test_update_person_profession_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating a profession for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        profession_id = get_profession_id(db)
        
        # Create a profession first
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
            "is_current": False,
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/professions",
            headers=headers,
            json=profession_data,
        )
        assert r.status_code == 200
        created_profession = r.json()
        
        # Update the profession
        update_data = {"is_current": True}
        r = client.patch(
            f"{settings.API_V1_STR}/person/{person.id}/professions/{created_profession['id']}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["is_current"] is True

    def test_update_person_profession_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating non-existent profession returns 404."""
        headers, person = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        update_data = {"is_current": True}
        r = client.patch(
            f"{settings.API_V1_STR}/person/{person.id}/professions/{non_existent_uuid}",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestDeletePersonProfession:
    """Integration tests for DELETE /person/{person_id}/professions/{profession_id} endpoint."""

    def test_delete_person_profession_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting a profession for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        profession_id = get_profession_id(db)
        
        # Create a profession first
        profession_data = {
            "profession_id": str(profession_id),
            "start_date": "2020-01-01",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/professions",
            headers=headers,
            json=profession_data,
        )
        assert r.status_code == 200
        created_profession = r.json()
        
        # Delete the profession
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/professions/{created_profession['id']}",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()

    def test_delete_person_profession_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting non-existent profession returns 404."""
        headers, person = create_test_user_with_person(client, db)
        non_existent_uuid = uuid.uuid4()
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/professions/{non_existent_uuid}",
            headers=headers,
        )
        assert r.status_code == 404
