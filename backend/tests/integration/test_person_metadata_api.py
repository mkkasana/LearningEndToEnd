"""Integration tests for Person Metadata API routes.

This module tests the Person Metadata API endpoints including:
- Metadata CRUD operations for /me/metadata (Task 32.3)
- Metadata CRUD operations for /{person_id}/metadata (Task 32.3)

Tests use dynamically created test data.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person import Person
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Helper Functions
# ============================================================================


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
# Integration Tests - /me/metadata Endpoints (Task 32.3)
# ============================================================================


@pytest.mark.integration
class TestGetMyMetadata:
    """Integration tests for GET /person/me/metadata endpoint."""

    def test_get_my_metadata_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting metadata when none exists returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
        )
        # New users don't have metadata by default
        assert r.status_code == 404

    def test_get_my_metadata_without_auth(self, client: TestClient) -> None:
        """Test getting metadata without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/person/me/metadata")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreateMyMetadata:
    """Integration tests for POST /person/me/metadata endpoint."""

    def test_create_my_metadata_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating metadata for current user."""
        headers, _ = create_test_user_with_person(client, db)
        
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Test bio for the user",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["profile_image_url"] == "https://example.com/image.jpg"
        assert data["bio"] == "Test bio for the user"

    def test_create_my_metadata_already_exists(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating metadata when it already exists returns 400."""
        headers, _ = create_test_user_with_person(client, db)
        
        # Create metadata first
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Test bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        
        # Try to create again
        r = client.post(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 400
        assert "already exists" in r.json()["detail"].lower()

    def test_create_my_metadata_without_auth(self, client: TestClient) -> None:
        """Test creating metadata without authentication returns 401."""
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Test bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/metadata",
            json=metadata_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestUpdateMyMetadata:
    """Integration tests for PATCH /person/me/metadata endpoint."""

    def test_update_my_metadata_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating metadata."""
        headers, _ = create_test_user_with_person(client, db)
        
        # Create metadata first
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Original bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        
        # Update the metadata
        update_data = {"bio": "Updated bio"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["bio"] == "Updated bio"
        # Original field should be preserved
        assert data["profile_image_url"] == "https://example.com/image.jpg"

    def test_update_my_metadata_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating metadata when none exists returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        
        update_data = {"bio": "Updated bio"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 404

    def test_update_my_metadata_without_auth(self, client: TestClient) -> None:
        """Test updating metadata without authentication returns 401."""
        update_data = {"bio": "Updated bio"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/me/metadata",
            json=update_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestDeleteMyMetadata:
    """Integration tests for DELETE /person/me/metadata endpoint."""

    def test_delete_my_metadata_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting metadata."""
        headers, _ = create_test_user_with_person(client, db)
        
        # Create metadata first
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Test bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        
        # Delete the metadata
        r = client.delete(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()
        
        # Verify it's deleted
        r = client.get(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
        )
        assert r.status_code == 404

    def test_delete_my_metadata_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting metadata when none exists returns 404."""
        headers, _ = create_test_user_with_person(client, db)
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/me/metadata",
            headers=headers,
        )
        assert r.status_code == 404

    def test_delete_my_metadata_without_auth(self, client: TestClient) -> None:
        """Test deleting metadata without authentication returns 401."""
        r = client.delete(f"{settings.API_V1_STR}/person/me/metadata")
        assert r.status_code == 401


# ============================================================================
# Integration Tests - /{person_id}/metadata Endpoints (Task 32.3)
# ============================================================================


@pytest.mark.integration
class TestGetPersonMetadata:
    """Integration tests for GET /person/{person_id}/metadata endpoint."""

    def test_get_person_metadata_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting metadata when none exists returns 404."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.get(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
        )
        # New users don't have metadata by default
        assert r.status_code == 404

    def test_get_person_metadata_without_auth(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting metadata without authentication returns 401."""
        _, person = create_test_user_with_person(client, db)
        
        r = client.get(f"{settings.API_V1_STR}/person/{person.id}/metadata")
        assert r.status_code == 401


@pytest.mark.integration
class TestCreatePersonMetadata:
    """Integration tests for POST /person/{person_id}/metadata endpoint."""

    def test_create_person_metadata_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating metadata for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        
        metadata_data = {
            "profile_image_url": "https://example.com/person-image.jpg",
            "bio": "Person bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["person_id"] == str(person.id)
        assert data["bio"] == "Person bio"

    def test_create_person_metadata_already_exists(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating metadata when it already exists returns 400."""
        headers, person = create_test_user_with_person(client, db)
        
        # Create metadata first
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Test bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        
        # Try to create again
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 400


@pytest.mark.integration
class TestUpdatePersonMetadata:
    """Integration tests for PATCH /person/{person_id}/metadata endpoint."""

    def test_update_person_metadata_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating metadata for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        
        # Create metadata first
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Original bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        
        # Update the metadata
        update_data = {"bio": "Updated person bio"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 200
        data = r.json()
        assert data["bio"] == "Updated person bio"

    def test_update_person_metadata_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating metadata when none exists returns 404."""
        headers, person = create_test_user_with_person(client, db)
        
        update_data = {"bio": "Updated bio"}
        r = client.patch(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
            json=update_data,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestDeletePersonMetadata:
    """Integration tests for DELETE /person/{person_id}/metadata endpoint."""

    def test_delete_person_metadata_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting metadata for a specific person."""
        headers, person = create_test_user_with_person(client, db)
        
        # Create metadata first
        metadata_data = {
            "profile_image_url": "https://example.com/image.jpg",
            "bio": "Test bio",
        }
        r = client.post(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
            json=metadata_data,
        )
        assert r.status_code == 200
        
        # Delete the metadata
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
        )
        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()

    def test_delete_person_metadata_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting metadata when none exists returns 404."""
        headers, person = create_test_user_with_person(client, db)
        
        r = client.delete(
            f"{settings.API_V1_STR}/person/{person.id}/metadata",
            headers=headers,
        )
        assert r.status_code == 404
