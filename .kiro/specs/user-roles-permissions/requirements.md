# Requirements Document

## Introduction

This feature expands the current two-level permission system (User/Superuser) to a three-level role-based permission system (User/Superuser/Admin). This provides more granular access control, allowing different levels of administrative capabilities within the application.

## Glossary

- **User**: A standard authenticated user with basic access to their own data and public resources
- **Superuser**: An elevated user with additional privileges to manage certain system resources (e.g., professions, support tickets)
- **Admin**: The highest privilege level with full system access, including user management and system configuration
- **Role**: A classification that determines a user's permission level in the system
- **Permission_System**: The backend logic that validates and enforces role-based access control

## Requirements

### Requirement 1: Role Definition

**User Story:** As a system architect, I want to define three distinct user roles, so that the system can support granular access control.

#### Acceptance Criteria

1. THE Permission_System SHALL support exactly three roles: "user", "superuser", and "admin"
2. THE Permission_System SHALL store the role as an enumerated value on the User model
3. WHEN a new user is created without specifying a role, THE Permission_System SHALL assign the "user" role by default
4. THE Permission_System SHALL maintain backward compatibility with existing `is_superuser` boolean field during migration

### Requirement 2: Role Hierarchy

**User Story:** As a developer, I want roles to follow a clear hierarchy, so that higher roles inherit permissions from lower roles.

#### Acceptance Criteria

1. THE Permission_System SHALL enforce the hierarchy: admin > superuser > user
2. WHEN an admin performs an action requiring superuser privileges, THE Permission_System SHALL allow the action
3. WHEN a superuser performs an action requiring user privileges, THE Permission_System SHALL allow the action
4. WHEN a user performs an action requiring superuser or admin privileges, THE Permission_System SHALL deny the action with a 403 error

### Requirement 3: Role-Based Access Dependencies

**User Story:** As a developer, I want FastAPI dependencies for each role level, so that I can easily protect routes based on required permissions.

#### Acceptance Criteria

1. THE Permission_System SHALL provide a `get_current_user` dependency for authenticated user access
2. THE Permission_System SHALL provide a `get_current_active_superuser` dependency that allows superuser and admin roles
3. THE Permission_System SHALL provide a `get_current_active_admin` dependency that allows only admin role
4. WHEN a user with insufficient role accesses a protected endpoint, THE Permission_System SHALL return HTTP 403 with message "The user doesn't have enough privileges"

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
2. WHEN a superuser attempts to change a user's role, THE Permission_System SHALL deny the action with a 403 error
3. WHEN an admin attempts to change their own role, THE Permission_System SHALL deny the action to prevent self-demotion
4. THE Permission_System SHALL validate that the new role is one of the allowed values

### Requirement 6: Migration Support

**User Story:** As a developer, I want existing users to be migrated to the new role system, so that the transition is seamless.

#### Acceptance Criteria

1. WHEN migrating existing data, THE Permission_System SHALL convert `is_superuser=True` users to "superuser" role
2. WHEN migrating existing data, THE Permission_System SHALL convert `is_superuser=False` users to "user" role
3. THE Permission_System SHALL provide an Alembic migration script for the schema change
