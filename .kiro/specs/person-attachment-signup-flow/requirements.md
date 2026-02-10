# Requirements Document: Person Attachment Signup Flow (Phase 2)

## Introduction

This feature modifies the signup and complete-profile flow to integrate with the Person Attachment Approval System (Phase 1). When a new user signs up, the system will check for potential duplicate Person records. If matches are found, the user can request to attach to an existing Person instead of creating a duplicate. The user must wait for approval from the original creator before gaining full access.

This is Phase 2 of the Person Attachment Approval System. Phase 1 (already implemented) provides the approval infrastructure (backend tables, APIs, and approval UI).

## Glossary

- **Attachment_Request**: A request from a new user to link their account to an existing Person record created by another user
- **Requester**: The new user who wants to attach to an existing Person record
- **Approver**: The user who originally created the Person record and must approve/deny the attachment
- **Target_Person**: The existing Person record that the requester wants to attach to
- **Temp_Person**: The temporary Person record created during signup (marked as inactive with `is_active=False`)
- **Duplicate_Check_Step**: A new step in the complete-profile flow that searches for matching persons
- **Pending_Approval_Step**: A waiting screen shown when user has submitted an attachment request
- **Profile_Completion_Flow**: The multi-step onboarding process at `/complete-profile`

## Requirements

### Requirement 1: Signup Creates Inactive Person

**User Story:** As a system administrator, I want new user signups to create inactive Person records, so that temporary persons don't appear in searches until verified.

#### Acceptance Criteria

1. WHEN a new user signs up, THE System SHALL create a Person record with `is_active` set to `False`
2. WHEN a Person is created with `is_active=False`, THE System SHALL exclude it from all search results
3. THE System SHALL NOT modify the existing signup API contract (same request/response format)

### Requirement 2: Profile Completion Flow Restructure

**User Story:** As a new user, I want the profile completion flow to guide me through checking for duplicates, so that I can link to my existing Person record if one exists.

#### Acceptance Criteria

1. THE System SHALL restructure the complete-profile flow into the following steps:
   - Step 1: Personal Information (existing - read-only display)
   - Step 2: Address Information (existing)
   - Step 3: Religion Information (existing)
   - Step 4: Marital Status (existing)
   - Step 5: Duplicate Check (NEW)
2. WHEN all basic profile steps (1-4) are complete, THE System SHALL automatically proceed to the Duplicate Check step
3. THE System SHALL display a progress indicator showing current step and completion status

### Requirement 3: Duplicate Check Step

**User Story:** As a new user, I want to see if my Person record already exists in the system, so that I can request to link to it instead of creating a duplicate.

#### Acceptance Criteria

1. THE System SHALL display a "Check for Existing Records" step after basic profile completion
2. WHEN the duplicate check step loads, THE System SHALL automatically search for matching persons using:
   - User's name (first, middle, last)
   - User's address (country, state, district)
   - User's religion
   - User's gender
3. WHEN matches are found, THE System SHALL display them in a list with:
   - Person's full name
   - Date of birth
   - Match score percentage
   - Address display string
   - Religion display string
4. WHEN no matches are found, THE System SHALL display a message "No matching records found"
5. THE System SHALL provide a "This is me" button for each matching person
6. THE System SHALL provide a "None of these are me" button to skip attachment
7. WHEN a user clicks "This is me", THE System SHALL create an attachment request and navigate to the Pending Approval step
8. WHEN a user clicks "None of these are me", THE System SHALL activate their Person record and complete the profile

### Requirement 4: Pending Approval Waiting Step

**User Story:** As a new user who has requested attachment, I want to see my request status, so that I know I'm waiting for approval.

#### Acceptance Criteria

1. WHEN a user has a pending attachment request, THE System SHALL display a "Pending Approval" screen
2. THE Pending Approval screen SHALL display:
   - Message explaining the user is waiting for approval
   - Target person's name and date of birth
   - Request submission date
   - Approver information (if available)
3. THE System SHALL provide a "Cancel Request" button
4. WHEN the user clicks "Cancel Request", THE System SHALL:
   - Call the cancel attachment request API
   - Navigate back to the Duplicate Check step
5. THE System SHALL poll for request status changes every 30 seconds
6. WHEN the request is approved, THE System SHALL automatically redirect to the dashboard
7. WHEN the request is denied, THE System SHALL display an error message and log the user out

### Requirement 5: Profile Completion Status Update

**User Story:** As a developer, I want the profile completion status to reflect the new flow, so that the system correctly determines when a user can access the main application.

#### Acceptance Criteria

1. THE Profile Completion Status API SHALL include a new field `has_duplicate_check` indicating whether the duplicate check step is complete
2. THE Profile Completion Status API SHALL include a new field `has_pending_attachment_request` indicating whether the user has a pending request
3. THE System SHALL consider a profile complete when:
   - `has_person` is true AND
   - `has_address` is true AND
   - `has_religion` is true AND
   - `has_marital_status` is true AND
   - `has_duplicate_check` is true AND
   - `has_pending_attachment_request` is false
4. WHEN a user has a pending attachment request, THE System SHALL redirect them to the Pending Approval step

### Requirement 6: Activate Person on Profile Completion

**User Story:** As a new user who completes their profile without attachment, I want my Person record to become active, so that family members can find and connect with me.

#### Acceptance Criteria

1. WHEN a user clicks "None of these are me" in the Duplicate Check step, THE System SHALL set their Person's `is_active` to `True`
2. WHEN a user's attachment request is approved, THE System SHALL NOT modify the target Person's `is_active` (it should already be active)
3. THE System SHALL provide an API endpoint to activate the current user's Person record

### Requirement 7: Backend API for Duplicate Check

**User Story:** As a developer, I want a dedicated API endpoint for the duplicate check, so that the frontend can search for matching persons during profile completion.

#### Acceptance Criteria

1. THE System SHALL provide a `GET /api/v1/profile/duplicate-check` endpoint
2. WHEN called, THE endpoint SHALL use the current user's Person data to search for matches
3. THE endpoint SHALL return a list of matching persons with:
   - Person ID
   - Full name
   - Date of birth
   - Match score
   - Address display
   - Religion display
4. THE endpoint SHALL exclude:
   - The current user's own Person record
   - Persons that already have a linked user account
   - Inactive persons
5. THE endpoint SHALL only return persons with a match score >= 40%

### Requirement 8: Complete Profile Without Attachment

**User Story:** As a new user, I want to complete my profile without attaching to an existing record, so that I can start using the application immediately.

#### Acceptance Criteria

1. THE System SHALL provide a `POST /api/v1/profile/complete-without-attachment` endpoint
2. WHEN called, THE endpoint SHALL:
   - Set the current user's Person `is_active` to `True`
   - Mark the duplicate check step as complete
3. THE endpoint SHALL return success response with updated profile status
4. IF the user already has a pending attachment request, THE endpoint SHALL return a 400 error

### Requirement 9: Redirect Logic Updates

**User Story:** As a user, I want to be redirected to the correct step based on my profile status, so that I can continue where I left off.

#### Acceptance Criteria

1. WHEN a user with incomplete profile accesses the main application, THE System SHALL redirect to `/complete-profile`
2. WHEN a user with a pending attachment request accesses the main application, THE System SHALL redirect to the Pending Approval step
3. WHEN a user's attachment request is approved, THE System SHALL redirect to the dashboard on next access
4. WHEN a user's attachment request is denied, THE System SHALL log them out and show an error message

### Requirement 10: UI/UX for Duplicate Check Step

**User Story:** As a new user, I want a clear and intuitive interface for the duplicate check, so that I can easily identify if my record exists.

#### Acceptance Criteria

1. THE Duplicate Check step SHALL display a clear heading explaining the purpose
2. THE System SHALL show a loading indicator while searching for matches
3. WHEN matches are found, THE System SHALL display them in a card-based layout
4. Each match card SHALL be clickable to select "This is me"
5. THE System SHALL highlight the match score with visual indicators (e.g., color coding)
6. THE "None of these are me" button SHALL be prominently displayed below the matches
7. THE System SHALL display helpful text explaining what happens with each choice

### Requirement 11: Responsive Design for New Steps

**User Story:** As a user, I want the new profile completion steps to work well on all devices, so that I can complete my profile on any screen size.

#### Acceptance Criteria

1. WHEN viewed on desktop, THE Duplicate Check step SHALL display match cards in a grid layout
2. WHEN viewed on mobile, THE Duplicate Check step SHALL display match cards in a single column
3. THE Pending Approval step SHALL be readable and usable on all screen sizes
4. All buttons and interactive elements SHALL be appropriately sized for touch interaction on mobile

## Technical Notes

### API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/profile/duplicate-check` | Search for matching persons |
| POST | `/api/v1/profile/complete-without-attachment` | Complete profile without attachment |
| GET | `/api/v1/profile/completion-status` | Updated to include new fields |

### Profile Completion Status Response (Updated)

```json
{
  "is_complete": false,
  "has_person": true,
  "has_address": true,
  "has_religion": true,
  "has_marital_status": true,
  "has_duplicate_check": false,
  "has_pending_attachment_request": false,
  "pending_request_id": null,
  "missing_fields": ["duplicate_check"]
}
```

### Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Signup    │────▶│  Complete   │────▶│  Duplicate  │────▶│  Dashboard  │
│  (inactive  │     │   Profile   │     │    Check    │     │  (active)   │
│   person)   │     │  (steps 1-4)│     │  (step 5)   │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘     └─────────────┘
                                               │
                                               │ "This is me"
                                               ▼
                                        ┌─────────────┐
                                        │   Pending   │
                                        │  Approval   │
                                        │   (wait)    │
                                        └──────┬──────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                              ▼                ▼                ▼
                        ┌──────────┐    ┌──────────┐    ┌──────────┐
                        │ Approved │    │  Denied  │    │ Cancelled│
                        │ (active) │    │ (logout) │    │ (back to │
                        └──────────┘    └──────────┘    │  check)  │
                                                        └──────────┘
```

### Dependencies

- Phase 1 Person Attachment Approval System (already implemented)
- PersonMatchingService (already implemented)
- AttachmentRequestService (already implemented)

