# Requirements Document

## Introduction

This feature adds marital status tracking at the person level. The marital status field allows users to indicate whether a person is single, married, divorced, widowed, or separated. This information is collected during profile completion as part of the "Personal Information" step and can be updated later. The marital status is essential for partner matching features and family tree context.

## Glossary

- **Person**: An individual in the system, either linked to a user account or a family member without an account
- **MaritalStatus**: An enumeration representing a person's current relationship status stored directly on the Person table
- **Profile_Completion**: The onboarding flow at `/complete-profile` that collects required information from new users
- **Profile_Service**: Backend service that checks profile completion status
- **Personal_Information_Step**: The first step in profile completion that shows person details and allows editing marital status

## Requirements

### Requirement 1: Marital Status Data Model

**User Story:** As a system administrator, I want marital status stored at the person level, so that each person's relationship status can be tracked independently.

#### Acceptance Criteria

1. THE Person table SHALL include a marital_status column that stores a MaritalStatus enum value
2. THE MaritalStatus enum SHALL include values: UNKNOWN, SINGLE, MARRIED, DIVORCED, WIDOWED, SEPARATED
3. WHEN a new person is created via signup, THE marital_status field SHALL default to UNKNOWN
4. THE marital_status field SHALL NOT be nullable - it SHALL always have a valid enum value

### Requirement 2: Profile Completion Integration

**User Story:** As a new user, I want to provide my marital status during profile completion, so that my profile is complete and I can access the application.

#### Acceptance Criteria

1. THE Personal_Information_Step in Profile_Completion SHALL be transformed from read-only to editable
2. THE Personal_Information_Step SHALL display the user's current details (name, gender, date of birth) as read-only
3. THE Personal_Information_Step SHALL include an "Edit Marital Status" button to update marital status
4. WHEN marital_status is UNKNOWN, THE Profile_Service SHALL include "marital_status" in the missing_fields list
5. WHEN marital_status is UNKNOWN, THE Profile_Service SHALL return has_marital_status as false
6. WHEN marital_status is any value other than UNKNOWN, THE Profile_Service SHALL return has_marital_status as true
7. WHEN all required fields are complete (person, address, religion, marital_status), THE Profile_Service SHALL return is_complete as true
8. THE marital status selection dialog SHALL display all MaritalStatus options except UNKNOWN with user-friendly labels

### Requirement 3: Marital Status API

**User Story:** As a frontend developer, I want API endpoints to get and update marital status, so that users can manage their marital status information.

#### Acceptance Criteria

1. THE System SHALL provide a GET endpoint to retrieve available marital status options with labels
2. THE System SHALL provide a PATCH endpoint to update a person's marital status
3. WHEN updating marital status, THE System SHALL validate that the provided value is a valid MaritalStatus enum value
4. IF an invalid marital status value is provided, THEN THE System SHALL return a 400 error with a descriptive message
5. THE PersonPublic schema SHALL include the marital_status field in API responses
6. THE marital status options endpoint SHALL NOT include UNKNOWN as a selectable option

### Requirement 4: Person Schema Updates

**User Story:** As a developer, I want the person schemas to include marital status, so that the field is properly serialized in API responses.

#### Acceptance Criteria

1. THE PersonPublic schema SHALL include marital_status as a required string field
2. THE PersonUpdate schema SHALL include marital_status as an optional field for updates
3. THE PersonCreate schema SHALL include marital_status with default value UNKNOWN
4. WHEN serializing a person, THE System SHALL include the marital_status enum value

### Requirement 5: Database Migration

**User Story:** As a system administrator, I want existing person records to be migrated with a default marital status, so that the system remains consistent.

#### Acceptance Criteria

1. THE database migration SHALL add the marital_status column to the person table
2. THE migration SHALL set marital_status to UNKNOWN for all existing person records
3. THE migration SHALL set the column as NOT NULL with default value UNKNOWN
