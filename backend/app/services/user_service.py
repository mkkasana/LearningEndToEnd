import logging
from uuid import UUID

from sqlmodel import Session

from app.core.security import get_password_hash, verify_password
from app.db_models.user import User
from app.enums.user_role import UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    """Service for user business logic"""

    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    def get_user_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID"""
        logger.debug(f"Fetching user by ID: {user_id}")
        user = self.user_repo.get_by_id(user_id)
        if user:
            logger.debug(f"User found: {user.email} (ID: {user_id})")
        else:
            logger.debug(f"User not found with ID: {user_id}")
        return user

    def get_user_by_email(self, email: str) -> User | None:
        """Get user by email"""
        logger.debug(f"Fetching user by email: {email}")
        user = self.user_repo.get_by_email(email)
        if user:
            logger.debug(f"User found: {email} (ID: {user.id})")
        else:
            logger.debug(f"User not found with email: {email}")
        return user

    def get_users(self, skip: int = 0, limit: int = 100) -> tuple[list[User], int]:
        """Get paginated list of users with total count"""
        logger.debug(f"Fetching users list: skip={skip}, limit={limit}")
        users = self.user_repo.get_all(skip=skip, limit=limit)
        count = self.user_repo.count()
        logger.info(f"Retrieved {len(users)} users out of {count} total")
        return users, count

    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user with hashed password"""
        logger.info(f"Creating new user: {user_create.email}")
        user = User(
            email=user_create.email,
            hashed_password=get_password_hash(user_create.password),
            is_active=user_create.is_active,
            role=user_create.role,
            full_name=user_create.full_name,
        )
        created_user = self.user_repo.create(user)
        logger.info(
            f"User created successfully: {created_user.email} (ID: {created_user.id}), "
            f"role={created_user.role.value}, is_active={created_user.is_active}"
        )
        return created_user

    def update_user(self, user: User, user_update: UserUpdate) -> User:
        """Update user information"""
        logger.info(f"Updating user: {user.email} (ID: {user.id})")
        update_data = user_update.model_dump(exclude_unset=True)

        # Log what fields are being updated (excluding password)
        update_fields = [k for k in update_data.keys() if k != "password"]
        if update_fields:
            logger.debug(f"Updating fields for user {user.email}: {update_fields}")

        # Handle password separately
        if "password" in update_data:
            logger.info(f"Password update requested for user: {user.email}")
            password = update_data.pop("password")
            update_data["hashed_password"] = get_password_hash(password)

        user.sqlmodel_update(update_data)
        updated_user = self.user_repo.update(user)
        logger.info(
            f"User updated successfully: {updated_user.email} (ID: {updated_user.id})"
        )
        return updated_user

    def delete_user(self, user: User) -> None:
        """Delete a user"""
        logger.warning(f"Deleting user: {user.email} (ID: {user.id})")
        self.user_repo.delete(user)
        logger.info(f"User deleted successfully: {user.email} (ID: {user.id})")

    def email_exists(self, email: str, exclude_user_id: UUID | None = None) -> bool:
        """Check if email exists, optionally excluding a specific user"""
        logger.debug(f"Checking if email exists: {email}")
        existing_user = self.user_repo.get_by_email(email)
        if not existing_user:
            logger.debug(f"Email does not exist: {email}")
            return False
        if exclude_user_id and existing_user.id == exclude_user_id:
            logger.debug(f"Email exists but excluded from check: {email}")
            return False
        logger.debug(f"Email already exists: {email}")
        return True

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        logger.debug("Verifying password")
        is_valid = verify_password(plain_password, hashed_password)
        if not is_valid:
            logger.debug("Password verification failed")
        return is_valid

    def update_password(self, user: User, new_password: str) -> User:
        """Update user password"""
        logger.info(f"Updating password for user: {user.email} (ID: {user.id})")
        user.hashed_password = get_password_hash(new_password)
        updated_user = self.user_repo.update(user)
        logger.info(f"Password updated successfully for user: {user.email}")
        return updated_user

    def update_user_role(self, user: User, new_role: UserRole) -> User:
        """Update user role
        
        Args:
            user: The user to update
            new_role: The new role to assign
            
        Returns:
            The updated user
        """
        old_role = user.role
        logger.info(
            f"Updating role for user: {user.email} (ID: {user.id}) "
            f"from {old_role.value} to {new_role.value}"
        )
        user.role = new_role
        updated_user = self.user_repo.update(user)
        logger.info(
            f"Role updated successfully for user: {updated_user.email} "
            f"(ID: {updated_user.id}), new role: {updated_user.role.value}"
        )
        return updated_user
