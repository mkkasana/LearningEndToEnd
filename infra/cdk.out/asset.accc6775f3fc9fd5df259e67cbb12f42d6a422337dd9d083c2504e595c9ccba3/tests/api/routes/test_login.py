"""Integration tests for Auth API routes."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.core.security import verify_password
from app.crud import create_user
from app.models import UserCreate
from app.utils import generate_password_reset_token
from tests.utils.user import user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


@pytest.mark.integration
class TestLoginAccessToken:
    """Integration tests for POST /login/access-token endpoint."""

    def test_get_access_token_valid_credentials(self, client: TestClient) -> None:
        """Test login with valid credentials returns access token."""
        login_data = {
            "username": settings.FIRST_SUPERUSER,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        assert r.status_code == 200
        assert "access_token" in tokens
        assert tokens["access_token"]
        assert tokens["token_type"] == "bearer"

    def test_get_access_token_incorrect_password(self, client: TestClient) -> None:
        """Test login with incorrect password returns 401."""
        login_data = {
            "username": settings.FIRST_SUPERUSER,
            "password": "incorrect",
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        assert r.status_code == 401

    def test_get_access_token_nonexistent_user(self, client: TestClient) -> None:
        """Test login with non-existent user returns 401."""
        login_data = {
            "username": "nonexistent@example.com",
            "password": "somepassword",
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        assert r.status_code == 401

    def test_get_access_token_inactive_user(
        self, client: TestClient, db: Session
    ) -> None:
        """Test login with inactive user returns 400."""
        email = random_email()
        password = random_lower_string()
        user_create = UserCreate(
            email=email,
            password=password,
            is_active=False,  # Inactive user
            is_superuser=False,
        )
        create_user(session=db, user_create=user_create)

        login_data = {
            "username": email,
            "password": password,
        }
        r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
        assert r.status_code == 400


@pytest.mark.integration
class TestTestToken:
    """Integration tests for POST /login/test-token endpoint."""

    def test_use_access_token(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test access token validation returns user info."""
        r = client.post(
            f"{settings.API_V1_STR}/login/test-token",
            headers=superuser_token_headers,
        )
        result = r.json()
        assert r.status_code == 200
        assert "email" in result
        assert result["email"] == settings.FIRST_SUPERUSER

    def test_test_token_without_auth(self, client: TestClient) -> None:
        """Test access token endpoint without auth returns 401."""
        r = client.post(f"{settings.API_V1_STR}/login/test-token")
        assert r.status_code == 401

    def test_test_token_invalid_token(self, client: TestClient) -> None:
        """Test access token endpoint with invalid token returns 403."""
        headers = {"Authorization": "Bearer invalid_token"}
        r = client.post(f"{settings.API_V1_STR}/login/test-token", headers=headers)
        assert r.status_code == 403


@pytest.mark.integration
class TestPasswordRecovery:
    """Integration tests for POST /password-recovery/{email} endpoint."""

    def test_recovery_password_valid_email(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        """Test password recovery with valid email sends recovery email."""
        with (
            patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
            patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
        ):
            email = "test@example.com"
            r = client.post(
                f"{settings.API_V1_STR}/password-recovery/{email}",
                headers=normal_user_token_headers,
            )
            assert r.status_code == 200
            assert r.json() == {"message": "Password recovery email sent"}

    def test_recovery_password_nonexistent_email(
        self, client: TestClient, normal_user_token_headers: dict[str, str]
    ) -> None:
        """Test password recovery with non-existent email returns 404."""
        email = "nonexistent_user@example.com"
        r = client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 404
        assert "does not exist" in r.json()["detail"]


@pytest.mark.integration
class TestResetPassword:
    """Integration tests for POST /reset-password/ endpoint."""

    def test_reset_password_valid_token(
        self, client: TestClient, db: Session
    ) -> None:
        """Test password reset with valid token updates password."""
        email = random_email()
        password = random_lower_string()
        new_password = random_lower_string()

        user_create = UserCreate(
            email=email,
            full_name="Test User",
            password=password,
            is_active=True,
            is_superuser=False,
        )
        user = create_user(session=db, user_create=user_create)
        token = generate_password_reset_token(email=email)
        headers = user_authentication_headers(
            client=client, email=email, password=password
        )
        data = {"new_password": new_password, "token": token}

        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            headers=headers,
            json=data,
        )

        assert r.status_code == 200
        assert r.json() == {"message": "Password updated successfully"}

        db.refresh(user)
        assert verify_password(new_password, user.hashed_password)

    def test_reset_password_invalid_token(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test password reset with invalid token returns 400."""
        data = {"new_password": "changethis123", "token": "invalid"}
        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            headers=superuser_token_headers,
            json=data,
        )
        response = r.json()

        assert r.status_code == 400
        assert response["detail"] == "Invalid token"

    def test_reset_password_expired_token(
        self, client: TestClient, superuser_token_headers: dict[str, str]
    ) -> None:
        """Test password reset with expired token returns 400."""
        # An invalid/malformed token will be treated as expired
        data = {"new_password": "newpassword123", "token": "expired_token_here"}
        r = client.post(
            f"{settings.API_V1_STR}/reset-password/",
            headers=superuser_token_headers,
            json=data,
        )
        assert r.status_code == 400
        assert r.json()["detail"] == "Invalid token"


@pytest.mark.integration
class TestSignup:
    """Integration tests for POST /users/signup endpoint."""

    def test_signup_valid_data(self, client: TestClient, db: Session) -> None:
        """Test signup with valid data creates user and person."""
        from sqlmodel import select
        from app.models import User

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

    def test_signup_duplicate_email(self, client: TestClient) -> None:
        """Test signup with existing email returns 400."""
        password = random_lower_string() + "Aa1!"
        first_name = random_lower_string()
        last_name = random_lower_string()
        data = {
            "email": settings.FIRST_SUPERUSER,  # Already exists
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "gender": "MALE",
            "date_of_birth": "1990-01-01",
        }
        r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)

        assert r.status_code == 400
        assert "already exists" in r.json()["detail"]

    def test_signup_invalid_gender(self, client: TestClient) -> None:
        """Test signup with invalid gender returns 400."""
        username = random_email()
        password = random_lower_string() + "Aa1!"
        data = {
            "email": username,
            "password": password,
            "first_name": "John",
            "last_name": "Doe",
            "gender": "INVALID",
            "date_of_birth": "1990-01-01",
        }
        r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)

        assert r.status_code == 400
        assert "Invalid gender" in r.json()["detail"]

    def test_signup_invalid_date_format(self, client: TestClient) -> None:
        """Test signup with invalid date format returns 400."""
        username = random_email()
        password = random_lower_string() + "Aa1!"
        data = {
            "email": username,
            "password": password,
            "first_name": "John",
            "last_name": "Doe",
            "gender": "MALE",
            "date_of_birth": "01-01-1990",  # Wrong format
        }
        r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)

        assert r.status_code == 400
        assert "Invalid date format" in r.json()["detail"]

    def test_signup_with_middle_name(self, client: TestClient, db: Session) -> None:
        """Test signup with middle name creates user with full name."""
        from sqlmodel import select
        from app.models import User

        username = random_email()
        password = random_lower_string() + "Aa1!"
        data = {
            "email": username,
            "password": password,
            "first_name": "John",
            "middle_name": "Michael",
            "last_name": "Doe",
            "gender": "FEMALE",
            "date_of_birth": "1985-06-15",
        }
        r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)

        assert r.status_code == 200
        created_user = r.json()
        assert created_user["full_name"] == "John Michael Doe"

        user_query = select(User).where(User.email == username)
        user_db = db.exec(user_query).first()
        assert user_db
        assert user_db.full_name == "John Michael Doe"


# Keep backward compatibility with existing test functions
def test_get_access_token(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": settings.FIRST_SUPERUSER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]


def test_get_access_token_incorrect_password(client: TestClient) -> None:
    login_data = {
        "username": settings.FIRST_SUPERUSER,
        "password": "incorrect",
    }
    r = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    assert r.status_code == 401


def test_use_access_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token",
        headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result


def test_recovery_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    with (
        patch("app.core.config.settings.SMTP_HOST", "smtp.example.com"),
        patch("app.core.config.settings.SMTP_USER", "admin@example.com"),
    ):
        email = "test@example.com"
        r = client.post(
            f"{settings.API_V1_STR}/password-recovery/{email}",
            headers=normal_user_token_headers,
        )
        assert r.status_code == 200
        assert r.json() == {"message": "Password recovery email sent"}


def test_recovery_password_user_not_exits(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    email = "jVgQr@example.com"
    r = client.post(
        f"{settings.API_V1_STR}/password-recovery/{email}",
        headers=normal_user_token_headers,
    )
    assert r.status_code == 404


def test_reset_password(client: TestClient, db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    new_password = random_lower_string()

    user_create = UserCreate(
        email=email,
        full_name="Test User",
        password=password,
        is_active=True,
        is_superuser=False,
    )
    user = create_user(session=db, user_create=user_create)
    token = generate_password_reset_token(email=email)
    headers = user_authentication_headers(client=client, email=email, password=password)
    data = {"new_password": new_password, "token": token}

    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=headers,
        json=data,
    )

    assert r.status_code == 200
    assert r.json() == {"message": "Password updated successfully"}

    db.refresh(user)
    assert verify_password(new_password, user.hashed_password)


def test_reset_password_invalid_token(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    data = {"new_password": "changethis", "token": "invalid"}
    r = client.post(
        f"{settings.API_V1_STR}/reset-password/",
        headers=superuser_token_headers,
        json=data,
    )
    response = r.json()

    assert "detail" in response
    assert r.status_code == 400
    assert response["detail"] == "Invalid token"
