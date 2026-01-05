# Implementation Plan: Block Exact Match Duplicates

## Overview

This implementation enhances the `ConnectExistingPersonStep` component to detect exact matches (score = 100 AND matching date of birth) and block users from creating duplicate person records. The implementation is frontend-only using TypeScript/React.

## Tasks

- [x] 1. Create exact match utility functions
  - [x] 1.1 Create `isExactMatch` helper function
    - Create new file `frontend/src/components/Family/exactMatchUtils.ts`
    - Implement function that returns true when match_score === 100 AND date_of_birth matches
    - Export function for use in component and tests
    - _Requirements: 1.1, 1.2_

  - [ ]* 1.2 Write property test for `isExactMatch` function
    - **Property 1: Exact Match Detection Accuracy**
    - Generate random PersonMatchResult with scores 0-100 and random DOBs
    - Verify function returns true iff score=100 AND DOB matches exactly
    - **Validates: Requirements 1.1, 1.2**

  - [x] 1.3 Create `findExactMatches` helper function
    - Implement function that filters array to return only exact matches
    - Handle empty arrays gracefully
    - _Requirements: 1.3_

  - [ ]* 1.4 Write property test for `findExactMatches` function
    - **Property 2: All Exact Matches Identified**
    - Generate arrays of random PersonMatchResults
    - Verify function returns exactly those with score=100 AND matching DOB
    - **Validates: Requirements 1.3**

- [x] 2. Implement exact match detection in component
  - [x] 2.1 Add exact match state derivation
    - Add `useMemo` to compute `exactMatches` from search results
    - Add `hasExactMatch` boolean derived state
    - Add `hasBlockingExactMatch` (exact match that is not already connected)
    - Add `allExactMatchesConnected` for special case handling
    - _Requirements: 1.1, 1.3, 4.1_

  - [ ]* 2.2 Write property test for blocking exact match detection
    - **Property 3: Create Button Disabled for Blocking Exact Matches**
    - Generate scenarios with exact matches (not already connected)
    - Verify hasBlockingExactMatch is true
    - **Validates: Requirements 2.1**

  - [ ]* 2.3 Write property test for no exact match scenario
    - **Property 4: Create Button Enabled When No Exact Match**
    - Generate scenarios with no exact matches
    - Verify hasBlockingExactMatch is false
    - **Validates: Requirements 1.4, 2.4**

- [x] 3. Implement sorting with exact matches first
  - [x] 3.1 Add sorting logic for results
    - Create `useMemo` to sort matchingPersons with exact matches first
    - Within each group, sort by match_score descending
    - _Requirements: 5.2_

  - [ ]* 3.2 Write property test for sorting
    - **Property 5: Exact Matches Sorted First**
    - Generate random arrays with mix of exact and non-exact matches
    - Verify all exact matches have lower indices than non-exact matches
    - **Validates: Requirements 5.2**

- [ ] 4. Checkpoint - Verify utility functions work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement UI changes for exact match warning
  - [x] 5.1 Add warning banner component
    - Import AlertTriangle icon from lucide-react
    - Add conditional rendering for warning banner when hasExactMatch is true
    - Show different message for allExactMatchesConnected case
    - _Requirements: 2.2, 3.1, 4.1_

  - [x] 5.2 Add exact match badge styling
    - Replace match score badge with "Exact Match" badge (destructive variant) for exact matches
    - Keep percentage badge for non-exact matches
    - _Requirements: 5.1, 5.3_

  - [ ]* 5.3 Write unit tests for warning banner rendering
    - Test banner renders when exact match exists
    - Test banner shows correct message for already-connected case
    - Test banner does not render when no exact match
    - _Requirements: 2.2, 4.1_

- [x] 6. Implement button state changes
  - [x] 6.1 Disable "Create New" button for exact matches
    - Add disabled condition: `hasBlockingExactMatch || allExactMatchesConnected`
    - Update button text to indicate why creation is blocked
    - _Requirements: 2.1, 4.2_

  - [x] 6.2 Handle Connect button state for already-connected exact matches
    - Connect button already disabled via `is_already_connected` flag
    - Verify existing behavior works correctly with exact matches
    - _Requirements: 3.2, 4.2_

  - [ ]* 6.3 Write property test for already-connected exact match
    - **Property 6: Both Buttons Disabled for Already-Connected Exact Match**
    - Generate exact matches with is_already_connected = true
    - Verify allExactMatchesConnected is true when all exact matches are connected
    - **Validates: Requirements 4.2**

  - [ ]* 6.4 Write property test for Connect button enabled
    - **Property 7: Connect Button Enabled for Non-Connected Exact Match**
    - Generate exact matches with is_already_connected = false
    - Verify Connect button should be enabled for these
    - **Validates: Requirements 3.2**

- [ ] 7. Checkpoint - Verify UI changes work correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Integration testing
  - [ ]* 8.1 Write integration test for exact match blocking flow
    - Test that user cannot proceed to create when exact match exists
    - Test that user can connect to exact match
    - _Requirements: 2.1, 3.3_

  - [ ]* 8.2 Write integration test for no exact match flow
    - Test that user can proceed to create when no exact match
    - _Requirements: 1.4, 2.4_

- [ ] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- This is a frontend-only implementation - no backend changes required
