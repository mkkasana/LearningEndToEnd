# Implementation Plan: Global Person Search

## Overview

This implementation plan covers adding a dedicated Search page to the sidebar navigation with advanced filtering capabilities. The feature includes a new backend API endpoint and frontend components for browsing and searching persons.

## Tasks

- [x] 1. Backend: Create search schemas and request/response models
  - Create `PersonSearchFilterRequest` schema with all filter fields and pagination
  - Create `PersonSearchResult` schema for individual person results
  - Create `PersonSearchResponse` schema with results array, total, skip, limit
  - Add validators for birth year range (from <= to)
  - _Requirements: 10.2, 10.3, 10.5_

- [x] 2. Backend: Create PersonSearchService
  - [x] 2.1 Create `person_search_service.py` in services/person/
    - Implement `search_persons` method with filter logic
    - Reuse existing `_find_persons_by_address` pattern from PersonMatchingService
    - Reuse existing `_find_persons_by_religion` pattern from PersonMatchingService
    - Add birth year range filtering using EXTRACT(YEAR FROM date_of_birth)
    - Add optional gender filtering
    - Add optional name fuzzy matching (reuse calculate_name_match_score)
    - Implement pagination with skip/limit and total count
    - _Requirements: 10.6, 10.7, 10.8_

  - [ ]* 2.2 Write property test for address filter intersection
    - **Property 1: Address Filter Intersection**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

  - [ ]* 2.3 Write property test for religion filter intersection
    - **Property 2: Religion Filter Intersection**
    - **Validates: Requirements 6.1, 6.2, 6.3**

  - [ ]* 2.4 Write property test for birth year range bounds
    - **Property 3: Birth Year Range Bounds**
    - **Validates: Requirements 8.3, 8.4, 8.5**

  - [ ]* 2.5 Write property test for pagination consistency
    - **Property 4: Pagination Consistency**
    - **Validates: Requirements 10.4, 10.5, 10.6, 10.8**

- [x] 3. Backend: Create search API route
  - [x] 3.1 Create `search_person.py` in api/routes/person/
    - Add POST /search endpoint
    - Wire up PersonSearchService
    - Add proper error handling and logging
    - _Requirements: 10.1, 10.2_

  - [x] 3.2 Register route in api/main.py
    - Import search_person router
    - Include router with /person prefix
    - _Requirements: 10.2_

  - [ ]* 3.3 Write integration tests for search API
    - Test endpoint with various filter combinations
    - Test pagination parameters
    - Test error cases (invalid birth year range)
    - _Requirements: 10.2, 10.3, 10.4, 10.5_

- [x] 4. Checkpoint - Backend complete
  - Ensure all backend tests pass
  - Regenerate OpenAPI client: `npm run generate-client`
  - Ask the user if questions arise

- [x] 5. Frontend: Create PersonSearchCard component
  - [x] 5.1 Create `PersonSearchCard.tsx` in components/Search/
    - Display full name (first + middle + last)
    - Display birth year
    - Add "Explore" button with onClick handler
    - Style with existing card patterns
    - _Requirements: 9.2_

  - [ ]* 5.2 Write unit tests for PersonSearchCard
    - Test name rendering with/without middle name
    - Test birth year display
    - Test explore button click
    - _Requirements: 9.2_

- [x] 6. Frontend: Create SearchFilterPanel component
  - [x] 6.1 Create `SearchFilterPanel.tsx` in components/Search/
    - Use shadcn/ui Sheet component for slide-out panel
    - Add Name section: First Name, Last Name inputs
    - Add Address section: Cascading dropdowns (reuse existing patterns)
    - Add Religion section: Cascading dropdowns (reuse existing patterns)
    - Add Demographics section: Gender dropdown, Birth Year From/To inputs
    - Add Apply Filters and Reset buttons
    - Add close button
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 5.1-5.7, 6.1-6.5, 7.1, 7.2, 8.1, 8.2_

  - [ ]* 6.2 Write unit tests for SearchFilterPanel
    - Test panel open/close behavior
    - Test form validation (birth year range)
    - Test reset functionality
    - _Requirements: 3.2, 3.5, 3.6, 8.6_

- [x] 7. Frontend: Create usePersonSearch hook
  - Create `usePersonSearch.ts` in hooks/
  - Wrap TanStack Query with proper query key
  - Handle loading and error states
  - Enable keepPreviousData for smooth pagination
  - _Requirements: 11.2_

- [x] 8. Frontend: Create Search page route
  - [x] 8.1 Create `search.tsx` in routes/_layout/
    - Add page header with title and filter icon button
    - Integrate SearchFilterPanel with open/close state
    - Display results grid with PersonSearchCard components
    - Add pagination controls
    - Add loading state
    - Add empty state for no results
    - Add filter active indicator on filter button
    - Fetch user's default address/religion for initial filters
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.7, 9.1, 9.3, 9.4, 9.5, 11.4_

  - [ ]* 8.2 Write unit tests for Search page
    - Test default filter initialization
    - Test filter panel toggle
    - Test results display
    - Test pagination
    - _Requirements: 2.1, 2.2, 9.3_

- [x] 9. Frontend: Add Search to sidebar navigation
  - Update `AppSidebar.tsx` to add Search item after Life Events
  - Use Search icon from lucide-react
  - Set path to "/search"
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 10. Checkpoint - Frontend complete
  - Ensure all frontend tests pass
  - Rebuild docker images and test manually
  - Ask the user if questions arise

- [ ] 11. Final integration testing
  - [ ] 11.1 Manual end-to-end testing
    - Test sidebar navigation to Search page
    - Test default results load (user's locality)
    - Test filter panel open/close
    - Test various filter combinations
    - Test pagination
    - Test explore button navigation to family tree
    - _Requirements: 1.1, 1.2, 2.2, 3.2, 9.3_

  - [ ]* 11.2 Write E2E tests with Playwright
    - Test full search flow
    - Test filter application
    - Test navigation to family tree
    - _Requirements: 1.2, 2.2, 9.3_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Reuse existing patterns from PersonMatchingService for address/religion filtering
- Reuse existing cascading dropdown patterns from AddFamilyMemberDialog
