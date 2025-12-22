import uuid

from pydantic import EmailStr, Field
from sqlmodel import SQLModel


class UserBase(SQLModel):
    """Shared user properties"""

    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Properties to receive via API on creation"""

    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    """Properties for user self-registration"""

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


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


class UsersPublic(SQLModel):
    """List of users response"""

    data: list[UserPublic]
    count: int
