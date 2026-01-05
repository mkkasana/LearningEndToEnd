# Requirements Document: Life Events in Person Details Panel

## Introduction

This feature enhances the Person Details Panel (sliding panel opened from Family Tree View) to display life events for the viewed person. Users will be able to see a chronological list of significant life events for any family member they view, providing richer context about that person's life story.

## Glossary

- **Person Details Panel**: The sliding panel that opens when clicking "View" button on a person card in Family Tree
- **Life Event**: A significant occurrence in a person's life (birth, marriage, death, purchase, achievement, etc.)
- **Viewed Person**: The person whose details are being displayed in the panel (may or may not be the current user)
- **Current User**: The authenticated user viewing the panel
- **System**: The Person Details Panel with Life Events feature

## Requirements

### Requirement 1: Display Life Events in Person Details Panel

**User Story:** As a user, I want to see life events for any person I view in the Family Tree, so that I can understand their life story and significant milestones.

#### Acceptance Criteria

1. WHEN a user clicks the "View" button on any person card in Family Tree THEN the System SHALL display the Person Details Panel with a Life Events section
2. WHEN the Life Events section loads THEN the System SHALL fetch and display all life events for that person
3. WHEN life events exist for the person THEN the System SHALL display them sorted by date (most recent first: year DESC, month DESC, date DESC)
4. WHEN no life events exist for the person THEN the System SHALL display a message "No life events recorded"
5. THE System SHALL display the Life Events section below the existing person details (photo, name, gender, address, religion)

### Requirement 2: Life Event Display Format

**User Story:** As a user, I want to see clear and concise information about each life event, so that I can quickly understand what happened and when.

#### Acceptance Criteria

1. WHEN displaying a life event THEN the System SHALL show the event type icon
2. WHEN displaying a life event THEN the System SHALL show the event title
3. WHEN displaying a life event THEN the System SHALL show the event date in format:
   - "Month Day, Year" if all date components exist (e.g., "January 15, 2020")
   - "Month Year" if only month and year exist (e.g., "January 2020")
   - "Year" if only year exists (e.g., "2020")
4. WHEN displaying a life event THEN the System SHALL show the location if available (formatted as comma-separated: locality, sub-district, district, state, country)
5. WHEN displaying a life event THEN the System SHALL show the description if available
6. THE System SHALL use appropriate icons for each event type (birth, marriage, death, purchase, sale, achievement, education, career, health, travel, other)

### Requirement 3: Loading and Error States

**User Story:** As a user, I want clear feedback when life events are loading or if there's an error, so that I understand the system status.

#### Acceptance Criteria

1. WHEN the Person Details Panel opens THEN the System SHALL show a loading indicator in the Life Events section while fetching data
2. WHEN life events fail to load THEN the System SHALL display an error message "Failed to load life events"
3. WHEN life events fail to load THEN the System SHALL provide a "Retry" button to attempt loading again
4. THE loading state SHALL NOT prevent the panel from displaying other person details (photo, name, gender, address, religion)
5. THE loading state SHALL NOT prevent the user from closing the panel

### Requirement 4: Backend API Endpoint

**User Story:** As a developer, I need a backend API endpoint to fetch life events for any person by their ID, so that the frontend can display life events for viewed persons.

#### Acceptance Criteria

1. THE System SHALL provide a GET endpoint at `/api/v1/life-events/person/{person_id}`
2. THE endpoint SHALL accept a person_id path parameter (UUID)
3. THE endpoint SHALL accept optional query parameters: skip (default: 0) and limit (default: 100)
4. THE endpoint SHALL return life events sorted by date descending (year DESC, month DESC NULLS LAST, date DESC NULLS LAST)
5. THE endpoint SHALL return a 404 error if the person does not exist
6. THE endpoint SHALL be accessible to all authenticated users (users can view life events of any person in the family tree)
7. THE endpoint SHALL return the same LifeEventsPublic schema as the existing `/me` endpoint

### Requirement 5: Privacy and Access Control

**User Story:** As a user, I want to see life events for family members I can view in the Family Tree, respecting appropriate privacy boundaries.

#### Acceptance Criteria

1. THE System SHALL allow authenticated users to view life events for any person they can see in the Family Tree
2. THE System SHALL NOT restrict viewing life events based on relationship (if you can see the person in Family Tree, you can see their life events)
3. THE System SHALL require authentication to access the life events endpoint
4. THE System SHALL return appropriate error messages for unauthorized access attempts

### Requirement 6: Performance and UX

**User Story:** As a user, I want the Person Details Panel to load quickly and smoothly, even when including life events.

#### Acceptance Criteria

1. THE System SHALL load person details and life events in parallel (not sequentially)
2. THE System SHALL display person details immediately while life events are still loading
3. THE System SHALL limit life events to 100 records by default to ensure fast loading
4. THE System SHALL use the same data fetching patterns (TanStack Query) as other features for consistency
5. THE Life Events section SHALL be visually distinct from other person details sections

## Non-Functional Requirements

### Performance
- Life events API response time should be < 500ms for typical datasets
- Panel should remain responsive during data loading

### Accessibility
- Life events section should be keyboard navigable
- Screen readers should announce life events clearly
- Icons should have appropriate aria-labels

### Maintainability
- Follow existing codebase patterns (similar to PersonDetailsPanel, LifeEventsPage)
- Reuse existing components where possible
- Use consistent styling with the rest of the application

## Out of Scope

The following are explicitly out of scope for this feature:

1. Editing or deleting life events from the Person Details Panel (users must go to the Life Events page)
2. Adding new life events from the Person Details Panel
3. Filtering or searching life events within the panel
4. Pagination of life events (showing more than 100 events)
5. Viewing life events for persons outside the family tree
6. Privacy settings to hide specific life events from other users

## Success Metrics

- Users can successfully view life events for any person in the Family Tree
- Life events load within 500ms for 95% of requests
- No increase in Person Details Panel load time for person details
- Zero accessibility violations in the Life Events section
