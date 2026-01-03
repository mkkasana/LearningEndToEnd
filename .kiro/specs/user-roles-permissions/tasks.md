# Implementation Plan: User Roles and Permissions

## Overview

This plan implements a three-level role-based permission system (User/Superuser/Admin) to replace the current binary `is_superuser` approach. The implementation follows an incremental approach, starting with the enum and model changes, then updating dependencies, and finally adding the migration.

## Tasks

- [x] 1. Create UserRole enum
  - [x] 1.1 Create `backend/app/enums/user_role.py` with UserRole enum
    - Define enum with values: USER, SUPERUSER, ADMIN
    - Implement `get_hierarchy_level()` class method returning numeric levels (1, 2, 3)
    - Implement `has_permission(required_role)` method for hierarchy checks
    - _Requirements: 1.1, 2.1_

  - [x] 1.2 Write property test for role hierarchy
    - **Property 3: Role Hierarchy Permission**
    - Test that has_permission correctly enforces admin > superuser > user
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

- [x] 2. Update User model and schemas
  - [x] 2.1 Update `backend/app/db_models/user.py`
    - Import UserRole enum
    - Replace `is_superuser: bool = False` with `role: UserRole = Field(default=UserRole.USER)`
    - Add `@property is_user` for backward compatibility (returns True if role is USER)
    - Add `@property is_superuser` for backward compatibility (returns True if role is SUPERUSER)
    - Add `@property is_admin` (returns True if role is ADMIN)
    - _Requirements: 1.2, 1.3, 1.4_

  - [x] 2.2 Update `backend/app/schemas/user.py`
    - Import UserRole enum
    - Update UserBase to use `role: UserRole = UserRole.USER` instead of `is_superuser`
    - Add `UserRoleUpdate` schema with single `role: UserRole` field
    - Update UserPublic to include role field
    - _Requirements: 1.2, 5.4_

  - [x] 2.3 Write property test for default role assignment
    - **Property 2: Default Role Assignment**
    - Test that users created without role get UserRole.USER
    - **Validates: Requirements 1.3**

- [x] 3. Checkpoint - Verify model changes
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update authentication dependencies
  - [x] 4.1 Update `backend/app/api/deps.py`
    - Import UserRole enum
    - Update `get_current_active_superuser` to check `current_user.role.has_permission(UserRole.SUPERUSER)`
    - Add new `get_current_active_admin` dependency that checks `current_user.role.has_permission(UserRole.ADMIN)`
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 4.2 Write property test for dependency role validation
    - **Property 4: Dependency Role Validation**
    - Test get_current_active_superuser allows superuser and admin, denies user
    - Test get_current_active_admin allows only admin
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [x] 5. Update database initialization
  - [x] 5.1 Update `backend/app/core/db.py`
    - Import UserRole enum
    - Update init_db to create first user with `role=UserRole.ADMIN` instead of `is_superuser=True`
    - _Requirements: 4.1, 4.2_

  - [x] 5.2 Write property test for init_db idempotence
    - **Property 5: Init DB Idempotence**
    - Test that calling init_db multiple times creates exactly one admin user
    - **Validates: Requirements 4.3**

- [x] 6. Add role management API endpoint
  - [x] 6.1 Add role update endpoint to `backend/app/api/routes/users.py`
    - Add PATCH `/users/{user_id}/role` endpoint
    - Use `get_current_active_admin` dependency
    - Prevent admin from changing their own role
    - Return updated user
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 6.2 Write property test for admin role management
    - **Property 6: Admin Role Management**
    - Test admin can change other users' roles
    - Test superuser cannot change roles (403)
    - Test admin cannot change own role
    - **Validates: Requirements 5.1, 5.2, 5.3**

- [x] 7. Checkpoint - Verify API changes
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Create database migration
  - [x] 8.1 Create Alembic migration script
    - Add `role` column with default 'user'
    - Migrate existing data: `is_superuser=True` → `role='superuser'`
    - Remove `is_superuser` column
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 8.2 Write property test for migration role conversion
    - **Property 8: Migration Role Conversion**
    - Test that is_superuser=True converts to superuser role
    - Test that is_superuser=False converts to user role
    - **Validates: Requirements 6.1, 6.2**

- [x] 9. Update existing route dependencies
  - [x] 9.1 Review and update routes using `get_current_active_superuser`
    - All the route were superuser-protected should be migrated to admin user protection.
    - There should not be any route for supre user, Either User or Admin protected only.
    - _Requirements: 3.2, 3.3_

- [x] 10. Update user service
  - [x] 10.1 Update `backend/app/services/user_service.py`
    - Update create_user to handle role field
    - Add update_user_role method for role changes
    - _Requirements: 1.3, 5.1_

- [ ] 11. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.
  - Run full test suite to verify backward compatibility

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- The migration (task 8) should be run after all code changes are deployed
