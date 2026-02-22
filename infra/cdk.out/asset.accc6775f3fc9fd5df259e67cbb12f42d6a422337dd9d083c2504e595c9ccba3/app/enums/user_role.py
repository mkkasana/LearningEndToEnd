"""User role enum with hierarchical permissions."""

from enum import Enum


class UserRole(str, Enum):
    """User role levels with hierarchical permissions.

    Hierarchy: ADMIN > SUPERUSER > USER
    Higher roles inherit all permissions from lower roles.
    """

    USER = "user"
    SUPERUSER = "superuser"
    ADMIN = "admin"

    @classmethod
    def get_hierarchy_level(cls, role: "UserRole") -> int:
        """Return numeric hierarchy level for comparison.

        Args:
            role: The UserRole to get the hierarchy level for.

        Returns:
            Numeric level: USER=0, SUPERUSER=1, ADMIN=10 (gaps allow future roles)
        """
        hierarchy = {
            cls.USER: 0,
            cls.SUPERUSER: 1,
            cls.ADMIN: 10,
        }
        return hierarchy[role]

    def has_permission(self, required_role: "UserRole") -> bool:
        """Check if this role has permission for the required role level.

        A role has permission if its hierarchy level is greater than or equal
        to the required role's hierarchy level.

        Args:
            required_role: The minimum role required for the action.

        Returns:
            True if this role has sufficient permission, False otherwise.
        """
        return self.get_hierarchy_level(self) >= self.get_hierarchy_level(required_role)
