# Requirements Document

## Introduction

This feature enables elevated users (SuperUser/Admin) to "assume" the role of any Person record they have created, allowing them to add direct relatives on behalf of that person. This solves the limitation where users can only add their own direct relatives (parents, spouse, children), preventing them from building multi-generational family trees. With this feature, a user can assume their Father's role to add Grandfather, then assume Grandfather's role to add Great-Grandfather, and so on indefinitely.

The assume role action is integrated directly into the family tree UI - users click an "Assume Role" button on any Person card they created to switch context. The assumed role is session-scoped - when a user logs out and back in, they return to their primary Person context.

## Dependencies

This feature depends on the **Person Context API Refactor** spec (`.kiro/specs/person-context-api-refactor/`), which must be completed first. That spec:
- Refactors APIs to accept explicit `person_id` parameters
- Creates the `ActivePersonContext` in the frontend
- Establishes the permission validation utility

This feature extends the `ActivePersonContext` to support assuming different persons.

## Glossary

- **User**: An authenticated account holder who can log into the system
- **Person**: An individual in the family tree (may or may not have a User account)
- **Primary_Person**: The Person record directly linked to a User via `user_id` field (the user's own identity)
- **Assumed_Person**: A Person record the user is temporarily "acting as" to manage their relatives
- **Active_Person_Context**: The currently active Person (either Primary_Person or Assumed_Person) used for family operations
- **Session**: The browser/client session that persists until logout or browser close
- **Direct_Relative**: A person with immediate family relationship (Parent, Spouse, Child, Sibling)
- **User_Role**: Permission level - USER (level 0), SUPERUSER (level 1), ADMIN (level 10)
- **Elevated_User**: A user with SUPERUSER or ADMIN role (permission level >= 1)
- **Person_Card**: The UI component displaying a Person's information in the family tree view

## Requirements

### Requirement 1: Role-Based Feature Access

**User Story:** As a system administrator, I want the assume role feature restricted to elevated users (SuperUser/Admin), so that regular users cannot access this advanced functionality.

#### Acceptance Criteria

1. THE System SHALL only allow Elevated_Users (SUPERUSER or ADMIN role) to access the assume person feature
2. IF a USER role attempts to access assume person functionality, THEN THE System SHALL reject the request with a 403 Forbidden error
3. WHEN displaying the UI, THE System SHALL hide assume person controls from USER role accounts
4. THE System SHALL validate user role on both frontend (UI visibility) and backend (API authorization)

### Requirement 2: Assume Person Role

**User Story:** As an elevated user, I want to assume the role of any Person I have created, so that I can add direct relatives on their behalf and build a multi-generational family tree.

#### Acceptance Criteria

1. WHEN an Elevated_User requests to assume a Person role, THE System SHALL verify the Person was created by that user (`created_by_user_id` matches)
2. WHEN an Elevated_User successfully assumes a Person role, THE System SHALL store the assumed Person ID in the frontend session state
3. WHEN an Elevated_User assumes a Person role, THE System SHALL update the Active_Person_Context to the Assumed_Person
4. IF an Elevated_User attempts to assume a Person they did not create, THEN THE System SHALL reject the request with an authorization error
5. WHEN an Elevated_User is in assumed role, THE System SHALL clearly indicate which Person they are acting as in the UI

### Requirement 3: Session-Scoped Assumed Role

**User Story:** As a user, I want my assumed role to be temporary and session-based, so that I always return to my primary identity when I log back in.

#### Acceptance Criteria

1. WHEN a user logs out, THE System SHALL clear the assumed Person context from the session
2. WHEN a user logs in, THE System SHALL set the Active_Person_Context to their Primary_Person
3. WHEN a browser session ends (tab/window close), THE System SHALL clear the assumed Person context
4. THE System SHALL NOT persist the assumed Person role to the database or backend storage
5. WHEN a user refreshes the page, THE System SHALL maintain the assumed role within the same session

### Requirement 4: Return to Primary Person

**User Story:** As a user, I want to easily return to my primary Person context, so that I can manage my own direct relatives after working on behalf of others.

#### Acceptance Criteria

1. WHEN a user is in an assumed role, THE System SHALL provide a clear option to return to Primary_Person
2. WHEN a user selects "Return to Primary", THE System SHALL set Active_Person_Context back to Primary_Person
3. WHEN a user returns to Primary_Person, THE System SHALL clear the assumed Person from session state
4. THE System SHALL always display the Primary_Person identity alongside any assumed role for reference

### Requirement 5: Family Operations with Active Person Context

**User Story:** As a user in an assumed role, I want all family member operations to work relative to the assumed Person, so that I can add their direct relatives seamlessly.

#### Acceptance Criteria

1. WHEN a user adds a family member while in assumed role, THE System SHALL create the relationship relative to the Assumed_Person
2. WHEN a user views "My Relationships" while in assumed role, THE System SHALL show relationships of the Assumed_Person
3. WHEN a user creates a new Person as a relative, THE System SHALL set `created_by_user_id` to the actual logged-in User (not the assumed Person)
4. WHEN viewing the family tree while in assumed role, THE System SHALL center the view on the Assumed_Person

### Requirement 6: Assume Role from Family Tree UI

**User Story:** As a user viewing the family tree, I want to click an "Assume Role" button on any Person card I created, so that I can quickly switch context and add their relatives without leaving the tree view.

#### Acceptance Criteria

1. WHEN rendering a Person card in the family tree, THE System SHALL display an "Assume Role" button if the user created that Person (`created_by_user_id` matches)
2. WHEN a user clicks "Assume Role" on a Person card, THE System SHALL switch the Active_Person_Context to that Person
3. WHEN the Active_Person_Context changes, THE System SHALL re-render the family tree centered on the newly assumed Person
4. THE System SHALL NOT display the "Assume Role" button on Person cards the user did not create
5. WHEN a user is viewing their Primary_Person's card while in assumed role, THE System SHALL show "Return to Primary" instead of "Assume Role"

### Requirement 7: Permission Validation

**User Story:** As a system administrator, I want the assume role feature to enforce proper permissions, so that users cannot access or modify data they don't own.

#### Acceptance Criteria

1. THE System SHALL validate on every family operation that the Active_Person_Context is either the user's Primary_Person OR a Person they created
2. IF a user's session contains an invalid assumed Person ID, THEN THE System SHALL fall back to Primary_Person
3. WHEN a Person record is deleted, THE System SHALL handle any sessions assuming that Person gracefully (fall back to Primary)
4. THE System SHALL log assume role actions for audit purposes
