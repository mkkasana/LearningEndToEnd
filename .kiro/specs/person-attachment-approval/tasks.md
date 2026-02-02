# Implementation Plan: Person Attachment Approval System

## Overview

This implementation plan covers Phase 1 of the Person Attachment Approval System. The tasks are organized to build the feature incrementally, starting with database changes, then backend services, and finally the frontend UI.

## Tasks

- [x] 1. Database Schema Updates
  - [x] 1.1 Add `is_active` field to Person model
    - Update `backend/app/db_models/person/person.py`
    - Add `is_active: bool = Field(default=True, description="Whether person is active and visible in searches")`
    - _Requirements: 1.1_
  - [x] 1.2 Create AttachmentRequestStatus enum
    - Create `backend/app/enums/attachment_request_status.py`
    - Define enum with values: PENDING, APPROVED, DENIED, CANCELLED
    - _Requirements: 2.1_
  - [x] 1.3 Create PersonAttachmentRequest model
    - Create `backend/app/db_models/person/person_attachment_request.py`
    - Define all fields as per design document
    - _Requirements: 2.1_
  - [x] 1.4 Create Alembic migration
    - Generate migration for is_active column and attachment_request table
    - Include indexes for efficient queries
    - Run migration on both app and app_test databases
    - _Requirements: 1.1, 2.1_

- [x] 2. Checkpoint - Verify database changes
  - Ensure migration runs successfully
  - Verify Person model has is_active field
  - Verify person_attachment_request table exists
  - Ask the user if questions arise

- [x] 3. Backend Schemas
  - [x] 3.1 Create attachment request schemas
    - Create `backend/app/schemas/attachment_request.py`
    - Define AttachmentRequestCreate, AttachmentRequestPublic
    - Define AttachmentRequestWithDetails, MyPendingRequestResponse
    - _Requirements: 3.1, 4.1, 5.1_
  - [x] 3.2 Update Person schema if needed
    - Ensure PersonPublic includes is_active field
    - _Requirements: 1.1_

- [x] 4. Backend Repository Layer
  - [x] 4.1 Create AttachmentRequestRepository
    - Create `backend/app/repositories/attachment_request_repository.py`
    - Implement create() method
    - Implement get_by_id() method
    - Implement get_pending_by_requester() method
    - Implement get_pending_by_approver() method
    - Implement count_pending_by_approver() method
    - Implement update() method
    - _Requirements: 2.2, 3.1, 4.1, 5.1_
  - [x] 4.2 Write unit tests for repository
    - Test CRUD operations
    - Test filtering by status and user
    - _Requirements: 2.2, 4.2, 4.3_

- [x] 5. Backend Service Layer
  - [x] 5.1 Create AttachmentRequestService
    - Create `backend/app/services/attachment_request_service.py`
    - Implement create_request() with validations
    - Implement get_requests_to_approve() with details
    - Implement get_my_pending_request()
    - Implement get_pending_count()
    - _Requirements: 3.2-3.9, 4.2-4.8, 5.2-5.5_
  - [x] 5.2 Implement approve_request() method
    - Validate authorization and status
    - Link user to target person
    - Delete temp person with cascade
    - Update request status
    - _Requirements: 6.2-6.5_
  - [x] 5.3 Implement deny_request() method
    - Validate authorization and status
    - Delete temp person with cascade
    - Delete requester user
    - Update request status
    - _Requirements: 7.2-7.5_
  - [x] 5.4 Implement cancel_request() method
    - Validate authorization and status
    - Update request status only
    - _Requirements: 8.2-8.5_
  - [x] 5.5 Implement _delete_person_with_metadata() helper
    - Delete person_address records
    - Delete person_religion records
    - Delete person_relationship records
    - Delete person_life_event records
    - Delete person_metadata records
    - Delete person_profession records
    - Delete person record
    - Use transaction for atomicity
    - _Requirements: 6.4, 7.4_
  - [x] 5.6 Write unit tests for service
    - Test create_request validations
    - Test approve/deny/cancel logic
    - Test cascade deletion
    - _Requirements: 3.7-3.9, 6.2-6.4, 7.2-7.4, 8.2-8.4_

- [x] 6. Checkpoint - Verify service layer
  - Ensure all service methods work correctly
  - Run unit tests
  - Ask the user if questions arise

- [x] 7. Backend API Routes
  - [x] 7.1 Create attachment requests router
    - Create `backend/app/api/routes/attachment_requests.py`
    - Implement POST / endpoint (create request)
    - Implement GET /to-approve endpoint
    - Implement GET /my-pending endpoint
    - Implement GET /pending-count endpoint
    - _Requirements: 3.1, 4.1, 5.1_
  - [x] 7.2 Implement action endpoints
    - Implement POST /{id}/approve endpoint
    - Implement POST /{id}/deny endpoint
    - Implement POST /{id}/cancel endpoint
    - _Requirements: 6.1, 7.1, 8.1_
  - [x] 7.3 Register router in main API
    - Update `backend/app/api/main.py`
    - Add attachment_requests router with prefix
    - _Requirements: 3.1_
  - [x] 7.4 Write integration tests for API
    - Test all endpoints with valid/invalid data
    - Test authorization checks
    - Test error responses
    - _Requirements: 3.7-3.9, 6.2-6.6, 7.2-7.6, 8.2-8.6_

- [x] 8. Update Person Search to Exclude Inactive
  - [x] 8.1 Update PersonMatchingService
    - Modify search queries to filter is_active=True
    - _Requirements: 1.3_
  - [x] 8.2 Update PersonSearchService (if exists)
    - Modify search queries to filter is_active=True
    - _Requirements: 1.3_
  - [x] 8.3 Update family tree queries
    - Ensure inactive persons are excluded
    - _Requirements: 1.3_
  - [x] 8.4 Write property test for inactive exclusion
    - **Property 2: Inactive Person Search Exclusion**
    - **Validates: Requirements 1.3**

- [x] 9. Checkpoint - Verify backend complete
  - Test all API endpoints manually or via tests
  - Verify inactive persons excluded from searches
  - Ask the user if questions arise

- [x] 10. Frontend: Generate OpenAPI Client
  - [x] 10.1 Rebuild backend and regenerate client
    - Run `docker compose build --no-cache backend`
    - Run `docker compose up -d`
    - Run `npm run generate-client` in frontend folder
    - Verify new AttachmentRequestService is generated
    - _Requirements: 3.1, 4.1, 5.1, 6.1, 7.1, 8.1_

- [x] 11. Frontend: Sidebar Navigation
  - [x] 11.1 Add User Approvals menu item
    - Update `frontend/src/components/Sidebar/AppSidebar.tsx`
    - Add menu item after "My Contributions"
    - Use UserCheck icon from lucide-react
    - Navigate to /user-approvals route
    - _Requirements: 9.1, 9.2, 9.3, 9.4_
  - [x] 11.2 Add pending count badge
    - Fetch count from /pending-count API
    - Display badge when count > 0
    - _Requirements: 9.5_

- [x] 12. Frontend: User Approvals Page
  - [x] 12.1 Create route file
    - Create `frontend/src/routes/_layout/user-approvals.tsx`
    - Set up route with createFileRoute
    - _Requirements: 10.1_
  - [x] 12.2 Create UserApprovalsPage component
    - Create `frontend/src/components/UserApprovals/UserApprovalsPage.tsx`
    - Implement page header with title
    - Fetch pending requests using useQuery
    - Display loading state
    - Display empty state when no requests
    - _Requirements: 10.2, 10.3, 10.5, 10.6_
  - [x] 12.3 Create ApprovalRequestCard component
    - Create `frontend/src/components/UserApprovals/ApprovalRequestCard.tsx`
    - Display requester name, DOB, gender
    - Display requester address and religion
    - Display target person name and DOB
    - Display request date
    - Handle click to open detail dialog
    - _Requirements: 10.4_
  - [x] 12.4 Implement responsive grid layout
    - 2-3 columns on desktop
    - 2 columns on tablet
    - 1 column on mobile
    - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [x] 13. Frontend: Approval Detail Dialog
  - [x] 13.1 Create ApprovalDetailDialog component
    - Create `frontend/src/components/UserApprovals/ApprovalDetailDialog.tsx`
    - Display complete requester information
    - Display complete target person information
    - _Requirements: 11.1, 11.2, 11.3_
  - [x] 13.2 Implement action buttons
    - Add Approve button (primary)
    - Add Deny button (destructive)
    - _Requirements: 11.4, 11.5_
  - [x] 13.3 Implement action handlers
    - Call approve API on Approve click
    - Show confirmation dialog before deny
    - Call deny API after confirmation
    - Show success/error toast
    - Close dialog and refresh list on success
    - _Requirements: 11.6, 11.7, 11.8_

- [x] 14. Checkpoint - Verify frontend complete
  - Test sidebar navigation and badge
  - Test approvals list page
  - Test approval/deny actions
  - Ask the user if questions arise

- [x] 15. Property-Based Tests
  - [x] 15.1 Write property test for one pending request constraint
    - **Property 4: One Pending Request Per User**
    - **Validates: Requirements 2.2, 3.7**
  - [x] 15.2 Write property test for target person validation
    - **Property 5: Target Person Must Not Have User**
    - **Validates: Requirements 2.3, 3.8**
  - [x] 15.3 Write property test for auto-population
    - **Property 7: Create Request Auto-Population**
    - **Validates: Requirements 3.2-3.6**
  - [x] 15.4 Write property test for approve side effects
    - **Property 12: Approve Side Effects**
    - **Validates: Requirements 6.4**
  - [x] 15.5 Write property test for deny side effects
    - **Property 13: Deny Side Effects**
    - **Validates: Requirements 7.4**
  - [x] 15.6 Write property test for cancel preserves records
    - **Property 14: Cancel Preserves Records**
    - **Validates: Requirements 8.4, 8.5**

- [x] 16. Final Checkpoint
  - Run all tests (unit, integration, property)
  - Verify complete user flow works
  - Ensure all requirements are met
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Remember to apply migrations to BOTH app and app_test databases
- Rebuild backend Docker image after code changes
- Regenerate OpenAPI client after backend API changes
