# Requirements Document

## Introduction

This feature expands the current two-level permission system (User/Superuser) to an expandable role-based permission system. The initial roles are User, Superuser, and Admin, but the system is designed to easily accommodate additional roles in the future using numeric permission levels with gaps for expansion.

## Glossary

- **User**: A standard authenticated user with basic access to their own data and public resources (level 0)
- **Superuser**: An elevated user with additional privileges to manage certain system resources (level 1)
- **Admin**: The highest privilege level with full system access, including user management and system configuration (level 10)
- **Role**: A classification that determines a user's permission level in the system
- **Role_Level**: A numeric value representing the permission hierarchy (higher = more privileges)
- **Permission_System**: The backend logic that validates and enforces role-based access control

## Requirements

### Requirement 1: Role Definition

**User Story:** As a system architect, I want to define expandable user roles with numeric levels, so that the system can support granular access control and future role additions.

#### Acceptance Criteria

1. THE Permission_System SHALL define roles as an enum with associated numeric levels: user=0, superuser=1, admin=10
2. THE Permission_System SHALL store the role as an enumerated string value on the User model
3. THE Permission_System SHALL use numeric levels for permission comparisons to support hierarchy
4. WHEN a new user is created without specifying a role, THE Permission_System SHALL assign the "user" role (level 0) by default
5. THE Permission_System SHALL allow future role additions by using gaps in numeric levels (e.g., levels 2-9 reserved for future roles)

### Requirement 2: Role Hierarchy

**User Story:** As a developer, I want roles to follow a clear numeric hierarchy, so that higher roles automatically inherit permissions from lower roles.

#### Acceptance Criteria

1. THE Permission_System SHALL enforce hierarchy based on numeric role levels (higher level = more privileges)
2. WHEN a user with role level N performs an action requiring level M (where N >= M), THE Permission_System SHALL allow the action
3. WHEN a user with role level N performs an action requiring level M (where N < M), THE Permission_System SHALL deny the action with a 403 error
4. THE Permission_System SHALL provide a helper method to check if a user meets a minimum role level

### Requirement 3: Role-Based Access Dependencies

**User Story:** As a developer, I want FastAPI dependencies for each role level, so that I can easily protect routes based on required permissions.

#### Acceptance Criteria

1. THE Permission_System SHALL provide a `get_current_user` dependency for authenticated user access (level 0+)
2. THE Permission_System SHALL provide a `get_current_active_superuser` dependency that requires level 1+ (superuser and admin)
3. THE Permission_System SHALL provide a `get_current_active_admin` dependency that requires level 10+ (admin only)
4. THE Permission_System SHALL provide a generic `require_role_level(min_level)` dependency factory for custom role checks
5. WHEN a user with insufficient role level accesses a protected endpoint, THE Permission_System SHALL return HTTP 403 with message "The user doesn't have enough privileges"

### Requirement 4: First Admin User Creation

**User Story:** As a system administrator, I want the first admin user to be created automatically on system initialization, so that I can manage the system from the start.

#### Acceptance Criteria

1. WHEN the database is initialized, THE Permission_System SHALL create the first user with admin role using environment variables
2. THE Permission_System SHALL read `FIRST_SUPERUSER` and `FIRST_SUPERUSER_PASSWORD` environment variables for the initial admin
3. IF the first admin user already exists, THEN THE Permission_System SHALL not create a duplicate

### Requirement 5: Role Management API

**User Story:** As an admin, I want to change user roles through the API, so that I can promote or demote users as needed.

#### Acceptance Criteria

1. WHEN an admin updates a user's role, THE Permission_System SHALL allow the change
2. WHEN a non-admin attempts to change a user's role, THE Permission_System SHALL deny the action with a 403 error
3. WHEN an admin attempts to change their own role, THE Permission_System SHALL deny the action to prevent self-demotion
4. THE Permission_System SHALL validate that the new role is one of the defined enum values

### Requirement 6: Migration Support

**User Story:** As a developer, I want existing users to be migrated to the new role system, so that the transition is seamless.

#### Acceptance Criteria

1. WHEN migrating existing data, THE Permission_System SHALL convert `is_superuser=True` users to "superuser" role
2. WHEN migrating existing data, THE Permission_System SHALL convert `is_superuser=False` users to "user" role
3. THE Permission_System SHALL provide an Alembic migration script for the schema change
4. THE Permission_System SHALL deprecate the `is_superuser` field after migration (can be removed in future release)

### Requirement 7: Backward Compatibility

**User Story:** As a developer, I want the existing `is_superuser` property to continue working during transition, so that existing code doesn't break.

#### Acceptance Criteria

1. THE User model SHALL provide an `is_superuser` computed property that returns True if role level >= 1
2. THE User model SHALL provide an `is_admin` computed property that returns True if role level >= 10
3. WHEN existing code checks `user.is_superuser`, THE Permission_System SHALL return the correct value based on the new role field
