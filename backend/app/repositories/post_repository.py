"""Post repository."""

import logging
import uuid

from sqlmodel import Session, desc, select

from app.db_models.post import Post
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PostRepository(BaseRepository[Post]):
    """Repository for Post data access."""

    def __init__(self, session: Session):
        super().__init__(Post, session)

    def get_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get all posts by a specific user."""
        logger.debug(
            f"Querying posts by user_id: {user_id}, skip={skip}, limit={limit}"
        )
        statement = (
            select(Post)
            .where(Post.user_id == user_id)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} posts for user {user_id}")
        return results

    def count_by_user(self, user_id: uuid.UUID) -> int:
        """Count posts by a specific user."""
        logger.debug(f"Counting posts for user: {user_id}")
        statement = select(Post).where(Post.user_id == user_id)
        count = len(list(self.session.exec(statement).all()))
        logger.debug(f"User {user_id} has {count} posts")
        return count

    def get_published(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get all published posts."""
        logger.debug(f"Querying published posts: skip={skip}, limit={limit}")
        statement = (
            select(Post)
            .where(Post.is_published)
            .order_by(desc(Post.created_at))
            .offset(skip)
            .limit(limit)
        )
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} published posts")
        return results

    def count_published(self) -> int:
        """Count all published posts."""
        logger.debug("Counting all published posts")
        statement = select(Post).where(Post.is_published)
        count = len(list(self.session.exec(statement).all()))
        logger.debug(f"Total published posts: {count}")
        return count
