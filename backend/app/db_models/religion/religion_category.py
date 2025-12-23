"""Religion Category database model."""

import uuid

from sqlmodel import Field, SQLModel


class ReligionCategory(SQLModel, table=True):
    """
    Religion Category model - Second level of religious demographics hierarchy.
    
    Examples:
    - For Hinduism: Brahmin, Kshatriya, Vaishya, Shudra, etc. (Castes)
    - For Islam: Sunni, Shia, Ahmadiyya, etc. (Sects)
    - For Christianity: Catholic, Protestant, Orthodox, etc. (Denominations)
    - For Buddhism: Theravada, Mahayana, Vajrayana, etc. (Schools)
    """

    __tablename__ = "religion_category"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True, description="Category name")
    code: str | None = Field(default=None, max_length=10, description="Category code")
    religion_id: uuid.UUID = Field(foreign_key="religion.id", index=True, description="Parent religion")
    description: str | None = Field(default=None, max_length=500, description="Optional description")
    is_active: bool = Field(default=True, description="Whether category is active")
