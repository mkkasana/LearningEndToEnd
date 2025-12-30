# Implementation Plan: Discover Family Members

## Overview

This implementation plan breaks down the "Discover Family Members" feature into discrete, manageable tasks. The feature adds intelligent family member discovery that proactively suggests connections before users enter the manual "Add Family Member" wizard.

## Tasks

- [x] 1. Create backend data models and schemas
  - [x] 1.1 Create PersonDiscoveryResult schema
    - Add schema file `backend/app/schemas/person/person_discovery.py`
    - Define PersonDiscoveryResult with all required fields
    - Add proximity_score and relationship_priority fields for sorting
    - _Requirements: 8.5_
  - [x] 1.2 Add discovery result to person schema exports
    - Update `backend/app/schemas/person/__init__.py`
    - Export PersonDiscoveryResult
    - _Requirements: 8.5_

- [x] 2. Implement PersonDiscoveryService
  - [x] 2.1 Create PersonDiscoveryService class structure
    - Create file `backend/app/services/person/person_discovery_service.py`
    - Initialize with session and repositories
    - Add main discover_family_members method signature
    - _Requirements: 4.1, 5.1, 6.1, 7.1, 8.1_
  - [x] 2.2 Implement _discover_spouses_children method
    - Query user's spouses (Wife/Husband/Spouse relationships)
    - For each spouse, find their children (Son/Daughter relationships)
    - Filter out already-connected children
    - Infer relationship type based on child's gender
    - Build connection path string
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  - [x] 2.3 Implement _discover_parents_spouse method
    - Query user's parents (Father/Mother relationships)
    - For each parent, find their spouse (Wife/Husband/Spouse relationships)
    - Filter out already-connected spouses
    - Infer relationship type based on spouse's gender
    - Build connection path string
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_
  - [x] 2.4 Implement _discover_childs_parent method
    - Query user's children (Son/Daughter relationships)
    - For each child, find their parents (Father/Mother relationships)
    - Filter out already-connected parents
    - Infer relationship type as "Spouse"
    - Build connection path string
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 2.5 Implement helper methods
    - Add _infer_child_relationship method (gender → Son/Daughter)
    - Add _infer_parent_relationship method (gender → Father/Mother)
    - Add _build_discovery_result method (person details + metadata)
    - Add _get_connected_person_ids method (get all related person IDs)
    - _Requirements: 4.4, 4.5, 5.4, 5.5_
  - [x] 2.6 Implement sorting and filtering logic
    - Combine results from all three discovery patterns
    - Deduplicate persons appearing through multiple paths
    - Sort by proximity_score, relationship_priority, first_name
    - Limit to top 20 results
    - _Requirements: 7.5, 10.1, 10.2, 10.3, 10.4, 10.5_
  - [x] 2.7 Add error handling and logging
    - Handle user with no person record
    - Handle missing person details gracefully
    - Add comprehensive logging for debugging
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 3. Create API endpoint
  - [x] 3.1 Add discover-family-members endpoint
    - Add GET endpoint to `backend/app/api/routes/person/person.py`
    - Implement authentication and authorization
    - Call PersonDiscoveryService
    - Return list of PersonDiscoveryResult
    - Add error handling and logging
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  - [x] 3.2 Update service exports
    - Export PersonDiscoveryService in `backend/app/services/person/__init__.py`
    - _Requirements: 8.1_

- [x] 4. Add frontend TypeScript types
  - [x] 4.1 Generate OpenAPI client types
    - Run OpenAPI generator to update client types
    - Verify PersonDiscoveryResult type is generated
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  - [x] 4.2 Add PersonService method
    - Add discoverFamilyMembers method to PersonService
    - Map to GET /api/v1/person/discover-family-members
    - _Requirements: 1.1, 8.1_

- [ ] 5. Create DiscoverFamilyMembersDialog component
  - [ ] 5.1 Create component file and basic structure
    - Create `frontend/src/components/Family/DiscoverFamilyMembersDialog.tsx`
    - Add component props interface
    - Add Dialog wrapper with header
    - _Requirements: 1.2, 2.1_
  - [ ] 5.2 Implement discovery API query
    - Use useQuery to fetch discovered family members
    - Handle loading state with spinner
    - Handle error state with error message
    - Enable query only when dialog is open
    - _Requirements: 1.1, 1.2_
  - [ ] 5.3 Implement discovered persons list UI
    - Create scrollable container (max-h-96)
    - Display person cards with all details
    - Show: Name, DOB, Address, Religion, Connection path
    - Show inferred relationship label
    - Add "Connect as <Relationship>" button for each person
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7_
  - [ ] 5.4 Implement connection flow
    - Add state for selected person and confirmation dialog
    - Handle "Connect as <Relationship>" button click
    - Show ConnectConfirmationDialog with person details
    - _Requirements: 3.1, 3.2_
  - [ ] 5.5 Implement connection mutation
    - Create useMutation for creating relationship
    - Call PersonService.createMyRelationship
    - Handle success: show toast, invalidate queries, close dialog
    - Handle error: show error toast, keep dialog open
    - _Requirements: 3.3, 3.4, 3.5_
  - [ ] 5.6 Add skip functionality
    - Add "Skip: Move to create new" button in footer
    - Call onSkip callback when clicked
    - Add "Close" button to close dialog
    - _Requirements: 1.3, 9.1, 9.2, 9.3_
  - [ ] 5.7 Handle auto-close after all connections
    - Check if discoveries list is empty after connection
    - Auto-close dialog if no more suggestions
    - _Requirements: 9.4, 9.5_

- [ ] 6. Integrate discovery dialog with Add Family Member flow
  - [ ] 6.1 Update family.tsx component
    - Add state for showDiscoveryDialog
    - Update "Add Family Member" button click handler
    - Show DiscoverFamilyMembersDialog first
    - _Requirements: 1.1, 1.2_
  - [ ] 6.2 Implement skip to manual wizard flow
    - Add handleSkipDiscovery callback
    - Close discovery dialog and open AddFamilyMemberDialog
    - _Requirements: 1.3, 9.1, 9.2_
  - [ ] 6.3 Handle no discoveries scenario
    - If API returns empty list, skip discovery dialog
    - Proceed directly to AddFamilyMemberDialog
    - _Requirements: 1.4_
  - [ ] 6.4 Handle dialog close without connecting
    - When user closes discovery dialog, open manual wizard
    - _Requirements: 1.5_

- [ ] 7. Add database indexes for performance
  - [ ] 7.1 Create migration for relationship indexes
    - Add index on person_relationship.person_id
    - Add index on person_relationship.related_person_id
    - Add index on person_relationship.relationship_type
    - Add composite index on (person_id, is_active)
    - _Requirements: 8.1_

- [ ] 8. Checkpoint - Test discovery patterns
  - Ensure all tests pass, ask the user if questions arise.
  - Test spouse's children discovery
  - Test parent's spouse discovery
  - Test child's parent discovery
  - Test with various family structures
  - _Requirements: 4.1, 5.1, 6.1_

- [ ] 9. Add comprehensive error handling
  - [ ] 9.1 Backend error handling
    - Handle user with no person record gracefully
    - Handle database query failures
    - Handle missing person details
    - Add comprehensive logging
    - _Requirements: 8.3_
  - [ ] 9.2 Frontend error handling
    - Display error message in dialog
    - Provide "Try Again" button
    - Allow skip to manual wizard on error
    - _Requirements: 1.1, 9.1_

- [ ] 10. Implement sorting and deduplication
  - [ ] 10.1 Add sorting logic
    - Sort by proximity_score (ascending)
    - Then by relationship_priority (ascending)
    - Then by first_name (alphabetical)
    - _Requirements: 10.1, 10.2, 10.3_
  - [ ] 10.2 Add deduplication logic
    - Detect persons appearing through multiple paths
    - Keep most direct connection (lowest proximity)
    - If same proximity, keep highest priority relationship
    - _Requirements: 7.5_
  - [ ] 10.3 Add result limiting
    - Limit to maximum 20 suggestions
    - _Requirements: 10.4, 10.5_

- [ ] 11. Add caching for performance
  - [ ] 11.1 Implement backend caching
    - Add cache decorator to discover_family_members
    - Set 5-minute TTL
    - Cache key: discovery:{user_id}
    - _Requirements: 8.1_
  - [ ] 11.2 Implement cache invalidation
    - Invalidate on relationship create
    - Invalidate on relationship update
    - Invalidate on relationship delete
    - _Requirements: 3.5_

- [ ] 12. Write unit tests
  - [ ] 12.1 Test PersonDiscoveryService methods
    - Test _discover_spouses_children with various scenarios
    - Test _discover_parents_spouse with various scenarios
    - Test _discover_childs_parent with various scenarios
    - Test relationship inference logic
    - Test sorting and filtering
    - Test deduplication
    - _Requirements: 4.1, 5.1, 6.1, 7.5, 10.1_
  - [ ] 12.2 Test API endpoint
    - Test successful discovery
    - Test empty results
    - Test authentication
    - Test error handling
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  - [ ] 12.3 Test frontend component
    - Test dialog rendering with mock data
    - Test connection flow
    - Test skip functionality
    - Test error states
    - Test loading states
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 9.1_

- [ ] 13. Write integration tests
  - [ ] 13.1 Test complete discovery flow
    - Create test users with various family structures
    - Test discovery API returns correct suggestions
    - Test connection creation after discovery
    - Test bidirectional relationship creation
    - _Requirements: 1.1, 1.2, 3.3, 4.1, 5.1, 6.1_
  - [ ] 13.2 Test edge cases
    - Test user with no relationships
    - Test circular relationships
    - Test deceased persons in suggestions
    - Test multiple spouses scenario
    - Test gender unknown scenario
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 14. Final checkpoint - End-to-end testing
  - Ensure all tests pass, ask the user if questions arise.
  - Test complete user flow from button click to connection
  - Test skip flow to manual wizard
  - Test no discoveries flow
  - Test error recovery
  - Verify UI/UX matches design
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Backend tasks should be completed before frontend tasks
- Database indexes should be added early for performance
- Testing tasks can be done in parallel with implementation

## Implementation Order

1. **Backend Foundation** (Tasks 1-3): Data models, service, API endpoint
2. **Database Optimization** (Task 7): Add indexes
3. **Frontend Components** (Tasks 4-6): UI components and integration
4. **Performance** (Task 11): Caching
5. **Error Handling** (Task 9): Comprehensive error handling
6. **Sorting & Filtering** (Task 10): Advanced features
7. **Testing** (Tasks 8, 12-14): Unit, integration, and E2E tests
