from datetime import timedelta

from sqlmodel import Session

from app.core.security import create_access_token, verify_password
from app.db_models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token


class AuthService:
    """Service for authentication operations"""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """
        Authenticate user with email and password.
        Returns User if valid, None otherwise.
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token_for_user(
        self, user: User, expires_delta: timedelta
    ) -> Token:
        """Create JWT access token for authenticated user"""
        access_token = create_access_token(user.id, expires_delta=expires_delta)
        return Token(access_token=access_token)

    def is_user_active(self, user: User) -> bool:
        """Check if user account is active"""
        return user.is_active
