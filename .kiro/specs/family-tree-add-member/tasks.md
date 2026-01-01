# Implementation Plan: Family Tree Add Member Card

## Overview

This plan implements the Add Family Member card feature for the Family Tree View, allowing users to add family members directly from the tree visualization by clicking a "+" card at the end of each row.

## Tasks

- [x] 1. Create AddFamilyMemberCard component
  - [x] 1.1 Create AddFamilyMemberCard.tsx in frontend/src/components/FamilyTree/
    - Create component with `variant` and `onClick` props
    - Use same dimensions as PersonCard based on variant (parent, center, child)
    - Style with dashed border and muted background
    - Add centered circle with Plus icon from lucide-react
    - Add hover effects (border color change, slight scale)
    - Add cursor-pointer and click handler
    - _Requirements: 1.5, 1.6_

  - [x] 1.2 Write unit tests for AddFamilyMemberCard
    - Test renders Plus icon
    - Test click handler is called
    - Test correct styling for each variant
    - _Requirements: 1.5, 1.6_

- [x] 2. Update HorizontalScrollRow to support Add Card
  - [x] 2.1 Modify HorizontalScrollRow.tsx
    - Add `showAddCard?: boolean` prop
    - Add `onAddClick?: () => void` prop
    - Render AddFamilyMemberCard at rightmost position when showAddCard is true
    - Pass variant prop to AddFamilyMemberCard based on row variant
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 2.2 Write property test for Add Card position
    - **Property 1: Add Card Position Invariant**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

- [x] 3. Update ParentsSection and ChildrenSection
  - [x] 3.1 Modify ParentsSection.tsx
    - Add `showAddCard?: boolean` prop
    - Add `onAddClick?: () => void` prop
    - Pass props to HorizontalScrollRow
    - _Requirements: 1.1_

  - [x] 3.2 Modify ChildrenSection.tsx
    - Add `showAddCard?: boolean` prop
    - Add `onAddClick?: () => void` prop
    - Pass props to HorizontalScrollRow
    - _Requirements: 1.3_

- [x] 4. Integrate Add Family Member flow in Family Tree View
  - [x] 4.1 Update family-tree.tsx route
    - Import DiscoverFamilyMembersDialog and AddFamilyMemberDialog from Family components
    - Add state: showDiscoveryDialog, showAddDialog
    - Add handleAddFamilyMember function to open discovery dialog
    - Add handleSkipDiscovery function to close discovery and open add dialog
    - Add handleDiscoveryDialogClose function
    - Pass showAddCard={true} and onAddClick={handleAddFamilyMember} to all row components
    - Render DiscoverFamilyMembersDialog and AddFamilyMemberDialog
    - _Requirements: 2.1, 3.1_

  - [x] 4.2 Handle data refresh after successful addition
    - Invalidate familyTreeData query on successful addition
    - The existing dialogs already handle success callbacks
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 5. Handle empty state
  - [x] 5.1 Update family-tree.tsx empty state handling
    - When no relationships exist, show all three rows with Add_Cards
    - Remove or modify the existing "No Family Relationships" empty state message
    - Display Parents row with Add_Card, Center row with selected person + Add_Card, Children row with Add_Card
    - _Requirements: 5.1, 5.2_

- [x] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks including tests are required for comprehensive coverage
- The existing DiscoverFamilyMembersDialog and AddFamilyMemberDialog components are reused without modification
- The Add_Card uses the same sizing system as PersonCard for visual consistency
- Data refresh is handled by React Query's invalidateQueries mechanism
