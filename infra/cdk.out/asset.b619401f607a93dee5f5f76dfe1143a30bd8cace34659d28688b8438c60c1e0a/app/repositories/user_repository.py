import logging

from sqlmodel import Session, select

from app.db_models.user import User
from app.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    """Repository for User data access"""

    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email address"""
        logger.debug(f"Querying user by email: {email}")
        statement = select(User).where(User.email == email)
        result = self.session.exec(statement).first()
        if result:
            logger.debug(f"User found by email: {email} (ID: {result.id})")
        else:
            logger.debug(f"No user found with email: {email}")
        return result

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users"""
        logger.debug(f"Querying active users: skip={skip}, limit={limit}")
        statement = select(User).where(User.is_active).offset(skip).limit(limit)
        results = list(self.session.exec(statement).all())
        logger.debug(f"Retrieved {len(results)} active users")
        return results

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        logger.debug(f"Checking if email exists: {email}")
        exists = self.get_by_email(email) is not None
        logger.debug(f"Email exists check for {email}: {exists}")
        return exists
