"""Person Metadata schemas."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PersonMetadataBase(SQLModel):
    """Base person metadata properties."""

    profile_image_url: str | None = Field(
        default=None, max_length=500, description="Profile image URL"
    )
    bio: str | None = Field(default=None, description="Person biography")


class PersonMetadataCreate(PersonMetadataBase):
    """Schema for creating person metadata."""

    pass


class PersonMetadataUpdate(SQLModel):
    """Schema for updating person metadata (all fields optional)."""

    profile_image_url: str | None = None
    bio: str | None = None


class PersonMetadataPublic(PersonMetadataBase):
    """Person metadata response schema."""

    id: uuid.UUID
    person_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
