"""Gender schemas."""

import uuid

from sqlmodel import Field, SQLModel


class GenderPublic(SQLModel):
    """Gender response schema for list endpoints."""

    genderId: uuid.UUID
    genderName: str
    genderCode: str


class GenderDetailPublic(SQLModel):
    """Detailed gender response with all fields."""

    id: uuid.UUID
    name: str = Field(max_length=100, description="Gender name")
    code: str = Field(max_length=10, description="Gender code")
    description: str | None = Field(
        default=None, max_length=500, description="Optional description"
    )
    is_active: bool = Field(default=True, description="Whether gender is active")
