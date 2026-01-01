"""User role enum with hierarchical permissions."""

from enum import Enum


class UserRole(str, Enum):
    """User role levels with hierarchical permissions.
    
    Roles are defined with numeric levels for permission hierarchy:
    - USER: level 0 (basic access)
    - SUPERUSER: level 1 (elevated privileges)
    - ADMIN: level 10 (full system access)
    
    Gaps in levels (2-9) are reserved for future role additions.
    """

    USER = "user"
    SUPERUSER = "superuser"
    ADMIN = "admin"

    @classmethod
    def get_hierarchy_level(cls, role: "UserRole") -> int:
        """Return numeric hierarchy level for comparison.
        
        Higher levels have more privileges. Gaps allow future role additions.
        
        Args:
            role: The UserRole to get the level for
            
        Returns:
            Numeric level: USER=0, SUPERUSER=1, ADMIN=10
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
        to the required role's level.
        
        Args:
            required_role: The minimum role required for the action
            
        Returns:
            True if this role meets or exceeds the required level
        """
        return self.get_hierarchy_level(self) >= self.get_hierarchy_level(required_role)
