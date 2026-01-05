# Implementation Plan: Life Events in Person Details Panel

## Overview

This implementation plan adds life events display to the Person Details Panel in the Family Tree view. The plan follows an incremental approach: backend API first, then frontend components, with testing throughout.

## Tasks

### Phase 1: Backend API Implementation

- [x] 1. Add new API endpoint for fetching person life events
  - [x] 1.1 Add endpoint to `backend/app/api/routes/life_events.py`
    - Add `GET /api/v1/life-events/person/{person_id}` endpoint
    - Accept path parameter: `person_id` (UUID)
    - Accept query parameters: `skip` (int, default 0), `limit` (int, default 100)
    - Use `PersonService` to verify person exists
    - Return 404 if person not found
    - Use `LifeEventService.get_life_events()` to fetch events
    - Return `LifeEventsPublic` schema
    - Add `@log_route` decorator
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_
  - [x] 1.2 Test the endpoint manually
    - Start backend server
    - Use curl or Postman to test endpoint
    - Verify response format matches `LifeEventsPublic`
    - Verify 404 for invalid person_id
    - Verify authentication is required
    - _Requirements: 4.1-4.7_
  - [x] 1.3 Git commit backend changes
    - Commit message: "feat: add API endpoint to fetch life events by person ID"

- [x] 2. Add backend tests for new endpoint
  - [x] 2.1 Add tests to `backend/tests/api/routes/test_life_events.py`
    - Test `test_get_person_life_events_success` - verify successful fetch
    - Test `test_get_person_life_events_not_found` - verify 404 for invalid person
    - Test `test_get_person_life_events_empty` - verify empty list when no events
    - Test `test_get_person_life_events_pagination` - verify skip/limit work
    - Test `test_get_person_life_events_sorting` - verify date sorting (year DESC, month DESC, date DESC)
    - Test `test_get_person_life_events_unauthorized` - verify auth required
    - _Requirements: 4.1-4.7, 5.3_
  - [x] 2.2 Run backend tests
    - Execute: `pytest backend/tests/api/routes/test_life_events.py -v`
    - Verify all tests pass
    - Fix any failures
  - [x] 2.3 Git commit test changes
    - Commit message: "test: add tests for person life events endpoint"

### Phase 2: Frontend Client Generation

- [x] 3. Regenerate OpenAPI client
  - [x] 3.1 Generate new client with updated endpoint
    - Ensure backend is running
    - Run client generation script
    - Verify `LifeEventsService.getPersonLifeEvents()` method exists in generated client
    - Verify method signature matches expected parameters
    - _Requirements: 4.1_
  - [x] 3.2 Git commit generated client
    - Commit message: "chore: regenerate OpenAPI client with person life events endpoint"

### Phase 3: Frontend Hook Implementation

- [x] 4. Create custom hook for fetching person life events
  - [x] 4.1 Create `frontend/src/hooks/usePersonLifeEvents.ts`
    - Import `useQuery` from TanStack Query
    - Import `LifeEventsService` from client
    - Create `usePersonLifeEvents(personId: string | null)` hook
    - Use query key: `["personLifeEvents", personId]`
    - Call `LifeEventsService.getPersonLifeEvents()` in queryFn
    - Set `enabled: !!personId` to only fetch when personId exists
    - Return query result with data, isLoading, error, refetch
    - _Requirements: 1.2, 3.1, 6.1, 6.4_
  - [x] 4.2 Test hook manually
    - Import hook in PersonDetailsPanel temporarily
    - Log results to console
    - Verify data fetches correctly
    - Verify loading states work
    - _Requirements: 3.1, 6.1_
  - [x] 4.3 Git commit hook
    - Commit message: "feat: add usePersonLifeEvents hook for fetching person life events"

### Phase 4: Life Events Display Components

- [x] 5. Create event type icons helper
  - [x] 5.1 Create `frontend/src/components/LifeEvents/eventTypeIcons.ts`
    - Import lucide-react icons (Baby, Heart, Cross, Home, DollarSign, Trophy, GraduationCap, Briefcase, Activity, Plane, Calendar)
    - Create `getEventTypeIcon(eventType: string): LucideIcon` function
    - Map event types to icons:
      - birth → Baby
      - marriage → Heart
      - death → Cross
      - purchase → Home
      - sale → DollarSign
      - achievement → Trophy
      - education → GraduationCap
      - career → Briefcase
      - health → Activity
      - travel → Plane
      - other → Calendar
    - Return Calendar as default for unknown types
    - _Requirements: 2.6_
  - [x] 5.2 Git commit helper
    - Commit message: "feat: add event type icons helper"

- [x] 6. Create LifeEventsList component
  - [x] 6.1 Create `frontend/src/components/LifeEvents/LifeEventsList.tsx`
    - Create `LifeEventsListProps` interface with `events` and `compact` props
    - Create `LifeEventsList` component that maps over events
    - Create `LifeEventCard` sub-component for individual events
    - Display event icon using `getEventTypeIcon()`
    - Display event title
    - Display formatted date using `formatEventDate()` helper
    - Display location using `formatEventLocation()` helper (not available so ignoring)
    - Display description (only in non-compact mode)
    - Apply compact styling when `compact={true}`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [x] 6.2 Create date formatting helper
    - Add `formatEventDate(year, month, date)` function
    - Return "Month Day, Year" if all components exist
    - Return "Month Year" if only month and year exist
    - Return "Year" if only year exists
    - _Requirements: 2.3_
  - [x] 6.3 Create location formatting helper
    - Add `formatEventLocation(event)` function
    - Combine locality, sub-district, district, state, country
    - Return comma-separated string or null if no location
    - _Requirements: 2.4_
  - [x] 6.4 Test component manually
    - Create test page with sample events
    - Verify rendering in both compact and normal modes
    - Verify date formatting for various date combinations
    - Verify location formatting
    - _Requirements: 2.1-2.6_
  - [x] 6.5 Git commit component
    - Commit message: "feat: add LifeEventsList component for displaying life events"

### Phase 5: Integrate Life Events into PersonDetailsPanel

- [x] 7. Update PersonDetailsPanel component
  - [x] 7.1 Import dependencies
    - Import `usePersonLifeEvents` hook
    - Import `LifeEventsList` component
    - Import `Calendar` icon from lucide-react
    - _Requirements: 1.1_
  - [x] 7.2 Add life events data fetching
    - Call `usePersonLifeEvents(personId)` hook
    - Destructure: `data: lifeEventsData`, `isLoading: isLoadingEvents`, `error: eventsError`, `refetch: refetchEvents`
    - _Requirements: 1.2, 3.1, 6.1_
  - [x] 7.3 Add Life Events section to panel
    - Add section after existing person details (below religion)
    - Add border-top separator
    - Add section heading "Life Events" with Calendar icon
    - _Requirements: 1.5, 6.5_
  - [x] 7.4 Implement loading state
    - Show Loader2 spinner while `isLoadingEvents` is true
    - Center spinner in section
    - _Requirements: 3.1, 3.4_
  - [x] 7.5 Implement error state
    - Show error message "Failed to load life events" when error exists
    - Add Retry button that calls `refetchEvents()`
    - Style with destructive text color
    - _Requirements: 3.2, 3.3_
  - [x] 7.6 Implement success state
    - Show "No life events recorded" message when data exists but array is empty
    - Show `<LifeEventsList events={lifeEventsData.data} compact />` when events exist
    - _Requirements: 1.3, 1.4, 2.1-2.6_
  - [x] 7.7 Verify parallel loading
    - Ensure person details and life events load independently
    - Person details should display even if life events are still loading
    - Life events error should not break person details display
    - _Requirements: 3.4, 6.1, 6.2_
  - [x] 7.8 Git commit changes
    - Commit message: "feat: integrate life events into PersonDetailsPanel"

### Phase 6: Manual Testing

- [ ] 8. Test complete feature end-to-end
  - [ ] 8.1 Test with person who has life events
    - Navigate to Family Tree
    - Click View button on person card
    - Verify panel opens with person details
    - Verify Life Events section appears
    - Verify events are displayed in correct order (most recent first)
    - Verify date formatting is correct
    - Verify location formatting is correct
    - Verify icons match event types
    - _Requirements: 1.1, 1.2, 1.3, 2.1-2.6_
  - [ ] 8.2 Test with person who has no life events
    - Click View button on person with no events
    - Verify "No life events recorded" message appears
    - _Requirements: 1.4_
  - [ ] 8.3 Test loading states
    - Open panel and observe loading spinner
    - Verify person details load independently
    - _Requirements: 3.1, 3.4, 6.1_
  - [ ] 8.4 Test error handling
    - Simulate network error (disconnect network or stop backend)
    - Open panel
    - Verify error message appears
    - Verify Retry button works
    - _Requirements: 3.2, 3.3_
  - [ ] 8.5 Test with different date formats
    - Verify events with full date (year, month, day)
    - Verify events with only year and month
    - Verify events with only year
    - _Requirements: 2.3_
  - [ ] 8.6 Test with partial location data
    - Verify events with full address
    - Verify events with partial address
    - Verify events with no address
    - _Requirements: 2.4_
  - [ ] 8.7 Test panel closing
    - Verify panel can close during life events loading
    - Verify panel can close when error occurs
    - _Requirements: 3.5_

### Phase 7: Frontend E2E Tests (Optional but Recommended)

- [ ] 9. Add E2E tests for life events in panel
  - [ ] 9.1 Create `frontend/tests/life-events-in-panel.spec.ts`
    - Test: Open person details panel and verify life events section appears
    - Test: Verify life events are displayed in correct order
    - Test: Verify empty state when no events exist
    - Test: Verify loading state while fetching
    - Test: Verify date formatting for different date combinations
    - Test: Verify location formatting with partial data
    - _Requirements: 1.1-1.5, 2.1-2.6, 3.1-3.5_
  - [ ] 9.2 Run E2E tests
    - Execute: `npm run test:e2e`
    - Verify all tests pass
    - Fix any failures
  - [ ] 9.3 Git commit tests
    - Commit message: "test: add E2E tests for life events in person details panel"

### Phase 8: Documentation and Cleanup

- [ ] 10. Update documentation
  - [ ] 10.1 Update API documentation
    - Document new endpoint in API docs
    - Add examples of request/response
    - _Requirements: 4.1-4.7_
  - [ ] 10.2 Update component documentation
    - Add JSDoc comments to new components
    - Document props and usage examples
    - _Requirements: 2.1-2.6_
  - [ ] 10.3 Git commit documentation
    - Commit message: "docs: document life events in person details panel feature"

- [ ] 11. Final review and cleanup
  - [ ] 11.1 Code review
    - Review all changes for code quality
    - Ensure consistent styling
    - Remove any console.logs or debug code
    - Verify error handling is comprehensive
  - [ ] 11.2 Performance check
    - Verify API response times are acceptable
    - Check for any unnecessary re-renders
    - Verify query caching works correctly
    - _Requirements: 6.1-6.5_
  - [ ] 11.3 Accessibility check
    - Verify keyboard navigation works
    - Check screen reader compatibility
    - Verify ARIA labels are appropriate
    - _Requirements: Non-functional requirements_
  - [ ] 11.4 Final git commit
    - Commit message: "chore: final cleanup for life events in person details panel"

## Testing Checklist

### Backend Tests
- [ ] Endpoint returns correct data for valid person_id
- [ ] Endpoint returns 404 for invalid person_id
- [ ] Endpoint returns empty list for person with no events
- [ ] Pagination (skip/limit) works correctly
- [ ] Events are sorted correctly (year DESC, month DESC, date DESC)
- [ ] Authentication is required

### Frontend Tests
- [ ] Life Events section appears in PersonDetailsPanel
- [ ] Events display in correct order
- [ ] Empty state shows when no events
- [ ] Loading state shows while fetching
- [ ] Error state shows on failure with retry button
- [ ] Date formatting works for all combinations
- [ ] Location formatting works with partial data
- [ ] Icons match event types correctly
- [ ] Compact mode styling works
- [ ] Panel can close during loading/error states

### Manual Testing
- [ ] Feature works end-to-end in browser
- [ ] UI looks good on desktop and mobile
- [ ] No console errors
- [ ] Performance is acceptable
- [ ] Accessibility is good

## Estimated Time

- Phase 1 (Backend API): 1-2 hours
- Phase 2 (Client Generation): 15 minutes
- Phase 3 (Frontend Hook): 30 minutes
- Phase 4 (Display Components): 2-3 hours
- Phase 5 (Integration): 1-2 hours
- Phase 6 (Manual Testing): 1 hour
- Phase 7 (E2E Tests): 2-3 hours (optional)
- Phase 8 (Documentation): 1 hour

**Total: 8-13 hours** (depending on whether E2E tests are included)

## Dependencies

- Backend must be deployed before frontend can use new endpoint
- OpenAPI client must be regenerated after backend changes
- LifeEventsList component must be created before integration

## Rollback Plan

If issues arise:
1. **Frontend**: Remove Life Events section from PersonDetailsPanel (revert commits)
2. **Backend**: Remove new endpoint (no breaking changes to existing features)
3. **Database**: No database changes, so no migration rollback needed

## Success Criteria

- [ ] Users can view life events for any person in Family Tree
- [ ] Life events display correctly with proper formatting
- [ ] Loading and error states work as expected
- [ ] All tests pass (backend and frontend)
- [ ] No performance degradation
- [ ] No accessibility issues
- [ ] Code is clean and well-documented
