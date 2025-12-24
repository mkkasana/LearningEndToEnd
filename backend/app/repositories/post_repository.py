"""Post repository."""

import uuid

from sqlmodel import Session, select

from app.db_models.post import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    """Repository for Post data access."""

    def __init__(self, session: Session):
        super().__init__(Post, session)

    def get_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[Post]:
        """Get all posts by a specific user."""
        statement = (
            select(Post)
            .where(Post.user_id == user_id)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def count_by_user(self, user_id: uuid.UUID) -> int:
        """Count posts by a specific user."""
        statement = select(Post).where(Post.user_id == user_id)
        return len(list(self.session.exec(statement).all()))

    def get_published(self, skip: int = 0, limit: int = 100) -> list[Post]:
        """Get all published posts."""
        statement = (
            select(Post)
            .where(Post.is_published == True)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(self.session.exec(statement).all())

    def count_published(self) -> int:
        """Count all published posts."""
        statement = select(Post).where(Post.is_published == True)
        return len(list(self.session.exec(statement).all()))
