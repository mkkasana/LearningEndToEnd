"""Post schemas."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PostBase(SQLModel):
    """Base post properties."""

    title: str = Field(max_length=255, description="Post title")
    content: str = Field(description="Post content")
    is_published: bool = Field(default=True, description="Whether post is published")


class PostCreate(PostBase):
    """Schema for creating a new post."""

    pass


class PostUpdate(SQLModel):
    """Schema for updating a post (all fields optional)."""

    title: str | None = Field(default=None, max_length=255)
    content: str | None = None
    is_published: bool | None = None


class PostPublic(PostBase):
    """Post response schema."""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PostsPublic(SQLModel):
    """List of posts response."""

    data: list[PostPublic]
    count: int
