"""Post database model."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class Post(SQLModel, table=True):
    """Post model - User-created text posts."""

    __tablename__ = "post"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", index=True, description="User who created the post"
    )
    title: str = Field(max_length=255, description="Post title")
    content: str = Field(description="Post content")
    is_published: bool = Field(default=True, description="Whether post is published")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
