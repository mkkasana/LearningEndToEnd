"""Post service."""

import logging
import uuid
from datetime import datetime

from sqlmodel import Session

from app.db_models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreate, PostUpdate

logger = logging.getLogger(__name__)


class PostService:
    """Service for post business logic."""

    def __init__(self, session: Session):
        self.session = session
        self.post_repo = PostRepository(session)

    def get_post_by_id(self, post_id: uuid.UUID) -> Post | None:
        """Get post by ID."""
        logger.debug(f"Fetching post by ID: {post_id}")
        post = self.post_repo.get_by_id(post_id)
        if post:
            logger.info(f"Post found: {post.title} (ID: {post.id})")
        else:
            logger.info(f"Post not found: ID {post_id}")
        return post

    def get_posts_by_user(
        self, user_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> tuple[list[Post], int]:
        """Get paginated list of posts by user with total count."""
        logger.debug(
            f"Fetching posts for user: {user_id}, skip={skip}, limit={limit}"
        )
        posts = self.post_repo.get_by_user(user_id, skip=skip, limit=limit)
        count = self.post_repo.count_by_user(user_id)
        logger.info(f"Retrieved {len(posts)} posts for user {user_id} (total: {count})")
        return posts, count

    def get_published_posts(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[list[Post], int]:
        """Get paginated list of published posts with total count."""
        logger.debug(f"Fetching published posts, skip={skip}, limit={limit}")
        posts = self.post_repo.get_published(skip=skip, limit=limit)
        count = self.post_repo.count_published()
        logger.info(f"Retrieved {len(posts)} published posts (total: {count})")
        return posts, count

    def create_post(self, user_id: uuid.UUID, post_create: PostCreate) -> Post:
        """Create a new post."""
        logger.info(f"Creating post: {post_create.title} for user: {user_id}")
        try:
            post = Post(
                user_id=user_id,
                title=post_create.title,
                content=post_create.content,
                is_published=post_create.is_published,
            )
            created_post = self.post_repo.create(post)
            logger.info(f"Post created: {created_post.title} (ID: {created_post.id})")
            return created_post
        except Exception as e:
            logger.error(
                f"Failed to create post: {post_create.title} for user: {user_id}",
                exc_info=True,
            )
            raise

    def update_post(self, post: Post, post_update: PostUpdate) -> Post:
        """Update a post."""
        logger.info(f"Updating post: {post.title} (ID: {post.id})")
        try:
            update_data = post_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(post, key, value)
            post.updated_at = datetime.utcnow()
            updated_post = self.post_repo.update(post)
            logger.info(f"Post updated: {updated_post.title} (ID: {updated_post.id})")
            return updated_post
        except Exception as e:
            logger.error(
                f"Failed to update post: {post.title} (ID: {post.id})", exc_info=True
            )
            raise

    def delete_post(self, post: Post) -> None:
        """Delete a post."""
        logger.info(f"Deleting post: {post.title} (ID: {post.id})")
        try:
            self.post_repo.delete(post)
            logger.info(f"Post deleted: {post.title} (ID: {post.id})")
        except Exception as e:
            logger.error(
                f"Failed to delete post: {post.title} (ID: {post.id})", exc_info=True
            )
            raise
