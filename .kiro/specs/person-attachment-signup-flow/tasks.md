# Implementation Plan: Person Attachment Signup Flow (Phase 2)

## Overview

This implementation plan covers Phase 2 of the Person Attachment Approval System - integrating the attachment flow into the signup and complete-profile process. The tasks are organized to build the feature incrementally, starting with backend changes, then frontend updates.

## Tasks

- [x] 1. Backend: Update Signup to Create Inactive Person
  - [x] 1.1 Update signup endpoint in users.py
    - Modify `backend/app/api/routes/users.py`
    - Change Person creation to set `is_active=False`
    - _Requirements: 1.1_
  - [ ]* 1.2 Write property test for signup creates inactive person
    - **Property 1: Signup Creates Inactive Person**
    - **Validates: Requirements 1.1**

- [x] 2. Backend: Update Profile Completion Status Schema
  - [x] 2.1 Update ProfileCompletionStatus schema
    - Modify `backend/app/schemas/profile.py`
    - Add `has_duplicate_check: bool` field
    - Add `has_pending_attachment_request: bool` field
    - Add `pending_request_id: uuid.UUID | None` field
    - _Requirements: 5.1, 5.2_

- [x] 3. Backend: Update Profile Service
  - [x] 3.1 Update check_profile_completion method
    - Modify `backend/app/services/profile_service.py`
    - Add AttachmentRequestRepository dependency
    - Check for pending attachment request
    - Calculate has_duplicate_check based on person.is_active or pending request
    - Update is_complete logic to include new conditions
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [x] 3.2 Implement get_duplicate_matches method
    - Add method to ProfileService
    - Get user's person, address, and religion data
    - Build PersonSearchRequest from user's data
    - Call PersonMatchingService.search_matching_persons()
    - Filter out persons with linked user accounts
    - Return filtered matches
    - _Requirements: 7.2, 7.3, 7.4, 7.5_
  - [x] 3.3 Implement complete_without_attachment method
    - Add method to ProfileService
    - Check for pending attachment request (return 400 if exists)
    - Set person.is_active = True
    - Return updated profile completion status
    - _Requirements: 8.2, 8.3, 8.4_
  - [x] 3.4 Add helper methods for address/religion display
    - Implement _build_address_display() method
    - Implement _build_religion_display() method
    - _Requirements: 7.3_

- [x] 4. Backend: Add Profile API Endpoints
  - [x] 4.1 Add duplicate-check endpoint
    - Modify `backend/app/api/routes/profile.py`
    - Add `GET /duplicate-check` endpoint
    - Return list of PersonMatchResult
    - _Requirements: 7.1_
  - [x] 4.2 Add complete-without-attachment endpoint
    - Add `POST /complete-without-attachment` endpoint
    - Return ProfileCompletionStatus
    - _Requirements: 8.1_
  - [x] 4.3 Write unit tests for profile service
    - Test check_profile_completion with various states
    - Test get_duplicate_matches filtering
    - Test complete_without_attachment logic
    - _Requirements: 5.1-5.4, 7.2-7.5, 8.2-8.4_

- [ ] 5. Checkpoint - Verify backend changes ✅
  - ✅ All new endpoints implemented correctly (code verified)
  - ✅ Profile completion status has new fields (has_duplicate_check, has_pending_attachment_request, pending_request_id)
  - ✅ All 14 unit tests pass
  - ⚠️ Backend Docker container needs rebuild to expose new endpoints

- [x] 6. Property-Based Tests for Backend
  - [x]* 6.1 Write property test for profile completion status accuracy
    - **Property 2: Profile Completion Status Accuracy**
    - **Validates: Requirements 2.2, 5.1, 5.2, 5.3, 5.4**
  - [x]* 6.2 Write property test for duplicate check results filtering
    - **Property 3: Duplicate Check Results Filtering**
    - **Validates: Requirements 3.2, 7.2, 7.3, 7.4, 7.5**
  - [x]* 6.3 Write property test for complete without attachment
    - **Property 4: Complete Without Attachment Activates Person**
    - **Validates: Requirements 3.8, 6.1, 8.2, 8.3**
  - [x]* 6.4 Write property test for complete without attachment blocked
    - **Property 5: Complete Without Attachment Blocked by Pending Request**
    - **Validates: Requirements 8.4**

- [x] 7. Frontend: Generate OpenAPI Client
  - [x] 7.1 Rebuild backend and regenerate client
    - Run `docker compose build --no-cache backend`
    - Run `docker compose up -d`
    - Run `npm run generate-client` in frontend folder
    - Verify new ProfileService methods are generated
    - _Requirements: 7.1, 8.1_

- [x] 8. Frontend: Create Progress Indicator Component
  - [x] 8.1 Create ProgressIndicator component
    - Create `frontend/src/components/Profile/ProgressIndicator.tsx`
    - Display 5 steps with completion status
    - Highlight current step
    - Show checkmarks for completed steps
    - _Requirements: 2.3_

- [x] 9. Frontend: Create Match Card Component
  - [x] 9.1 Create MatchCard component
    - Create `frontend/src/components/Profile/MatchCard.tsx`
    - Display person name, DOB, address, religion
    - Display match score with color coding
    - Add "This is me" button
    - Handle click to select match
    - _Requirements: 10.3, 10.4, 10.5_

- [x] 10. Frontend: Create Duplicate Check Step Component
  - [x] 10.1 Create DuplicateCheckStep component
    - Create `frontend/src/components/Profile/DuplicateCheckStep.tsx`
    - Fetch matches using useQuery
    - Display loading state
    - Display matches in grid layout
    - Display "No matches found" when empty
    - Add "None of these are me" button
    - Handle "This is me" click (create attachment request)
    - Handle "None of these are me" click (complete without attachment)
    - _Requirements: 3.1-3.8, 10.1, 10.2, 10.6, 10.7_

- [x] 11. Frontend: Create Pending Approval Step Component
  - [x] 11.1 Create PendingApprovalStep component
    - Create `frontend/src/components/Profile/PendingApprovalStep.tsx`
    - Fetch pending request using useQuery
    - Display target person details
    - Display request submission date
    - Add "Cancel Request" button
    - Implement 30-second polling for status changes
    - Handle approval (redirect to dashboard)
    - Handle denial (show error, logout)
    - _Requirements: 4.1-4.7_

- [x] 12. Frontend: Update Complete Profile Page
  - [x] 12.1 Restructure complete-profile.tsx
    - Modify `frontend/src/routes/complete-profile.tsx`
    - Add step state management
    - Determine current step from profile status
    - Add ProgressIndicator component
    - Render appropriate step component based on state
    - Handle step transitions
    - _Requirements: 2.1, 2.2_
  - [x] 12.2 Update existing step components
    - Ensure AddressStep, ReligionStep, MaritalStatusStep work with new flow
    - Add onComplete callbacks for step transitions
    - _Requirements: 2.1_

- [x] 13. Frontend: Implement Responsive Design
  - [x] 13.1 Add responsive styles to DuplicateCheckStep
    - Grid layout: 2-3 columns on desktop, 2 on tablet, 1 on mobile
    - _Requirements: 11.1, 11.2, 11.3_
  - [x] 13.2 Add responsive styles to PendingApprovalStep
    - Ensure readable on all screen sizes
    - _Requirements: 11.4_

- [x] 14. Checkpoint - Verify frontend changes
  - Test complete profile flow with new steps
  - Test duplicate check step with matches
  - Test duplicate check step without matches
  - Test pending approval step
  - Test cancel request functionality
  - Ask the user if questions arise

- [x] 15. Integration Testing
  - [x] 15.1 Write integration tests for new endpoints
    - Test GET /profile/duplicate-check
    - Test POST /profile/complete-without-attachment
    - Test profile completion status with new fields
    - _Requirements: 7.1, 8.1, 5.1-5.4_
  - [x] 15.2 Test full signup flow
    - Signup creates inactive person
    - Complete profile steps 1-4
    - Duplicate check shows matches
    - Complete without attachment activates person
    - _Requirements: 1.1, 3.8, 6.1_

- [x] 16. Final Checkpoint
  - ✅ All unit tests pass (14 tests in test_profile_service.py)
  - ✅ All integration tests pass (28 tests in test_profile_api.py)
  - ✅ All property-based tests pass (4 tests in test_profile_service_properties.py)
  - ✅ All frontend components have no TypeScript errors
  - ⚠️ Manual testing required: Rebuild Docker images and test complete user flow
  - ⚠️ Test with existing users to verify they are not affected

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- No database migration required (Phase 1 already created necessary schema)
- Rebuild backend Docker image after code changes
- Regenerate OpenAPI client after backend API changes

