# Design Document: User Roles and Permissions

## Overview

This design introduces a three-level role-based permission system to replace the current binary `is_superuser` approach. The system will use a `UserRole` enum with values `user`, `superuser`, and `admin`, stored as a string field on the User model. Role hierarchy ensures that higher roles inherit all permissions from lower roles.

## Architecture

The role system follows a layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                    API Routes Layer                      │
│  (Uses role dependencies to protect endpoints)           │
├─────────────────────────────────────────────────────────┤
│                  Dependencies Layer                      │
│  get_current_user → get_current_active_superuser        │
│                   → get_current_active_admin             │
├─────────────────────────────────────────────────────────┤
│                    Enum Layer                            │
│  UserRole enum with hierarchy logic                      │
├─────────────────────────────────────────────────────────┤
│                   Model Layer                            │
│  User model with role field                              │
└─────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### UserRole Enum

Location: `backend/app/enums/user_role.py`

```python
from enum import Enum


class UserRole(str, Enum):
    """User role levels with hierarchical permissions."""
    
    USER = "user"
    SUPERUSER = "superuser"
    ADMIN = "admin"
    
    @classmethod
    def get_hierarchy_level(cls, role: "UserRole") -> int:
        """Return numeric hierarchy level for comparison."""
        hierarchy = {
            cls.USER: 1,
            cls.SUPERUSER: 2,
            cls.ADMIN: 3,
        }
        return hierarchy[role]
    
    def has_permission(self, required_role: "UserRole") -> bool:
        """Check if this role has permission for the required role level."""
        return self.get_hierarchy_level(self) >= self.get_hierarchy_level(required_role)
```

### Updated User Model

Location: `backend/app/db_models/user.py`

```python
import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from app.enums.user_role import UserRole

if TYPE_CHECKING:
    from app.db_models.item import Item


class User(SQLModel, table=True):
    """User database model"""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    hashed_password: str
    is_active: bool = True
    role: UserRole = Field(default=UserRole.USER)
    full_name: str | None = Field(default=None, max_length=255)

    # Relationships
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    
    # Computed properties for backward compatibility
    @property
    def is_superuser(self) -> bool:
        """Backward compatibility: returns True if role is superuser or admin."""
        return self.role in (UserRole.SUPERUSER, UserRole.ADMIN)
    
    @property
    def is_admin(self) -> bool:
        """Returns True if user has admin role."""
        return self.role == UserRole.ADMIN
```

### Updated Dependencies

Location: `backend/app/api/deps.py`

```python
from app.enums.user_role import UserRole

def get_current_active_superuser(current_user: CurrentUser) -> User:
    """Require superuser or admin role."""
    if not current_user.role.has_permission(UserRole.SUPERUSER):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_active_admin(current_user: CurrentUser) -> User:
    """Require admin role only."""
    if not current_user.role.has_permission(UserRole.ADMIN):
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
```

### Updated User Schemas

Location: `backend/app/schemas/user.py`

```python
from app.enums.user_role import UserRole

class UserBase(SQLModel):
    """Shared user properties"""
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    role: UserRole = UserRole.USER
    full_name: str | None = Field(default=None, max_length=255)


class UserRoleUpdate(SQLModel):
    """Schema for updating user role (admin only)"""
    role: UserRole
```

## Data Models

### Database Schema Change

The User table will be modified:

| Column | Type | Change |
|--------|------|--------|
| role | VARCHAR(20) | NEW - stores "user", "superuser", or "admin" |
| is_superuser | BOOLEAN | REMOVED after migration |

### Migration Strategy

1. Add new `role` column with default "user"
2. Migrate existing data: `is_superuser=True` → `role="superuser"`
3. Remove `is_superuser` column

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Role Enum Completeness

*For any* value in the UserRole enum, it must be one of exactly three values: "user", "superuser", or "admin", and the enum must contain no other values.

**Validates: Requirements 1.1**

### Property 2: Default Role Assignment

*For any* user creation where no role is specified, the resulting user must have role equal to UserRole.USER.

**Validates: Requirements 1.3**

### Property 3: Role Hierarchy Permission

*For any* two roles A and B, if A.has_permission(B) returns True, then the hierarchy level of A must be greater than or equal to the hierarchy level of B. Specifically:
- admin.has_permission(superuser) = True
- admin.has_permission(user) = True
- superuser.has_permission(user) = True
- superuser.has_permission(admin) = False
- user.has_permission(superuser) = False
- user.has_permission(admin) = False

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 4: Dependency Role Validation

*For any* user with a given role:
- get_current_active_superuser allows the user if and only if role is superuser or admin
- get_current_active_admin allows the user if and only if role is admin
- When denied, the HTTP status code is 403 and message is "The user doesn't have enough privileges"

**Validates: Requirements 3.2, 3.3, 3.4**

### Property 5: Init DB Idempotence

*For any* database state, calling init_db multiple times must result in exactly one admin user with the configured email, never creating duplicates.

**Validates: Requirements 4.3**

### Property 6: Admin Role Management

*For any* role change operation:
- If the requester is admin and target is a different user, the operation succeeds
- If the requester is superuser, the operation fails with 403
- If the requester is admin and target is themselves, the operation fails

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 7: Role Validation

*For any* role update request, if the provided role value is not one of "user", "superuser", or "admin", the request must be rejected with a validation error.

**Validates: Requirements 5.4**

### Property 8: Migration Role Conversion

*For any* existing user during migration:
- If is_superuser was True, the new role must be "superuser"
- If is_superuser was False, the new role must be "user"

**Validates: Requirements 6.1, 6.2**

## Error Handling

| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| User lacks required role | 403 | "The user doesn't have enough privileges" |
| Invalid role value in request | 422 | Pydantic validation error |
| Admin tries to change own role | 403 | "Cannot change your own role" |
| Non-admin tries to change roles | 403 | "The user doesn't have enough privileges" |

## Testing Strategy

### Unit Tests

- Test UserRole enum values and hierarchy methods
- Test User model role property and computed is_superuser/is_admin properties
- Test dependency functions with mocked users of each role

### Property-Based Tests

Using `hypothesis` library for Python property-based testing:

1. **Role hierarchy property**: Generate all role combinations and verify has_permission logic
2. **Default role property**: Generate random user data without role, verify default
3. **Dependency validation property**: Generate users with random roles, verify dependency behavior
4. **Role validation property**: Generate random strings, verify only valid roles accepted

### Integration Tests

- Test protected endpoints with users of each role level
- Test role update API with various requester/target combinations
- Test init_db creates admin user correctly

### Test Configuration

- Minimum 100 iterations per property test
- Each property test tagged with: **Feature: user-roles-permissions, Property {number}: {property_text}**
