# Implementation Plan: Contribution Stats

## Overview

This implementation plan breaks down the Contribution Stats feature into discrete, incremental tasks. Each task builds on previous work and includes validation through code execution. The implementation follows a bottom-up approach: Database → Repository → Service → API → Frontend.

## Tasks

- [x] 1. Create database model and migration
  - Create ProfileViewTracking SQLModel with all required fields
  - Generate Alembic migration for profile_view_tracking table
  - Include foreign key constraints and indexes
  - Run migration and verify table creation
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_

- [x] 1.1 Write unit tests for ProfileViewTracking model
  - Test model instantiation with default values
  - Test field constraints and types
  - _Requirements: 2.7, 2.8_

- [x] 2. Implement ProfileViewTrackingRepository
  - [x] 2.1 Create ProfileViewTrackingRepository class extending BaseRepository
    - Implement `get_non_aggregated_view()` method
    - Implement `get_total_views_for_person()` method
    - Implement `get_total_views_for_persons()` bulk method
    - _Requirements: 4.1, 4.2, 4.3, 7.1, 7.3, 7.4_

  - [x] 2.2 Write unit tests for ProfileViewTrackingRepository
    - Test `get_non_aggregated_view()` with existing and non-existing pairs
    - Test `get_total_views_for_person()` with zero views
    - Test `get_total_views_for_persons()` with empty list
    - Test aggregation with mixed aggregated/non-aggregated records
    - _Requirements: 4.3, 4.4, 4.6_

  - [ ]* 2.3 Write property test for view count aggregation
    - **Property 12: View Count Aggregation**
    - **Validates: Requirements 4.2, 4.3**

- [x] 3. Extend PersonRepository
  - [x] 3.1 Add `get_by_creator()` method to PersonRepository
    - Query persons WHERE created_by_user_id matches user ID
    - Return list of Person objects
    - _Requirements: 1.1, 7.5_

  - [x] 3.2 Write unit tests for `get_by_creator()`
    - Test with user who created no persons
    - Test with user who created multiple persons
    - Test that only persons by that creator are returned
    - _Requirements: 1.1_

  - [x] 3.3 Write property test for contribution query correctness
    - **Property 1: Contribution Query Correctness**
    - **Validates: Requirements 1.1**

- [x] 4. Implement ProfileViewTrackingService
  - [x] 4.1 Create ProfileViewTrackingService class
    - Implement `record_view()` method with create/update logic
    - Implement `get_total_views()` method
    - Implement `get_total_views_bulk()` method
    - Add error handling (log but don't raise)
    - Include self-view prevention logic
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 4.1, 7.2, 7.3_

  - [x] 4.2 Write unit tests for ProfileViewTrackingService
    - Test `record_view()` with self-view (should not record)
    - Test `record_view()` with first view (creates new record)
    - Test `record_view()` with subsequent view (increments count)
    - Test `record_view()` with database error (should not raise)
    - Test `get_total_views()` with person who has no views
    - Test `get_total_views_bulk()` with empty list
    - _Requirements: 3.4, 3.5, 3.6, 3.7, 3.8, 4.4, 4.6_

  - [x] 4.3 Write property tests for view recording
    - **Property 7: View Recording on Endpoint Call**
    - **Property 9: First View Creates New Record**
    - **Property 10: Subsequent Views Increment Count**
    - **Property 11: Error Resilience**
    - **Validates: Requirements 3.1, 3.6, 3.7, 3.8**

- [ ]* 5. Checkpoint - Ensure repository and service tests pass
  - Run all repository and service tests
  - Verify database operations work correctly
  - Ask user if questions arise


- [x] 6. Extend PersonService for contributions
  - [x] 6.1 Add `get_my_contributions()` method to PersonService
    - Query persons by creator using PersonRepository
    - Fetch addresses for each person
    - Fetch view counts using ProfileViewTrackingService
    - Format addresses as comma-separated string
    - Build response with all required fields
    - Sort by total_views descending
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 5.1, 5.2, 5.3, 5.4, 5.5, 7.6_

  - [x] 6.2 Add `_format_addresses()` helper method
    - Concatenate address components with commas
    - Handle empty address lists
    - _Requirements: 1.3, 5.3_

  - [x] 6.3 Write unit tests for PersonService contributions
    - Test `get_my_contributions()` with user who has no contributions
    - Test `get_my_contributions()` with user who has multiple contributions
    - Test `_format_addresses()` with empty list
    - Test `_format_addresses()` with single address
    - Test `_format_addresses()` with multiple addresses
    - Verify sorting by view count
    - _Requirements: 1.7, 5.5, 5.6_

  - [x] 6.4 Write property tests for contribution formatting
    - **Property 2: Name Display Format**
    - **Property 3: Address Formatting**
    - **Property 4: Date Range Formatting for Living Persons**
    - **Property 5: Date Range Formatting for Deceased Persons**
    - **Property 15: Contributions Sorted by View Count**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 5.5**

- [x] 7. Create API schemas
  - [x] 7.1 Create PersonContributionPublic schema
    - Define all required fields (id, first_name, last_name, dates, address, views)
    - Add Pydantic validation
    - _Requirements: 5.2, 5.3, 5.4_

  - [x] 7.2 Write unit tests for schemas
    - Test schema validation with valid data
    - Test schema serialization
    - _Requirements: 5.2_

- [x] 8. Implement contributions API endpoint
  - [x] 8.1 Add GET /api/v1/person/my-contributions endpoint
    - Use CurrentUser dependency for authentication
    - Call PersonService.get_my_contributions()
    - Return list of PersonContributionPublic
    - Add logging
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

  - [x] 8.2 Write integration tests for contributions endpoint
    - Test endpoint with authenticated user
    - Test endpoint returns correct data structure
    - Test endpoint with user who has no contributions
    - Test endpoint with user who has multiple contributions
    - Verify sorting by view count
    - _Requirements: 5.1, 5.5, 5.6_

  - [x]* 8.3 Write property test for response completeness
    - **Property 14: Contributions API Response Completeness**
    - **Validates: Requirements 5.2, 5.3, 5.4**

- [x] 9. Add profile view tracking to relationships endpoint
  - [x] 9.1 Modify GET /person/{person_id}/relationships/with-details endpoint
    - Get viewer's person record from current_user
    - Call ProfileViewTrackingService.record_view()
    - Wrap in try-except to prevent failures
    - Add logging
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.8_

  - [x]* 9.2 Write integration tests for view tracking
    - Test view is recorded when endpoint is called
    - Test self-view is not recorded
    - Test viewer without person record doesn't create view
    - Test subsequent views increment count
    - Test view tracking error doesn't break endpoint
    - _Requirements: 3.1, 3.4, 3.5, 3.7, 3.8_

  - [x]* 9.3 Write property test for correct viewer/viewed mapping
    - **Property 8: Correct Viewer and Viewed Mapping**
    - **Validates: Requirements 3.2, 3.3**

- [ ]* 10. Checkpoint - Ensure all backend tests pass
  - Run full backend test suite
  - Verify API endpoints work correctly
  - Test view tracking in development environment
  - Ask user if questions arise


- [ ] 11. Create frontend TypeScript types
  - [ ] 11.1 Add PersonContributionPublic interface to types
    - Define all fields matching backend schema
    - Export from types file
    - _Requirements: 5.2, 5.3, 5.4_

- [ ] 12. Implement frontend API client
  - [ ] 12.1 Add getMyContributions() method to PersonService
    - Make GET request to /api/v1/person/my-contributions
    - Return typed response
    - Handle errors
    - _Requirements: 5.1_

- [ ] 13. Create ContributionStatsDialog component
  - [ ] 13.1 Create ContributionStatsDialog.tsx component
    - Implement dialog with open/close state
    - Add loading state with spinner
    - Add error state with message
    - Add empty state with helpful message
    - Fetch contributions on dialog open
    - _Requirements: 6.1, 6.2, 6.3, 6.9, 6.10_

  - [ ] 13.2 Implement contribution list display
    - Display person name (first + last)
    - Display formatted address with MapPin icon
    - Display date range with Calendar icon
    - Display active/deactivated status (green/gray circle)
    - Display view count with Eye icon and Badge
    - Add hover effects
    - _Requirements: 6.4, 6.5, 6.6, 6.7, 6.8_

  - [ ] 13.3 Add date formatting helper
    - Format birth-death range for deceased persons
    - Format birth year only for living persons
    - _Requirements: 6.6_

- [ ] 14. Integrate ContributionStatsDialog into navigation
  - [ ] 14.1 Add "Contribution Stats" menu item
    - Add to user profile menu or navigation
    - Add appropriate icon (BarChart or similar)
    - Wire up dialog open/close state
    - _Requirements: 6.1, 6.2_

- [ ] 15. Final integration testing
  - [ ] 15.1 Test complete user flow
    - Create user and person
    - Create multiple family members
    - Have another user view those profiles
    - Open Contribution Stats dialog
    - Verify all data displays correctly
    - Verify view counts are accurate
    - Verify sorting by view count
    - _Requirements: All_

- [ ] 16. Final checkpoint - Complete feature verification
  - Test all functionality in development environment
  - Verify database migrations applied correctly
  - Verify view tracking works automatically
  - Verify contribution stats display correctly
  - Verify UI matches design requirements
  - Ask user for final approval

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Integration tests verify end-to-end workflows
