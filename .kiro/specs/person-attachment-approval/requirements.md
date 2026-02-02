# Requirements Document: Person Attachment Approval System

## Introduction

This feature implements a person attachment approval system that prevents duplicate Person records when new users sign up. When a user signs up and their details match an existing Person record (created by another user in their family tree), the new user can request to "attach" to that existing Person instead of creating a duplicate. The original creator must approve or deny the attachment request.

This is Phase 1 of a two-phase implementation. Phase 1 focuses on the approval infrastructure (backend tables, APIs, and approval UI). Phase 2 will modify the signup/complete-profile flow to use this system.

## Glossary

- **Attachment_Request**: A request from a new user to link their account to an existing Person record created by another user
- **Requester**: The new user who wants to attach to an existing Person record
- **Approver**: The user who originally created the Person record and must approve/deny the attachment
- **Target_Person**: The existing Person record that the requester wants to attach to
- **Temp_Person**: The temporary Person record created during signup (marked as inactive)
- **Person_Active_Status**: A boolean flag indicating whether a Person record is active and visible in searches

## Requirements

### Requirement 1: Person Active Status Field

**User Story:** As a system administrator, I want Person records to have an active status, so that temporary or pending persons are not visible in searches and family trees.

#### Acceptance Criteria

1. THE Person table SHALL include an `is_active` boolean field with a default value of `True`
2. WHEN a new Person is created during user signup, THE System SHALL set `is_active` to `False`
3. WHEN searching for persons (matching, family tree, contributions), THE System SHALL exclude persons where `is_active` is `False`
4. WHEN a user completes their profile without attachment, THE System SHALL set their Person's `is_active` to `True`
5. WHEN an attachment request is approved, THE System SHALL NOT modify the target Person's `is_active` status (it remains as-is)

### Requirement 2: Attachment Request Data Model

**User Story:** As a developer, I want a database table to store attachment requests, so that the system can track and manage pending approvals.

#### Acceptance Criteria

1. THE System SHALL create a `person_attachment_request` table with the following fields:
   - `id` (UUID, primary key)
   - `requester_user_id` (UUID, foreign key to user, the user requesting attachment)
   - `requester_person_id` (UUID, foreign key to person, the temp person created during signup)
   - `target_person_id` (UUID, foreign key to person, the existing person to attach to)
   - `approver_user_id` (UUID, foreign key to user, the user who created target_person)
   - `status` (ENUM: PENDING, APPROVED, DENIED, CANCELLED)
   - `created_at` (datetime)
   - `resolved_at` (datetime, nullable)
   - `resolved_by_user_id` (UUID, foreign key to user, nullable)
2. THE System SHALL enforce that a user can have only one PENDING attachment request at a time
3. THE System SHALL enforce that `target_person_id` references a Person where `user_id` is NULL (no existing user linked)

### Requirement 3: Create Attachment Request API

**User Story:** As a new user, I want to create an attachment request, so that I can link my account to an existing Person record.

#### Acceptance Criteria

1. THE System SHALL provide a `POST /api/v1/attachment-requests` endpoint
2. WHEN creating an attachment request, THE System SHALL accept `target_person_id` in the request body
3. WHEN creating an attachment request, THE System SHALL automatically set `requester_user_id` to the current user
4. WHEN creating an attachment request, THE System SHALL automatically set `requester_person_id` to the current user's Person record
5. WHEN creating an attachment request, THE System SHALL automatically set `approver_user_id` to the `created_by_user_id` of the target Person
6. WHEN creating an attachment request, THE System SHALL set `status` to PENDING
7. IF the current user already has a PENDING attachment request, THE System SHALL return a 400 error
8. IF the target Person already has a `user_id` set, THE System SHALL return a 400 error
9. IF the target Person's `created_by_user_id` equals the current user, THE System SHALL return a 400 error (cannot attach to own creation)

### Requirement 4: List Pending Requests for Approver

**User Story:** As a user who has created family members, I want to see attachment requests for persons I created, so that I can approve or deny them.

#### Acceptance Criteria

1. THE System SHALL provide a `GET /api/v1/attachment-requests/to-approve` endpoint
2. WHEN listing requests to approve, THE System SHALL return only requests where `approver_user_id` equals the current user
3. WHEN listing requests to approve, THE System SHALL return only requests where `status` is PENDING
4. WHEN listing requests to approve, THE System SHALL include requester details: name, date of birth, gender
5. WHEN listing requests to approve, THE System SHALL include requester's address information (formatted string)
6. WHEN listing requests to approve, THE System SHALL include requester's religion information (formatted string)
7. WHEN listing requests to approve, THE System SHALL include target Person details: name, date of birth
8. THE System SHALL sort results by `created_at` descending (newest first)

### Requirement 5: Get My Pending Request

**User Story:** As a new user with a pending attachment request, I want to see my request status, so that I know if I'm waiting for approval.

#### Acceptance Criteria

1. THE System SHALL provide a `GET /api/v1/attachment-requests/my-pending` endpoint
2. WHEN getting my pending request, THE System SHALL return the current user's PENDING request if one exists
3. WHEN getting my pending request, THE System SHALL return 404 if no pending request exists
4. WHEN getting my pending request, THE System SHALL include target Person details: name, date of birth, gender
5. WHEN getting my pending request, THE System SHALL include approver information (for display purposes)

### Requirement 6: Approve Attachment Request

**User Story:** As an approver, I want to approve an attachment request, so that the new user can be linked to the Person I created.

#### Acceptance Criteria

1. THE System SHALL provide a `POST /api/v1/attachment-requests/{id}/approve` endpoint
2. WHEN approving a request, THE System SHALL verify the current user is the `approver_user_id`
3. WHEN approving a request, THE System SHALL verify the request status is PENDING
4. WHEN approving a request, THE System SHALL:
   - Set the target Person's `user_id` to the `requester_user_id`
   - Set the target Person's `is_primary` to `True`
   - Delete the requester's temporary Person record and all associated metadata (address, religion, etc.)
   - Update the request `status` to APPROVED
   - Set `resolved_at` to current timestamp
   - Set `resolved_by_user_id` to current user
5. WHEN approval is complete, THE System SHALL return success response
6. IF the request is not found or not PENDING, THE System SHALL return appropriate error

### Requirement 7: Deny Attachment Request

**User Story:** As an approver, I want to deny an attachment request, so that I can reject users who are not the real person.

#### Acceptance Criteria

1. THE System SHALL provide a `POST /api/v1/attachment-requests/{id}/deny` endpoint
2. WHEN denying a request, THE System SHALL verify the current user is the `approver_user_id`
3. WHEN denying a request, THE System SHALL verify the request status is PENDING
4. WHEN denying a request, THE System SHALL:
   - Delete the requester's temporary Person record and all associated metadata
   - Delete the requester's User record
   - Update the request `status` to DENIED
   - Set `resolved_at` to current timestamp
   - Set `resolved_by_user_id` to current user
5. WHEN denial is complete, THE System SHALL return success response
6. IF the request is not found or not PENDING, THE System SHALL return appropriate error

### Requirement 8: Cancel Attachment Request

**User Story:** As a new user, I want to cancel my attachment request, so that I can go back and modify my details or choose a different person.

#### Acceptance Criteria

1. THE System SHALL provide a `POST /api/v1/attachment-requests/{id}/cancel` endpoint
2. WHEN cancelling a request, THE System SHALL verify the current user is the `requester_user_id`
3. WHEN cancelling a request, THE System SHALL verify the request status is PENDING
4. WHEN cancelling a request, THE System SHALL:
   - Update the request `status` to CANCELLED
   - Set `resolved_at` to current timestamp
   - Set `resolved_by_user_id` to current user (the requester)
5. WHEN cancellation is complete, THE System SHALL return success response
6. THE System SHALL NOT delete any Person or User records when cancelling (user goes back to previous step)

### Requirement 9: User Approvals Sidebar Navigation

**User Story:** As a user, I want to access pending approval requests from the sidebar, so that I can easily manage attachment requests.

#### Acceptance Criteria

1. THE System SHALL add a "User Approvals" menu item to the sidebar navigation
2. WHEN displaying the sidebar, THE System SHALL position "User Approvals" after "My Contributions"
3. THE System SHALL use an appropriate icon (e.g., UserCheck or ClipboardCheck) for the menu item
4. WHEN a user clicks "User Approvals", THE System SHALL navigate to the `/user-approvals` route
5. THE System SHALL display a badge with the count of pending requests (if count > 0)

### Requirement 10: User Approvals List Page

**User Story:** As a user, I want to see a list of pending attachment requests, so that I can review and act on them.

#### Acceptance Criteria

1. THE System SHALL create a new route at `/user-approvals` for the approvals page
2. WHEN the approvals page loads, THE System SHALL display a page header with title "User Approvals"
3. WHEN the approvals page loads, THE System SHALL fetch and display all pending requests for the current user
4. WHEN displaying requests, THE System SHALL show each request in a card format with:
   - Requester's name, date of birth, gender
   - Requester's address (formatted)
   - Requester's religion (formatted)
   - Target Person's name and date of birth
   - Request creation date
5. WHEN the page is loading, THE System SHALL display a loading indicator
6. WHEN there are no pending requests, THE System SHALL display an empty state with a helpful message

### Requirement 11: Approval Action Dialog

**User Story:** As an approver, I want to view full details and take action on an attachment request, so that I can make an informed decision.

#### Acceptance Criteria

1. WHEN a user clicks on a request card, THE System SHALL open a detail dialog/panel
2. THE detail dialog SHALL display complete requester information:
   - Full name (first, middle, last)
   - Date of birth
   - Gender
   - Full address details
   - Full religion details
3. THE detail dialog SHALL display target Person information:
   - Full name
   - Date of birth
   - When the Person was created
4. THE detail dialog SHALL provide an "Approve" button
5. THE detail dialog SHALL provide a "Deny" button
6. WHEN the user clicks "Approve", THE System SHALL call the approve API and show success/error feedback
7. WHEN the user clicks "Deny", THE System SHALL show a confirmation dialog before calling the deny API
8. WHEN an action is completed, THE System SHALL close the dialog and refresh the list

### Requirement 12: Responsive Design

**User Story:** As a user, I want the approvals page to work well on different screen sizes, so that I can manage approvals on any device.

#### Acceptance Criteria

1. WHEN viewed on desktop, THE System SHALL display request cards in a grid layout (2-3 columns)
2. WHEN viewed on tablet, THE System SHALL display request cards in a 2-column layout
3. WHEN viewed on mobile, THE System SHALL display request cards in a single column layout
4. THE System SHALL ensure all text and buttons are readable at all screen sizes

## Technical Notes

### Database Migration

- Add `is_active` boolean field to `person` table with default `True`
- Create `person_attachment_request` table with appropriate indexes
- Create enum type for request status

### API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/attachment-requests` | Create new attachment request |
| GET | `/api/v1/attachment-requests/to-approve` | List requests to approve |
| GET | `/api/v1/attachment-requests/my-pending` | Get my pending request |
| POST | `/api/v1/attachment-requests/{id}/approve` | Approve a request |
| POST | `/api/v1/attachment-requests/{id}/deny` | Deny a request |
| POST | `/api/v1/attachment-requests/{id}/cancel` | Cancel my request |

### Frontend Routes

- New route: `/user-approvals`
- Route file: `frontend/src/routes/_layout/user-approvals.tsx`

### Cascade Deletion

When deleting a Person record (on approve or deny), the system must also delete:
- `person_address` records
- `person_religion` records
- `person_relationship` records (if any)
- `person_life_event` records (if any)
- `person_metadata` records (if any)
- `person_profession` records (if any)

## Future Enhancements (Phase 2)

1. Modify `/complete-profile` flow to add duplicate check step
2. Add matching step UI (reuse existing matching service)
3. Add "Pending Approval" step UI
4. Update signup to set Person `is_active=False`
5. Activate Person when profile completed without attachment
6. Allow modification of basic info in complete-profile flow
