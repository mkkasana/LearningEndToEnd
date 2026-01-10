# Implementation Plan: Assume Person Role

## Overview

This implementation adds the "Assume Person Role" feature for elevated users (SuperUser/Admin) to act on behalf of persons they created. The foundation (person-specific APIs, ActivePersonContext, permission utility) is already complete from the Person Context API Refactor.

## Tasks

- [x] 1. Backend: Add can-assume endpoint and schemas
  - [x] 1.1 Create `app/schemas/person/person_assume.py` with CanAssumeResponse schema
    - Define `can_assume: bool`, `reason: str | None`, `person_name: str | None`
    - _Requirements: 2.1, 2.4_
  - [x] 1.2 Add `GET /api/v1/persons/{person_id}/can-assume` endpoint
    - Check user has SUPERUSER or ADMIN role
    - Check person.created_by_user_id matches current_user.id
    - Return CanAssumeResponse with appropriate reason if denied
    - _Requirements: 1.1, 1.2, 2.1, 2.4_
  - [ ]* 1.3 Write property test for role-based access control
    - **Property 1: Role-Based Access Control**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**
  - [ ]* 1.4 Write property test for creator-only assumption
    - **Property 2: Creator-Only Assumption**
    - **Validates: Requirements 2.1, 2.4**

- [x] 2. Checkpoint - Backend API complete
  - Ensure can-assume endpoint works correctly
  - Run backend tests
  - Ask the user if questions arise

- [x] 3. Frontend: Extend ActivePersonContext for assumed person
  - [x] 3.1 Update `ActivePersonContext.tsx` to support assumed person state
    - Add `assumedPerson`, `primaryPerson`, `isAssuming` to context state
    - Read assumed person from sessionStorage on mount
    - Validate assumed person still exists via can-assume API
    - _Requirements: 2.2, 2.3, 3.5, 7.2_
  - [x] 3.2 Add `assumePerson()` function to context
    - Call can-assume API to validate
    - Store in sessionStorage on success
    - Update context state
    - _Requirements: 2.2, 2.3_
  - [x] 3.3 Add `returnToPrimary()` function to context
    - Clear sessionStorage
    - Reset context to primary person
    - _Requirements: 4.2, 4.3_
  - [x] 3.4 Add `clearAssumedPerson()` on logout
    - Hook into logout flow to clear sessionStorage
    - _Requirements: 3.1_
  - [ ]* 3.5 Write property test for session scope invariant
    - **Property 3: Session Scope Invariant**
    - **Validates: Requirements 3.1, 3.2**
  - [ ]* 3.6 Write property test for return to primary idempotence
    - **Property 6: Return to Primary Idempotence**
    - **Validates: Requirements 4.2, 4.3**

- [x] 4. Frontend: Add canAssume helper based on user role
  - [x] 4.1 Create utility to check if current user can assume roles
    - Check user.is_superuser or user.is_admin (role >= 1)
    - Export from context or as separate hook
    - _Requirements: 1.1, 1.3_

- [x] 5. Checkpoint - Context updates complete
  - Verify context correctly manages assumed person state
  - Verify sessionStorage persistence works
  - Ask the user if questions arise

- [x] 6. Frontend: Regenerate OpenAPI client
  - [x] 6.1 Run `npm run generate-client` to pick up can-assume endpoint
    - Verify `canAssumePerson` method is available in PersonService
    - _Requirements: 2.1_

- [x] 7. Frontend: Create AssumeRoleButton component
  - [x] 7.1 Create `src/components/Family/AssumeRoleButton.tsx`
    - Accept personId, personName, createdByUserId props
    - Only render if user canAssume AND createdByUserId matches current user
    - Call assumePerson() on click
    - Show loading state during API call
    - _Requirements: 6.1, 6.2, 6.4_
  - [x] 7.2 Style button to fit family tree card design
    - Use existing button styles from the project
    - _Requirements: 6.1_

- [x] 8. Frontend: Create ActivePersonIndicator component
  - [x] 8.1 Create `src/components/Family/ActivePersonIndicator.tsx`
    - Show banner when isAssuming is true
    - Display assumed person name and "Return to Primary" button
    - Always show primary person name for reference
    - _Requirements: 2.5, 4.1, 4.4_
  - [x] 8.2 Style indicator as a prominent banner
    - Use warning/info color to indicate assumed state
    - _Requirements: 2.5_

- [x] 9. Frontend: Integrate assume controls into family tree
  - [x] 9.1 Add AssumeRoleButton to person cards in family tree
    - Import and render in PersonCard or equivalent component
    - Pass person data to button
    - _Requirements: 6.1, 6.2_
  - [x] 9.2 Add ActivePersonIndicator to family tree view
    - Show at top of family tree when assuming
    - _Requirements: 2.5, 4.1_
  - [x] 9.3 Update family tree to center on active person
    - Use activePerson.id from context instead of primaryPerson.id
    - Re-center when active person changes
    - _Requirements: 5.4, 6.3_
  - [x] 9.4 Show "Return to Primary" on primary person's card when assuming
    - Replace "Assume Role" with "Return to Primary" on own card
    - _Requirements: 6.5_

- [x] 10. Checkpoint - UI integration complete
  - Verify assume button appears on created persons
  - Verify indicator shows when assuming
  - Verify tree re-centers on assumed person
  - Ask the user if questions arise

- [x] 11. Frontend: Handle invalid session fallback
  - [x] 11.1 Add validation on context mount for stale assumed person
    - If can-assume returns false, clear sessionStorage and fall back to primary
    - Handle deleted person gracefully
    - _Requirements: 7.2, 7.3_
  - [ ]* 11.2 Write property test for invalid session fallback
    - **Property 7: Invalid Session Fallback**
    - **Validates: Requirements 7.2, 7.3**

- [x] 12. Backend: Add audit logging for assume actions
  - [x] 12.1 Log when user assumes a person role
    - Include user_id, assumed_person_id, timestamp
    - Use existing logging infrastructure
    - _Requirements: 7.4_

- [x] 13. Final checkpoint
  - Ensure all tests pass
  - Verify end-to-end flow: login → assume → add relative → return to primary
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property-based tests
- The foundation (person-specific APIs, ActivePersonContext, validate_person_access) is already complete
- sessionStorage is used for assumed person to ensure it clears on tab close
- The can-assume endpoint provides server-side validation before allowing assume
