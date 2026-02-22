"""Tests for Items API routes.

Tests cover:
- Read operations (Requirements 4.1, 4.2, 4.3, 4.4)
- Write operations (Requirements 4.5, 4.6, 4.7, 4.8)
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app import crud
from tests.utils.item import create_random_item


# =============================================================================
# Helper Functions
# =============================================================================


def get_superuser_id(db: Session) -> uuid.UUID:
    """Get the superuser's ID from the database."""
    superuser = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert superuser is not None
    assert superuser.id is not None
    return superuser.id


# =============================================================================
# Read Operations Tests
# =============================================================================


@pytest.mark.integration
class TestReadItems:
    """Tests for GET /items endpoint.
    
    Validates: Requirements 4.1
    """

    def test_read_items_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test successful retrieval of items list."""
        # Create items owned by the superuser
        superuser_id = get_superuser_id(db)
        create_random_item(db, owner_id=superuser_id)
        create_random_item(db, owner_id=superuser_id)

        response = client.get(
            f"{settings.API_V1_STR}/items/",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert "data" in content
        assert "count" in content
        assert isinstance(content["data"], list)
        assert len(content["data"]) >= 2

    def test_read_items_with_pagination(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test items retrieval with skip and limit parameters."""
        # Create items owned by the superuser
        superuser_id = get_superuser_id(db)
        for _ in range(5):
            create_random_item(db, owner_id=superuser_id)

        # Test with limit
        response = client.get(
            f"{settings.API_V1_STR}/items/?skip=0&limit=2",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert len(content["data"]) <= 2

    def test_read_items_requires_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test that items endpoint requires authentication."""
        response = client.get(f"{settings.API_V1_STR}/items/")

        assert response.status_code == 401


@pytest.mark.integration
class TestReadItem:
    """Tests for GET /items/{id} endpoint.
    
    Validates: Requirements 4.2, 4.3, 4.4
    """

    def test_read_item_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test successful retrieval of a single item."""
        superuser_id = get_superuser_id(db)
        item = create_random_item(db, owner_id=superuser_id)

        response = client.get(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["id"] == str(item.id)
        assert content["title"] == item.title
        assert content["description"] == item.description
        assert content["owner_id"] == str(item.owner_id)

    def test_read_item_not_found(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 404 when item doesn't exist."""
        non_existent_id = uuid.uuid4()

        response = client.get(
            f"{settings.API_V1_STR}/items/{non_existent_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 404
        content = response.json()
        assert "not found" in content["detail"].lower()

    def test_read_item_permission_denied(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test 403 when user doesn't have permission to access item."""
        # Create item owned by a different user
        item = create_random_item(db)

        response = client.get(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=normal_user_token_headers,
        )

        assert response.status_code == 403
        content = response.json()
        assert "permission" in content["detail"].lower()

    def test_read_item_requires_authentication(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Test that item endpoint requires authentication."""
        item = create_random_item(db)

        response = client.get(f"{settings.API_V1_STR}/items/{item.id}")

        assert response.status_code == 401



# =============================================================================
# Write Operations Tests
# =============================================================================


@pytest.mark.integration
class TestCreateItem:
    """Tests for POST /items endpoint.
    
    Validates: Requirements 4.5
    """

    def test_create_item_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test successful item creation."""
        data = {"title": "Test Item", "description": "Test Description"}

        response = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["title"] == data["title"]
        assert content["description"] == data["description"]
        assert "id" in content
        assert "owner_id" in content

    def test_create_item_minimal(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test item creation with only required fields."""
        data = {"title": "Minimal Item"}

        response = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["title"] == data["title"]
        assert content["description"] is None

    def test_create_item_requires_authentication(
        self,
        client: TestClient,
    ) -> None:
        """Test that item creation requires authentication."""
        data = {"title": "Test Item"}

        response = client.post(
            f"{settings.API_V1_STR}/items/",
            json=data,
        )

        assert response.status_code == 401

    def test_create_item_validation_error(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test validation error for invalid item data."""
        # Empty title should fail validation
        data = {"title": "", "description": "Test"}

        response = client.post(
            f"{settings.API_V1_STR}/items/",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 422


@pytest.mark.integration
class TestUpdateItem:
    """Tests for PUT /items/{id} endpoint.
    
    Validates: Requirements 4.6, 4.7
    """

    def test_update_item_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test successful item update."""
        superuser_id = get_superuser_id(db)
        item = create_random_item(db, owner_id=superuser_id)
        data = {"title": "Updated Title", "description": "Updated Description"}

        response = client.put(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["title"] == data["title"]
        assert content["description"] == data["description"]
        assert content["id"] == str(item.id)

    def test_update_item_partial(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test partial item update (only title)."""
        superuser_id = get_superuser_id(db)
        item = create_random_item(db, owner_id=superuser_id)
        original_description = item.description
        data = {"title": "New Title Only"}

        response = client.put(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["title"] == data["title"]
        # Description should remain unchanged or be updated based on schema

    def test_update_item_not_found(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 404 when updating non-existent item."""
        non_existent_id = uuid.uuid4()
        data = {"title": "Updated Title"}

        response = client.put(
            f"{settings.API_V1_STR}/items/{non_existent_id}",
            headers=superuser_token_headers,
            json=data,
        )

        assert response.status_code == 404
        content = response.json()
        assert "not found" in content["detail"].lower()

    def test_update_item_permission_denied(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test 403 when user doesn't have permission to update item."""
        item = create_random_item(db)
        data = {"title": "Unauthorized Update"}

        response = client.put(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=normal_user_token_headers,
            json=data,
        )

        assert response.status_code == 403
        content = response.json()
        assert "permission" in content["detail"].lower()

    def test_update_item_requires_authentication(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Test that item update requires authentication."""
        item = create_random_item(db)
        data = {"title": "Updated Title"}

        response = client.put(
            f"{settings.API_V1_STR}/items/{item.id}",
            json=data,
        )

        assert response.status_code == 401


@pytest.mark.integration
class TestDeleteItem:
    """Tests for DELETE /items/{id} endpoint.
    
    Validates: Requirements 4.8
    """

    def test_delete_item_success(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test successful item deletion."""
        superuser_id = get_superuser_id(db)
        item = create_random_item(db, owner_id=superuser_id)

        response = client.delete(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        content = response.json()
        assert content["message"] == "Item deleted successfully"

        # Verify item is actually deleted
        get_response = client.get(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=superuser_token_headers,
        )
        assert get_response.status_code == 404

    def test_delete_item_not_found(
        self,
        client: TestClient,
        superuser_token_headers: dict[str, str],
    ) -> None:
        """Test 404 when deleting non-existent item."""
        non_existent_id = uuid.uuid4()

        response = client.delete(
            f"{settings.API_V1_STR}/items/{non_existent_id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 404
        content = response.json()
        assert "not found" in content["detail"].lower()

    def test_delete_item_permission_denied(
        self,
        client: TestClient,
        normal_user_token_headers: dict[str, str],
        db: Session,
    ) -> None:
        """Test 403 when user doesn't have permission to delete item."""
        item = create_random_item(db)

        response = client.delete(
            f"{settings.API_V1_STR}/items/{item.id}",
            headers=normal_user_token_headers,
        )

        assert response.status_code == 403
        content = response.json()
        assert "permission" in content["detail"].lower()

    def test_delete_item_requires_authentication(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Test that item deletion requires authentication."""
        item = create_random_item(db)

        response = client.delete(f"{settings.API_V1_STR}/items/{item.id}")

        assert response.status_code == 401
