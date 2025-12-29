import logging
from datetime import timedelta

from sqlmodel import Session

from app.core.security import create_access_token, verify_password
from app.db_models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token

logger = logging.getLogger(__name__)


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
        logger.debug(f"Attempting authentication for email: {email}")

        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"Authentication failed: User not found for email: {email}")
            return None

        if not verify_password(password, user.hashed_password):
            logger.warning(
                f"Authentication failed: Invalid password for email: {email}"
            )
            return None

        logger.info(f"Authentication successful for user: {email} (ID: {user.id})")
        return user

    def create_access_token_for_user(
        self, user: User, expires_delta: timedelta
    ) -> Token:
        """Create JWT access token for authenticated user"""
        logger.debug(f"Creating access token for user: {user.email} (ID: {user.id})")
        access_token = create_access_token(user.id, expires_delta=expires_delta)
        logger.info(
            f"Access token created for user: {user.email}, expires in {expires_delta}"
        )
        return Token(access_token=access_token)

    def is_user_active(self, user: User) -> bool:
        """Check if user account is active"""
        is_active = user.is_active
        if not is_active:
            logger.warning(
                f"Inactive user attempted access: {user.email} (ID: {user.id})"
            )
        return is_active
