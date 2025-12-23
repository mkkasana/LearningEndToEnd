"""Religion database model."""

import uuid

from sqlmodel import Field, SQLModel


class Religion(SQLModel, table=True):
    """
    Religion model - Top level of religious demographics hierarchy.
    
    Examples: Hinduism, Islam, Christianity, Buddhism, Sikhism, Judaism, etc.
    """

    __tablename__ = "religion"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True, description="Religion name")
    code: str = Field(max_length=10, unique=True, index=True, description="Religion code")
    description: str | None = Field(default=None, max_length=500, description="Optional description")
    is_active: bool = Field(default=True, description="Whether religion is active")
