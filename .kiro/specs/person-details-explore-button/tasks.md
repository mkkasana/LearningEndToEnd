# Implementation Plan: Person Details Explore Button

## Overview

This implementation adds an "Explore in Family Tree" button to the PersonDetailsPanel component. The button uses the existing explore pattern (sessionStorage + custom event) to navigate users to the Family Tree view with the selected person.

## Tasks

- [x] 1. Add Explore Button to PersonDetailsPanel
  - [x] 1.1 Add required imports (useNavigate, Network icon)
    - Import `useNavigate` from `@tanstack/react-router`
    - Import `Network` from `lucide-react`
    - _Requirements: 1.2_

  - [x] 1.2 Implement handleExplorePerson function
    - Create function that stores personId in sessionStorage
    - Close the panel via onOpenChange(false)
    - Navigate to /family-tree route
    - Dispatch custom event after 100ms delay
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 1.3 Add Explore button to the component JSX
    - Place button below Avatar, before Name section
    - Use outline variant Button component
    - Include Network icon and "Explore in Family Tree" text
    - Add aria-label for accessibility
    - Only render when data is loaded (not during loading/error states)
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.4, 4.1, 4.2, 4.3_

- [x] 2. Add Unit Tests for Explore Button
  - [x] 2.1 Create test file for PersonDetailsPanel explore functionality
    - Test button renders when data is loaded
    - Test button has correct text and icon
    - Test button has aria-label
    - Test button not rendered during loading state
    - Test button not rendered during error state
    - Test click handler stores personId in sessionStorage
    - Test click handler closes panel
    - Test click handler triggers navigation
    - _Requirements: 1.1, 1.2, 2.1, 2.2, 2.3, 3.4, 4.1, 4.2_

  - [ ]* 2.2 Write property test for sessionStorage persistence
    - **Property 1: Session Storage Persistence**
    - Generate random valid UUIDs
    - Simulate button click
    - Verify sessionStorage contains exact UUID
    - **Validates: Requirements 2.1**

  - [ ]* 2.3 Write property test for conditional rendering
    - **Property 3: Conditional Button Rendering**
    - Generate random combinations of loading/error/data states
    - Verify button presence matches expected condition
    - **Validates: Requirements 4.1, 4.2, 4.3**

- [x] 3. Checkpoint - Verify Implementation
  - Ensure all tests pass, ask the user if questions arise.
  - Manually verify the button appears in PersonDetailsPanel
  - Test the explore flow from Find Partner page

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The implementation reuses the existing explore pattern from ContributionStatsDialog
- No backend changes required - this is a frontend-only feature
- The Family Tree already handles the sessionStorage and custom event, so no changes needed there
