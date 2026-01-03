"""Unit tests for User schemas."""

import uuid

import pytest
from pydantic import ValidationError

from app.enums.user_role import UserRole
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserRegister,
    UserUpdate,
    UserUpdateMe,
    UpdatePassword,
    UserPublic,
    UsersPublic,
)


@pytest.mark.unit
class TestUserBase:
    """Tests for UserBase schema."""

    def test_valid_user_base(self) -> None:
        """Test UserBase with valid data."""
        user = UserBase(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.is_active is True
        assert user.role == UserRole.USER
        assert user.full_name is None

    def test_user_base_with_all_fields(self) -> None:
        """Test UserBase with all fields."""
        user = UserBase(
            email="test@example.com",
            is_active=False,
            role=UserRole.SUPERUSER,
            full_name="John Doe",
        )
        assert user.is_active is False
        assert user.role == UserRole.SUPERUSER
        assert user.full_name == "John Doe"

    def test_user_base_invalid_email(self) -> None:
        """Test UserBase with invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email="invalid-email")
        assert "email" in str(exc_info.value)

    def test_user_base_email_required(self) -> None:
        """Test UserBase requires email."""
        with pytest.raises(ValidationError) as exc_info:
            UserBase()
        assert "email" in str(exc_info.value)

    def test_user_base_email_max_length(self) -> None:
        """Test UserBase email max length validation."""
        long_email = "a" * 250 + "@example.com"
        with pytest.raises(ValidationError) as exc_info:
            UserBase(email=long_email)
        assert "email" in str(exc_info.value)


@pytest.mark.unit
class TestUserCreate:
    """Tests for UserCreate schema."""

    def test_valid_user_create(self) -> None:
        """Test UserCreate with valid data."""
        user = UserCreate(email="test@example.com", password="securepassword123")
        assert user.email == "test@example.com"
        assert user.password == "securepassword123"

    def test_user_create_password_required(self) -> None:
        """Test UserCreate requires password."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com")
        assert "password" in str(exc_info.value)

    def test_user_create_password_min_length(self) -> None:
        """Test UserCreate password minimum length."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="short")
        assert "password" in str(exc_info.value)

    def test_user_create_password_max_length(self) -> None:
        """Test UserCreate password maximum length."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="test@example.com", password="a" * 129)
        assert "password" in str(exc_info.value)

    def test_user_create_password_exactly_8_chars(self) -> None:
        """Test UserCreate password with exactly 8 characters (minimum)."""
        user = UserCreate(email="test@example.com", password="12345678")
        assert len(user.password) == 8


@pytest.mark.unit
class TestUserRegister:
    """Tests for UserRegister schema."""

    def test_valid_user_register(self) -> None:
        """Test UserRegister with valid data."""
        user = UserRegister(
            first_name="John",
            last_name="Doe",
            gender="MALE",
            date_of_birth="1990-01-15",
            email="test@example.com",
            password="securepassword123",
        )
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.gender == "MALE"

    def test_user_register_with_middle_name(self) -> None:
        """Test UserRegister with middle name."""
        user = UserRegister(
            first_name="John",
            middle_name="Michael",
            last_name="Doe",
            gender="MALE",
            date_of_birth="1990-01-15",
            email="test@example.com",
            password="securepassword123",
        )
        assert user.middle_name == "Michael"

    def test_user_register_first_name_required(self) -> None:
        """Test UserRegister requires first_name."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                last_name="Doe",
                gender="MALE",
                date_of_birth="1990-01-15",
                email="test@example.com",
                password="securepassword123",
            )
        assert "first_name" in str(exc_info.value)

    def test_user_register_gender_required(self) -> None:
        """Test UserRegister requires gender."""
        with pytest.raises(ValidationError) as exc_info:
            UserRegister(
                first_name="John",
                last_name="Doe",
                date_of_birth="1990-01-15",
                email="test@example.com",
                password="securepassword123",
            )
        assert "gender" in str(exc_info.value)


@pytest.mark.unit
class TestUserUpdate:
    """Tests for UserUpdate schema."""

    def test_user_update_all_optional(self) -> None:
        """Test UserUpdate with email only (inherited from UserBase)."""
        user = UserUpdate(email="test@example.com")
        assert user.email == "test@example.com"
        assert user.password is None

    def test_user_update_with_password(self) -> None:
        """Test UserUpdate with password."""
        user = UserUpdate(email="test@example.com", password="newpassword123")
        assert user.password == "newpassword123"

    def test_user_update_password_min_length(self) -> None:
        """Test UserUpdate password minimum length."""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(email="test@example.com", password="short")
        assert "password" in str(exc_info.value)


@pytest.mark.unit
class TestUserUpdateMe:
    """Tests for UserUpdateMe schema."""

    def test_user_update_me_all_optional(self) -> None:
        """Test UserUpdateMe with no fields."""
        user = UserUpdateMe()
        assert user.full_name is None
        assert user.email is None

    def test_user_update_me_partial(self) -> None:
        """Test UserUpdateMe with partial fields."""
        user = UserUpdateMe(full_name="John Doe")
        assert user.full_name == "John Doe"
        assert user.email is None

    def test_user_update_me_invalid_email(self) -> None:
        """Test UserUpdateMe with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdateMe(email="invalid-email")
        assert "email" in str(exc_info.value)


@pytest.mark.unit
class TestUpdatePassword:
    """Tests for UpdatePassword schema."""

    def test_valid_update_password(self) -> None:
        """Test UpdatePassword with valid data."""
        update = UpdatePassword(
            current_password="oldpassword123",
            new_password="newpassword456",
        )
        assert update.current_password == "oldpassword123"
        assert update.new_password == "newpassword456"

    def test_update_password_current_required(self) -> None:
        """Test UpdatePassword requires current_password."""
        with pytest.raises(ValidationError) as exc_info:
            UpdatePassword(new_password="newpassword456")
        assert "current_password" in str(exc_info.value)

    def test_update_password_new_required(self) -> None:
        """Test UpdatePassword requires new_password."""
        with pytest.raises(ValidationError) as exc_info:
            UpdatePassword(current_password="oldpassword123")
        assert "new_password" in str(exc_info.value)

    def test_update_password_min_length(self) -> None:
        """Test UpdatePassword password minimum length."""
        with pytest.raises(ValidationError) as exc_info:
            UpdatePassword(current_password="short", new_password="newpassword456")
        assert "current_password" in str(exc_info.value)


@pytest.mark.unit
class TestUserPublic:
    """Tests for UserPublic schema."""

    def test_valid_user_public(self) -> None:
        """Test UserPublic with valid data."""
        user = UserPublic(
            id=uuid.uuid4(),
            email="test@example.com",
        )
        assert user.email == "test@example.com"

    def test_user_public_requires_id(self) -> None:
        """Test UserPublic requires id."""
        with pytest.raises(ValidationError) as exc_info:
            UserPublic(email="test@example.com")
        assert "id" in str(exc_info.value)


@pytest.mark.unit
class TestUsersPublic:
    """Tests for UsersPublic schema."""

    def test_valid_users_public(self) -> None:
        """Test UsersPublic with valid data."""
        users = UsersPublic(
            data=[
                UserPublic(id=uuid.uuid4(), email="user1@example.com"),
                UserPublic(id=uuid.uuid4(), email="user2@example.com"),
            ],
            count=2,
        )
        assert len(users.data) == 2
        assert users.count == 2

    def test_users_public_empty_list(self) -> None:
        """Test UsersPublic with empty list."""
        users = UsersPublic(data=[], count=0)
        assert len(users.data) == 0
        assert users.count == 0
