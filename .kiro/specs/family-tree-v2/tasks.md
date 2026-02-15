# Implementation Plan: Family Tree V2

## Overview

This plan breaks down the Family Tree V2 feature into discrete, incremental tasks. Each task builds on previous work. The order is: backend schemas → backend service → backend routes → frontend data hook → frontend components (bottom-up) → route + navigation → tests.

## Tasks

### Phase 1: Backend

- [ ] 1. Backend schemas
  - [ ] 1.1 Create `backend/app/schemas/family_tree_v2.py` with `TreeNodeResponse`, `SpouseSummary`, `FamilyTreeV2Response`, `ChildrenResponse`, `ParentsResponse`
    - _Requirements: 2.3_
  - [ ]* 1.2 Verify schemas serialize correctly with sample data

- [ ] 2. Backend service
  - [ ] 2.1 Create `backend/app/services/family_tree_v2_service.py` with `FamilyTreeV2Service` class
    - _Requirements: 2.9_
  - [ ] 2.2 Implement `get_tree(person_id)` — builds root node with 1 level parents + 1 level children, sets `has_children`/`has_parents` flags on leaf nodes
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [ ] 2.3 Implement `get_children_nodes(person_id)` — returns immediate children as `TreeNodeResponse` list with flags
    - _Requirements: 2.5_
  - [ ] 2.4 Implement `get_parent_nodes(person_id)` — returns immediate parents as `TreeNodeResponse` list with flags
    - _Requirements: 2.6_
  - [ ] 2.5 Implement helper `_build_node(person, expanded_down, expanded_up)` — converts person + relationships into `TreeNodeResponse`
    - _Requirements: 2.3_

- [ ] 3. Backend routes
  - [ ] 3.1 Create `backend/app/api/routes/family_tree_v2/__init__.py` with router
    - _Requirements: 2.9_
  - [ ] 3.2 Create `backend/app/api/routes/family_tree_v2/routes.py` with three endpoints: `GET /{person_id}`, `GET /{person_id}/children`, `GET /{person_id}/parents`
    - _Requirements: 2.1, 2.5, 2.6, 2.7, 2.8_
  - [ ] 3.3 Register router in `backend/app/api/main.py` with prefix `/family-tree-v2`
    - _Requirements: 2.1_
  - [ ]* 3.4 Test endpoints manually or with pytest

- [ ] 4. Backend unit tests
  - [ ]* 4.1 Test `get_tree` with person who has parents, children, and spouses
    - _Requirements: 2.2, 2.3_
  - [ ]* 4.2 Test `get_tree` with person who has no relationships
    - _Requirements: 2.4_
  - [ ]* 4.3 Test `get_children_nodes` returns correct children with flags
    - _Requirements: 2.5_
  - [ ]* 4.4 Test `get_parent_nodes` returns correct parents with flags
    - _Requirements: 2.6_
  - [ ]* 4.5 Test 404 for invalid person_id
    - _Requirements: 2.7_
  - [ ]* 4.6 Test `has_children`/`has_parents` flag accuracy
    - _Requirements: 2.3, 2.4_

- [ ] 5. Backend property tests
  - [ ]* 5.1 Write property test for tree node data completeness
    - **Property 1: Tree Node Data Completeness**
    - **Validates: Requirement 2.3**
  - [ ]* 5.2 Write property test for expand flag consistency
    - **Property 2: Expand Flag Consistency**
    - **Validates: Requirement 2.4**
  - [ ]* 5.3 Write property test for has_children/has_parents accuracy
    - **Property 3: Has-Children/Has-Parents Accuracy**
    - **Validates: Requirements 2.3, 2.4, 3.4, 3.5**

- [ ] 6. Checkpoint - Backend complete
  - Ensure all backend tests pass, ask the user if questions arise.

### Phase 2: Frontend — Data Layer

- [ ] 7. Regenerate OpenAPI client
  - [ ] 7.1 Rebuild backend Docker image: `docker compose build --no-cache backend && docker compose up -d`
  - [ ] 7.2 Run `npm run generate-client` in frontend folder to pick up new endpoints
  - [ ] 7.3 Verify generated types include `FamilyTreeV2Response`, `TreeNodeResponse`, etc.
    - _Requirements: 2.1, 2.3_

- [ ] 8. Frontend data hook
  - [ ] 8.1 Create `frontend/src/hooks/useFamilyTreeV2Data.ts`
    - _Requirements: 10.3_
  - [ ] 8.2 Implement `useFamilyTreeV2Data(rootPersonId)` — fetches initial tree via TanStack Query
    - _Requirements: 8.1, 8.3_
  - [ ] 8.3 Implement `fetchChildren(personId)` and `fetchParents(personId)` — for on-demand expansion
    - _Requirements: 4.1, 4.2, 8.4_
  - [ ] 8.4 Configure caching: staleTime 5 min, gcTime 10 min
    - _Requirements: 8.1, 8.2_

### Phase 3: Frontend — Components (bottom-up)

- [ ] 9. PersonCardV2
  - [ ] 9.1 Create `frontend/src/components/FamilyTreeV2/PersonCardV2.tsx`
    - _Requirements: 10.1_
  - [ ] 9.2 Render avatar (gender-based placeholder), full name, years display, spouse badge(s)
    - _Requirements: 3.1, 3.3_
  - [ ] 9.3 Root node gets highlighted border (`border-2 border-green-500`)
    - _Requirements: 3.2_
  - [ ] 9.4 Click handler opens PersonDetailsPanel
    - _Requirements: 3.8_

- [ ] 10. ExpandButton
  - [ ] 10.1 Create `frontend/src/components/FamilyTreeV2/ExpandButton.tsx`
  - [ ] 10.2 Render chevron-up/down when collapsed, minus icon when expanded, spinner when loading
    - _Requirements: 3.4, 3.5, 3.6, 3.7, 4.3_
  - [ ] 10.3 Small circular button with muted styling

- [ ] 11. ConnectorLines
  - [ ] 11.1 Create `frontend/src/components/FamilyTreeV2/ConnectorLines.tsx`
    - _Requirements: 5.5_
  - [ ] 11.2 Implement CSS-based vertical line from parent to horizontal bar
    - _Requirements: 5.1_
  - [ ] 11.3 Implement horizontal bar spanning children with drop-lines to each child
    - _Requirements: 5.2_
  - [ ] 11.4 Handle single-child case (straight vertical line)
    - _Requirements: 5.3_
  - [ ] 11.5 Use muted color (`border-muted-foreground/30`)
    - _Requirements: 5.7_

- [ ] 12. TreeNode (recursive)
  - [ ] 12.1 Create `frontend/src/components/FamilyTreeV2/TreeNode.tsx`
    - _Requirements: 10.1_
  - [ ] 12.2 Render: expand-up button → parent nodes (recursive) → PersonCardV2 → connector lines → children row → expand-down button
    - _Requirements: 3.4, 3.5, 3.6, 3.7, 5.4_
  - [ ] 12.3 Children rendered as horizontal flex row
    - _Requirements: 6.2_
  - [ ] 12.4 Wrap with `React.memo` for performance
    - _Requirements: 8.6_

- [ ] 13. TreeContainer
  - [ ] 13.1 Create `frontend/src/components/FamilyTreeV2/TreeContainer.tsx`
    - _Requirements: 10.1_
  - [ ] 13.2 Manage local tree state with `useState<TreeNode>`
    - _Requirements: 8.5_
  - [ ] 13.3 Implement `expandDown(nodeId)` — fetch children, merge into tree
    - _Requirements: 4.1_
  - [ ] 13.4 Implement `expandUp(nodeId)` — fetch parents, merge into tree
    - _Requirements: 4.2_
  - [ ] 13.5 Implement `collapseDown(nodeId)` / `collapseUp(nodeId)` — toggle flags locally
    - _Requirements: 4.5_
  - [ ] 13.6 Implement `mergeChildrenIntoTree` / `mergeParentsIntoTree` recursive helpers
    - _Requirements: 4.6_
  - [ ] 13.7 Scrollable container with overflow-auto, center root on mount
    - _Requirements: 6.3, 6.4, 6.5_

- [ ] 14. Checkpoint - Components complete
  - Ensure all components render correctly, ask the user if questions arise.

### Phase 4: Frontend — Route & Navigation

- [ ] 15. Route
  - [ ] 15.1 Create `frontend/src/routes/_layout/family-tree-v2.tsx`
    - _Requirements: 10.2_
  - [ ] 15.2 Integrate `useFamilyTreeV2Data` with `ActivePersonContext` for root person
    - _Requirements: 1.3, 1.5_
  - [ ] 15.3 Handle loading, error, and no-profile states
    - _Requirements: 1.4_
  - [ ] 15.4 Integrate SearchPersonDialog for re-rooting the tree
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [ ] 15.5 Integrate PersonDetailsPanel for viewing person details
    - _Requirements: 3.8_

- [ ] 16. Sidebar navigation
  - [ ] 16.1 Add "Family View V2" item to `baseItems` in `AppSidebar.tsx` with appropriate icon
    - _Requirements: 1.1, 10.6_
  - [ ] 16.2 Verify route generation (`routeTree.gen.ts` auto-updates)
    - _Requirements: 1.2_

- [ ] 17. Checkpoint - Feature complete
  - Ensure the feature works end-to-end, ask the user if questions arise.

### Phase 5: Frontend Tests

- [ ] 18. Component tests
  - [ ]* 18.1 Test PersonCardV2 renders name, years, spouse badge, root highlighting
    - _Requirements: 3.1, 3.2, 3.3_
  - [ ]* 18.2 Test ExpandButton states (collapsed, expanded, loading)
    - _Requirements: 3.4, 3.5, 3.6, 3.7_
  - [ ]* 18.3 Test ConnectorLines with 1, 2, 3+ children
    - _Requirements: 5.2, 5.3_
  - [ ]* 18.4 Test TreeNode recursive rendering with mock data
    - _Requirements: 3.4, 3.5_
  - [ ]* 18.5 Test TreeContainer expand/collapse state management
    - _Requirements: 4.5, 4.6_

- [ ] 19. Integration tests
  - [ ]* 19.1 Test initial tree load renders root + parents + children
    - _Requirements: 2.2, 8.3_
  - [ ]* 19.2 Test expand-down fetches children and renders them
    - _Requirements: 4.1_
  - [ ]* 19.3 Test expand-up fetches parents and renders them
    - _Requirements: 4.2_
  - [ ]* 19.4 Test collapse hides nodes without API call
    - _Requirements: 4.5_
  - [ ]* 19.5 Test re-expand shows cached data instantly
    - _Requirements: 4.6_
  - [ ]* 19.6 Test search re-roots the tree
    - _Requirements: 7.3, 7.4_

- [ ] 20. Property tests (frontend)
  - [ ]* 20.1 Write property test for expand idempotency
    - **Property 4: Expand Idempotency**
    - **Validates: Requirement 4.6**
  - [ ]* 20.2 Write property test for collapse preserves data
    - **Property 5: Collapse Preserves Data**
    - **Validates: Requirements 4.5, 4.6**
  - [ ]* 20.3 Write property test for connector line correctness
    - **Property 6: Connector Line Correctness**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  - [ ]* 20.4 Write property test for root person highlighting
    - **Property 7: Root Person Highlighting**
    - **Validates: Requirement 3.2**
  - [ ]* 20.5 Write property test for initial load completeness
    - **Property 8: Initial Load Completeness**
    - **Validates: Requirements 2.2, 8.3**

- [ ] 21. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
