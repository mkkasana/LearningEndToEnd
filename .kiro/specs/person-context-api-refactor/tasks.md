# Implementation Plan: Person Context API Refactor

## Overview

This implementation refactors person-related APIs to accept explicit `person_id` parameters instead of deriving them from the session. The work is organized to minimize risk: backend changes first (with backward compatibility), then frontend updates.

## Tasks

- [x] 1. Create permission validation utility
  - [x] 1.1 Create `app/utils/person_permissions.py` with `validate_person_access()` function
    - Implement permission checks: own person, created by, admin override
    - Return person if allowed, raise HTTPException if denied
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [ ]* 1.2 Write property tests for permission validation
    - **Property 1: Own Person Access**
    - **Property 2: Created Person Access**
    - **Property 3: Unauthorized Access Denial**
    - **Property 4: Admin Override**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 2. Add person-specific relationship endpoints
  - [x] 2.1 Add `POST /api/v1/persons/{person_id}/relationships` endpoint
    - Use `validate_person_access()` for permission check
    - Delegate to existing `PersonRelationshipService.create_relationship()`
    - _Requirements: 2.1, 2.4, 2.5, 2.6_
  - [x] 2.2 Add `GET /api/v1/persons/{person_id}/relationships` endpoint
    - Use `validate_person_access()` for permission check
    - Delegate to existing `PersonRelationshipService.get_relationships_by_person()`
    - _Requirements: 2.2, 2.4_
  - [x] 2.3 Update existing `GET /{person_id}/relationships/with-details` to use permission utility
    - Already exists, just add permission validation
    - _Requirements: 2.3, 2.4_
  - [ ]* 2.4 Write property test for relationship data integrity
    - **Property 7: Data Integrity**
    - **Validates: Requirements 2.1**

- [x] 3. Add person-specific address endpoints
  - [x] 3.1 Add `GET /api/v1/persons/{person_id}/addresses` endpoint
    - Use `validate_person_access()` for permission check
    - _Requirements: 3.1, 3.5_
  - [x] 3.2 Update existing `POST /{person_id}/addresses` to use permission utility
    - Already exists at line ~250, add consistent permission check
    - _Requirements: 3.2, 3.5_
  - [x] 3.3 Add `PATCH /api/v1/persons/{person_id}/addresses/{address_id}` endpoint
    - Validate person access, then validate address belongs to person
    - _Requirements: 3.3, 3.5_
  - [x] 3.4 Add `DELETE /api/v1/persons/{person_id}/addresses/{address_id}` endpoint
    - Validate person access, then validate address belongs to person
    - _Requirements: 3.4, 3.5_

- [x] 4. Add person-specific profession endpoints
  - [x] 4.1 Add `GET /api/v1/persons/{person_id}/professions` endpoint
    - Use `validate_person_access()` for permission check
    - _Requirements: 4.1, 4.5_
  - [x] 4.2 Add `POST /api/v1/persons/{person_id}/professions` endpoint
    - Use `validate_person_access()` for permission check
    - _Requirements: 4.2, 4.5_
  - [x] 4.3 Add `PATCH /api/v1/persons/{person_id}/professions/{profession_id}` endpoint
    - Validate person access, then validate profession belongs to person
    - _Requirements: 4.3, 4.5_
  - [x] 4.4 Add `DELETE /api/v1/persons/{person_id}/professions/{profession_id}` endpoint
    - Validate person access, then validate profession belongs to person
    - _Requirements: 4.4, 4.5_

- [x] 5. Add person-specific metadata endpoints
  - [x] 5.1 Add `GET /api/v1/persons/{person_id}/metadata` endpoint
    - Use `validate_person_access()` for permission check
    - _Requirements: 5.1, 5.5_
  - [x] 5.2 Add `POST /api/v1/persons/{person_id}/metadata` endpoint
    - Use `validate_person_access()` for permission check
    - _Requirements: 5.2, 5.5_
  - [x] 5.3 Add `PATCH /api/v1/persons/{person_id}/metadata` endpoint
    - Use `validate_person_access()` for permission check
    - _Requirements: 5.3, 5.5_
  - [x] 5.4 Add `DELETE /api/v1/persons/{person_id}/metadata` endpoint
    - Use `validate_person_access()` for permission check
    - _Requirements: 5.4, 5.5_

- [x] 6. Checkpoint - Backend API complete
  - Ensure all new endpoints work correctly
  - Verify existing `/me` endpoints still function
  - Run backend tests
  - Ask the user if questions arise
  - **COMPLETED**: All 1062 tests pass. Fixed route ordering issue where `/me/*` routes were being matched by `/{person_id}/*` routes.

- [x] 7. Create frontend Active Person Context
  - [x] 7.1 Create `src/contexts/ActivePersonContext.tsx`
    - Create context with `activePerson`, `activePersonId`, `isLoading`, `error`
    - Fetch primary person on mount using existing `getMyPerson()` query
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - [x] 7.2 Add `ActivePersonProvider` to app root
    - Wrap app in provider in `main.tsx` or layout
    - _Requirements: 1.1_
  - [ ]* 7.3 Write property test for context initialization
    - **Property 5: Context Initialization**
    - **Validates: Requirements 1.2**

- [x] 8. Regenerate OpenAPI client
  - [x] 8.1 Run OpenAPI client generation to pick up new endpoints
    - Run `npm run generate-client` or equivalent
    - Verify new endpoint methods are available
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 9. Update frontend API calls - Relationships
  - [x] 9.1 Update `AddFamilyMemberDialog.tsx` to use person-specific endpoint
    - Import `useActivePersonContext`
    - Change `createMyRelationship` to `createPersonRelationship` with `personId`
    - _Requirements: 7.1_
  - [x] 9.2 Update `useFamilyTreeData.ts` to always use person-specific endpoint
    - Remove conditional logic for `/me` vs `/{person_id}`
    - Always use `getPersonRelationshipsWithDetails({ personId })`
    - _Requirements: 7.1_
  - [x] 9.3 Update `family.tsx` route to use person-specific endpoint
    - Use `activePersonId` from context
    - _Requirements: 7.1_

- [x] 10. Update frontend API calls - Other endpoints
  - [x] 10.1 Update address-related components to use person-specific endpoints
    - Find and update any components using `/me/addresses`
    - _Requirements: 7.2_
  - [x] 10.2 Update profession-related components to use person-specific endpoints
    - Find and update any components using `/me/professions`
    - _Requirements: 7.3_
  - [x] 10.3 Update metadata-related components to use person-specific endpoints
    - Find and update any components using `/me/metadata`
    - _Requirements: 7.4_

- [x] 11. Checkpoint - Frontend updates complete
  - Ensure all API calls use new endpoints with person context
  - Verify application works end-to-end
  - Ask the user if questions arise

- [ ] 12. Backward compatibility verification
  - [ ]* 12.1 Write property test for backward compatibility
    - **Property 6: Backward Compatibility**
    - **Validates: Requirements 8.1, 8.2**
  - [ ] 12.2 Manual verification that existing workflows work
    - Test login → view family tree → add family member flow
    - _Requirements: 8.2, 8.3_

- [ ] 13. Final checkpoint
  - Ensure all tests pass
  - Verify no regressions in existing functionality
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property-based tests
- Backend changes are designed to be backward compatible - existing `/me` endpoints continue to work
- Frontend changes can be done incrementally - each component can be updated independently
- The `ActivePersonContext` is initialized to Primary Person for now; the "Assume Person Role" feature will extend this later
