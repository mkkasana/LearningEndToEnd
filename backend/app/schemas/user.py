import uuid
from typing import Any

from pydantic import EmailStr, Field
from sqlmodel import SQLModel

from app.enums.user_role import UserRole


class UserBase(SQLModel):
    """Shared user properties"""

    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    role: UserRole = UserRole.USER
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Properties to receive via API on creation"""

    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    """Properties for user self-registration"""

    first_name: str = Field(max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    last_name: str = Field(max_length=100)
    gender: str = Field(description="Gender: MALE or FEMALE")
    date_of_birth: str = Field(description="Date of birth in YYYY-MM-DD format")
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(UserBase):
    """Properties to receive via API on update, all are optional"""

    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    """Properties for user self-update"""

    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Password update request"""

    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(UserBase):
    """Properties to return via API"""

    id: uuid.UUID
    is_superuser: bool = False

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> "UserPublic":
        """Override model_validate to compute is_superuser from role."""
        instance = super().model_validate(obj, **kwargs)
        # Compute is_superuser based on role (only SUPERUSER role)
        if hasattr(obj, "role"):
            role = obj.role
            if isinstance(role, str):
                role = UserRole(role)
            instance.is_superuser = role == UserRole.SUPERUSER
        return instance


class UsersPublic(SQLModel):
    """List of users response"""

    data: list[UserPublic]
    count: int


class UserRoleUpdate(SQLModel):
    """Schema for updating user role (admin only)"""

    role: UserRole
