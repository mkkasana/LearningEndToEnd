# Implementation Plan: Person Marital Status

## Overview

This implementation adds marital status tracking to the Person model, integrates it into the profile completion flow, and provides API endpoints for managing marital status. The implementation follows the existing patterns in the codebase.

## Tasks

- [x] 1. Create MaritalStatus enum
  - [x] 1.1 Create `backend/app/enums/marital_status.py` with MaritalStatus enum
    - Define enum values: UNKNOWN, SINGLE, MARRIED, DIVORCED, WIDOWED, SEPARATED
    - Add `label` property for human-readable labels
    - Add `get_selectable_options()` class method that excludes UNKNOWN
    - _Requirements: 1.2_
  - [ ]* 1.2 Write unit tests for MaritalStatus enum
    - Test all enum values exist
    - Test label property returns correct labels
    - Test get_selectable_options excludes UNKNOWN
    - **Property 1: Default Marital Status on Person Creation**
    - **Validates: Requirements 1.2**

- [x] 2. Update Person model and schemas
  - [x] 2.1 Add marital_status field to Person model
    - Add field to `backend/app/db_models/person/person.py`
    - Set default value to MaritalStatus.UNKNOWN
    - Field should be non-nullable
    - _Requirements: 1.1, 1.3, 1.4_
  - [x] 2.2 Update Person schemas
    - Add marital_status to PersonPublic schema
    - Add marital_status to PersonUpdate schema (optional)
    - Add marital_status to PersonCreate schema with default UNKNOWN
    - Update `backend/app/schemas/person/person.py`
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  - [ ]* 2.3 Write unit tests for Person schemas with marital_status
    - Test PersonPublic includes marital_status
    - Test PersonCreate defaults to UNKNOWN
    - Test PersonUpdate accepts marital_status
    - **Property 2: Marital Status Non-Nullability**
    - **Validates: Requirements 1.4, 4.1, 4.2, 4.3**

- [x] 3. Create database migration
  - [x] 3.1 Create Alembic migration for marital_status column
    - Add marital_status column to person table
    - Set default value to 'unknown'
    - Set column as NOT NULL
    - Update existing records to 'unknown'
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 4. Update ProfileService and schema
  - [x] 4.1 Update ProfileCompletionStatus schema
    - Add has_marital_status field to `backend/app/schemas/profile.py`
    - _Requirements: 2.5, 2.6_
  - [x] 4.2 Update ProfileService.check_profile_completion
    - Add marital status check (UNKNOWN = incomplete)
    - Add "marital_status" to missing_fields when UNKNOWN
    - Update is_complete logic to include has_marital_status
    - Update `backend/app/services/profile_service.py`
    - _Requirements: 2.4, 2.5, 2.6, 2.7_
  - [ ]* 4.3 Write unit tests for ProfileService marital status logic
    - Test has_marital_status is false when UNKNOWN
    - Test has_marital_status is true for non-UNKNOWN values
    - Test missing_fields includes "marital_status" when UNKNOWN
    - Test is_complete requires has_marital_status
    - **Property 3: Profile Completion Status for UNKNOWN Marital Status**
    - **Property 4: Profile Completion Status for Non-UNKNOWN Marital Status**
    - **Property 5: Profile Completeness Requires Marital Status**
    - **Validates: Requirements 2.4, 2.5, 2.6, 2.7**

- [x] 5. Checkpoint - Backend core implementation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Create marital status metadata endpoint
  - [x] 6.1 Add GET endpoint for marital status options
    - Create endpoint in metadata routes or new file
    - Return list of {value, label} objects
    - Exclude UNKNOWN from options
    - _Requirements: 3.1, 3.6_
  - [ ]* 6.2 Write integration tests for marital status endpoint
    - Test endpoint returns all options except UNKNOWN
    - Test response format includes value and label
    - **Validates: Requirements 3.1, 3.6**

- [x] 7. Update person update endpoint
  - [x] 7.1 Ensure PATCH /persons/{id} handles marital_status
    - Validate marital_status is valid enum value
    - Return 400 for invalid values
    - _Requirements: 3.2, 3.3, 3.4_
  - [ ]* 7.2 Write integration tests for person marital status update
    - Test successful update with valid values
    - Test 400 error for invalid values
    - **Property 6: Marital Status Validation on Update**
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [x] 8. Checkpoint - Backend API complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Regenerate OpenAPI client
  - [x] 9.1 Rebuild backend and regenerate frontend client
    - Run `docker compose build --no-cache backend && docker compose up -d`
    - Run `npm run generate-client` in frontend folder
    - Verify new types are generated
    - _Requirements: 3.5_

- [x] 10. Create EditMaritalStatusDialog component
  - [x] 10.1 Create `frontend/src/components/Profile/EditMaritalStatusDialog.tsx`
    - Fetch marital status options from API
    - Display select dropdown with options
    - Call PATCH endpoint to update person
    - Trigger refetch on success
    - Follow pattern of AddReligionDialog
    - _Requirements: 2.3, 2.8_

- [x] 11. Update complete-profile page
  - [x] 11.1 Update Personal Information step in complete-profile.tsx
    - Show person details (name, gender, DOB) as read-only
    - Add "Edit Marital Status" button when has_marital_status is false
    - Show current marital status when set
    - Integrate EditMaritalStatusDialog
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 12. Final checkpoint - Full integration
  - Ensure all tests pass, ask the user if questions arise.
  - Test complete profile flow end-to-end manually

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Follow the backend schema to frontend type sync process from project-settings.md
