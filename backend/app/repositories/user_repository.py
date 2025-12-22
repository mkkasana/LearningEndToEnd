from sqlmodel import Session, select

from app.db_models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User data access"""

    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email address"""
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all active users"""
        statement = select(User).where(User.is_active == True).offset(skip).limit(limit)
        return list(self.session.exec(statement).all())

    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.get_by_email(email) is not None
