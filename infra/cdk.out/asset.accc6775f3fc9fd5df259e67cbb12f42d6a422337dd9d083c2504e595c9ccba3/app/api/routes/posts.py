"""Post API routes."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser, SessionDep
from app.schemas.common import Message
from app.schemas.post import PostCreate, PostPublic, PostsPublic, PostUpdate
from app.services.post_service import PostService
from app.utils.logging_decorator import log_route

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=PostsPublic)
@log_route
def get_published_posts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Get all published posts (public endpoint).
    """
    post_service = PostService(session)
    posts, count = post_service.get_published_posts(skip=skip, limit=limit)
    return PostsPublic(data=posts, count=count)


@router.get("/me", response_model=PostsPublic)
@log_route
def get_my_posts(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get current user's posts.
    """
    post_service = PostService(session)
    posts, count = post_service.get_posts_by_user(
        current_user.id, skip=skip, limit=limit
    )
    return PostsPublic(data=posts, count=count)


@router.post("/", response_model=PostPublic)
@log_route
def create_post(
    session: SessionDep, current_user: CurrentUser, post_in: PostCreate
) -> Any:
    """
    Create a new post.
    """
    post_service = PostService(session)
    post = post_service.create_post(current_user.id, post_in)
    return post


@router.get("/{post_id}", response_model=PostPublic)
@log_route
def get_post(session: SessionDep, post_id: uuid.UUID) -> Any:
    """
    Get a specific post by ID.
    """
    post_service = PostService(session)
    post = post_service.get_post_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not post.is_published:
        raise HTTPException(status_code=404, detail="Post not found or not published")

    return post


@router.patch("/{post_id}", response_model=PostPublic)
@log_route
def update_post(
    session: SessionDep,
    current_user: CurrentUser,
    post_id: uuid.UUID,
    post_in: PostUpdate,
) -> Any:
    """
    Update a post (only owner can update).
    """
    post_service = PostService(session)
    post = post_service.get_post_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    post = post_service.update_post(post, post_in)
    return post


@router.delete("/{post_id}", response_model=Message)
@log_route
def delete_post(
    session: SessionDep, current_user: CurrentUser, post_id: uuid.UUID
) -> Any:
    """
    Delete a post (only owner can delete).
    """
    post_service = PostService(session)
    post = post_service.get_post_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    post_service.delete_post(post)
    return Message(message="Post deleted successfully")
