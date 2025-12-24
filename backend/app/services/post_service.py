"""Post service."""

import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    """Service for post business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.post_repo = PostRepository(session)

    def get_post_by_id(self, post_id: uuid.UUID) -> Post | None:
        """Get post by ID."""
        return self.post_repo.get_by_id(post_id)

    def get_posts_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Post], int]:
        """Get paginated list of posts by user with total count."""
        posts = self.post_repo.get_by_user(user_id, skip=skip, limit=limit)
        count = self.post_repo.count_by_user(user_id)
        return posts, count

    def get_published_posts(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Post], int]:
        """Get paginated list of published posts with total count."""
        posts = self.post_repo.get_published(skip=skip, limit=limit)
        count = self.post_repo.count_published()
        return posts, count

    def create_post(self, user_id: uuid.UUID, post_create: PostCreate) -> Post:
        """Create a new post."""
        post = Post(
            user_id=user_id,
            title=post_create.title,
            content=post_create.content,
            is_published=post_create.is_published,
        )
        return self.post_repo.create(post)

    def update_post(self, post: Post, post_update: PostUpdate) -> Post:
        """Update a post."""
        update_data = post_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(post, key, value)
        post.updated_at = datetime.utcnow()
        return self.post_repo.update(post)

    def delete_post(self, post: Post) -> None:
        """Delete a post."""
        self.post_repo.delete(post)
