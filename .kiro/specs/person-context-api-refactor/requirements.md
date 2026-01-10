# Requirements Document

## Introduction

This feature refactors the person-related APIs to accept `person_id` as an explicit parameter from the frontend instead of deriving it from the logged-in user's session. This foundational change enables future features like "Assume Person Role" where users can act on behalf of other persons they created.

Currently, many `/me` endpoints derive the person context from `current_user.id` in the backend. After this refactor, the frontend will maintain an "Active Person Context" and pass the `person_id` explicitly to APIs that need it.

## Glossary

- **User**: An authenticated account holder who can log into the system
- **Person**: An individual in the family tree (may or may not have a User account)
- **Primary_Person**: The Person record directly linked to a User via `user_id` field
- **Active_Person_Context**: Frontend state holding the currently active Person ID for operations
- **Me_Endpoint**: API endpoint using `/me` path that derives person from session (e.g., `/api/v1/person/me/relationships`)
- **Person_Endpoint**: API endpoint using `/{person_id}` path that accepts explicit person ID

## Requirements

### Requirement 1: Active Person Context State

**User Story:** As a frontend developer, I want a centralized state for the active person context, so that all components can access and use the correct person ID for API calls.

#### Acceptance Criteria

1. THE System SHALL provide a React hook `useActivePersonContext` that returns the current active person ID
2. WHEN a user logs in, THE System SHALL initialize the Active_Person_Context to the user's Primary_Person ID
3. THE System SHALL store the Active_Person_Context in React state (not sessionStorage yet - that's for assume role feature)
4. WHEN the Active_Person_Context changes, THE System SHALL trigger re-renders in consuming components
5. THE System SHALL provide the active person's full details (name, id) through the context

### Requirement 2: Backend API Refactoring - Relationships

**User Story:** As a backend developer, I want relationship APIs to accept explicit person_id, so that the frontend can specify which person to operate on.

#### Acceptance Criteria

1. THE System SHALL provide `POST /api/v1/persons/{person_id}/relationships` to create relationships for a specific person
2. THE System SHALL provide `GET /api/v1/persons/{person_id}/relationships` to get relationships for a specific person
3. THE System SHALL provide `GET /api/v1/persons/{person_id}/relationships/with-details` to get detailed relationships
4. THE System SHALL validate that the requesting user has permission to access the specified person
5. WHEN a user requests operations on a person they created, THE System SHALL allow the operation
6. WHEN a user requests operations on their own Primary_Person, THE System SHALL allow the operation

### Requirement 3: Backend API Refactoring - Addresses

**User Story:** As a backend developer, I want address APIs to accept explicit person_id, so that the frontend can manage addresses for any person in the family tree.

#### Acceptance Criteria

1. THE System SHALL provide `GET /api/v1/persons/{person_id}/addresses` to get addresses for a specific person
2. THE System SHALL provide `POST /api/v1/persons/{person_id}/addresses` to create address for a specific person
3. THE System SHALL provide `PATCH /api/v1/persons/{person_id}/addresses/{address_id}` to update address
4. THE System SHALL provide `DELETE /api/v1/persons/{person_id}/addresses/{address_id}` to delete address
5. THE System SHALL validate user has permission to manage the specified person's addresses

### Requirement 4: Backend API Refactoring - Professions

**User Story:** As a backend developer, I want profession APIs to accept explicit person_id, so that the frontend can manage professions for any person in the family tree.

#### Acceptance Criteria

1. THE System SHALL provide `GET /api/v1/persons/{person_id}/professions` to get professions for a specific person
2. THE System SHALL provide `POST /api/v1/persons/{person_id}/professions` to create profession for a specific person
3. THE System SHALL provide `PATCH /api/v1/persons/{person_id}/professions/{profession_id}` to update profession
4. THE System SHALL provide `DELETE /api/v1/persons/{person_id}/professions/{profession_id}` to delete profession
5. THE System SHALL validate user has permission to manage the specified person's professions

### Requirement 5: Backend API Refactoring - Metadata

**User Story:** As a backend developer, I want metadata APIs to accept explicit person_id, so that the frontend can manage metadata for any person in the family tree.

#### Acceptance Criteria

1. THE System SHALL provide `GET /api/v1/persons/{person_id}/metadata` to get metadata for a specific person
2. THE System SHALL provide `POST /api/v1/persons/{person_id}/metadata` to create metadata for a specific person
3. THE System SHALL provide `PATCH /api/v1/persons/{person_id}/metadata` to update metadata
4. THE System SHALL provide `DELETE /api/v1/persons/{person_id}/metadata` to delete metadata
5. THE System SHALL validate user has permission to manage the specified person's metadata

### Requirement 6: Permission Validation

**User Story:** As a system administrator, I want all person-specific APIs to validate permissions consistently, so that users can only access data they're authorized to manage.

#### Acceptance Criteria

1. THE System SHALL allow operations when `person.user_id == current_user.id` (user's own person)
2. THE System SHALL allow operations when `person.created_by_user_id == current_user.id` (person created by user)
3. THE System SHALL allow operations when user has ADMIN role (admin override)
4. IF none of the above conditions are met, THEN THE System SHALL return 403 Forbidden
5. THE System SHALL implement permission checking in a reusable utility function

### Requirement 7: Frontend API Client Updates

**User Story:** As a frontend developer, I want the API client to use the new person-specific endpoints, so that all API calls pass the active person context.

#### Acceptance Criteria

1. THE System SHALL update all relationship API calls to use `/{person_id}/relationships` endpoints
2. THE System SHALL update all address API calls to use `/{person_id}/addresses` endpoints
3. THE System SHALL update all profession API calls to use `/{person_id}/professions` endpoints
4. THE System SHALL update all metadata API calls to use `/{person_id}/metadata` endpoints
5. WHEN making API calls, THE System SHALL pass the person_id from Active_Person_Context

### Requirement 8: Backward Compatibility

**User Story:** As a user, I want the application to work exactly as before after the refactor, so that my workflow is not disrupted.

#### Acceptance Criteria

1. THE System SHALL maintain existing `/me` endpoints as aliases that use the user's Primary_Person
2. WHEN using the application normally, THE System SHALL behave identically to before the refactor
3. THE System SHALL not require any user action to continue using the application
4. THE System SHALL preserve all existing data and relationships
