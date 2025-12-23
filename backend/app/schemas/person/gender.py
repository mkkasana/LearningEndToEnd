"""Gender schemas."""

import uuid

from sqlmodel import Field, SQLModel


class GenderBase(SQLModel):
    """Base gender properties."""

    name: str = Field(max_length=100, description="Gender name")
    code: str = Field(max_length=10, description="Gender code")
    description: str | None = Field(
        default=None, max_length=500, description="Optional description"
    )
    is_active: bool = Field(default=True, description="Whether gender is active")


class GenderCreate(GenderBase):
    """Schema for creating a new gender."""

    pass


class GenderUpdate(SQLModel):
    """Schema for updating a gender (all fields optional)."""

    name: str | None = Field(default=None, max_length=100)
    code: str | None = Field(default=None, max_length=10)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class GenderPublic(SQLModel):
    """Gender response schema for list endpoints."""

    genderId: uuid.UUID
    genderName: str
    genderCode: str


class GenderDetailPublic(GenderBase):
    """Detailed gender response with all fields."""

    id: uuid.UUID
