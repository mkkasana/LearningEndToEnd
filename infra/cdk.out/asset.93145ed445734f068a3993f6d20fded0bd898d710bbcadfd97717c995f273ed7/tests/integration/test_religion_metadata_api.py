"""Integration tests for Religion Metadata API routes.

This module tests the Religion Metadata API endpoints including:
- Religion endpoints (Task 31.1)
- Religion category endpoints (Task 31.2)
- Religion sub-category endpoints (Task 31.3)

Tests use seeded data from init_seed scripts and dynamically created test data.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.db_models.religion.religion_sub_category import ReligionSubCategory
from tests.factories import UserFactory
from tests.utils.user import user_authentication_headers


# ============================================================================
# Helper Functions
# ============================================================================


def get_admin_auth_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Create an admin user and return auth headers."""
    user = UserFactory.create_admin(db, password="adminpassword123")
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="adminpassword123",
    )
    return headers


def get_seeded_religion_hierarchy(db: Session) -> dict[str, uuid.UUID | None]:
    """Get IDs from seeded religion hierarchy."""
    religion = db.exec(select(Religion)).first()
    category = db.exec(select(ReligionCategory)).first() if religion else None
    sub_category = db.exec(select(ReligionSubCategory)).first() if category else None
    
    return {
        "religion_id": religion.id if religion else None,
        "category_id": category.id if category else None,
        "sub_category_id": sub_category.id if sub_category else None,
    }


# ============================================================================
# Integration Tests - Religion Endpoints (Task 31.1)
# ============================================================================


@pytest.mark.integration
class TestReligionEndpoints:
    """Integration tests for religion endpoints.
    
    Tests GET /metadata/religion/religions endpoints.
    _Requirements: 11.6, 11.7_
    """

    def test_get_religions_list(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/religion/religions - list all religions."""
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_religion_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/religion/religions/{religion_id} - get religion by ID."""
        religion = db.exec(select(Religion)).first()
        if not religion:
            pytest.skip("No religions found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions/{religion.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(religion.id)
        assert data["name"] == religion.name

    def test_get_religion_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/religion/religions/{religion_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_religion_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/religion/religions/{religion_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions/not-a-valid-uuid")
        assert r.status_code == 422

    def test_get_categories_by_religion_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/religion/religion/{religion_id}/categories - get categories by religion."""
        religion = db.exec(select(Religion)).first()
        if not religion:
            pytest.skip("No religions found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{religion.id}/categories")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_categories_by_religion_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/religion/religion/{religion_id}/categories - non-existent religion returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{non_existent_uuid}/categories")
        assert r.status_code == 404


# ============================================================================
# Integration Tests - Religion Category Endpoints (Task 31.2)
# ============================================================================


@pytest.mark.integration
class TestReligionCategoryEndpoints:
    """Integration tests for religion category endpoints.
    
    Tests GET /metadata/religion/categories endpoints.
    _Requirements: 11.7, 11.8_
    """

    def test_get_category_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/religion/categories/{category_id} - get category by ID."""
        category = db.exec(select(ReligionCategory)).first()
        if not category:
            pytest.skip("No religion categories found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/categories/{category.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(category.id)
        assert data["name"] == category.name

    def test_get_category_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/religion/categories/{category_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/categories/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_category_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/religion/categories/{category_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/categories/not-a-valid-uuid")
        assert r.status_code == 422

    def test_get_sub_categories_by_category_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/religion/category/{category_id}/sub-categories - get sub-categories."""
        category = db.exec(select(ReligionCategory)).first()
        if not category:
            pytest.skip("No religion categories found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/category/{category.id}/sub-categories")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_get_sub_categories_by_category_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/religion/category/{category_id}/sub-categories - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/category/{non_existent_uuid}/sub-categories")
        assert r.status_code == 404


# ============================================================================
# Integration Tests - Religion Sub-Category Endpoints (Task 31.3)
# ============================================================================


@pytest.mark.integration
class TestReligionSubCategoryEndpoints:
    """Integration tests for religion sub-category endpoints.
    
    Tests GET /metadata/religion/sub-categories endpoints.
    _Requirements: 11.8_
    """

    def test_get_sub_category_by_id_success(self, client: TestClient, db: Session) -> None:
        """Test GET /metadata/religion/sub-categories/{sub_category_id} - get sub-category by ID."""
        sub_category = db.exec(select(ReligionSubCategory)).first()
        if not sub_category:
            pytest.skip("No religion sub-categories found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/sub-categories/{sub_category.id}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == str(sub_category.id)
        assert data["name"] == sub_category.name

    def test_get_sub_category_by_id_not_found(self, client: TestClient) -> None:
        """Test GET /metadata/religion/sub-categories/{sub_category_id} - non-existent returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/sub-categories/{non_existent_uuid}")
        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_sub_category_invalid_uuid_format(self, client: TestClient) -> None:
        """Test GET /metadata/religion/sub-categories/{sub_category_id} - invalid UUID format returns 422."""
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/sub-categories/not-a-valid-uuid")
        assert r.status_code == 422


# ============================================================================
# Integration Tests - Religion Hierarchy Validation
# ============================================================================


@pytest.mark.integration
class TestReligionHierarchyValidation:
    """Integration tests for religion hierarchy validation."""

    def test_category_belongs_to_religion(self, client: TestClient, db: Session) -> None:
        """Test that categories returned for a religion actually belong to that religion."""
        religion = db.exec(select(Religion)).first()
        if not religion:
            pytest.skip("No religions found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{religion.id}/categories")
        assert r.status_code == 200
        categories = r.json()
        
        # Verify each category belongs to the religion
        for category in categories:
            category_id = category.get("id") or category.get("categoryId")
            if category_id:
                category_detail = client.get(
                    f"{settings.API_V1_STR}/metadata/religion/categories/{category_id}"
                )
                if category_detail.status_code == 200:
                    assert category_detail.json().get("religion_id") == str(religion.id)

    def test_sub_category_belongs_to_category(self, client: TestClient, db: Session) -> None:
        """Test that sub-categories returned for a category actually belong to that category."""
        category = db.exec(select(ReligionCategory)).first()
        if not category:
            pytest.skip("No religion categories found in database")
        
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/category/{category.id}/sub-categories")
        assert r.status_code == 200
        sub_categories = r.json()
        
        # Verify each sub-category belongs to the category
        for sub_category in sub_categories:
            sub_category_id = sub_category.get("id") or sub_category.get("subCategoryId")
            if sub_category_id:
                sub_category_detail = client.get(
                    f"{settings.API_V1_STR}/metadata/religion/sub-categories/{sub_category_id}"
                )
                if sub_category_detail.status_code == 200:
                    assert sub_category_detail.json().get("category_id") == str(category.id)


# ============================================================================
# Integration Tests - Non-Existent Religion Hierarchy Returns 404
# ============================================================================


@pytest.mark.integration
class TestNonExistentReligionHierarchy:
    """Integration tests for non-existent religion hierarchy returning 404.
    
    **Feature: backend-testing-coverage, Property 2: Non-Existent Resource Returns 404**
    **Validates: Requirements 11.11**
    """

    def test_non_existent_religion_returns_404(self, client: TestClient) -> None:
        """Test that non-existent religion returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religions/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_category_returns_404(self, client: TestClient) -> None:
        """Test that non-existent category returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/categories/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_sub_category_returns_404(self, client: TestClient) -> None:
        """Test that non-existent sub-category returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/sub-categories/{non_existent_uuid}")
        assert r.status_code == 404

    def test_non_existent_religion_for_categories_returns_404(self, client: TestClient) -> None:
        """Test that getting categories for non-existent religion returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/religion/{non_existent_uuid}/categories")
        assert r.status_code == 404

    def test_non_existent_category_for_sub_categories_returns_404(self, client: TestClient) -> None:
        """Test that getting sub-categories for non-existent category returns 404."""
        non_existent_uuid = uuid.uuid4()
        r = client.get(f"{settings.API_V1_STR}/metadata/religion/category/{non_existent_uuid}/sub-categories")
        assert r.status_code == 404
