"""Person Profession database model."""

import uuid

from sqlmodel import Field, SQLModel


class Profession(SQLModel, table=True):
    """
    Profession model - Represents different professions/occupations.
    """

    __tablename__ = "person_profession"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(
        max_length=255, unique=True, index=True, description="Profession name"
    )
    description: str | None = Field(
        default=None, max_length=500, description="Optional description"
    )
    weight: int = Field(default=0, description="Weight for sorting/priority")
    is_active: bool = Field(default=True, description="Whether profession is active")
