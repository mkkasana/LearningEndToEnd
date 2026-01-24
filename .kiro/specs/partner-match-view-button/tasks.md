# Implementation Plan: Partner Match View Button

## Overview

This plan implements the View button feature for the Find Partner match graph, following a bottom-up approach: starting with the MatchPersonNode component, then wiring up the callback through the component hierarchy, and finally integrating the PersonDetailsPanel in the FindPartnerPage.

## Tasks

- [x] 1. Add View button to MatchPersonNode component
  - [x] 1.1 Update MatchPersonNodeData interface with onViewClick callback
    - Add optional `onViewClick?: (personId: string) => void` to the interface in `types.ts`
    - _Requirements: 3.3_
  - [x] 1.2 Add View button UI to MatchPersonNode
    - Import Eye icon from lucide-react and Button component
    - Add View button below the Seeker/Match label with Eye icon and "View" text
    - Use outline variant and sm size for consistency with Family Tree
    - Add aria-label "View details for {firstName} {lastName}"
    - _Requirements: 1.1, 1.5, 4.1, 4.2, 4.3, 4.4_
  - [x] 1.3 Implement click and keyboard handlers
    - Add handleViewClick that stops propagation and calls onViewClick with personId
    - Add handleViewKeyDown for Enter and Space key accessibility
    - _Requirements: 1.2, 1.3, 1.4, 3.3_
  - [ ]* 1.4 Write property test for View button callback
    - **Property 1: View Button Callback Invocation**
    - Generate random person IDs, verify callback receives exact ID
    - **Validates: Requirements 1.2, 3.3**
  - [ ]* 1.5 Write property test for aria-label correctness
    - **Property 2: Aria Label Correctness**
    - Generate random first/last name strings, verify aria-label format
    - **Validates: Requirements 1.5**

- [x] 2. Update MatchGraph to pass callback to nodes
  - [x] 2.1 Update MatchGraphProps interface
    - Add optional `onNodeViewClick?: (personId: string) => void` prop
    - _Requirements: 3.1_
  - [x] 2.2 Inject callback into node data
    - Map over nodes to add onViewClick callback to each node's data
    - Pass the injected nodes to MatchGraphInner
    - _Requirements: 3.2_
  - [ ]* 2.3 Write unit test for callback injection
    - Verify nodes receive onViewClick in their data
    - _Requirements: 3.2_

- [x] 3. Update PartnerResultsDisplay to accept and pass callback
  - [x] 3.1 Update PartnerResultsDisplayProps interface
    - Add optional `onViewPerson?: (personId: string) => void` prop
    - _Requirements: 3.4_
  - [x] 3.2 Pass callback to MatchGraph
    - Pass onViewPerson as onNodeViewClick prop to MatchGraph component
    - _Requirements: 3.5_
  - [ ]* 3.3 Write unit test for callback passing
    - Verify onViewPerson is passed to MatchGraph
    - _Requirements: 3.5_

- [x] 4. Integrate PersonDetailsPanel in FindPartnerPage
  - [x] 4.1 Add state for panel management
    - Add detailsPanelPersonId state (string | null)
    - Add isDetailsPanelOpen state (boolean)
    - _Requirements: 2.1_
  - [x] 4.2 Implement handleViewClick handler
    - Set detailsPanelPersonId to the clicked person's ID
    - Set isDetailsPanelOpen to true
    - _Requirements: 2.2_
  - [x] 4.3 Add PersonDetailsPanel component
    - Import PersonDetailsPanel from FamilyTree components
    - Add PersonDetailsPanel with personId, open, and onOpenChange props
    - _Requirements: 2.1, 2.3, 2.4, 2.5_
  - [x] 4.4 Wire up callback to PartnerResultsDisplay
    - Pass handleViewClick as onViewPerson prop
    - _Requirements: 2.2_
  - [ ]* 4.5 Write property test for panel state
    - **Property 3: Panel Opens With Correct Person ID**
    - Generate random person IDs, verify panel receives correct ID
    - **Validates: Requirements 2.2**

- [x] 5. Checkpoint - Verify integration
  - Ensure all tests pass
  - Manually verify View button appears on all person nodes in the graph
  - Verify clicking View opens the panel with correct person details
  - Verify panel closes without affecting graph state
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The PersonDetailsPanel component is reused from FamilyTree - no modifications needed
- Property tests use fast-check library for random input generation
- Each task references specific requirements for traceability
