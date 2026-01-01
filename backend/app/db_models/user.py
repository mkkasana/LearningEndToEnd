import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.enums.user_role import UserRole

if TYPE_CHECKING:
    from app.db_models.item import Item


class User(SQLModel, table=True):
    """User database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    is_active: bool = True
    role: UserRole = Field(default=UserRole.USER)
    full_name: str | None = Field(default=None, max_length=255)

    # Relationships
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

    @property
    def is_superuser(self) -> bool:
        """Backward compatibility: returns True if role is superuser or admin."""
        return self.role in (UserRole.SUPERUSER, UserRole.ADMIN)

    @property
    def is_admin(self) -> bool:
        """Returns True if user has admin role."""
        return self.role == UserRole.ADMIN
