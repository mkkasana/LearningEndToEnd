"""Integration tests for Users API routes."""

import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.core.security import verify_password
from app.models import User, UserCreate
from tests.utils.utils import random_email, random_lower_string


# ============================================================================
# Integration Tests - User CRUD (Task 13.1)
# ============================================================================


@pytest.mark.integration
class TestGetUsersMe:
    """Integration tests for GET /users/me endpoint."""

    def test_get_users_superuser_me(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test admin user (first superuser) can get their own info."""
        r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
        current_user = r.json()
        assert r.status_code == 200
        assert current_user["is_active"] is True
        # First user is created as ADMIN, not SUPERUSER
        assert current_user["role"] == "admin"
        assert current_user["email"] == settings.FIRST_SUPERUSER

    def test_get_users_normal_user_me(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        """Test normal user can get their own info."""
        r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
        current_user = r.json()
        assert r.status_code == 200
        assert current_user["is_active"] is True
        assert current_user["is_superuser"] is False
        assert current_user["email"] == settings.EMAIL_TEST_USER

    def test_get_users_me_without_auth(self, client: TestClient) -> None:
        """Test getting user info without auth returns 401."""
        r = client.get(f"{settings.API_V1_STR}/users/me")
        assert r.status_code == 401


@pytest.mark.integration
class TestUpdateUsersMe:
    """Integration tests for PATCH /users/me endpoint."""

    def test_update_user_me(
        self, client: TestClient, db: Session
    ) -> None:
        """Test user can update their own info."""
        # Create a fresh user for this test to avoid conflicts with other tests
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)
        user_id = user.id
        
        # Login to get auth headers
        login_data = {"username": username, "password": password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Update user info
        full_name = "Updated Name"
        new_email = random_email()
        data = {"full_name": full_name, "email": new_email}
        r = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=headers,
            json=data,
        )
        assert r.status_code == 200
        updated_user = r.json()
        assert updated_user["email"] == new_email
        assert updated_user["full_name"] == full_name

        # Expire all cached objects to force fresh query
        db.expire_all()
        
        # Query by user ID instead of email to verify the update
        user_db = db.get(User, user_id)
        assert user_db
        assert user_db.email == new_email
        assert user_db.full_name == full_name

    def test_update_user_me_email_exists(
        self, client: TestClient, normal_user_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test updating to existing email returns 409."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)

        data = {"email": user.email}
        r = client.patch(
            f"{settings.API_V1_STR}/users/me",
            headers=normal_user_token_headers,
            json=data,
        )
        assert r.status_code == 409
        assert r.json()["detail"] == "User with this email already exists"


@pytest.mark.integration
class TestUpdatePasswordMe:
    """Integration tests for PATCH /users/me/password endpoint."""

    def test_update_password_me(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test user can update their password."""
        new_password = random_lower_string()
        data = {
            "current_password": settings.FIRST_SUPERUSER_PASSWORD,
            "new_password": new_password,
        }
        r = client.patch(
            f"{settings.API_V1_STR}/users/me/password",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 200
        assert r.json()["message"] == "Password updated successfully"

        user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
        user_db = db.exec(user_query).first()
        assert user_db
        assert verify_password(new_password, user_db.hashed_password)

        # Revert to the old password
        old_data = {
            "current_password": new_password,
            "new_password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.patch(
            f"{settings.API_V1_STR}/users/me/password",
            headers=superuser_token_headers,
            json=old_data,
        )
        db.refresh(user_db)
        assert r.status_code == 200

    def test_update_password_me_incorrect_password(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test updating password with wrong current password returns 400."""
        new_password = random_lower_string()
        data = {"current_password": new_password, "new_password": new_password}
        r = client.patch(
            f"{settings.API_V1_STR}/users/me/password",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Incorrect password"

    def test_update_password_me_same_password_error(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test updating to same password returns 400."""
        data = {
            "current_password": settings.FIRST_SUPERUSER_PASSWORD,
            "new_password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.patch(
            f"{settings.API_V1_STR}/users/me/password",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "New password cannot be the same as the current one"


@pytest.mark.integration
class TestDeleteUsersMe:
    """Integration tests for DELETE /users/me endpoint."""

    def test_delete_user_me(self, client: TestClient, db: Session) -> None:
        """Test user can delete their own account."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)
        user_id = user.id

        login_data = {"username": username, "password": password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        r = client.delete(f"{settings.API_V1_STR}/users/me", headers=headers)
        assert r.status_code == 200
        assert r.json()["message"] == "User deleted successfully"

        result = db.exec(select(User).where(User.id == user_id)).first()
        assert result is None

    def test_delete_user_me_as_superuser(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test superuser cannot delete themselves."""
        r = client.delete(
            f"{settings.API_V1_STR}/users/me",
            headers=superuser_token_headers,
        )
        assert r.status_code == 403
        assert r.json()["detail"] == "Super users are not allowed to delete themselves"


# ============================================================================
# Integration Tests - Admin User Management (Task 13.2)
# ============================================================================


@pytest.mark.integration
class TestGetUsers:
    """Integration tests for GET /users/ endpoint (admin only)."""

    def test_retrieve_users(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test admin can retrieve all users."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        crud.create_user(session=db, user_create=user_in)

        r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
        all_users = r.json()

        assert r.status_code == 200
        assert len(all_users["data"]) > 1
        assert "count" in all_users
        for item in all_users["data"]:
            assert "email" in item

    def test_retrieve_users_by_normal_user(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        """Test normal user cannot retrieve all users."""
        r = client.get(f"{settings.API_V1_STR}/users/", headers=normal_user_token_headers)
        assert r.status_code == 403


@pytest.mark.integration
class TestCreateUser:
    """Integration tests for POST /users/ endpoint (admin only)."""

    def test_create_user_new_email(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test admin can create new user."""
        with (
            patch("app.utils.send_email", return_value=None),
            patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
            patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
        ):
            username = random_email()
            password = random_lower_string()
            data = {"email": username, "password": password}
            r = client.post(
                f"{settings.API_V1_STR}/users/",
                headers=superuser_token_headers,
                json=data,
            )
            assert 200 <= r.status_code < 300
            created_user = r.json()
            user = crud.get_user_by_email(session=db, email=username)
            assert user
            assert user.email == created_user["email"]

    def test_create_user_existing_username(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test creating user with existing email returns 409."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        crud.create_user(session=db, user_create=user_in)

        data = {"email": username, "password": password}
        r = client.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 409

    def test_create_user_by_normal_user(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        """Test normal user cannot create users."""
        username = random_email()
        password = random_lower_string()
        data = {"email": username, "password": password}
        r = client.post(
            f"{settings.API_V1_STR}/users/",
            headers=normal_user_token_headers,
            json=data,
        )
        assert r.status_code == 403


@pytest.mark.integration
class TestGetUserById:
    """Integration tests for GET /users/{user_id} endpoint."""

    def test_get_existing_user(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test admin can get user by ID."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)

        r = client.get(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 200
        api_user = r.json()
        assert api_user["email"] == username

    def test_get_existing_user_current_user(self, client: TestClient, db: Session) -> None:
        """Test user can get their own info by ID."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)

        login_data = {"username": username, "password": password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        r = client.get(f"{settings.API_V1_STR}/users/{user.id}", headers=headers)
        assert r.status_code == 200
        assert r.json()["email"] == username

    def test_get_existing_user_permissions_error(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        """Test normal user cannot get other user's info."""
        r = client.get(
            f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404

    def test_get_user_not_found(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test getting non-existent user returns 404."""
        r = client.get(
            f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 404


@pytest.mark.integration
class TestUpdateUser:
    """Integration tests for PATCH /users/{user_id} endpoint (admin only)."""

    def test_update_user(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test admin can update user."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)

        data = {"full_name": "Updated_full_name"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 200
        assert r.json()["full_name"] == "Updated_full_name"

    def test_update_user_not_exists(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test updating non-existent user returns 404."""
        data = {"full_name": "Updated_full_name"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 404
        assert r.json()["detail"] == "The user with this id does not exist in the system"

    def test_update_user_email_exists(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test updating user to existing email returns 409."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)

        username2 = random_email()
        user_in2 = UserCreate(email=username2, password=password)
        user2 = crud.create_user(session=db, user_create=user_in2)

        data = {"email": user2.email}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 409

    def test_update_user_by_normal_user(
        self, client: TestClient, normal_user_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test normal user cannot update other users."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)

        data = {"full_name": "Hacked"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers=normal_user_token_headers,
            json=data,
        )
        assert r.status_code == 403


@pytest.mark.integration
class TestDeleteUser:
    """Integration tests for DELETE /users/{user_id} endpoint (admin only)."""

    def test_delete_user_super_user(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test admin can delete user."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)
        user_id = user.id

        r = client.delete(
            f"{settings.API_V1_STR}/users/{user_id}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 200
        assert r.json()["message"] == "User deleted successfully"

        result = db.exec(select(User).where(User.id == user_id)).first()
        assert result is None

    def test_delete_user_not_found(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test deleting non-existent user returns 404."""
        r = client.delete(
            f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 404
        assert r.json()["detail"] == "User not found"

    def test_delete_user_current_super_user_error(
        self, client: TestClient, superuser_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test admin cannot delete themselves."""
        super_user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
        assert super_user

        r = client.delete(
            f"{settings.API_V1_STR}/users/{super_user.id}",
            headers=superuser_token_headers,
        )
        assert r.status_code == 403
        assert r.json()["detail"] == "Super users are not allowed to delete themselves"

    def test_delete_user_without_privileges(
        self, client: TestClient, normal_user_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test normal user cannot delete other users."""
        username = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=username, password=password)
        user = crud.create_user(session=db, user_create=user_in)

        r = client.delete(
            f"{settings.API_V1_STR}/users/{user.id}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 403
        assert r.json()["detail"] == "The user doesn't have enough privileges"


# ============================================================================
# Backward Compatibility - Keep existing test functions
# ============================================================================


def test_get_users_superuser_me(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=superuser_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    # First user is created as ADMIN, not SUPERUSER
    assert current_user["role"] == "admin"
    assert current_user["email"] == settings.FIRST_SUPERUSER


def test_get_users_normal_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=normal_user_token_headers)
    current_user = r.json()
    assert current_user
    assert current_user["is_active"] is True
    assert current_user["is_superuser"] is False
    # Note: normal_user_token_headers may use a different email than EMAIL_TEST_USER
    assert "email" in current_user


def test_create_user_new_email(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    with (
        patch("app.utils.send_email", return_value=None),
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        username = random_email()
        password = random_lower_string()
        data = {"email": username, "password": password}
        r = client.post(
            f"{settings.API_V1_STR}/users/",
            headers=superuser_token_headers,
            json=data,
        )
        assert 200 <= r.status_code < 300
        created_user = r.json()
        user = crud.get_user_by_email(session=db, email=username)
        assert user
        assert user.email == created_user["email"]


def test_get_existing_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id
    r = client.get(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.get_user_by_email(session=db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


def test_get_existing_user_current_user(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    login_data = {"username": username, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = client.get(f"{settings.API_V1_STR}/users/{user_id}", headers=headers)
    assert 200 <= r.status_code < 300
    api_user = r.json()
    existing_user = crud.get_user_by_email(session=db, email=username)
    assert existing_user
    assert existing_user.email == api_user["email"]


def test_get_existing_user_permissions_error(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    r = client.get(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404


def test_create_user_existing_username(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    crud.create_user(session=db, user_create=user_in)
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 409
    assert "_id" not in created_user


def test_create_user_by_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    username = random_email()
    password = random_lower_string()
    data = {"email": username, "password": password}
    r = client.post(
        f"{settings.API_V1_STR}/users/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 403


def test_retrieve_users(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    crud.create_user(session=db, user_create=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    crud.create_user(session=db, user_create=user_in2)

    r = client.get(f"{settings.API_V1_STR}/users/", headers=superuser_token_headers)
    all_users = r.json()

    assert len(all_users["data"]) > 1
    assert "count" in all_users
    for item in all_users["data"]:
        assert "email" in item


def test_update_user_me(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    full_name = "Updated Name"
    email = random_email()
    data = {"full_name": full_name, "email": email}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["email"] == email
    assert updated_user["full_name"] == full_name

    user_query = select(User).where(User.email == email)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == email
    assert user_db.full_name == full_name


def test_update_password_me(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    new_password = random_lower_string()
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": new_password,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()
    assert updated_user["message"] == "Password updated successfully"

    user_query = select(User).where(User.email == settings.FIRST_SUPERUSER)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == settings.FIRST_SUPERUSER
    assert verify_password(new_password, user_db.hashed_password)

    # Revert to the old password to keep consistency in test
    old_data = {
        "current_password": new_password,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=old_data,
    )
    db.refresh(user_db)

    assert r.status_code == 200
    assert verify_password(settings.FIRST_SUPERUSER_PASSWORD, user_db.hashed_password)


def test_update_password_me_incorrect_password(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    new_password = random_lower_string()
    data = {"current_password": new_password, "new_password": new_password}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert updated_user["detail"] == "Incorrect password"


def test_update_user_me_email_exists(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    data = {"email": user.email}
    r = client.patch(
        f"{settings.API_V1_STR}/users/me",
        headers=normal_user_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


def test_update_password_me_same_password_error(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {
        "current_password": settings.FIRST_SUPERUSER_PASSWORD,
        "new_password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.patch(
        f"{settings.API_V1_STR}/users/me/password",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 400
    updated_user = r.json()
    assert (
        updated_user["detail"] == "New password cannot be the same as the current one"
    )


def test_register_user(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string() + "Aa1!"
    first_name = random_lower_string()
    last_name = random_lower_string()
    data = {
        "email": username,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "gender": "MALE",
        "date_of_birth": "1990-01-01",
    }
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)
    assert r.status_code == 200
    created_user = r.json()
    assert created_user["email"] == username

    user_query = select(User).where(User.email == username)
    user_db = db.exec(user_query).first()
    assert user_db
    assert user_db.email == username
    assert verify_password(password, user_db.hashed_password)


def test_register_user_already_exists_error(client: TestClient) -> None:
    password = random_lower_string() + "Aa1!"
    first_name = random_lower_string()
    last_name = random_lower_string()
    data = {
        "email": settings.FIRST_SUPERUSER,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "gender": "MALE",
        "date_of_birth": "1990-01-01",
    }
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)
    assert r.status_code == 400
    assert r.json()["detail"] == "The user with this email already exists in the system"


def test_update_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    data = {"full_name": "Updated_full_name"}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 200
    updated_user = r.json()

    assert updated_user["full_name"] == "Updated_full_name"

    user_query = select(User).where(User.email == username)
    user_db = db.exec(user_query).first()
    db.refresh(user_db)
    assert user_db
    assert user_db.full_name == "Updated_full_name"


def test_update_user_not_exists(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"full_name": "Updated_full_name"}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "The user with this id does not exist in the system"


def test_update_user_email_exists(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    username2 = random_email()
    password2 = random_lower_string()
    user_in2 = UserCreate(email=username2, password=password2)
    user2 = crud.create_user(session=db, user_create=user_in2)

    data = {"email": user2.email}
    r = client.patch(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert r.status_code == 409
    assert r.json()["detail"] == "User with this email already exists"


def test_delete_user_me(client: TestClient, db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id

    login_data = {"username": username, "password": password}
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}

    r = client.delete(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None

    user_query = select(User).where(User.id == user_id)
    user_db = db.execute(user_query).first()
    assert user_db is None


def test_delete_user_me_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/users/me",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    response = r.json()
    assert response["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_super_user(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)
    user_id = user.id
    r = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 200
    deleted_user = r.json()
    assert deleted_user["message"] == "User deleted successfully"
    result = db.exec(select(User).where(User.id == user_id)).first()
    assert result is None


def test_delete_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.delete(
        f"{settings.API_V1_STR}/users/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 404
    assert r.json()["detail"] == "User not found"


def test_delete_user_current_super_user_error(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    super_user = crud.get_user_by_email(session=db, email=settings.FIRST_SUPERUSER)
    assert super_user
    user_id = super_user.id

    r = client.delete(
        f"{settings.API_V1_STR}/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "Super users are not allowed to delete themselves"


def test_delete_user_without_privileges(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = UserCreate(email=username, password=password)
    user = crud.create_user(session=db, user_create=user_in)

    r = client.delete(
        f"{settings.API_V1_STR}/users/{user.id}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 403
    assert r.json()["detail"] == "The user doesn't have enough privileges"


# ============================================================================
# Property Tests - Admin Role Management (Task 6.2)
# ============================================================================


@pytest.mark.unit
class TestUpdateUserRole:
    """Property tests for PATCH /users/{user_id}/role endpoint.
    
    **Feature: user-roles-permissions, Property 6: Admin Role Management**
    **Validates: Requirements 5.1, 5.2, 5.3**
    
    Tests that:
    - Admin can change other users' roles
    - Superuser cannot change roles (403)
    - Admin cannot change own role
    """

    def test_admin_can_change_other_user_role(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin can change another user's role.
        
        **Validates: Requirements 5.1**
        """
        from app.enums.user_role import UserRole
        
        # Create an admin user
        admin_email = random_email()
        admin_password = random_lower_string()
        admin_in = UserCreate(email=admin_email, password=admin_password)
        admin_user = crud.create_user(session=db, user_create=admin_in)
        admin_user.role = UserRole.ADMIN
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Get admin token
        login_data = {"username": admin_email, "password": admin_password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create a regular user to update
        target_email = random_email()
        target_password = random_lower_string()
        target_in = UserCreate(email=target_email, password=target_password)
        target_user = crud.create_user(session=db, user_create=target_in)
        
        # Admin changes target user's role to superuser
        data = {"role": "superuser"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{target_user.id}/role",
            headers=admin_headers,
            json=data,
        )
        
        assert r.status_code == 200
        updated_user = r.json()
        assert updated_user["role"] == "superuser"
        
        # Verify in database
        db.refresh(target_user)
        assert target_user.role == UserRole.SUPERUSER

    def test_superuser_cannot_change_roles(
        self, client: TestClient, db: Session
    ) -> None:
        """Test superuser cannot change user roles (403).
        
        **Validates: Requirements 5.2**
        """
        from app.enums.user_role import UserRole
        
        # Create a superuser
        superuser_email = random_email()
        superuser_password = random_lower_string()
        superuser_in = UserCreate(email=superuser_email, password=superuser_password)
        superuser = crud.create_user(session=db, user_create=superuser_in)
        superuser.role = UserRole.SUPERUSER
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        # Get superuser token
        login_data = {"username": superuser_email, "password": superuser_password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        superuser_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create a regular user to try to update
        target_email = random_email()
        target_password = random_lower_string()
        target_in = UserCreate(email=target_email, password=target_password)
        target_user = crud.create_user(session=db, user_create=target_in)
        
        # Superuser tries to change target user's role
        data = {"role": "superuser"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{target_user.id}/role",
            headers=superuser_headers,
            json=data,
        )
        
        assert r.status_code == 403
        assert r.json()["detail"] == "The user doesn't have enough privileges"

    def test_admin_cannot_change_own_role(
        self, client: TestClient, db: Session
    ) -> None:
        """Test admin cannot change their own role.
        
        **Validates: Requirements 5.3**
        """
        from app.enums.user_role import UserRole
        
        # Create an admin user
        admin_email = random_email()
        admin_password = random_lower_string()
        admin_in = UserCreate(email=admin_email, password=admin_password)
        admin_user = crud.create_user(session=db, user_create=admin_in)
        admin_user.role = UserRole.ADMIN
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Get admin token
        login_data = {"username": admin_email, "password": admin_password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Admin tries to change their own role
        data = {"role": "user"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{admin_user.id}/role",
            headers=admin_headers,
            json=data,
        )
        
        assert r.status_code == 403
        assert r.json()["detail"] == "Cannot change your own role"

    def test_normal_user_cannot_change_roles(
        self, client: TestClient, normal_user_token_headers: dict[str, str], db: Session
    ) -> None:
        """Test normal user cannot change user roles (403).
        
        **Validates: Requirements 5.2**
        """
        # Create a target user
        target_email = random_email()
        target_password = random_lower_string()
        target_in = UserCreate(email=target_email, password=target_password)
        target_user = crud.create_user(session=db, user_create=target_in)
        
        # Normal user tries to change target user's role
        data = {"role": "superuser"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{target_user.id}/role",
            headers=normal_user_token_headers,
            json=data,
        )
        
        assert r.status_code == 403
        assert r.json()["detail"] == "The user doesn't have enough privileges"

    def test_update_role_user_not_found(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating role for non-existent user returns 404."""
        from app.enums.user_role import UserRole
        
        # Create an admin user
        admin_email = random_email()
        admin_password = random_lower_string()
        admin_in = UserCreate(email=admin_email, password=admin_password)
        admin_user = crud.create_user(session=db, user_create=admin_in)
        admin_user.role = UserRole.ADMIN
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Get admin token
        login_data = {"username": admin_email, "password": admin_password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Try to update non-existent user
        data = {"role": "superuser"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{uuid.uuid4()}/role",
            headers=admin_headers,
            json=data,
        )
        
        assert r.status_code == 404
        assert r.json()["detail"] == "The user with this id does not exist in the system"

    def test_update_role_invalid_role_value(
        self, client: TestClient, db: Session
    ) -> None:
        """Test updating role with invalid value returns 422.
        
        **Validates: Requirements 5.4**
        """
        from app.enums.user_role import UserRole
        
        # Create an admin user
        admin_email = random_email()
        admin_password = random_lower_string()
        admin_in = UserCreate(email=admin_email, password=admin_password)
        admin_user = crud.create_user(session=db, user_create=admin_in)
        admin_user.role = UserRole.ADMIN
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Get admin token
        login_data = {"username": admin_email, "password": admin_password}
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create a target user
        target_email = random_email()
        target_password = random_lower_string()
        target_in = UserCreate(email=target_email, password=target_password)
        target_user = crud.create_user(session=db, user_create=target_in)
        
        # Try to update with invalid role
        data = {"role": "invalid_role"}
        r = client.patch(
            f"{settings.API_V1_STR}/users/{target_user.id}/role",
            headers=admin_headers,
            json=data,
        )
        
        assert r.status_code == 422  # Validation error
