# Implementation Plan: Person Details Panel

## Overview

This implementation plan covers adding a "View" button to person cards in the Family Tree view that opens a sliding panel displaying comprehensive person details. The implementation includes a new backend API endpoint and frontend components.

## Tasks

- [x] 1. Create backend schema for complete person details
  - Create `backend/app/schemas/person/person_complete_details.py`
  - Define `PersonAddressDetails` schema with resolved location names
  - Define `PersonReligionDetails` schema with resolved names
  - Define `PersonCompleteDetailsResponse` schema
  - Export schemas in `backend/app/schemas/person/__init__.py`
  - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 2. Implement backend API endpoint
  - [x] 2.1 Add `get_person_complete_details` method to PersonService
    - Fetch person by ID
    - Resolve gender name from gender_id
    - Fetch current address and resolve location names (country, state, district, sub-district, locality)
    - Fetch religion and resolve names (religion, category, sub-category)
    - Return complete details response
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [x] 2.2 Add API route `GET /api/v1/person/{person_id}/complete-details`
    - Add endpoint to `backend/app/api/routes/person/person.py`
    - Handle 404 for invalid person ID
    - Return `PersonCompleteDetailsResponse`
    - _Requirements: 4.1_

  - [ ]* 2.3 Write unit tests for complete details endpoint
    - Test successful response with all data
    - Test response with missing address (null)
    - Test response with missing religion (null)
    - Test 404 for invalid person ID
    - _Requirements: 4.1, 4.5, 4.6_

- [x] 3. Checkpoint - Backend API complete
  - Ensure all backend tests pass
  - Verify API returns correct data structure
  - Ask the user if questions arise

- [x] 4. Generate frontend API client
  - Run `npm run generate-client` to regenerate TypeScript types
  - Verify `PersonCompleteDetailsResponse` type is generated
  - _Requirements: 4.1_

- [x] 5. Create frontend hook for fetching person details
  - [x] 5.1 Create `frontend/src/hooks/usePersonCompleteDetails.ts`
    - Implement TanStack Query hook
    - Call `PersonService.getPersonCompleteDetails`
    - Return data, isLoading, error, and refetch
    - Configure appropriate cache settings
    - _Requirements: 5.1, 5.2_

  - [ ]* 5.2 Write unit tests for usePersonCompleteDetails hook
    - Test successful data fetch
    - Test loading state
    - Test error handling
    - _Requirements: 5.1, 5.2_

- [x] 6. Create PersonDetailsPanel component
  - [x] 6.1 Create `frontend/src/components/FamilyTree/PersonDetailsPanel.tsx`
    - Use Sheet component from ui/sheet
    - Display loading state with spinner
    - Display error state with retry button
    - Display person photo (Avatar with fallback)
    - Display full name (first, middle, last)
    - Display birth/death years in correct format
    - Display gender name
    - Display address as comma-separated values
    - Display religion as comma-separated values
    - Handle null values gracefully
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 5.1, 5.2, 5.3_

  - [ ]* 6.2 Write unit tests for PersonDetailsPanel
    - Test renders loading state
    - Test renders error state with retry button
    - Test renders all person details correctly
    - Test handles null address gracefully
    - Test handles null religion gracefully
    - Test close button works
    - **Property 2: Panel Open/Close State Consistency**
    - **Validates: Requirements 2.1, 2.2, 2.3**
    - _Requirements: 2.2, 2.3, 3.7, 5.1, 5.2_

- [x] 7. Modify PersonCard to add View button
  - [x] 7.1 Update PersonCard component
    - Add optional `onViewClick` prop
    - Add "View" button to card layout
    - Stop event propagation on View button click
    - Style button appropriately for each variant
    - Ensure keyboard accessibility (tabIndex, onKeyDown)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ]* 7.2 Write unit tests for PersonCard View button
    - Test View button renders when onViewClick provided
    - Test View button click calls onViewClick with person ID
    - Test View button click does not trigger card onClick
    - **Property 1: View Button Event Isolation**
    - **Validates: Requirements 1.4**
    - _Requirements: 1.1, 1.3, 1.4_

- [x] 8. Integrate PersonDetailsPanel into Family Tree view
  - [x] 8.1 Update family-tree.tsx
    - Add state for selected person ID for details panel
    - Add state for panel open/close
    - Add PersonDetailsPanel component
    - Pass onViewClick handler to PersonCard components
    - Wire up panel open/close logic
    - _Requirements: 1.1, 2.1_

  - [x] 8.2 Update section components to pass onViewClick
    - Update ParentsSection to pass onViewClick to PersonCard
    - Update HorizontalScrollRow to pass onViewClick to PersonCard
    - Update ChildrenSection to pass onViewClick to PersonCard
    - _Requirements: 1.1_

- [ ] 9. Final checkpoint - Feature complete
  - Ensure all tests pass
  - Verify end-to-end flow works correctly
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The Sheet component from `@/components/ui/sheet` provides the sliding panel functionality
- TanStack Query handles caching and loading states automatically
