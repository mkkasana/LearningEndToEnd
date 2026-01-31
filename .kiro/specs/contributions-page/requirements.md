# Requirements Document: Contributions Page

## Introduction

This feature adds a dedicated "My Contributions" page accessible from the sidebar navigation. Currently, contribution stats are only viewable via a dialog from the user profile menu. This enhancement provides a full-page experience for viewing contributions, offering better visibility and a more prominent placement in the navigation.

## Glossary

- **Contributions_Page**: A full-page view displaying all persons created by the current user with their view statistics
- **Sidebar_Navigation**: The main navigation menu on the left side of the application
- **Person_Card**: A UI component displaying individual person details and statistics
- **View_Count**: The total number of times a person's profile has been viewed by other users
- **Contribution_Stats_Dialog**: The existing dialog component that displays contribution stats (to be retained)

## Requirements

### Requirement 1: Sidebar Navigation Integration

**User Story:** As a user, I want to access my contributions from the sidebar menu, so that I can quickly view my contribution statistics without navigating through the profile menu.

#### Acceptance Criteria

1. THE System SHALL add a "My Contributions" menu item to the sidebar navigation
2. WHEN displaying the sidebar, THE System SHALL position "My Contributions" after "Find Partner" and before "Report Ticket"
3. THE System SHALL use the BarChart3 icon (or similar analytics icon) for the "My Contributions" menu item
4. WHEN a user clicks "My Contributions", THE System SHALL navigate to the /contributions route

### Requirement 2: Contributions Page Layout

**User Story:** As a user, I want to see my contributions in a full-page layout, so that I have more space to view and interact with my contribution data.

#### Acceptance Criteria

1. THE System SHALL create a new route at /contributions for the contributions page
2. WHEN the contributions page loads, THE System SHALL display a page header with title "My Contributions"
3. WHEN the contributions page loads, THE System SHALL display a summary section showing total contributions count and total views count
4. WHEN the contributions page loads, THE System SHALL fetch and display all persons created by the current user
5. WHEN displaying contributions, THE System SHALL show each person in a card format with adequate spacing
6. WHEN the page is loading, THE System SHALL display a loading indicator
7. WHEN there are no contributions, THE System SHALL display an empty state with a helpful message

### Requirement 3: Person Card Display

**User Story:** As a user, I want to see detailed information about each person I created, so that I can understand my contributions and their engagement.

#### Acceptance Criteria

1. WHEN displaying a person card, THE System SHALL show the full name (first_name + last_name)
2. WHEN displaying a person card, THE System SHALL show the active/deactivated status indicator (green circle for active, gray circle for deactivated)
3. WHEN displaying a person card, THE System SHALL show the birth year for living persons
4. WHEN displaying a person card for a deceased person, THE System SHALL show birth year hyphen death year
5. WHEN displaying a person card, THE System SHALL show the formatted address if available
6. WHEN displaying a person card, THE System SHALL show the total view count with an Eye icon
7. WHEN displaying a person card, THE System SHALL provide an "Explore" button to navigate to that person in the family tree

### Requirement 4: Sorting and Organization

**User Story:** As a user, I want my contributions sorted by engagement, so that I can see which profiles are most viewed.

#### Acceptance Criteria

1. WHEN displaying contributions, THE System SHALL sort persons by total_views in descending order (most viewed first)
2. THE System SHALL maintain the existing API behavior for fetching contributions (GET /api/v1/person/my-contributions)

### Requirement 5: Retain Existing Dialog Access

**User Story:** As a user, I want to still access contribution stats from the profile menu, so that I have multiple ways to view this information.

#### Acceptance Criteria

1. THE System SHALL retain the existing "Contribution Stats" option in the user profile dropdown menu
2. WHEN a user clicks "Contribution Stats" from the profile menu, THE System SHALL continue to open the ContributionStatsDialog
3. THE System SHALL NOT remove or modify the existing ContributionStatsDialog component functionality

### Requirement 6: Responsive Design

**User Story:** As a user, I want the contributions page to work well on different screen sizes, so that I can view my contributions on any device.

#### Acceptance Criteria

1. WHEN viewed on desktop, THE System SHALL display person cards in a grid layout (2-3 columns)
2. WHEN viewed on tablet, THE System SHALL display person cards in a 2-column layout
3. WHEN viewed on mobile, THE System SHALL display person cards in a single column layout
4. THE System SHALL ensure all text and icons are readable at all screen sizes

## Technical Notes

### Route Configuration

- New route: `/contributions`
- Route file: `frontend/src/routes/_layout/contributions.tsx`

### Components

- New page component: `ContributionsPage.tsx`
- Reuse existing: `ContributionStatsDialog.tsx` (for profile menu access)
- Consider extracting shared card component for reuse

### API

- Uses existing endpoint: `GET /api/v1/person/my-contributions`
- No backend changes required

## Future Enhancements

1. **Filtering**: Allow filtering by active/deactivated status
2. **Search**: Add search functionality within contributions
3. **Pagination**: Add pagination for users with many contributions
4. **Export**: Allow exporting contribution data to CSV
5. **Date Range**: Filter contributions by creation date

