"""Person Gender database model."""

import uuid

from sqlmodel import Field, SQLModel


class Gender(SQLModel, table=True):
    """Gender model - Represents different gender options."""

    __tablename__ = "person_gender"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(
        max_length=100, unique=True, index=True, description="Gender name"
    )
    code: str = Field(
        max_length=10, unique=True, index=True, description="Gender code"
    )
    description: str | None = Field(
        default=None, max_length=500, description="Optional description"
    )
    is_active: bool = Field(default=True, description="Whether gender is active")
