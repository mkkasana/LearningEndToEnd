from uuid import UUID

from sqlmodel import Session

from app.core.security import get_password_hash, verify_password
from app.db_models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for user business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID"""
        return self.user_repo.get_by_id(user_id)

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""
        return self.user_repo.get_by_email(email)

    def get_users(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """Get paginated list of users with total count"""
        users = self.user_repo.get_all(skip=skip, limit=limit)
        count = self.user_repo.count()
        return users, count

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user with hashed password"""
        user = User(
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
            is_active=user_create.is_active,
            is_superuser=user_create.is_superuser,
            full_name=user_create.full_name,
        )
        return self.user_repo.create(user)

    def update_user(self, user: User, user_update: UserUpdate) -> User:
        """Update user information"""
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Handle password separately
        if "password" in update_data:
            password = update_data.pop("password")
            update_data["hashed_password"] = get_password_hash(password)
        
        user.sqlmodel_update(update_data)
        return self.user_repo.update(user)

    def delete_user(self, user: User) -> None:
        """Delete a user"""
        self.user_repo.delete(user)

    def email_exists(self, email: str, exclude_user_id: UUID | None = None) -> bool:
        """Check if email exists, optionally excluding a specific user"""
        existing_user = self.user_repo.get_by_email(email)
        if not existing_user:
            return False
        if exclude_user_id and existing_user.id == exclude_user_id:
            return False
        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return verify_password(plain_password, hashed_password)

    def update_password(self, user: User, new_password: str) -> User:
        """Update user password"""
        user.hashed_password = get_password_hash(new_password)
        return self.user_repo.update(user)
