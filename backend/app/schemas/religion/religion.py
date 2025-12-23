"""Religion schemas."""

import uuid

from sqlmodel import Field, SQLModel


class ReligionBase(SQLModel):
    """Base religion properties."""

    name: str = Field(max_length=255, description="Religion name")
    code: str = Field(max_length=10, description="Religion code")
    description: str | None = Field(default=None, max_length=500, description="Optional description")
    is_active: bool = Field(default=True, description="Whether religion is active")


class ReligionCreate(ReligionBase):
    """Schema for creating a new religion."""

    pass


class ReligionUpdate(SQLModel):
    """Schema for updating a religion (all fields optional)."""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=10)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class ReligionPublic(SQLModel):
    """Religion response schema for list endpoints."""

    religionId: uuid.UUID
    religionName: str


class ReligionDetailPublic(ReligionBase):
    """Detailed religion response with all fields."""

    id: uuid.UUID
