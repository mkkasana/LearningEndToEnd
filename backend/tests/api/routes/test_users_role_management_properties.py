"""Property-based tests for admin role management.

**Feature: user-roles-permissions, Property 6: Admin Role Management**
**Validates: Requirements 5.1, 5.2, 5.3**
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from sqlmodel import Session

from app import crud
from app.core.config import settings as app_settings
from app.enums.user_role import UserRole
from app.models import UserCreate, UserUpdate
from tests.utils.utils import random_email, random_lower_string


class TestAdminRoleManagement:
    """Tests for Property 6: Admin Role Management.
    
    **Feature: user-roles-permissions, Property 6: Admin Role Management**
    **Validates: Requirements 5.1, 5.2, 5.3**
    
    Tests that:
    - Admin can change other users' roles
    - Superuser cannot change roles (403)
    - Admin cannot change own role
    """

    def test_admin_can_change_other_user_role(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Admin users should be able to change other users' roles.
        
        **Property 6: Admin Role Management**
        **Validates: Requirements 5.1**
        """
        # Get admin token (first superuser is admin)
        login_data = {
            "username": app_settings.FIRST_SUPERUSER,
            "password": app_settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create a regular user
        email = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=email, password=password, role=UserRole.USER)
        user = crud.create_user(session=db, user_create=user_in)
        
        # Admin changes user's role to superuser
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{user.id}/role",
            headers=admin_headers,
            json={"role": "superuser"},
        )
        
        assert r.status_code == 200
        updated_user = r.json()
        assert updated_user["role"] == "superuser"
        
        # Verify in database
        db.refresh(user)
        assert user.role == UserRole.SUPERUSER

    @settings(max_examples=100)
    @given(target_role=st.sampled_from(list(UserRole)))
    def test_admin_can_change_to_any_valid_role(
        self,
        client: TestClient,
        db: Session,
        target_role: UserRole,
    ) -> None:
        """Admin should be able to change users to any valid role.
        
        **Property 6: Admin Role Management**
        **Validates: Requirements 5.1**
        """
        # Get admin token
        login_data = {
            "username": app_settings.FIRST_SUPERUSER,
            "password": app_settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create a regular user
        email = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=email, password=password, role=UserRole.USER)
        user = crud.create_user(session=db, user_create=user_in)
        
        # Admin changes user's role
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{user.id}/role",
            headers=admin_headers,
            json={"role": target_role.value},
        )
        
        assert r.status_code == 200
        updated_user = r.json()
        assert updated_user["role"] == target_role.value

    def test_superuser_cannot_change_roles(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Superuser (non-admin) should not be able to change user roles.
        
        **Property 6: Admin Role Management**
        **Validates: Requirements 5.2**
        """
        # Create a superuser (not admin)
        superuser_email = random_email()
        superuser_password = random_lower_string()
        superuser_in = UserCreate(
            email=superuser_email, 
            password=superuser_password, 
            role=UserRole.SUPERUSER
        )
        superuser = crud.create_user(session=db, user_create=superuser_in)
        
        # Get superuser token
        login_data = {
            "username": superuser_email,
            "password": superuser_password,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        superuser_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create a regular user to try to modify
        target_email = random_email()
        target_password = random_lower_string()
        target_in = UserCreate(email=target_email, password=target_password, role=UserRole.USER)
        target_user = crud.create_user(session=db, user_create=target_in)
        
        # Superuser tries to change user's role - should fail
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{target_user.id}/role",
            headers=superuser_headers,
            json={"role": "superuser"},
        )
        
        assert r.status_code == 403
        assert r.json()["detail"] == "The user doesn't have enough privileges"

    def test_regular_user_cannot_change_roles(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Regular user should not be able to change user roles.
        
        **Property 6: Admin Role Management**
        **Validates: Requirements 5.2**
        """
        # Create a regular user
        user_email = random_email()
        user_password = random_lower_string()
        user_in = UserCreate(
            email=user_email, 
            password=user_password, 
            role=UserRole.USER
        )
        user = crud.create_user(session=db, user_create=user_in)
        
        # Get user token
        login_data = {
            "username": user_email,
            "password": user_password,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        user_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create another user to try to modify
        target_email = random_email()
        target_password = random_lower_string()
        target_in = UserCreate(email=target_email, password=target_password, role=UserRole.USER)
        target_user = crud.create_user(session=db, user_create=target_in)
        
        # Regular user tries to change user's role - should fail
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{target_user.id}/role",
            headers=user_headers,
            json={"role": "superuser"},
        )
        
        assert r.status_code == 403
        assert r.json()["detail"] == "The user doesn't have enough privileges"

    def test_admin_cannot_change_own_role(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Admin should not be able to change their own role.
        
        **Property 6: Admin Role Management**
        **Validates: Requirements 5.3**
        """
        # Get admin user and token
        admin_user = crud.get_user_by_email(session=db, email=app_settings.FIRST_SUPERUSER)
        assert admin_user is not None
        
        login_data = {
            "username": app_settings.FIRST_SUPERUSER,
            "password": app_settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Admin tries to change their own role - should fail
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{admin_user.id}/role",
            headers=admin_headers,
            json={"role": "user"},
        )
        
        assert r.status_code == 403
        assert r.json()["detail"] == "Cannot change your own role"

    @settings(max_examples=100)
    @given(target_role=st.sampled_from(list(UserRole)))
    def test_admin_cannot_change_own_role_to_any_role(
        self,
        client: TestClient,
        db: Session,
        target_role: UserRole,
    ) -> None:
        """Admin should not be able to change their own role to any role.
        
        **Property 6: Admin Role Management**
        **Validates: Requirements 5.3**
        """
        # Get admin user and token
        admin_user = crud.get_user_by_email(session=db, email=app_settings.FIRST_SUPERUSER)
        assert admin_user is not None
        
        login_data = {
            "username": app_settings.FIRST_SUPERUSER,
            "password": app_settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Admin tries to change their own role - should fail
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{admin_user.id}/role",
            headers=admin_headers,
            json={"role": target_role.value},
        )
        
        assert r.status_code == 403
        assert r.json()["detail"] == "Cannot change your own role"

    def test_role_update_user_not_found(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Role update should return 404 for non-existent user.
        
        **Property 6: Admin Role Management**
        """
        # Get admin token
        login_data = {
            "username": app_settings.FIRST_SUPERUSER,
            "password": app_settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Try to update non-existent user
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{uuid.uuid4()}/role",
            headers=admin_headers,
            json={"role": "superuser"},
        )
        
        assert r.status_code == 404
        assert r.json()["detail"] == "User not found"

    def test_invalid_role_rejected(
        self,
        client: TestClient,
        db: Session,
    ) -> None:
        """Invalid role values should be rejected with validation error.
        
        **Property 7: Role Validation**
        **Validates: Requirements 5.4**
        """
        # Get admin token
        login_data = {
            "username": app_settings.FIRST_SUPERUSER,
            "password": app_settings.FIRST_SUPERUSER_PASSWORD,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        admin_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create a user to modify
        email = random_email()
        password = random_lower_string()
        user_in = UserCreate(email=email, password=password, role=UserRole.USER)
        user = crud.create_user(session=db, user_create=user_in)
        
        # Try to set invalid role
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{user.id}/role",
            headers=admin_headers,
            json={"role": "invalid_role"},
        )
        
        assert r.status_code == 422  # Validation error

    @settings(max_examples=100)
    @given(
        requester_role=st.sampled_from(list(UserRole)),
        target_role=st.sampled_from(list(UserRole)),
    )
    def test_role_change_permission_property(
        self,
        client: TestClient,
        db: Session,
        requester_role: UserRole,
        target_role: UserRole,
    ) -> None:
        """Property: Only admin can change roles, and not their own.
        
        **Property 6: Admin Role Management**
        **Validates: Requirements 5.1, 5.2, 5.3**
        """
        # Create requester with specified role
        requester_email = random_email()
        requester_password = random_lower_string()
        requester_in = UserCreate(
            email=requester_email, 
            password=requester_password, 
            role=requester_role
        )
        requester = crud.create_user(session=db, user_create=requester_in)
        
        # Get requester token
        login_data = {
            "username": requester_email,
            "password": requester_password,
        }
        r = client.post(f"{app_settings.API_V1_STR}/login/access-token", data=login_data)
        tokens = r.json()
        requester_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Create target user
        target_email = random_email()
        target_password = random_lower_string()
        target_in = UserCreate(email=target_email, password=target_password, role=UserRole.USER)
        target_user = crud.create_user(session=db, user_create=target_in)
        
        # Try to change target user's role
        r = client.patch(
            f"{app_settings.API_V1_STR}/users/{target_user.id}/role",
            headers=requester_headers,
            json={"role": target_role.value},
        )
        
        # Only admin should succeed
        if requester_role == UserRole.ADMIN:
            assert r.status_code == 200
            assert r.json()["role"] == target_role.value
        else:
            assert r.status_code == 403
            assert r.json()["detail"] == "The user doesn't have enough privileges"
