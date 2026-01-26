"""Tests for Person Religion API routes (/person-religion endpoints).

This module tests the Person Religion API endpoints in app/api/routes/person_religion.py:
- GET /person-religion/me - Get current user's religion
- POST /person-religion/ - Create religion for current user
- PUT /person-religion/me - Update current user's religion
- DELETE /person-religion/me - Delete current user's religion

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.person.person_religion import PersonReligion
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.db_models.religion.religion_sub_category import ReligionSubCategory
from tests.factories import UserFactory, PersonFactory
from tests.utils.user import user_authentication_headers


# ============================================================================
# Helper Functions
# ============================================================================


def create_authenticated_user_with_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID, uuid.UUID]:
    """Create a test user with a person profile and return auth headers."""
    user = UserFactory.create(db, password="testpassword123")
    person = PersonFactory.create_with_user(db, user)
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="testpassword123",
    )
    return headers, user.id, person.id


def create_authenticated_user_without_person(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID]:
    """Create a test user without a person profile and return auth headers."""
    user = UserFactory.create(db, password="testpassword123")
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="testpassword123",
    )
    return headers, user.id


def get_test_religion_ids(db: Session) -> dict[str, uuid.UUID | None]:
    """Get religion, category, and sub-category IDs from seeded data."""
    religion = db.exec(select(Religion)).first()
    
    if not religion:
        pytest.skip("No religions found in database. Ensure seed data exists.")
    
    category = db.exec(
        select(ReligionCategory).where(ReligionCategory.religion_id == religion.id)
    ).first()
    
    sub_category = None
    if category:
        sub_category = db.exec(
            select(ReligionSubCategory).where(
                ReligionSubCategory.category_id == category.id
            )
        ).first()
    
    return {
        "religion_id": religion.id,
        "category_id": category.id if category else None,
        "sub_category_id": sub_category.id if sub_category else None,
    }


def cleanup_person_religion(db: Session, person_id: uuid.UUID) -> None:
    """Clean up person religion for a specific person."""
    existing = db.exec(
        select(PersonReligion).where(PersonReligion.person_id == person_id)
    ).first()
    if existing:
        db.delete(existing)
        db.commit()


def create_person_religion_for_user(
    db: Session, person_id: uuid.UUID, religion_id: uuid.UUID
) -> PersonReligion:
    """Create a person religion record directly in the database."""
    person_religion = PersonReligion(
        person_id=person_id,
        religion_id=religion_id,
    )
    db.add(person_religion)
    db.commit()
    db.refresh(person_religion)
    return person_religion



# ============================================================================
# GET /person-religion/me Tests (Requirements: 1.1, 1.2, 1.7)
# ============================================================================


class TestGetMyReligion:
    """Tests for GET /api/v1/person-religion/me endpoint."""

    def test_get_religion_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test successful retrieval of religion with valid user."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        religion_ids = get_test_religion_ids(db)
        
        cleanup_person_religion(db, person_id)
        create_person_religion_for_user(db, person_id, religion_ids["religion_id"])
        
        response = client.get(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["religion_id"] == str(religion_ids["religion_id"])
        assert data["person_id"] == str(person_id)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_religion_no_person_profile_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 404 when user has no person profile."""
        headers, user_id = create_authenticated_user_without_person(client, db)
        
        response = client.get(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_religion_not_found_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 404 when religion not found for user."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        
        cleanup_person_religion(db, person_id)
        
        response = client.get(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_religion_without_auth_returns_401(
        self, client: TestClient
    ) -> None:
        """Test 401 without authentication."""
        response = client.get(f"{settings.API_V1_STR}/person-religion/me")
        
        assert response.status_code == 401



# ============================================================================
# POST /person-religion/ Tests (Requirements: 1.3, 1.4, 1.7)
# ============================================================================


class TestCreateMyReligion:
    """Tests for POST /api/v1/person-religion/ endpoint."""

    def test_create_religion_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test successful creation of religion."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        religion_ids = get_test_religion_ids(db)
        
        cleanup_person_religion(db, person_id)
        
        religion_data = {
            "religion_id": str(religion_ids["religion_id"]),
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/person-religion/",
            headers=headers,
            json=religion_data,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["religion_id"] == str(religion_ids["religion_id"])
        assert data["person_id"] == str(person_id)
        assert "id" in data

    def test_create_religion_no_person_profile_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 404 when no person profile exists."""
        headers, user_id = create_authenticated_user_without_person(client, db)
        religion_ids = get_test_religion_ids(db)
        
        religion_data = {
            "religion_id": str(religion_ids["religion_id"]),
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/person-religion/",
            headers=headers,
            json=religion_data,
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_create_religion_duplicate_returns_400(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 400 for duplicate religion."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        religion_ids = get_test_religion_ids(db)
        
        cleanup_person_religion(db, person_id)
        create_person_religion_for_user(db, person_id, religion_ids["religion_id"])
        
        religion_data = {
            "religion_id": str(religion_ids["religion_id"]),
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/person-religion/",
            headers=headers,
            json=religion_data,
        )
        
        assert response.status_code == 400
        assert "already" in response.json()["detail"].lower()

    def test_create_religion_without_auth_returns_401(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 401 without authentication."""
        religion_ids = get_test_religion_ids(db)
        
        religion_data = {
            "religion_id": str(religion_ids["religion_id"]),
        }
        
        response = client.post(
            f"{settings.API_V1_STR}/person-religion/",
            json=religion_data,
        )
        
        assert response.status_code == 401



# ============================================================================
# PUT /person-religion/me Tests (Requirements: 1.5, 1.7)
# ============================================================================


class TestUpdateMyReligion:
    """Tests for PUT /api/v1/person-religion/me endpoint."""

    def test_update_religion_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test successful update of religion."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        religion_ids = get_test_religion_ids(db)
        
        cleanup_person_religion(db, person_id)
        create_person_religion_for_user(db, person_id, religion_ids["religion_id"])
        
        update_data = {}
        if religion_ids.get("category_id"):
            update_data["religion_category_id"] = str(religion_ids["category_id"])
        else:
            update_data["religion_id"] = str(religion_ids["religion_id"])
        
        response = client.put(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
            json=update_data,
        )
        
        assert response.status_code == 200
        data = response.json()
        if religion_ids.get("category_id"):
            assert data["religion_category_id"] == str(religion_ids["category_id"])

    def test_update_religion_not_found_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 404 when religion not found."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        religion_ids = get_test_religion_ids(db)
        
        cleanup_person_religion(db, person_id)
        
        update_data = {
            "religion_id": str(religion_ids["religion_id"]),
        }
        
        response = client.put(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
            json=update_data,
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_update_religion_without_auth_returns_401(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 401 without authentication."""
        religion_ids = get_test_religion_ids(db)
        
        update_data = {
            "religion_id": str(religion_ids["religion_id"]),
        }
        
        response = client.put(
            f"{settings.API_V1_STR}/person-religion/me",
            json=update_data,
        )
        
        assert response.status_code == 401



# ============================================================================
# DELETE /person-religion/me Tests (Requirements: 1.6, 1.7)
# ============================================================================


class TestDeleteMyReligion:
    """Tests for DELETE /api/v1/person-religion/me endpoint."""

    def test_delete_religion_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test successful deletion of religion."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        religion_ids = get_test_religion_ids(db)
        
        cleanup_person_religion(db, person_id)
        create_person_religion_for_user(db, person_id, religion_ids["religion_id"])
        
        response = client.delete(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
        )
        
        assert response.status_code == 204
        
        # Verify deletion
        verify_response = client.get(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
        )
        assert verify_response.status_code == 404

    def test_delete_religion_not_found_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        """Test 404 when religion not found."""
        headers, user_id, person_id = create_authenticated_user_with_person(client, db)
        
        cleanup_person_religion(db, person_id)
        
        response = client.delete(
            f"{settings.API_V1_STR}/person-religion/me",
            headers=headers,
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_religion_without_auth_returns_401(
        self, client: TestClient
    ) -> None:
        """Test 401 without authentication."""
        response = client.delete(f"{settings.API_V1_STR}/person-religion/me")
        
        assert response.status_code == 401
