# Implementation Plan: Family Tree View

## Overview

This implementation plan breaks down the Family Tree View feature into discrete, incremental tasks. Each task builds on previous work, with testing integrated throughout to validate functionality early. The plan focuses on creating a visual, interactive family tree centered on a selected person, with navigation capabilities and responsive design.

## Tasks

- [x] 1. Set up route and basic page structure
  - Create new route file at `frontend/src/routes/_layout/family-tree.tsx`
  - Add "Family View" navigation link to `_layout.tsx`
  - Create basic FamilyTreeView component with loading and error states
  - Verify route navigation works correctly
  - Git commit all the change made for this task
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Implement data fetching and processing
  - [x] 2.1 Create useFamilyTreeData custom hook
    - Implement TanStack Query integration for fetching relationship data
    - Use existing `/api/v1/person/{person_id}/relationships/with-details` endpoint
    - Handle loading, error, and success states
    - Initialize with current user's person profile
    - _Requirements: 1.3, 9.1, 9.2_

  - [ ] 2.2 Write property test for relationship categorization
    - **Property 2: Relationship Categorization**
    - **Validates: Requirements 9.3**

  - [x] 2.3 Implement categorizeRelationships function
    - Categorize relationships into parents, spouses, and children based on relationship_type
    - Extract parent IDs for sibling calculation
    - Handle edge cases (empty relationships, unknown types)
    - _Requirements: 9.3_

  - [x] 2.4 Write property test for sibling calculation
    - **Property 3: Sibling Calculation**
    - **Validates: Requirements 9.4**

  - [x] 2.5 Implement calculateSiblings function
    - Find people who share parents with selected person
    - Exclude the selected person from results
    - Deduplicate siblings (same person through both parents)
    - _Requirements: 9.4_

  - [x] 2.6 Write property test for data caching
    - **Property 9: Data Caching**
    - **Validates: Requirements 9.5**

  - [x] 2.7 Implement data caching in useFamilyTreeData hook
    - Configure TanStack Query cache settings
    - Verify cached data is reused for previously viewed persons
    - _Requirements: 9.5_
  - [x] 2.8 Git commit all the change made for this task


- [ ] 3. Create PersonCard component
  - [ ] 3.1 Implement PersonCard component with variants
    - Create component with props: person, relationshipType, variant, onClick, showPhoto
    - Implement variants: selected, parent, spouse, sibling, child
    - Add click handler for navigation
    - _Requirements: 2.1, 2.3_

  - [ ] 3.2 Write property test for person information formatting
    - **Property 1: Person Information Formatting**
    - **Validates: Requirements 2.2, 3.4, 4.3, 6.3**

  - [ ] 3.3 Implement person information display formatting
    - Display first name and last name
    - Format birth/death years as "YYYY - YYYY" or "YYYY -"
    - Show relationship label for non-selected cards
    - _Requirements: 2.2, 3.4, 4.3, 6.3_

  - [ ] 3.4 Write unit tests for PersonCard edge cases
    - Test with missing photo (shows placeholder)
    - Test with missing middle name
    - Test with missing death date
    - Test different variants render with correct styling
    - _Requirements: 2.4, 2.5_

  - [ ] 3.5 Implement photo display with fallback
    - Display profile photo if available
    - Show gender-based avatar placeholder if no photo
    - _Requirements: 2.4, 2.5_

 - [ ] 3.6 Git commit all the change made for this task

- [ ] 4. Implement family tree layout sections
  - [ ] 4.1 Create ParentsSection component
    - Display parent cards above selected person
    - Show mother and father side-by-side
    - Handle cases with 0, 1, or 2 parents
    - _Requirements: 3.1, 3.2, 3.5, 3.6_

  - [ ] 4.2 Write property test for relationship display
    - **Property 4: Relationship Display**
    - **Validates: Requirements 3.1, 4.1, 5.1, 6.1**

  - [ ] 4.3 Create SpouseSection component
    - Display spouse card(s) horizontally adjacent to selected person
    - Handle single spouse case
    - _Requirements: 4.1, 4.5_

  - [ ] 4.4 Write property test for multiple spouse display
    - **Property 5: Multiple Spouse Display**
    - **Validates: Requirements 4.4**

  - [ ] 4.5 Implement SpouseCarousel for multiple spouses
    - Create carousel/slideshow component for multiple spouses
    - Add prev/next navigation buttons
    - Add indicator dots showing current spouse
    - Implement smooth transitions
    - _Requirements: 4.4_

  - [ ] 4.6 Create SiblingsSection component
    - Display sibling cards near selected person
    - Apply de-emphasized styling (smaller, reduced opacity)
    - Handle case with no siblings
    - _Requirements: 5.1, 5.2, 5.4_

  - [ ] 4.7 Write property test for multiple sibling display
    - **Property 6: Multiple Sibling Display**
    - **Validates: Requirements 5.3**

  - [ ] 4.8 Implement SiblingsList with horizontal scrolling
    - Create horizontally scrollable container for siblings
    - Add scroll indicators if overflow
    - Handle many siblings gracefully
    - _Requirements: 5.3_

  - [ ] 4.9 Create ChildrenSection component
    - Display child cards below selected person
    - Apply smaller styling compared to selected person
    - Handle case with no children
    - _Requirements: 6.1, 6.4, 6.6_

  - [ ] 4.10 Write property test for all children display
    - **Property 7: All Children Display**
    - **Validates: Requirements 6.5**

  - [ ] 4.11 Ensure all children display regardless of spouse
    - Verify children from all spouses are shown
    - Test with children from multiple spouses
    - _Requirements: 6.5_

 - [ ] 4.12 Git commit all the change made for this task

- [ ] 5. Implement visual relationship connectors
  - [ ] 5.1 Create RelationshipLines component
    - Implement SVG-based line drawing
    - Support different line types: parent-child, spouse, sibling
    - Calculate line positions based on card positions
    - _Requirements: 3.3, 4.2, 6.2_

  - [ ] 5.2 Write unit tests for RelationshipLines
    - Test parent-child vertical lines
    - Test spouse horizontal lines
    - Test line positioning calculations
    - _Requirements: 3.3, 4.2, 6.2_

  - [ ] 5.3 Git commit all the change made for this task

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement person selection and navigation
  - [ ] 7.1 Write property test for person selection navigation
    - **Property 8: Person Selection Navigation**
    - **Validates: Requirements 7.1, 7.2, 7.3**

  - [ ] 7.2 Implement person selection logic
    - Handle click events on person cards
    - Update selected person state
    - Fetch new person's relationship data
    - Re-render tree centered on new person
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ] 7.3 Write unit test for loading indicator
    - Test loading indicator appears during data fetch
    - Test loading indicator disappears after data loads
    - _Requirements: 7.5_

  - [ ] 7.4 Add loading indicator during data fetch
    - Display loading overlay or spinner while fetching
    - Maintain previous data during loading (if available)
    - _Requirements: 7.5_

  - [ ] 7.5 Git commit all the change made for this task
- [ ] 8. Implement error handling
  - [ ] 8.1 Add error handling for no person profile
    - Display message prompting profile completion
    - Add link to profile completion page
    - _Requirements: 1.4_

  - [ ] 8.2 Write unit tests for error scenarios
    - Test API fetch failure handling
    - Test invalid person ID handling
    - Test empty relationship data handling
    - Test partial data handling

  - [ ] 8.3 Implement error recovery mechanisms
    - Add retry buttons for failed API calls
    - Show partial data if some relationships fail
    - Provide clear error messages
    - Add fallback navigation to user's own profile

  - [ ] 8.4 Git commit all the change made for this task
- [ ] 9. Implement responsive design
  - [ ] 9.1 Write property test for responsive layout adaptation
    - **Property 10: Responsive Layout Adaptation**
    - **Validates: Requirements 10.4**

  - [ ] 9.2 Implement responsive breakpoints
    - Desktop: Full layout with all sections visible
    - Tablet: Adjusted card sizes and spacing
    - Mobile: Vertical stacking, smaller cards
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [ ] 9.3 Write unit tests for touch interactions
    - Test touch events for selecting persons
    - Test touch scrolling for siblings/spouses
    - _Requirements: 10.5_

  - [ ] 9.4 Add touch interaction support
    - Ensure touch events work for person selection
    - Ensure touch scrolling works for horizontal lists
    - _Requirements: 10.5_

  - [ ] 9.5 Git commit all the change made for this task

- [ ] 10. Styling and polish
  - [ ] 10.1 Apply consistent styling with Tailwind CSS
    - Style all components following existing design patterns
    - Ensure visual hierarchy (selected person prominent)
    - Add hover states and transitions
    - Ensure color contrast for accessibility

  - [ ] 10.2 Add accessibility features
    - Add keyboard navigation support
    - Add ARIA labels for screen readers
    - Manage focus when navigating between persons
    - Ensure sufficient color contrast

  - [ ] 10.3 Optimize performance
    - Add React.memo to PersonCard components
    - Verify TanStack Query caching is working
    - Test with large family structures

  - [ ] 10.4 Git commit all the change made for this task

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The backend API endpoint already exists, so no backend changes are needed
- Focus on frontend implementation using React, TypeScript, TanStack Router, and TanStack Query
- All tests are required for comprehensive validation from the start
