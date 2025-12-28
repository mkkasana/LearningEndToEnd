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
  - [x] 3.1 Implement PersonCard component with variants
    - Create component with props: person, relationshipType, variant, onClick, showPhoto
    - Implement variants: selected, parent, spouse, sibling, child
    - Add click handler for navigation
    - _Requirements: 2.1, 2.3_

  - [ ] 3.2 Write property test for person information formatting
    - **Property 1: Person Information Formatting**
    - **Validates: Requirements 2.2, 3.4, 4.3, 6.3**

  - [x] 3.3 Implement person information display formatting
    - Display first name and last name
    - Format birth/death years as "YYYY - YYYY" or "YYYY -"
    - Show relationship label for non-selected cards
    - _Requirements: 2.2, 3.4, 4.3, 6.3_

  - [x] 3.4 Write unit tests for PersonCard edge cases
    - Test with missing photo (shows placeholder)
    - Test with missing middle name
    - Test with missing death date
    - Test different variants render with correct styling
    - _Requirements: 2.4, 2.5_

  - [x] 3.5 Implement photo display with fallback
    - Display profile photo if available
    - Show gender-based avatar placeholder if no photo
    - _Requirements: 2.4, 2.5_

 - [x] 3.6 Git commit all the change made for this task

- [ ] 4. Implement family tree layout sections
  - [x] 4.1 Create ParentsSection component
    - Display parent cards above selected person
    - Show mother and father side-by-side
    - Handle cases with 0, 1, or 2 parents
    - _Requirements: 3.1, 3.2, 3.5, 3.6_

  - [x] 4.2 Write property test for relationship display
    - **Property 4: Relationship Display**
    - **Validates: Requirements 3.1, 4.1, 5.1, 6.1**

  - [x] 4.3 Create SpouseSection component
    - Display spouse card(s) horizontally adjacent to selected person
    - Handle single spouse case
    - _Requirements: 4.1, 4.5_

  - [x] 4.4 Write property test for multiple spouse display
    - **Property 5: Multiple Spouse Display**
    - **Validates: Requirements 4.4**

  - [x] 4.5 Implement SpouseCarousel for multiple spouses
    - Create carousel/slideshow component for multiple spouses
    - Add prev/next navigation buttons
    - Add indicator dots showing current spouse
    - Implement smooth transitions
    - _Requirements: 4.4_

  - [x] 4.6 Create SiblingsSection component
    - Display sibling cards near selected person
    - Apply de-emphasized styling (smaller, reduced opacity)
    - Handle case with no siblings
    - _Requirements: 5.1, 5.2, 5.4_

  - [x] 4.7 Write property test for multiple sibling display
    - **Property 6: Multiple Sibling Display**
    - **Validates: Requirements 5.3**

  - [x] 4.8 Implement SiblingsList with horizontal scrolling
    - Create horizontally scrollable container for siblings
    - Add scroll indicators if overflow
    - Handle many siblings gracefully
    - _Requirements: 5.3_

  - [x] 4.9 Create ChildrenSection component
    - Display child cards below selected person
    - Apply smaller styling compared to selected person
    - Handle case with no children
    - _Requirements: 6.1, 6.4, 6.6_

  - [x] 4.10 Write property test for all children display
    - **Property 7: All Children Display**
    - **Validates: Requirements 6.5**

  - [x] 4.11 Ensure all children display regardless of spouse
    - Verify children from all spouses are shown
    - Test with children from multiple spouses
    - _Requirements: 6.5_

 - [x] 4.12 Git commit all the change made for this task

- [-] 5. Implement visual relationship connectors
  - [x] 5.1 Create RelationshipLines component
    - Implement SVG-based line drawing
    - Support different line types: parent-child, spouse, sibling
    - Calculate line positions based on card positions
    - _Requirements: 3.3, 4.2, 6.2_

  - [x] 5.2 Write unit tests for RelationshipLines
    - Test parent-child vertical lines
    - Test spouse horizontal lines
    - Test line positioning calculations
    - _Requirements: 3.3, 4.2, 6.2_

  - [x] 5.3 Git commit all the change made for this task

- [x] 7. Implement person selection and navigation
  - [x] 7.1 Write property test for person selection navigation
    - **Property 8: Person Selection Navigation**
    - **Validates: Requirements 7.1, 7.2, 7.3**

  - [x] 7.2 Implement person selection logic
    - Handle click events on person cards
    - Update selected person state
    - Fetch new person's relationship data
    - Re-render tree centered on new person
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 7.3 Write unit test for loading indicator
    - Test loading indicator appears during data fetch
    - Test loading indicator disappears after data loads
    - _Requirements: 7.5_

  - [x] 7.4 Add loading indicator during data fetch
    - Display loading overlay or spinner while fetching
    - Maintain previous data during loading (if available)
    - _Requirements: 7.5_

  - [x] 7.5 Git commit all the change made for this task
- [x] 8. Implement error handling
  - [x] 8.1 Add error handling for no person profile
    - Display message prompting profile completion
    - Add link to profile completion page
    - _Requirements: 1.4_

  - [x] 8.2 Write unit tests for error scenarios
    - Test API fetch failure handling
    - Test invalid person ID handling
    - Test empty relationship data handling
    - Test partial data handling

  - [x] 8.3 Implement error recovery mechanisms
    - Add retry buttons for failed API calls
    - Show partial data if some relationships fail
    - Provide clear error messages
    - Add fallback navigation to user's own profile

  - [x] 8.4 Git commit all the change made for this task
- [x] 9. Implement responsive design
  - [x] 9.1 Write property test for responsive layout adaptation
    - **Property 10: Responsive Layout Adaptation**
    - **Validates: Requirements 10.4**

  - [x] 9.2 Implement responsive breakpoints
    - Desktop: Full layout with all sections visible
    - Tablet: Adjusted card sizes and spacing
    - Mobile: Vertical stacking, smaller cards
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 9.3 Write unit tests for touch interactions
    - Test touch events for selecting persons
    - Test touch scrolling for siblings/spouses
    - _Requirements: 10.5_

  - [x] 9.4 Add touch interaction support
    - Ensure touch events work for person selection
    - Ensure touch scrolling works for horizontal lists
    - _Requirements: 10.5_

  - [x] 9.5 Git commit all the change made for this task

- [x] 10. Styling and polish
  - [x] 10.1 Apply consistent styling with Tailwind CSS
    - Style all components following existing design patterns
    - Ensure visual hierarchy (selected person prominent)
    - Add hover states and transitions
    - Ensure color contrast for accessibility

  - [x] 10.2 Add accessibility features
    - Add keyboard navigation support
    - Add ARIA labels for screen readers
    - Manage focus when navigating between persons
    - Ensure sufficient color contrast

  - [x] 10.3 Optimize performance
    - Add React.memo to PersonCard components
    - Verify TanStack Query caching is working
    - Test with large family structures

  - [x] 10.4 Git commit all the change made for this task

- [x] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## UI Improvement Tasks (Horizontal Scrolling Layout)

- [x] 12. Refactor layout to three-row horizontal scrolling design
  - [x] 12.1 Create HorizontalScrollRow component
    - Implement unified component for displaying people in horizontally scrollable rows
    - Support variants: 'parent', 'center', 'child'
    - Add color-coding support for center row (siblings vs spouses)
    - Ensure smooth horizontal scrolling with scroll indicators
    - Make touch-friendly for mobile devices
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 12.2 Write property test for three-row horizontal layout
    - **Property 11: Three-Row Horizontal Layout**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

  - [x] 12.3 Refactor ParentsSection to use HorizontalScrollRow
    - Replace existing parent layout with HorizontalScrollRow
    - Ensure all parents display horizontally without vertical stacking
    - Test with 0, 1, 2, and many parents
    - _Requirements: 9.2_

  - [x] 12.4 Refactor center section to combine siblings and spouses
    - Merge SiblingsSection and SpouseSection into single HorizontalScrollRow
    - Position siblings on left, selected person in center, spouses on right
    - Add color-coding to differentiate siblings from spouses
    - Ensure horizontal scrolling works for many siblings/spouses
    - _Requirements: 9.3_

  - [x] 12.5 Refactor ChildrenSection to use HorizontalScrollRow
    - Replace existing children layout with HorizontalScrollRow
    - Ensure all children display horizontally without vertical stacking
    - Test with 0, 1, and many children
    - _Requirements: 9.4_

  - [x] 12.6 Write unit tests for HorizontalScrollRow
    - Test horizontal scrolling behavior
    - Test color-coding in center row
    - Test scroll indicators appear when needed
    - Test touch interactions on mobile
    - _Requirements: 9.5, 9.7_

  - [x] 12.7 Update responsive styles for all screen sizes
    - Ensure three-row layout maintained on mobile, tablet, and desktop
    - Adjust card sizes based on viewport
    - Verify no vertical stacking occurs on any screen size
    - Test horizontal scrolling works on all devices
    - _Requirements: 9.5, 9.6_

  - [x] 12.8 Update RelationshipLines for new layout
    - Adjust line drawing logic for three-row layout
    - Ensure lines connect properly in horizontal scroll containers
    - Test with various family structures

  - [x] 12.9 Git commit all changes made for this task

- [x] 13. Final checkpoint - Verify UI improvements
  - Test on desktop, tablet, and mobile viewports
  - Verify no vertical stacking of same-type relationships
  - Verify horizontal scrolling works smoothly
  - Verify color-coding clearly differentiates siblings from spouses
  - Ensure all tests pass

## UI Polish Tasks (Centering and Color Coding)

- [-] 14. Implement selected person centering and comprehensive color coding
  - [x] 14.1 Write property test for selected person centering
    - **Property 12: Selected Person Centering**
    - **Validates: Requirements 9.8, 9.9**

  - [x] 14.2 Implement auto-scroll to center selected person
    - Add scroll logic to HorizontalScrollRow to center the selected person
    - Use scrollIntoView or manual scroll calculation
    - Trigger on initial render and when person selection changes
    - Ensure smooth scrolling animation
    - _Requirements: 9.8, 9.9_

  - [x] 14.3 Write property test for relationship type color coding
    - **Property 13: Relationship Type Color Coding**
    - **Validates: Requirements 9.2, 9.3, 9.4**

  - [x] 14.4 Extend color coding to all relationship types
    - Add distinct colors for parents (e.g., blue/indigo)
    - Add distinct colors for children (e.g., green/emerald)
    - Keep existing colors for siblings and spouses
    - Ensure selected person has most prominent styling
    - Update PersonCard component to accept color variant
    - _Requirements: 9.2, 9.3, 9.4_

  - [ ] 14.5 Write unit tests for centering behavior
    - Test selected person is centered on initial render
    - Test selected person is centered after selection change
    - Test centering works with different numbers of siblings/spouses
    - _Requirements: 9.8, 9.9_

  - [ ] 14.6 Write unit tests for color coding
    - Test parent cards have parent color
    - Test sibling cards have sibling color
    - Test spouse cards have spouse color
    - Test child cards have child color
    - Test selected person has selected styling
    - _Requirements: 9.2, 9.3, 9.4_

  - [ ] 14.7 Update documentation and comments
    - Document color scheme in design document
    - Add comments explaining centering logic
    - Update component prop documentation

  - [x] 14.8 Git commit all changes made for this task

- [x] 15. Final checkpoint - Verify centering and color coding
  - Test selected person is always centered initially
  - Test all relationship types have distinct colors
  - Test color scheme is visually clear and accessible
  - Verify smooth scrolling animation
  - Ensure all tests pass

## UI Refinement Tasks (Center All Rows and Distinct Colors)

- [x] 16. Refine row centering and color palette
  - [x] 16.1 Write property test for row content centering
    - **Property 14: Row Content Centering**
    - **Validates: Requirements 9.2, 9.4**

  - [x] 16.2 Implement center alignment for parents and children rows
    - Update HorizontalScrollRow to center content when narrower than viewport
    - Apply to parent row (top)
    - Apply to children row (bottom)
    - Use CSS flexbox justify-center or similar approach
    - Maintain scrollability when content exceeds viewport width
    - _Requirements: 9.2, 9.4_

  - [x] 16.3 Update color palette to be more distinct
    - Change parent color to light amber/orange (bg-amber-100, border-amber-300)
    - Change sibling color to light blue/sky (bg-blue-100, border-blue-300)
    - Change spouse color to light purple/violet (bg-purple-100, border-purple-300)
    - Change children color to light pink/rose (bg-pink-100, border-pink-300)
    - Keep selected person as light green with prominent border (bg-green-100, border-green-500)
    - Ensure all colors are light and easily distinguishable
    - _Requirements: 9.10_

  - [x] 16.4 Write unit tests for row centering
    - Test parent row centers when content is narrow
    - Test children row centers when content is narrow
    - Test rows remain scrollable when content is wide
    - _Requirements: 9.2, 9.4_

  - [x] 16.5 Update unit tests for new color palette
    - Update color assertions in PersonCard tests
    - Update color assertions in HorizontalScrollRow tests
    - Verify each relationship type has correct color
    - _Requirements: 9.10_

  - [x] 16.6 Update design documentation with color scheme
    - Document the specific color palette in design.md
    - Add rationale for color choices (distinguishability, accessibility)
    - Include Tailwind class names for reference

  - [x] 16.7 Git commit all changes made for this task

- [x] 17. Final checkpoint - Verify all UI refinements
  - Test all rows center their content appropriately
  - Test parent row uses amber/orange color
  - Test sibling row uses blue color
  - Test spouse row uses purple color
  - Test children row uses pink color
  - Test selected person uses green with prominent styling
  - Verify colors are distinct and easily distinguishable
  - Test on desktop, tablet, and mobile viewports
  - Ensure all tests pass

## Visual Enhancement Tasks (Relationship Lines and Spouse Differentiation)

- [ ] 18. Add visual relationship lines between generations
  - [x] 18.1 Implement parent-to-children connecting lines
    - Draw vertical lines from parents row to center row (selected person and siblings)
    - Connect each parent to their children in the center row
    - Use SVG paths for smooth, scalable lines
    - Ensure lines work with horizontal scrolling
    - _Requirements: 3.3_

  - [x] 18.2 Implement selected-person-to-children connecting lines
    - Draw vertical lines from center row (selected person and spouses) to children row
    - Connect selected person to their children
    - Connect spouses to their children (if applicable)
    - Handle multiple spouses with children from different relationships
    - _Requirements: 6.2_

  - [x] 18.3 Write unit tests for generation connecting lines
    - Test parent-to-children lines render correctly
    - Test selected-person-to-children lines render correctly
    - Test lines update when scrolling horizontally
    - Test lines work with various family structures (0-N parents, 0-N children)

  - [x] 18.4 Update RelationshipLines component for generation connections
    - Extend component to support vertical generation lines
    - Calculate line positions dynamically based on card positions
    - Handle edge cases (no parents, no children, scrolled positions)

  - [x] 18.5 Git commit all changes made for this task

- [-] 19. Add visual differentiation for spouses
  - [x] 19.1 Implement reduced opacity for spouse cards
    - Apply opacity reduction (0.7-0.8) to spouse cards in center row
    - Maintain readability while creating visual hierarchy
    - Ensure selected person remains fully opaque
    - Keep siblings at normal opacity
    - _Requirements: 4.1_

  - [x] 19.2 Write unit tests for spouse visual differentiation
    - Test spouse cards have reduced opacity
    - Test selected person has full opacity
    - Test sibling cards have full opacity
    - Test opacity values are correct

  - [x] 19.3 Update PersonCard component for spouse opacity
    - Add opacity styling based on relationship type
    - Ensure opacity works with existing color coding
    - Test visual hierarchy is clear and intuitive

  - [x] 19.4 Git commit all changes made for this task

- [ ] 20. Final checkpoint - Verify visual enhancements
  - Test connecting lines appear between parents and center row
  - Test connecting lines appear between center row and children
  - Test lines work correctly with horizontal scrolling
  - Test spouse cards have reduced opacity
  - Test visual hierarchy clearly differentiates blood relatives from spouses
  - Verify enhancements work on desktop, tablet, and mobile
  - Ensure all tests pass

## Notes

- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The backend API endpoint already exists, so no backend changes are needed
- Focus on frontend implementation using React, TypeScript, TanStack Router, and TanStack Query
- All tests are required for comprehensive validation from the start
