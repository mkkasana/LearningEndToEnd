"""Religion Sub-Category schemas."""

import uuid

from sqlmodel import Field, SQLModel


class ReligionSubCategoryBase(SQLModel):
    """Base religion sub-category properties."""

    name: str = Field(
        max_length=255, description="Sub-category name (e.g., Sub-caste, Sub-sect)"
    )
    code: str | None = Field(
        default=None, max_length=10, description="Sub-category code"
    )
    description: str | None = Field(
        default=None, max_length=500, description="Optional description"
    )
    is_active: bool = Field(default=True, description="Whether sub-category is active")


class ReligionSubCategoryCreate(ReligionSubCategoryBase):
    """Schema for creating a new religion sub-category."""

    category_id: uuid.UUID = Field(
        description="Category ID this sub-category belongs to"
    )


class ReligionSubCategoryUpdate(SQLModel):
    """Schema for updating a religion sub-category (all fields optional)."""

    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=10)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class ReligionSubCategoryPublic(SQLModel):
    """Religion sub-category response schema for list endpoints."""

    subCategoryId: uuid.UUID
    subCategoryName: str


class ReligionSubCategoryDetailPublic(ReligionSubCategoryBase):
    """Detailed religion sub-category response with all fields."""

    id: uuid.UUID
    category_id: uuid.UUID
