# Implementation Plan: Relatives Network

## Overview

This implementation plan covers the "Relatives Network" feature - a dedicated page for listing relatives up to a configurable depth with filtering capabilities. The implementation is split into backend (Python/FastAPI) and frontend (React/TypeScript) tasks, with all components in dedicated folders to avoid affecting existing features.

## Tasks

- [x] 1. Backend: Add configuration setting
  - [x] 1.1 Add `RELATIVES_NETWORK_MAX_DEPTH` to config
    - Add setting to `backend/app/core/config.py`
    - Default value: 20
    - _Requirements: 11.1, 11.2_

- [x] 2. Backend: Create schemas
  - [x] 2.1 Create `backend/app/schemas/relatives_network/` folder structure
    - Create `__init__.py` with exports
    - _Requirements: 12.5_
  - [x] 2.2 Create `relatives_network_schemas.py`
    - Implement `RelativesNetworkRequest` with validation
    - Implement `RelativeInfo` model
    - Implement `RelativesNetworkResponse` model
    - Add depth_mode validation (must be 'up_to' or 'only_at')
    - _Requirements: 10.2_

- [x] 3. Backend: Create service
  - [x] 3.1 Create `backend/app/services/relatives_network/` folder structure
    - Create `__init__.py` with exports
    - _Requirements: 12.3_
  - [x] 3.2 Implement `RelativesNetworkService` class
    - Implement `__init__` with session and max_depth from config
    - Implement `find_relatives` main method
    - _Requirements: 10.3_
  - [x] 3.3 Implement BFS traversal method `_bfs_traverse`
    - Use deque for level-by-level traversal
    - Track visited nodes with depth mapping
    - Return dict[person_id -> depth]
    - _Requirements: 10.3_
  - [x] 3.4 Implement depth mode filtering `_filter_by_depth_mode`
    - Handle 'up_to' mode: return all with depth <= N
    - Handle 'only_at' mode: return all with depth == N
    - _Requirements: 6.4, 6.5_
  - [x] 3.5 Implement filters `_apply_filters`
    - Living filter: exclude persons with date_of_death
    - Gender filter: match gender_id
    - Address filters: match address hierarchy
    - _Requirements: 8.2, 8.5, 7.7_
  - [x] 3.6 Implement `_enrich_relative_info`
    - Fetch person details (name, gender, birth/death year)
    - Fetch address (district, locality names)
    - Build RelativeInfo object
    - _Requirements: 10.4_
  - [x] 3.7 Implement self exclusion and result limiting
    - Exclude requesting person from results
    - Limit to 100 results maximum
    - _Requirements: 2.7, 3.4, 10.5, 10.6_
  - [ ]* 3.8 Write property test for self exclusion
    - **Property 1: Self Exclusion**
    - **Validates: Requirements 2.7, 10.6**
  - [ ]* 3.9 Write property test for depth bounds (up_to mode)
    - **Property 2: Depth Bounds - Up To Mode**
    - **Validates: Requirements 6.4**
  - [ ]* 3.10 Write property test for depth bounds (only_at mode)
    - **Property 3: Depth Bounds - Only At Mode**
    - **Validates: Requirements 6.5**
  - [ ]* 3.11 Write property test for max depth enforcement
    - **Property 4: Max Depth Enforcement**
    - **Validates: Requirements 6.6, 11.3**
  - [ ]* 3.12 Write property test for living filter
    - **Property 5: Living Filter Correctness**
    - **Validates: Requirements 8.2**
  - [ ]* 3.13 Write property test for gender filter
    - **Property 6: Gender Filter Correctness**
    - **Validates: Requirements 8.5**
  - [ ]* 3.14 Write property test for results limit
    - **Property 7: Results Limit**
    - **Validates: Requirements 3.4, 10.5**

- [x] 4. Backend: Create API route
  - [x] 4.1 Create `backend/app/api/routes/relatives_network/` folder structure
    - Create `__init__.py` with router export
    - _Requirements: 12.4_
  - [x] 4.2 Implement `find_relatives.py` route
    - POST `/find` endpoint
    - Validate request, call service, return response
    - Handle 404 for person not found
    - _Requirements: 10.1, 10.7_
  - [x] 4.3 Register route in main router
    - Add to `backend/app/api/main.py`
    - Use prefix `/api/v1/relatives-network`
    - _Requirements: 10.1_
  - [ ]* 4.4 Write unit tests for API route
    - Test valid request handling
    - Test 404 error for invalid person_id
    - Test 400 error for invalid depth_mode
    - _Requirements: 10.7_

- [x] 5. Checkpoint - Backend complete
  - Ensure all backend tests pass
  - Rebuild backend: `docker compose build --no-cache backend && docker compose up -d`
  - Regenerate OpenAPI client: `npm run generate-client` in frontend folder
  - Ask the user if questions arise

- [x] 6. Frontend: Create types and folder structure
  - [x] 6.1 Create `frontend/src/components/RelativesNetwork/` folder
    - Create `index.ts` barrel export
    - _Requirements: 12.1_
  - [x] 6.2 Create `types.ts`
    - Define `RelativesFilters` interface
    - Define `DEFAULT_FILTERS` constant (depth: 3, depthMode: 'up_to', livingOnly: true)
    - _Requirements: 2.2, 2.3, 2.4_

- [x] 7. Frontend: Create RelativeCard component
  - [x] 7.1 Implement `RelativeCard.tsx`
    - Gender-based avatar icon
    - Name display with truncation
    - Birth/death year formatting (YYYY - YYYY or just YYYY if alive)
    - District-locality display with truncation
    - Depth badge
    - View button
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  - [ ]* 7.2 Write unit tests for RelativeCard
    - Test rendering with various data combinations
    - Test truncation behavior
    - Test year formatting (alive vs deceased)
    - _Requirements: 4.3, 4.4_

- [x] 8. Frontend: Create RelativesFilterPanel component
  - [x] 8.1 Implement `RelativesFilterPanel.tsx`
    - Sheet component sliding from left
    - Depth number input (1 to max)
    - Depth mode toggle (Up to / Only at)
    - Living only checkbox (default: checked)
    - Gender dropdown (Any, Male, Female)
    - Cascading address dropdowns (Country → State → District → Sub-District → Locality)
    - Reset and Apply buttons
    - _Requirements: 6.1, 6.2, 6.3, 7.1, 8.1, 8.4, 9.1, 9.4, 9.6_
  - [ ]* 8.2 Write unit tests for RelativesFilterPanel
    - Test filter state management
    - Test cascading dropdown behavior
    - Test reset functionality
    - _Requirements: 9.5_

- [x] 9. Frontend: Create RelativesResultsGrid component
  - [x] 9.1 Implement `RelativesResultsGrid.tsx`
    - Responsive grid layout (1-4 columns)
    - Map relatives to RelativeCard components
    - Handle empty state
    - _Requirements: 3.2, 3.6_

- [x] 10. Frontend: Create main page route
  - [x] 10.1 Create `frontend/src/routes/_layout/relatives-network.tsx`
    - Page header with title and Filters button
    - Active person check (show message if not set)
    - Results count display
    - Loading state with skeleton cards
    - Error state display
    - Empty state display
    - Integration with RelativesFilterPanel
    - Integration with PersonDetailsPanel for View action
    - _Requirements: 1.3, 1.4, 1.5, 3.1, 3.3, 3.5, 3.6, 3.7, 5.1, 5.2_
  - [x] 10.2 Implement API call with TanStack Query
    - Query key includes activePersonId and filters
    - Auto-fetch on page load with defaults
    - Refetch on filter changes
    - _Requirements: 2.1_

- [x] 11. Frontend: Add sidebar navigation
  - [x] 11.1 Add "Relatives Network" menu item to AppSidebar
    - Add icon and label
    - Link to `/relatives-network` route
    - _Requirements: 1.1, 1.2_

- [x] 12. Checkpoint - Frontend complete
  - Ensure all frontend tests pass
  - Rebuild frontend: `docker compose build --no-cache frontend && docker compose up -d`
  - Test end-to-end flow manually
  - Ask the user if questions arise

- [x] 13. Final integration testing
  - [x] 13.1 Test complete flow
    - Navigate to Relatives Network from sidebar
    - Verify default search executes
    - Test filter panel interactions
    - Test View button opens PersonDetailsPanel
    - Test various depth/filter combinations
    - _Requirements: 1.1, 1.2, 2.1, 5.1_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests use `hypothesis` library for Python backend
- All components are in dedicated folders to avoid breaking existing features
- The PersonDetailsPanel is reused from existing FamilyTree components (only exception to isolation rule)
