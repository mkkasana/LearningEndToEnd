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

## Bug Fixes and Enhancements (Post-Testing)

- [x] 14. Add ActivePersonIndicator to Update Family page
  - [x] 14.1 Import and add ActivePersonIndicator to family.tsx
    - Add banner at top of page when assuming
    - _Requirements: 2.5, 4.1_

- [x] 15. Add ActivePersonIndicator to Life Events page
  - [x] 15.1 Import and add ActivePersonIndicator to life-events.tsx
    - Add banner at top of page when assuming
    - _Requirements: 2.5, 4.1_

- [x] 16. Update Life Events to use active person context
  - [x] 16.1 Refactor life-events.tsx to use activePersonId from context
    - Replace getMyLifeEvents with person-specific endpoint
    - Fetch life events for assumed person when assuming
    - _Requirements: 5.1, 5.2_
  - [x] 16.2 Update AddLifeEventDialog to create events for active person
    - Pass activePersonId to create mutation
    - Events should be created for assumed person when assuming
    - _Requirements: 5.1, 5.2_
  - [x] 16.3 Update delete functionality to work with active person
    - Delete works via life_event_id (already person-agnostic)
    - Backend validates access via user_can_access_event
    - _Requirements: 5.1, 5.2_

- [x] 17. Checkpoint - All pages support assumed person
  - Verify indicator shows on Family Tree, Update Family, and Life Events
  - Verify Life Events shows assumed person's events
  - Verify creating/deleting events works for assumed person
  - Ask the user if questions arise

- [x] 18. Backend: Add person-specific discover family members endpoint
  - [x] 18.1 Add `GET /api/v1/person/{person_id}/discover-family-members` endpoint
    - Accept person_id parameter to discover for a specific person
    - Use validate_person_access to check user has permission
    - Call PersonDiscoveryService with the specified person_id instead of current_user
    - _Requirements: 5.1, 5.2_
  - [x] 18.2 Update PersonDiscoveryService to accept person_id parameter
    - Modify discover_family_members() to accept optional person_id
    - When person_id provided, use it instead of looking up by user_id
    - _Requirements: 5.1, 5.2_

- [x] 19. Backend: Add person-specific create relationship endpoint
  - [x] 19.1 Add `POST /api/v1/person/{person_id}/relationships` endpoint
    - Accept person_id parameter to create relationship for a specific person
    - Use validate_person_access to check user has permission
    - Create relationship with person_id as the source person
    - _Requirements: 5.1, 5.2_

- [x] 20. Frontend: Regenerate OpenAPI client for new endpoints
  - [x] 20.1 Run `npm run generate-client` to pick up new endpoints
    - Verify `discoverPersonFamilyMembers` method is available
    - Verify `createPersonRelationship` method is available
    - _Requirements: 5.1, 5.2_

- [x] 21. Frontend: Update DiscoverFamilyMembersDialog to use active person
  - [x] 21.1 Accept activePersonId prop in DiscoverFamilyMembersDialog
    - Pass activePersonId from parent components
    - _Requirements: 5.1, 5.2_
  - [x] 21.2 Update discovery query to use person-specific endpoint
    - When activePersonId provided, call discoverPersonFamilyMembers
    - Otherwise fall back to discoverFamilyMembers (primary person)
    - _Requirements: 5.1, 5.2_
  - [x] 21.3 Update connect mutation to use person-specific endpoint
    - When activePersonId provided, call createPersonRelationship
    - Otherwise fall back to createMyRelationship (primary person)
    - _Requirements: 5.1, 5.2_

- [x] 22. Frontend: Pass activePersonId to DiscoverFamilyMembersDialog
  - [x] 22.1 Update family-tree.tsx to pass activePersonId
    - Get activePersonId from useActivePersonContext
    - Pass to DiscoverFamilyMembersDialog component
    - _Requirements: 5.1, 5.2_
  - [x] 22.2 Update family.tsx to pass activePersonId
    - Get activePersonId from useActivePersonContext
    - Pass to DiscoverFamilyMembersDialog component
    - _Requirements: 5.1, 5.2_

- [x] 23. Checkpoint - Discover and Connect work with assumed person
  - Verify discovery shows recommendations for assumed person
  - Verify connecting creates relationship with assumed person
  - Verify cache invalidation works correctly
  - Ask the user if questions arise

- [x] 24. Backend: Add person-specific delete relationship endpoint
  - [x] 24.1 Add `DELETE /api/v1/person/{person_id}/relationships/{relationship_id}` endpoint
    - Accept person_id and relationship_id parameters
    - Use validate_person_access to check user has permission to access the person
    - Validate the relationship belongs to the specified person
    - Call relationship_service.delete_relationship() to delete bidirectionally
    - _Requirements: 5.1, 5.2_

- [x] 25. Frontend: Regenerate OpenAPI client for delete endpoint
  - [x] 25.1 Run `npm run generate-client` to pick up new delete endpoint
    - Verify `deletePersonRelationship` method is available in PersonService
    - _Requirements: 5.1, 5.2_

- [x] 26. Frontend: Update family.tsx to use person-specific delete
  - [x] 26.1 Update deleteMutation to use person-specific endpoint
    - When activePersonId provided, call deletePersonRelationship with personId
    - Otherwise fall back to deleteMyRelationship (primary person)
    - _Requirements: 5.1, 5.2_

- [x] 27. Checkpoint - Delete relationship works with assumed person
  - Verify deleting relationship works for assumed person
  - Verify cache invalidation refreshes the UI correctly
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property-based tests
- The foundation (person-specific APIs, ActivePersonContext, validate_person_access) is already complete
- sessionStorage is used for assumed person to ensure it clears on tab close
- The can-assume endpoint provides server-side validation before allowing assume
