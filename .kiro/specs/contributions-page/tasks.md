# Implementation Plan: Contributions Page

## Overview

This implementation plan adds a dedicated Contributions Page accessible from the sidebar navigation. The feature is frontend-only, reusing the existing `/api/v1/person/my-contributions` API endpoint. Implementation follows a bottom-up approach: Route → Component → Sidebar Integration.

## Tasks

- [x] 1. Create route configuration
  - [x] 1.1 Create contributions route file
    - Create `frontend/src/routes/_layout/contributions.tsx`
    - Configure route to render ContributionsPage component
    - _Requirements: 2.1_

- [x] 2. Create ContributionsPage component
  - [x] 2.1 Create base component structure
    - Create `frontend/src/components/Contributions/ContributionsPage.tsx`
    - Add page header with title "My Contributions" and BarChart3 icon
    - Add description text
    - _Requirements: 2.2_

  - [x] 2.2 Implement data fetching
    - Add useQuery hook to fetch from PersonService.getMyContributions()
    - Implement loading state with Loader2 spinner
    - Implement error state with error message
    - _Requirements: 2.4, 2.6_

  - [x] 2.3 Implement summary stats section
    - Create two Card components for Total Contributions and Total Views
    - Calculate totals from contributions array
    - Display with Users and Eye icons
    - _Requirements: 2.3_

  - [x] 2.4 Implement empty state
    - Display when contributions array is empty
    - Show helpful message and "Add Family Members" button
    - Navigate to /family on button click
    - _Requirements: 2.7_

  - [x] 2.5 Implement person cards grid
    - Create responsive grid layout (1/2/3 columns)
    - Use Card component for each person
    - _Requirements: 2.5, 6.1, 6.2, 6.3_

  - [x] 2.6 Implement person card content
    - Display full name (first_name + last_name)
    - Display active/deactivated status indicator (green/gray circle)
    - Display date range using formatDateRange helper
    - Display address with MapPin icon (if available)
    - Display view count with Eye icon in Badge
    - Add Explore button with Network icon
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

  - [x] 2.7 Implement Explore navigation
    - Add handleExplorePerson function
    - Store personId in sessionStorage
    - Navigate to /family-tree
    - Dispatch custom event for family tree component
    - _Requirements: 3.7_

- [x] 3. Add sidebar navigation item
  - [x] 3.1 Update AppSidebar component
    - Import BarChart3 icon from lucide-react
    - Add "My Contributions" item to baseItems array
    - Position after "Find Partner" and before "Report Ticket"
    - Set path to "/contributions"
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ] 4. Write unit tests
  - [ ]* 4.1 Test ContributionsPage component
    - Test loading state renders spinner
    - Test error state renders error message
    - Test empty state renders message and button
    - Test person cards render with correct data
    - Test summary stats calculate correctly
    - _Requirements: 2.3, 2.6, 2.7_

  - [ ]* 4.2 Test sidebar integration
    - Test "My Contributions" item exists in sidebar
    - Test item is positioned correctly
    - Test navigation to /contributions works
    - _Requirements: 1.1, 1.2, 1.4_

- [x] 5. Verify existing dialog still works
  - [x] 5.1 Manual verification
    - Open profile menu
    - Click "Contribution Stats"
    - Verify dialog opens and displays data correctly
    - _Requirements: 5.1, 5.2, 5.3_

- [ ] 6. Final checkpoint
  - Rebuild frontend: `docker compose build --no-cache frontend && docker compose up -d`
  - Test complete user flow
  - Verify sidebar navigation works
  - Verify page displays correctly on desktop/tablet/mobile
  - Verify Explore button navigates to family tree
  - Verify existing dialog still works
  - Ask user for final approval

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- No backend changes required - reuses existing API
- Existing ContributionStatsDialog remains unchanged
- Property tests not needed - existing contribution-stats tests cover data logic

