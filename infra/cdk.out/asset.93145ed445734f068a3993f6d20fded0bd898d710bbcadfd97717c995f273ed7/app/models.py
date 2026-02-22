"""Models module - re-exports from db_models and schemas for backward compatibility."""

from app.db_models.item import Item
from app.db_models.user import User
from app.schemas.item import ItemCreate
from app.schemas.user import UserCreate, UserUpdate

__all__ = ["Item", "ItemCreate", "User", "UserCreate", "UserUpdate"]
