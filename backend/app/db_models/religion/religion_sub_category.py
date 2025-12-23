"""Religion Sub-Category database model."""

import uuid

from sqlmodel import Field, SQLModel


class ReligionSubCategory(SQLModel, table=True):
    """
    Religion Sub-Category model - Third level of religious demographics hierarchy.
    
    Examples:
    - For Hindu Brahmin: Iyer, Iyengar, Gaur, Kanyakubja, etc. (Sub-castes)
    - For Sunni Islam: Hanafi, Maliki, Shafi'i, Hanbali, etc. (Schools of jurisprudence)
    - For Catholic: Roman Catholic, Eastern Catholic, etc. (Rites)
    - For Theravada Buddhism: Thai Forest, Sri Lankan, Burmese, etc. (Traditions)
    """

    __tablename__ = "religion_sub_category"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True, description="Sub-category name")
    code: str | None = Field(default=None, max_length=10, description="Sub-category code")
    category_id: uuid.UUID = Field(
        foreign_key="religion_category.id", index=True, description="Parent category"
    )
    description: str | None = Field(default=None, max_length=500, description="Optional description")
    is_active: bool = Field(default=True, description="Whether sub-category is active")
