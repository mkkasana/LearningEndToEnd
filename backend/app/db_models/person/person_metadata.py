"""Person Metadata database model."""

import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class PersonMetadata(SQLModel, table=True):
    """Person Metadata model - Stores additional person details like profile image."""

    __tablename__ = "person_metadata"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    person_id: uuid.UUID = Field(
        foreign_key="person.id", index=True, description="Person reference"
    )
    profile_image_url: str | None = Field(
        default=None, max_length=500, description="Profile image URL"
    )
    bio: str | None = Field(default=None, description="Person biography")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Last update timestamp"
    )
