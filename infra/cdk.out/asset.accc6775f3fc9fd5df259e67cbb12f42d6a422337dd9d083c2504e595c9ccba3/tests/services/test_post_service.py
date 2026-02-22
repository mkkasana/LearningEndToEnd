"""Unit tests for PostService.

Tests cover:
- Post CRUD operations
- Owner validation

Requirements: 2.14, 2.18
"""

import uuid
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.db_models.post import Post
from app.schemas.post import PostCreate, PostUpdate
from app.services.post_service import PostService


@pytest.mark.unit
class TestPostServiceQueries:
    """Tests for post query operations."""

    def test_get_post_by_id_returns_post(self, mock_session: MagicMock) -> None:
        """Test getting post by ID returns the post."""
        # Arrange
        post_id = uuid.uuid4()
        mock_post = Post(
            id=post_id,
            title="Test Post",
            content="Test Content",
            user_id=uuid.uuid4(),
            is_published=True,
        )

        service = PostService(mock_session)
        with patch.object(service.post_repo, "get_by_id", return_value=mock_post):
            # Act
            result = service.get_post_by_id(post_id)

            # Assert
            assert result is not None
            assert result.id == post_id
            assert result.title == "Test Post"

    def test_get_post_by_id_returns_none_for_nonexistent(
        self, mock_session: MagicMock
    ) -> None:
        """Test getting nonexistent post returns None."""
        # Arrange
        service = PostService(mock_session)
        with patch.object(service.post_repo, "get_by_id", return_value=None):
            # Act
            result = service.get_post_by_id(uuid.uuid4())

            # Assert
            assert result is None

    def test_get_posts_by_user_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting posts by user returns list with count."""
        # Arrange
        user_id = uuid.uuid4()
        mock_posts = [
            Post(id=uuid.uuid4(), title="Post 1", content="Content 1", user_id=user_id),
            Post(id=uuid.uuid4(), title="Post 2", content="Content 2", user_id=user_id),
        ]

        service = PostService(mock_session)
        with patch.object(
            service.post_repo, "get_by_user", return_value=mock_posts
        ), patch.object(service.post_repo, "count_by_user", return_value=2):
            # Act
            posts, count = service.get_posts_by_user(user_id, skip=0, limit=100)

            # Assert
            assert len(posts) == 2
            assert count == 2

    def test_get_published_posts_returns_list(self, mock_session: MagicMock) -> None:
        """Test getting published posts returns list with count."""
        # Arrange
        mock_posts = [
            Post(
                id=uuid.uuid4(),
                title="Published Post",
                content="Content",
                user_id=uuid.uuid4(),
                is_published=True,
            ),
        ]

        service = PostService(mock_session)
        with patch.object(
            service.post_repo, "get_published", return_value=mock_posts
        ), patch.object(service.post_repo, "count_published", return_value=1):
            # Act
            posts, count = service.get_published_posts(skip=0, limit=100)

            # Assert
            assert len(posts) == 1
            assert count == 1
            assert posts[0].is_published is True


@pytest.mark.unit
class TestPostServiceCreate:
    """Tests for post creation."""

    def test_create_post_with_valid_data(self, mock_session: MagicMock) -> None:
        """Test creating post with valid data."""
        # Arrange
        user_id = uuid.uuid4()
        post_create = PostCreate(
            title="New Post", content="New Content", is_published=False
        )

        service = PostService(mock_session)

        def return_post(post: Post) -> Post:
            return post

        with patch.object(service.post_repo, "create", side_effect=return_post):
            # Act
            result = service.create_post(user_id, post_create)

            # Assert
            assert result.title == "New Post"
            assert result.content == "New Content"
            assert result.user_id == user_id
            assert result.is_published is False

    def test_create_published_post(self, mock_session: MagicMock) -> None:
        """Test creating a published post."""
        # Arrange
        user_id = uuid.uuid4()
        post_create = PostCreate(
            title="Published Post", content="Content", is_published=True
        )

        service = PostService(mock_session)

        def return_post(post: Post) -> Post:
            return post

        with patch.object(service.post_repo, "create", side_effect=return_post):
            # Act
            result = service.create_post(user_id, post_create)

            # Assert
            assert result.is_published is True


@pytest.mark.unit
class TestPostServiceUpdate:
    """Tests for post update operations."""

    def test_update_post_title(self, mock_session: MagicMock) -> None:
        """Test updating post title."""
        # Arrange
        old_timestamp = datetime(2020, 1, 1, 0, 0, 0)
        mock_post = Post(
            id=uuid.uuid4(),
            title="Old Title",
            content="Content",
            user_id=uuid.uuid4(),
            created_at=old_timestamp,
            updated_at=old_timestamp,
        )
        post_update = PostUpdate(title="New Title")

        service = PostService(mock_session)

        def return_post(post: Post) -> Post:
            return post

        with patch.object(service.post_repo, "update", side_effect=return_post):
            # Act
            result = service.update_post(mock_post, post_update)

            # Assert
            assert result.title == "New Title"

    def test_update_post_content(self, mock_session: MagicMock) -> None:
        """Test updating post content."""
        # Arrange
        mock_post = Post(
            id=uuid.uuid4(),
            title="Title",
            content="Old Content",
            user_id=uuid.uuid4(),
        )
        post_update = PostUpdate(content="New Content")

        service = PostService(mock_session)

        def return_post(post: Post) -> Post:
            return post

        with patch.object(service.post_repo, "update", side_effect=return_post):
            # Act
            result = service.update_post(mock_post, post_update)

            # Assert
            assert result.content == "New Content"

    def test_update_post_publish_status(self, mock_session: MagicMock) -> None:
        """Test updating post publish status."""
        # Arrange
        mock_post = Post(
            id=uuid.uuid4(),
            title="Title",
            content="Content",
            user_id=uuid.uuid4(),
            is_published=False,
        )
        post_update = PostUpdate(is_published=True)

        service = PostService(mock_session)

        def return_post(post: Post) -> Post:
            return post

        with patch.object(service.post_repo, "update", side_effect=return_post):
            # Act
            result = service.update_post(mock_post, post_update)

            # Assert
            assert result.is_published is True

    def test_update_post_updates_timestamp(self, mock_session: MagicMock) -> None:
        """Test that updating post updates the timestamp."""
        # Arrange
        old_timestamp = datetime(2020, 1, 1, 0, 0, 0)
        mock_post = Post(
            id=uuid.uuid4(),
            title="Title",
            content="Content",
            user_id=uuid.uuid4(),
            created_at=old_timestamp,
            updated_at=old_timestamp,
        )
        post_update = PostUpdate(title="New Title")

        service = PostService(mock_session)

        def return_post(post: Post) -> Post:
            return post

        with patch.object(service.post_repo, "update", side_effect=return_post):
            # Act
            result = service.update_post(mock_post, post_update)

            # Assert
            assert result.updated_at > old_timestamp


@pytest.mark.unit
class TestPostServiceDelete:
    """Tests for post deletion."""

    def test_delete_post_calls_repository(self, mock_session: MagicMock) -> None:
        """Test that delete calls the repository delete method."""
        # Arrange
        mock_post = Post(
            id=uuid.uuid4(),
            title="Post to Delete",
            content="Content",
            user_id=uuid.uuid4(),
        )

        service = PostService(mock_session)
        mock_delete = MagicMock()

        with patch.object(service.post_repo, "delete", mock_delete):
            # Act
            service.delete_post(mock_post)

            # Assert
            mock_delete.assert_called_once_with(mock_post)
