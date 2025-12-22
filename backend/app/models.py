# Legacy models file - kept for backward compatibility
# New code should import from app.models.* and app.schemas.*

from app.db_models.item import Item
from app.db_models.user import User
from app.schemas.auth import NewPassword, Token, TokenPayload
from app.schemas.common import Message
from app.schemas.item import ItemBase, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate
from app.schemas.user import (
    UpdatePassword,
    UserBase,
    UserCreate,
    UserPublic,
    UserRegister,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)

__all__ = [
    # Database Models
    "User",
    "Item",
    # User Schemas
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdateMe",
    "UpdatePassword",
    "UserPublic",
    "UsersPublic",
    # Item Schemas
    "ItemBase",
    "ItemCreate",
    "ItemUpdate",
    "ItemPublic",
    "ItemsPublic",
    # Auth Schemas
    "Token",
    "TokenPayload",
    "NewPassword",
    # Common
    "Message",
]
