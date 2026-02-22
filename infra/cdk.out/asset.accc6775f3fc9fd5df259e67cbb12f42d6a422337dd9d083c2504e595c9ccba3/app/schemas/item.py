import uuid

from pydantic import Field
from sqlmodel import SQLModel


class ItemBase(SQLModel):
    """Shared item properties"""

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class ItemCreate(ItemBase):
    """Properties to receive on item creation"""

    pass


class ItemUpdate(ItemBase):
    """Properties to receive on item update"""

    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class ItemPublic(ItemBase):
    """Properties to return via API"""

    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """List of items response"""

    data: list[ItemPublic]
    count: int
