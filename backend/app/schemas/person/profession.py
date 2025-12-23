"""Profession schemas."""

import uuid

from sqlmodel import Field, SQLModel


class ProfessionBase(SQLModel):
    """Base profession properties."""

    name: str = Field(max_length=255, description="Profession name")
    description: str | None = Field(default=None, max_length=500, description="Optional description")
    weight: int = Field(default=0, description="Weight for sorting/priority")
    is_active: bool = Field(default=True, description="Whether profession is active")


class ProfessionCreate(ProfessionBase):
    """Schema for creating a new profession."""

    pass


class ProfessionUpdate(SQLModel):
    """Schema for updating a profession (all fields optional)."""

    name: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)
    weight: int | None = None
    is_active: bool | None = None


class ProfessionPublic(SQLModel):
    """Profession response schema for list endpoints."""

    professionId: uuid.UUID
    professionName: str
    professionDescription: str | None = None
    professionWeight: int


class ProfessionDetailPublic(ProfessionBase):
    """Detailed profession response with all fields."""

    id: uuid.UUID
