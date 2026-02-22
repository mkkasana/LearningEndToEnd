"""Unit tests for PostRepository."""

import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.db_models.post import Post
from app.repositories.post_repository import PostRepository


@pytest.mark.unit
class TestGetByUser:
    """Tests for get_by_user method."""

    def test_get_by_user_returns_posts(self, mock_session: MagicMock) -> None:
        """Test get_by_user returns list of posts."""
        repo = PostRepository(mock_session)
        user_id = uuid.uuid4()
        posts = [
            Post(
                id=uuid.uuid4(),
                title="Post 1",
                content="Content 1",
                user_id=user_id,
                is_published=True,
            ),
            Post(
                id=uuid.uuid4(),
                title="Post 2",
                content="Content 2",
                user_id=user_id,
                is_published=False,
            ),
        ]
        mock_session.exec.return_value.all.return_value = posts

        result = repo.get_by_user(user_id)

        assert len(result) == 2
        mock_session.exec.assert_called_once()

    def test_get_by_user_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_by_user returns empty list when no posts."""
        repo = PostRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_by_user(uuid.uuid4())

        assert result == []

    def test_get_by_user_with_pagination(self, mock_session: MagicMock) -> None:
        """Test get_by_user respects skip and limit."""
        repo = PostRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_by_user(uuid.uuid4(), skip=10, limit=50)

        mock_session.exec.assert_called_once()


@pytest.mark.unit
class TestCountByUser:
    """Tests for count_by_user method."""

    def test_count_by_user_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_by_user returns correct count."""
        repo = PostRepository(mock_session)
        user_id = uuid.uuid4()
        posts = [
            Post(
                id=uuid.uuid4(),
                title="Post 1",
                content="Content 1",
                user_id=user_id,
                is_published=True,
            ),
            Post(
                id=uuid.uuid4(),
                title="Post 2",
                content="Content 2",
                user_id=user_id,
                is_published=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = posts

        result = repo.count_by_user(user_id)

        assert result == 2

    def test_count_by_user_returns_zero(self, mock_session: MagicMock) -> None:
        """Test count_by_user returns 0 when no posts."""
        repo = PostRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.count_by_user(uuid.uuid4())

        assert result == 0


@pytest.mark.unit
class TestGetPublished:
    """Tests for get_published method."""

    def test_get_published_returns_published_posts(
        self, mock_session: MagicMock
    ) -> None:
        """Test get_published returns only published posts."""
        repo = PostRepository(mock_session)
        published_posts = [
            Post(
                id=uuid.uuid4(),
                title="Published Post 1",
                content="Content 1",
                user_id=uuid.uuid4(),
                is_published=True,
            ),
            Post(
                id=uuid.uuid4(),
                title="Published Post 2",
                content="Content 2",
                user_id=uuid.uuid4(),
                is_published=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = published_posts

        result = repo.get_published()

        assert len(result) == 2
        for post in result:
            assert post.is_published is True

    def test_get_published_returns_empty_list(self, mock_session: MagicMock) -> None:
        """Test get_published returns empty list when no published posts."""
        repo = PostRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.get_published()

        assert result == []

    def test_get_published_with_pagination(self, mock_session: MagicMock) -> None:
        """Test get_published respects skip and limit."""
        repo = PostRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        repo.get_published(skip=5, limit=25)

        mock_session.exec.assert_called_once()


@pytest.mark.unit
class TestCountPublished:
    """Tests for count_published method."""

    def test_count_published_returns_count(self, mock_session: MagicMock) -> None:
        """Test count_published returns correct count."""
        repo = PostRepository(mock_session)
        published_posts = [
            Post(
                id=uuid.uuid4(),
                title="Published Post",
                content="Content",
                user_id=uuid.uuid4(),
                is_published=True,
            ),
        ]
        mock_session.exec.return_value.all.return_value = published_posts

        result = repo.count_published()

        assert result == 1

    def test_count_published_returns_zero(self, mock_session: MagicMock) -> None:
        """Test count_published returns 0 when no published posts."""
        repo = PostRepository(mock_session)
        mock_session.exec.return_value.all.return_value = []

        result = repo.count_published()

        assert result == 0
