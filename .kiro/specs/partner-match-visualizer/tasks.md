# Implementation Plan: Partner Match Visualizer

## Overview

This implementation plan enhances the Find Partner UI by replacing the raw JSON results display with an interactive graph visualization. Users can select a match from a dropdown and see the relationship path rendered as a generation-based family tree using React Flow.

All new components are created within the `FindPartner/` folder to maintain complete isolation from Rishte components.

## Tasks

- [x] 1. Add new types to FindPartner types.ts
  - [x] 1.1 Add TypeScript interfaces for match visualization
    - Add `MatchItem`, `MatchPersonNodeData`, `MatchRelationshipEdgeData`
    - Add `MatchNode`, `MatchEdge`, `TransformedMatchPath`
    - Add `MatchGenerationInfo`
    - Add component props interfaces (`MatchSelectorProps`, `MatchPathSummaryProps`, `MatchGraphProps`)
    - _Requirements: 1.1, 6.1-6.5, 7.1-7.5_

- [x] 2. Implement path extraction utility
  - [x] 2.1 Create `frontend/src/components/FindPartner/utils/matchPathExtractor.ts`
    - Implement `extractPathToMatch()` - trace backwards from match to seeker via `from_person`
    - Implement `buildMatchItems()` - build dropdown items sorted by depth
    - Implement `generateMatchPathSummary()` - generate array of names for path summary
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 1.4_
  - [x]* 2.2 Write property tests for path extraction
    - **Property 1: Path Extraction Correctness**
    - **Property 2: Match Sorting by Depth**
    - **Validates: Requirements 3.1, 3.2, 1.4**

- [x] 3. Implement graph transformation utility
  - [x] 3.1 Create `frontend/src/components/FindPartner/utils/matchGraphTransformer.ts`
    - Implement relationship type helpers (`isChildRelationship`, `isParentRelationship`, `isSpouseRelationship`)
    - Implement `assignGenerations()` - assign generation levels based on relationships
    - Implement `calculatePositions()` - convert generations to pixel positions
    - Implement `getEdgeHandles()` - determine source/target handles based on positions
    - Implement `transformMatchPath()` - main function to create React Flow nodes/edges
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [x]* 3.2 Write property tests for graph transformation
    - **Property 4: Generation Layout Correctness**
    - **Validates: Requirements 5.1, 5.2, 5.3**

- [x] 4. Checkpoint - Core utilities complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement MatchSelector component
  - [x] 5.1 Create `frontend/src/components/FindPartner/MatchSelector.tsx`
    - Display total matches count ("N matches found")
    - Render Select dropdown with match items (first name, last name, birth year)
    - Handle match selection change
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 6. Implement MatchPathSummary component
  - [x] 6.1 Create `frontend/src/components/FindPartner/MatchPathSummary.tsx`
    - Display path as "Name1 → Name2 → Name3..."
    - Accept array of names as prop
    - _Requirements: 4.1, 4.2, 4.3_
  - [x]* 6.2 Write property test for path summary
    - **Property 3: Path Summary Correctness**
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 7. Implement MatchPersonNode component
  - [x] 7.1 Create `frontend/src/components/FindPartner/MatchPersonNode.tsx`
    - Display circular avatar with User icon
    - Display first name + last name
    - Display birth year - death year (format: "1990 -" or "1990 - 2020")
    - Apply green border + "Seeker" label for seeker
    - Apply blue border + "Match" label for match
    - Add React Flow handles (top, bottom, left, right)
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  - [x]* 7.2 Write property tests for node display
    - **Property 5: Node Label Correctness**
    - **Property 6: Birth-Death Year Formatting**
    - **Validates: Requirements 6.3, 6.4, 6.5**

- [x] 8. Implement MatchRelationshipEdge component
  - [x] 8.1 Create `frontend/src/components/FindPartner/MatchRelationshipEdge.tsx`
    - Display relationship label on edge
    - Use straight path for spouse edges (horizontal)
    - Use bezier path for parent-child edges (vertical)
    - Apply distinct styling for spouse edges (dashed, purple color)
    - Add arrow markers
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [x]* 8.2 Write property test for edge styling
    - **Property 7: Edge Styling Correctness**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.5**

- [x] 9. Implement MatchGraphControls component
  - [x] 9.1 Create `frontend/src/components/FindPartner/MatchGraphControls.tsx`
    - Add zoom in button
    - Add zoom out button
    - Add fit view button
    - Use React Flow's useReactFlow hook
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 10. Checkpoint - UI components complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. Implement MatchGraph component
  - [x] 11.1 Create `frontend/src/components/FindPartner/MatchGraph.tsx`
    - Set up ReactFlow with ReactFlowProvider
    - Register custom node type 'matchPersonNode'
    - Register custom edge type 'matchRelationshipEdge'
    - Configure default edge options with arrow markers
    - Enable zoom, pan, fit view
    - Auto-fit view on initial render
    - Disable node dragging for cleaner visualization
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 12. Update PartnerResultsDisplay component
  - [x] 12.1 Replace JSON display with graph visualization
    - Remove raw JSON pretty-print display
    - Add state for selected match ID
    - Use `buildMatchItems()` to create dropdown items
    - Use `extractPathToMatch()` to get path for selected match
    - Use `transformMatchPath()` to create React Flow elements
    - Use `generateMatchPathSummary()` for path summary
    - Render MatchSelector when matches exist
    - Render MatchPathSummary when match selected
    - Render MatchGraph when match selected
    - Auto-select first match on results load
    - Handle match selection change
    - _Requirements: 10.1, 10.2, 10.3, 1.5, 1.6_
  - [x] 12.2 Handle empty/no matches state
    - Show "No matches found" message when total_matches = 0
    - Hide MatchSelector and MatchGraph when no matches
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 13. Update barrel exports
  - [x] 13.1 Update `frontend/src/components/FindPartner/index.ts`
    - Export all new components
    - Export utility functions
    - _Requirements: 9.1_

- [x] 14. Final Checkpoint
  - Ensure all tests pass, ask the user if questions arise.
  - Verify the feature works end-to-end with the backend API
  - Verify Rishte components are unchanged and still working

## Notes

- Tasks marked with `*` are optional property-based tests
- All new components go in `FindPartner/` folder - NO imports from Rishte
- React Flow is already installed (used by Rishte)
- The existing PartnerFilterPanel, TagInput, and usePartnerDefaults remain unchanged
- This replaces the raw JSON display with interactive graph visualization

