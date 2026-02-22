import uuid
from typing import TYPE_CHECKING, Any

from pydantic import EmailStr, field_validator
from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
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
    role: UserRole = Field(
        default=UserRole.USER,
        sa_column=Column(
            SAEnum(UserRole, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
            default=UserRole.USER,
        ),
    )
    full_name: str | None = Field(default=None, max_length=255)

    # Relationships
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

    @field_validator("role", mode="before")
    @classmethod
    def convert_role(cls, v: Any) -> UserRole:
        """Convert string role to UserRole enum."""
        if isinstance(v, str):
            return UserRole(v)
        if isinstance(v, UserRole):
            return v
        return UserRole.USER  # Default fallback

    @property
    def is_user(self) -> bool:
        """Backward compatibility: returns True if role is just user."""
        return self.role == UserRole.USER

    @property
    def is_superuser(self) -> bool:
        """Backward compatibility: returns True if role is superuser."""
        return self.role == UserRole.SUPERUSER

    @property
    def is_admin(self) -> bool:
        """Returns True if user has admin role."""
        return self.role == UserRole.ADMIN
