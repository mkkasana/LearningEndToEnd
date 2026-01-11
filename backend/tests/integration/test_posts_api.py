"""Integration tests for Posts API routes.

This module tests the Posts API endpoints including:
- Post CRUD operations (Task 22.1)

Tests use dynamically created test data with proper cleanup.
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from tests.factories import UserFactory
from tests.utils.user import user_authentication_headers


# ============================================================================
# Helper Functions
# ============================================================================


def create_test_user_with_auth(
    client: TestClient, db: Session
) -> tuple[dict[str, str], uuid.UUID]:
    """Create a test user and return auth headers and user ID."""
    user = UserFactory.create(db, password="testpassword123")
    headers = user_authentication_headers(
        client=client,
        email=user.email,
        password="testpassword123",
    )
    return headers, user.id


# ============================================================================
# Integration Tests - Post CRUD (Task 22.1)
# ============================================================================


@pytest.mark.integration
class TestCreatePost:
    """Integration tests for POST /posts/ endpoint."""

    def test_create_post_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a post with valid data."""
        headers, user_id = create_test_user_with_auth(client, db)

        post_data = {
            "title": "Test Post Title",
            "content": "This is the content of the test post.",
            "is_published": True,
        }

        r = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Test Post Title"
        assert data["content"] == "This is the content of the test post."
        assert data["is_published"] is True
        assert data["user_id"] == str(user_id)
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_post_draft(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a draft post (not published)."""
        headers, _ = create_test_user_with_auth(client, db)

        post_data = {
            "title": "Draft Post",
            "content": "This is a draft post content.",
            "is_published": False,
        }

        r = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["is_published"] is False

    def test_create_post_without_auth(
        self, client: TestClient
    ) -> None:
        """Test creating a post without authentication returns 401."""
        post_data = {
            "title": "Unauthorized Post",
            "content": "This should fail.",
            "is_published": True,
        }

        r = client.post(
            f"{settings.API_V1_STR}/posts/",
            json=post_data,
        )

        assert r.status_code == 401

    def test_create_post_missing_title(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a post without title returns 422."""
        headers, _ = create_test_user_with_auth(client, db)

        post_data = {
            "content": "Missing title field.",
            "is_published": True,
        }

        r = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        assert r.status_code == 422

    def test_create_post_missing_content(
        self, client: TestClient, db: Session
    ) -> None:
        """Test creating a post without content returns 422."""
        headers, _ = create_test_user_with_auth(client, db)

        post_data = {
            "title": "Missing Content",
            "is_published": True,
        }

        r = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        assert r.status_code == 422


@pytest.mark.integration
class TestGetPublishedPosts:
    """Integration tests for GET /posts/ endpoint."""

    def test_get_published_posts_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting all published posts."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a published post
        post_data = {
            "title": "Published Post for List",
            "content": "Test content.",
            "is_published": True,
        }
        client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        # Get published posts (public endpoint)
        r = client.get(f"{settings.API_V1_STR}/posts/")

        assert r.status_code == 200
        data = r.json()
        assert "data" in data
        assert "count" in data
        assert data["count"] >= 1
        assert len(data["data"]) >= 1

    def test_get_published_posts_excludes_drafts(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that draft posts are not included in published posts list."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a draft post with unique title
        unique_title = f"Draft Post {uuid.uuid4().hex[:8]}"
        post_data = {
            "title": unique_title,
            "content": "Draft content.",
            "is_published": False,
        }
        client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        # Get published posts
        r = client.get(f"{settings.API_V1_STR}/posts/")

        assert r.status_code == 200
        data = r.json()
        # Verify draft post is not in the list
        draft_in_list = any(p["title"] == unique_title for p in data["data"])
        assert not draft_in_list

    def test_get_published_posts_pagination(
        self, client: TestClient, db: Session
    ) -> None:
        """Test pagination of published posts."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create multiple posts
        for i in range(3):
            post_data = {
                "title": f"Pagination Test Post {i}",
                "content": f"Content {i}.",
                "is_published": True,
            }
            client.post(
                f"{settings.API_V1_STR}/posts/",
                headers=headers,
                json=post_data,
            )

        # Get with pagination
        r = client.get(
            f"{settings.API_V1_STR}/posts/",
            params={"skip": 0, "limit": 2},
        )

        assert r.status_code == 200
        data = r.json()
        assert len(data["data"]) <= 2


@pytest.mark.integration
class TestGetMyPosts:
    """Integration tests for GET /posts/me endpoint."""

    def test_get_my_posts_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting current user's posts."""
        headers, user_id = create_test_user_with_auth(client, db)

        # Create a post
        post_data = {
            "title": "My Test Post",
            "content": "Test content.",
            "is_published": True,
        }
        client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        # Get user's posts
        r = client.get(
            f"{settings.API_V1_STR}/posts/me",
            headers=headers,
        )

        assert r.status_code == 200
        data = r.json()
        assert "data" in data
        assert "count" in data
        assert data["count"] >= 1
        # Verify all posts belong to the user
        assert all(p["user_id"] == str(user_id) for p in data["data"])

    def test_get_my_posts_includes_drafts(
        self, client: TestClient, db: Session
    ) -> None:
        """Test that user's draft posts are included in their posts list."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a draft post with unique title
        unique_title = f"My Draft Post {uuid.uuid4().hex[:8]}"
        post_data = {
            "title": unique_title,
            "content": "Draft content.",
            "is_published": False,
        }
        client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )

        # Get user's posts
        r = client.get(
            f"{settings.API_V1_STR}/posts/me",
            headers=headers,
        )

        assert r.status_code == 200
        data = r.json()
        # Verify draft post is in the list
        draft_in_list = any(p["title"] == unique_title for p in data["data"])
        assert draft_in_list

    def test_get_my_posts_without_auth(
        self, client: TestClient
    ) -> None:
        """Test getting posts without authentication returns 401."""
        r = client.get(f"{settings.API_V1_STR}/posts/me")
        assert r.status_code == 401


@pytest.mark.integration
class TestGetPostById:
    """Integration tests for GET /posts/{post_id} endpoint."""

    def test_get_post_by_id_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting a specific published post by ID."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a post
        post_data = {
            "title": "Get By ID Test",
            "content": "Test content.",
            "is_published": True,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Get the post by ID (public endpoint for published posts)
        r = client.get(f"{settings.API_V1_STR}/posts/{post_id}")

        assert r.status_code == 200
        data = r.json()
        assert data["id"] == post_id
        assert data["title"] == "Get By ID Test"

    def test_get_post_not_found(
        self, client: TestClient
    ) -> None:
        """Test getting non-existent post returns 404."""
        non_existent_id = uuid.uuid4()

        r = client.get(f"{settings.API_V1_STR}/posts/{non_existent_id}")

        assert r.status_code == 404
        assert "not found" in r.json()["detail"].lower()

    def test_get_draft_post_returns_404(
        self, client: TestClient, db: Session
    ) -> None:
        """Test getting a draft post returns 404 (not published)."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a draft post
        post_data = {
            "title": "Draft Post",
            "content": "Draft content.",
            "is_published": False,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Try to get the draft post (should fail)
        r = client.get(f"{settings.API_V1_STR}/posts/{post_id}")

        assert r.status_code == 404


@pytest.mark.integration
class TestUpdatePost:
    """Integration tests for PATCH /posts/{post_id} endpoint."""

    def test_update_post_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating a post."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a post
        post_data = {
            "title": "Original Title",
            "content": "Original content.",
            "is_published": True,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Update the post
        update_data = {
            "title": "Updated Title",
            "content": "Updated content.",
        }
        r = client.patch(
            f"{settings.API_V1_STR}/posts/{post_id}",
            headers=headers,
            json=update_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content."

    def test_update_post_partial(
        self, client: TestClient, db: Session
    ) -> None:
        """Test partial update of a post."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a post
        post_data = {
            "title": "Original Title",
            "content": "Original content.",
            "is_published": True,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Update only the title
        update_data = {"title": "Only Title Updated"}
        r = client.patch(
            f"{settings.API_V1_STR}/posts/{post_id}",
            headers=headers,
            json=update_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["title"] == "Only Title Updated"
        assert data["content"] == "Original content."  # Unchanged

    def test_update_post_publish_status(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating post publish status."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a draft post
        post_data = {
            "title": "Draft to Publish",
            "content": "Content.",
            "is_published": False,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Publish the post
        update_data = {"is_published": True}
        r = client.patch(
            f"{settings.API_V1_STR}/posts/{post_id}",
            headers=headers,
            json=update_data,
        )

        assert r.status_code == 200
        data = r.json()
        assert data["is_published"] is True

    def test_update_post_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating non-existent post returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        update_data = {"title": "Updated Title"}
        r = client.patch(
            f"{settings.API_V1_STR}/posts/{non_existent_id}",
            headers=headers,
            json=update_data,
        )

        assert r.status_code == 404

    def test_update_post_other_user_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating another user's post returns 403."""
        # Create first user and their post
        headers1, _ = create_test_user_with_auth(client, db)
        post_data = {
            "title": "User 1 Post",
            "content": "Content.",
            "is_published": True,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers1,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Create second user and try to update first user's post
        headers2, _ = create_test_user_with_auth(client, db)
        update_data = {"title": "Hacked Title"}
        r = client.patch(
            f"{settings.API_V1_STR}/posts/{post_id}",
            headers=headers2,
            json=update_data,
        )

        assert r.status_code == 403
        assert "permission" in r.json()["detail"].lower()

    def test_update_post_without_auth(
        self, client: TestClient
    ) -> None:
        """Test updating post without authentication returns 401."""
        update_data = {"title": "Updated Title"}
        r = client.patch(
            f"{settings.API_V1_STR}/posts/{uuid.uuid4()}",
            json=update_data,
        )
        assert r.status_code == 401


@pytest.mark.integration
class TestDeletePost:
    """Integration tests for DELETE /posts/{post_id} endpoint."""

    def test_delete_post_success(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting a post."""
        headers, _ = create_test_user_with_auth(client, db)

        # Create a post
        post_data = {
            "title": "Post to Delete",
            "content": "This post will be deleted.",
            "is_published": True,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Delete the post
        r = client.delete(
            f"{settings.API_V1_STR}/posts/{post_id}",
            headers=headers,
        )

        assert r.status_code == 200
        assert "deleted" in r.json()["message"].lower()

        # Verify post is deleted
        r = client.get(f"{settings.API_V1_STR}/posts/{post_id}")
        assert r.status_code == 404

    def test_delete_post_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting non-existent post returns 404."""
        headers, _ = create_test_user_with_auth(client, db)
        non_existent_id = uuid.uuid4()

        r = client.delete(
            f"{settings.API_V1_STR}/posts/{non_existent_id}",
            headers=headers,
        )

        assert r.status_code == 404

    def test_delete_post_other_user_forbidden(
        self, client: TestClient, db: Session
    ) -> None:
        """Test deleting another user's post returns 403."""
        # Create first user and their post
        headers1, _ = create_test_user_with_auth(client, db)
        post_data = {
            "title": "User 1 Post",
            "content": "Content.",
            "is_published": True,
        }
        create_response = client.post(
            f"{settings.API_V1_STR}/posts/",
            headers=headers1,
            json=post_data,
        )
        post_id = create_response.json()["id"]

        # Create second user and try to delete first user's post
        headers2, _ = create_test_user_with_auth(client, db)
        r = client.delete(
            f"{settings.API_V1_STR}/posts/{post_id}",
            headers=headers2,
        )

        assert r.status_code == 403
        assert "permission" in r.json()["detail"].lower()

    def test_delete_post_without_auth(
        self, client: TestClient
    ) -> None:
        """Test deleting post without authentication returns 401."""
        r = client.delete(f"{settings.API_V1_STR}/posts/{uuid.uuid4()}")
        assert r.status_code == 401
