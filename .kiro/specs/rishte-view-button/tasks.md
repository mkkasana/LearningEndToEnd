# Implementation Plan: Rishte View Button

## Overview

Add a View button to each PersonNode in the Rishte graph, following the same pattern as the Find Partner feature. The implementation modifies Rishte-specific components directly (no sharing with Find Partner).

## Tasks

- [x] 1. Update PersonNodeData interface
  - Add optional `onViewClick` callback property to `PersonNodeData` in `/components/Rishte/types.ts`
  - _Requirements: 3.4_

- [x] 2. Add View button to PersonNode component
  - [x] 2.1 Add imports for Eye icon and Button component
    - Import `Eye` from `lucide-react`
    - Import `Button` from `@/components/ui/button`
    - _Requirements: 1.1, 4.3_

  - [x] 2.2 Add click and keyboard handlers
    - Implement `handleViewClick` with `stopPropagation()` and callback invocation
    - Implement `handleViewKeyDown` for Enter and Space key accessibility
    - _Requirements: 1.2, 1.3, 1.4_

  - [x] 2.3 Add View button JSX
    - Render button with Eye icon and "View" text
    - Use outline variant and sm size
    - Add aria-label with person's name
    - Add `nodrag nopan pointer-events-auto cursor-pointer` classes
    - Only render when `onViewClick` callback is provided
    - _Requirements: 1.1, 1.5, 4.1, 4.2, 4.3, 4.4_

  - [ ]* 2.4 Write property test for callback invocation
    - **Property 1: View Button Callback Invocation**
    - **Validates: Requirements 1.2, 3.3**

  - [ ]* 2.5 Write property test for aria-label correctness
    - **Property 2: Aria Label Correctness**
    - **Validates: Requirements 1.5**

- [x] 3. Update RishteGraph component
  - [x] 3.1 Add onNodeViewClick prop to RishteGraphProps interface
    - Add optional `onNodeViewClick?: (personId: string) => void` prop
    - _Requirements: 3.1_

  - [x] 3.2 Inject callback into node data
    - Use `useMemo` to create `nodesWithCallback` array
    - Map over nodes and add `onViewClick` to each node's data
    - Pass `nodesWithCallback` to `RishteGraphInner`
    - _Requirements: 3.2_

  - [ ]* 3.3 Write property test for callback injection
    - **Property 4: Callback Injection to All Nodes**
    - **Validates: Requirements 3.2**

- [x] 4. Integrate PersonDetailsPanel in RishtePage
  - [x] 4.1 Add state for panel management
    - Add `detailsPanelPersonId` state (string | null)
    - Add `isDetailsPanelOpen` state (boolean)
    - _Requirements: 2.1_

  - [x] 4.2 Add handleViewClick callback
    - Create `handleViewClick` function with `useCallback`
    - Set person ID and open panel state
    - _Requirements: 2.2_

  - [x] 4.3 Pass callback to RishteGraph
    - Add `onNodeViewClick={handleViewClick}` prop to RishteGraph
    - _Requirements: 3.2, 3.3_

  - [x] 4.4 Add PersonDetailsPanel component
    - Import `PersonDetailsPanel` from `@/components/FamilyTree/PersonDetailsPanel`
    - Render panel with `personId`, `open`, and `onOpenChange` props
    - _Requirements: 2.1, 2.3, 2.4, 2.5_

  - [ ]* 4.5 Write property test for panel receiving correct person ID
    - **Property 3: Panel Opens With Correct Person ID**
    - **Validates: Requirements 2.2**

- [x] 5. Checkpoint - Verify implementation
  - Ensure all tests pass
  - Manually verify View button appears on all PersonNodes in Rishte graph
  - Verify clicking View opens PersonDetailsPanel with correct person
  - Verify Explore button in panel navigates to Family Tree
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation follows the same pattern as partner-match-view-button
- Property tests use `fast-check` library for random input generation
