"""CRUD operations - backward compatibility wrapper around services."""

from sqlmodel import Session

from app.db_models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user."""
    service = UserService(session)
    return service.create_user(user_create)


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Get user by email."""
    service = UserService(session)
    return service.get_user_by_email(email)


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update user."""
    service = UserService(session)
    return service.update_user(db_user, user_in)


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate user."""
    service = UserService(session)
    user = service.get_user_by_email(email)
    if not user:
        return None
    if not service.verify_password(password, user.hashed_password):
        return None
    return user
