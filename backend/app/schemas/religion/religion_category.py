"""Religion Category schemas."""

import uuid

from sqlmodel import Field, SQLModel


class ReligionCategoryBase(SQLModel):
    """Base religion category properties."""

    name: str = Field(
        max_length=255, description="Category name (e.g., Caste, Sect, Denomination)"
    )
    code: str | None = Field(default=None, max_length=10, description="Category code")
    description: str | None = Field(
        default=None, max_length=500, description="Optional description"
    )
    is_active: bool = Field(default=True, description="Whether category is active")


class ReligionCategoryCreate(ReligionCategoryBase):
    """Schema for creating a new religion category."""

    religion_id: uuid.UUID = Field(description="Religion ID this category belongs to")


class ReligionCategoryUpdate(SQLModel):
    """Schema for updating a religion category (all fields optional)."""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=10)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class ReligionCategoryPublic(SQLModel):
    """Religion category response schema for list endpoints."""

    categoryId: uuid.UUID
    categoryName: str


class ReligionCategoryDetailPublic(ReligionCategoryBase):
    """Detailed religion category response with all fields."""

    id: uuid.UUID
    religion_id: uuid.UUID
