# Implementation Plan: Find Partner UI

## Overview

This implementation plan creates the "Find Partner" feature as a new frontend page with a filter panel for searching potential marriage matches. The implementation is isolated in a new `FindPartner/` folder and reuses the existing `partner-match/find` backend API.

## Tasks

- [ ] 1. Set up project structure and types
  - [ ] 1.1 Create `frontend/src/components/FindPartner/` folder structure
    - Create `types.ts` with TypeScript interfaces (TagItem, PartnerFilters, props interfaces)
    - Create `index.ts` barrel export
    - _Requirements: 12.1_

  - [ ] 1.2 Create `frontend/src/components/FindPartner/utils/defaultsCalculator.ts`
    - Implement `calculateOppositeGender` function
    - Implement `calculateBirthYearRange` function
    - Implement `validateBirthYearRange` function
    - Implement `buildDefaultFilters` function
    - _Requirements: 3.2, 3.3, 4.2, 4.3, 4.5_

  - [ ]* 1.3 Write property tests for defaultsCalculator
    - **Property 1: Gender defaults to opposite of active person**
    - **Property 2: Birth year range defaults correctly**
    - **Property 3: Birth year validation rejects invalid ranges**
    - **Validates: Requirements 3.2, 3.3, 4.2, 4.3, 4.5**

- [ ] 2. Implement TagInput component
  - [ ] 2.1 Create `frontend/src/components/FindPartner/TagInput.tsx`
    - Implement multi-select tag display with removable badges
    - Implement dropdown for adding new items
    - Filter dropdown to exclude already selected items
    - _Requirements: 5.1, 5.3, 5.4, 5.5, 5.6, 6.1, 6.5, 7.1, 7.5, 8.1, 8.7_

  - [ ]* 2.2 Write property tests for TagInput operations
    - **Property 4: Tag add/remove operations maintain correct count**
    - **Validates: Requirements 5.4, 5.6**

- [ ] 3. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Implement PartnerFilterPanel component
  - [ ] 4.1 Create `frontend/src/components/FindPartner/PartnerFilterPanel.tsx`
    - Implement Sheet-based sliding panel layout
    - Add Gender dropdown filter
    - Add Birth Year range inputs with validation
    - Add Include Religions TagInput
    - Add Include Categories TagInput with cascading from religions
    - Add Include Sub-Categories TagInput with cascading from categories
    - Add Exclude Sub-Categories TagInput with cascading from categories
    - Add Search Depth dropdown (1-50, default 10)
    - Add Reset Filters and Find Matches buttons
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 4.1, 9.1, 9.2, 10.1, 10.3_

  - [ ] 4.2 Implement cascading filter logic
    - Fetch categories based on selected religions
    - Fetch sub-categories based on selected categories
    - Remove orphaned categories when religion is removed
    - Remove orphaned sub-categories when category is removed
    - _Requirements: 6.3, 6.4, 7.3, 7.4, 8.5, 8.6_

  - [ ]* 4.3 Write property tests for cascading filter logic
    - **Property 5: Cascading dropdown options are filtered by parent selections**
    - **Property 6: Cascading removal removes orphaned children**
    - **Validates: Requirements 6.3, 6.4, 7.3, 7.4, 8.5, 8.6**

- [ ] 5. Implement default values initialization
  - [ ] 5.1 Create hook for fetching active person defaults
    - Fetch active person's gender, birth year, religion, category, sub-category
    - Fetch mother's sub-category from relationships (graceful if missing)
    - Fetch maternal grandmother's sub-category (graceful if missing)
    - _Requirements: 2.4, 5.2, 6.2, 8.2, 8.3, 8.4_

  - [ ] 5.2 Integrate defaults into PartnerFilterPanel
    - Initialize filters with calculated defaults on mount
    - Handle missing data gracefully (empty defaults)
    - _Requirements: 3.4, 4.4, 5.7, 6.6_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Implement results display
  - [ ] 7.1 Create `frontend/src/components/FindPartner/PartnerResultsDisplay.tsx`
    - Display raw JSON response with pretty-printing
    - Show total matches count
    - Handle empty results with "No matches found" message
    - Handle loading state with spinner
    - Handle error state with error message
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 10.5, 10.6_

- [ ] 8. Implement main page route
  - [ ] 8.1 Create `frontend/src/routes/_layout/find-partner.tsx`
    - Set up route with TanStack Router
    - Integrate ActivePersonContext for seeker ID
    - Manage filter panel open/close state
    - Manage filter state and defaults
    - Implement API call to partner-match/find on "Find Matches" click
    - Display results using PartnerResultsDisplay
    - _Requirements: 1.2, 1.3, 10.4_

  - [ ] 8.2 Implement Reset Filters functionality
    - Restore all filters to initial default values
    - _Requirements: 10.2_

  - [ ]* 8.3 Write property tests for reset and API mapping
    - **Property 7: Reset restores all filters to defaults**
    - **Property 8: API call includes all current filter values**
    - **Validates: Requirements 9.3, 10.2, 10.4**

- [ ] 9. Add menu bar entry
  - [ ] 9.1 Add "Find Partner" menu item to navigation
    - Add menu item to sidebar/navigation component
    - Link to /find-partner route
    - _Requirements: 1.1_

- [ ] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The feature is isolated in `FindPartner/` folder to avoid conflicts with existing code
- Uses existing `partner-match/find` API without backend modifications

