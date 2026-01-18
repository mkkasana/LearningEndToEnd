# Implementation Plan: Rishte Relationship Visualizer

## Overview

This implementation plan creates the Rishte feature as a standalone module for visualizing relationship paths between two persons. The feature uses React Flow for the interactive graph and includes custom nodes, edges, and a path transformation algorithm.

## Tasks

- [x] 1. Project Setup and Dependencies
  - [x] 1.1 Install React Flow dependency
    - Run `npm install @xyflow/react` in the frontend directory
    - _Requirements: 1.4_
  - [x] 1.2 Create Rishte component folder structure
    - Create `src/components/Rishte/` directory
    - Create `src/components/Rishte/index.ts` barrel export
    - Create `src/components/Rishte/types.ts` for TypeScript interfaces
    - _Requirements: 1.1, 1.3_

- [x] 2. Implement Core Types and Utilities
  - [x] 2.1 Define TypeScript interfaces in types.ts
    - Define `SelectedPerson`, `PersonNodeData`, `RelationshipEdgeData`
    - Define `RishteNode`, `RishteEdge`, `TransformedPath`
    - Define `GenerationInfo` for layout calculation
    - _Requirements: 5.1, 7.1-7.5_
  - [x] 2.2 Implement path transformation utility
    - Create `src/components/Rishte/utils/pathTransformer.ts`
    - Implement `buildPathArray()` to extract ordered path from linked list
    - Implement `assignGenerations()` to determine generation levels
    - Implement `transformApiResponse()` main function
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - [ ]* 2.3 Write property tests for path transformation
    - **Property 2: Path Transformation Validity**
    - **Validates: Requirements 5.1, 5.2**
  - [x] 2.4 Implement layout calculator utility
    - Create `src/components/Rishte/utils/layoutCalculator.ts`
    - Implement `calculatePositions()` for node positioning
    - Handle spouse side-by-side positioning
    - Handle generation-based row layout
    - _Requirements: 5.5, 6.1, 6.2, 6.3, 6.4_
  - [ ]* 2.5 Write property tests for layout calculator
    - **Property 3: Generation-Based Layout Correctness**
    - **Property 4: Spouse Positioning Correctness**
    - **Validates: Requirements 5.5, 6.1, 6.2, 6.3, 6.4**

- [x] 3. Checkpoint - Core utilities complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement UI Components
  - [x] 4.1 Implement PersonNode component
    - Create `src/components/Rishte/PersonNode.tsx`
    - Display avatar with User icon placeholder
    - Display first name + last name
    - Display birth year - death year
    - Apply green border for Person A, blue border for Person B
    - Style similar to FamilyTree PersonCard
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_
  - [ ]* 4.2 Write property test for birth-death year formatting
    - **Property 5: Birth-Death Year Formatting**
    - **Validates: Requirements 7.3**
  - [x] 4.3 Implement RelationshipEdge component
    - Create `src/components/Rishte/RelationshipEdge.tsx`
    - Display relationship label on edge
    - Use different styling for spouse edges (horizontal)
    - Add arrow markers for direction
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  - [x] 4.4 Implement PersonSelector component
    - Create `src/components/Rishte/PersonSelector.tsx`
    - Integrate with existing person search hook
    - Display searchable dropdown with person results
    - Show first name, last name, birth year in results
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [x] 4.5 Implement PathSummary component
    - Create `src/components/Rishte/PathSummary.tsx`
    - Display person count
    - Display path as "name1 → name2 → name3..."
    - _Requirements: 11.1, 11.2_
  - [ ]* 4.6 Write property test for path summary
    - **Property 6: Path Summary Accuracy**
    - **Validates: Requirements 11.1, 11.2**
  - [x] 4.7 Implement GraphControls component
    - Create `src/components/Rishte/GraphControls.tsx`
    - Add zoom in, zoom out, fit view buttons
    - Use React Flow's useReactFlow hook for controls
    - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 5. Checkpoint - UI components complete
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Implement Main Graph and Page
  - [x] 6.1 Implement RishteGraph component
    - Create `src/components/Rishte/RishteGraph.tsx`
    - Set up ReactFlow with custom node and edge types
    - Handle zoom, pan, and fit view
    - Auto-fit view on initial render
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 9.1, 9.2, 9.3, 9.4, 9.5_
  - [x] 6.2 Create barrel export
    - Update `src/components/Rishte/index.ts` with all exports
    - _Requirements: 1.1_
  - [x] 6.3 Implement Rishte route page
    - Create `src/routes/_layout/rishte.tsx`
    - Add page header with title
    - Add two PersonSelector components
    - Add Find Relationship button with proper enabled state
    - Integrate with lineage-path API
    - Handle loading, error, and no-connection states
    - Render RishteGraph when connection found
    - _Requirements: 3.1, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4_
  - [ ]* 6.4 Write property test for Find button state
    - **Property 1: Find Button State**
    - **Validates: Requirements 3.5**

- [x] 7. Integrate with Sidebar
  - [x] 7.1 Add Rishte menu item to sidebar
    - Update `src/components/Sidebar/AppSidebar.tsx`
    - Add "Rishte" item after "Search" with GitBranch icon
    - Link to `/rishte` route
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 8. Responsive Design
  - [x] 8.1 Add responsive styles
    - Stack PersonSelectors vertically on smaller screens
    - Ensure graph fills available space
    - _Requirements: 10.1, 10.2, 10.3_

- [x] 9. Final Checkpoint
  - Ensure all tests pass, ask the user if questions arise.
  - Verify the feature works end-to-end with the backend API

## Notes

- Tasks marked with `*` are optional property-based tests
- React Flow is used for the interactive graph visualization
- The path transformation algorithm is the core logic that converts the linear API response to a tree structure
- All components are self-contained in `src/components/Rishte/` folder
