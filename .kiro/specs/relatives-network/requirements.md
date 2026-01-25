# Requirements Document

## Introduction

The Relatives Network feature provides a dedicated page for users to list their relatives up to a configurable relationship depth. This is particularly useful for generating invitation lists for family functions (weddings, ceremonies, etc.) where invitations are sent to relatives based on the type and size of the event. The feature allows filtering by depth mode, address location, gender, and living status.

## Glossary

- **Relatives_Network_Service**: Backend service that performs BFS traversal to find relatives up to a specified depth
- **Relatives_Network_Page**: Frontend page accessible from sidebar menu showing the relatives list
- **Relative_Card**: UI component displaying individual relative information
- **Filter_Panel**: Slide-out panel for configuring search filters
- **Depth**: Number of relationship hops from the active person (1 = parents/children/spouse/siblings, 2 = grandparents/uncles/aunts, etc.)
- **Depth_Mode**: Either "up_to" (all relatives from depth 1 to X) or "only_at" (only relatives exactly at depth X)
- **Active_Person**: The currently selected person in the application context

## Requirements

### Requirement 1: Page Access and Navigation

**User Story:** As a user, I want to access the Relatives Network page from the sidebar menu, so that I can view my relatives for invitation planning.

#### Acceptance Criteria

1. THE Sidebar SHALL display a "Relatives Network" menu item
2. WHEN a user clicks the "Relatives Network" menu item, THE System SHALL navigate to the `/relatives-network` route
3. THE Relatives_Network_Page SHALL display a header with title "Relatives Network"
4. THE Relatives_Network_Page SHALL display a "Filters" button in the header
5. WHEN no active person is set, THE System SHALL display a message prompting the user to complete their profile

### Requirement 2: Default Search Behavior

**User Story:** As a user, I want the page to automatically load my relatives with sensible defaults, so that I can quickly see my close family network.

#### Acceptance Criteria

1. WHEN the page loads with an active person, THE System SHALL automatically search for relatives
2. THE System SHALL use depth 3 as the default depth value
3. THE System SHALL use "up_to" as the default depth mode
4. THE System SHALL include only living relatives by default (living_only = true)
5. THE System SHALL NOT apply any address filters by default
6. THE System SHALL NOT apply any gender filter by default
7. THE System SHALL exclude the active person from the results

### Requirement 3: Results Display

**User Story:** As a user, I want to see my relatives displayed in a clear grid layout with relevant information, so that I can easily identify who to invite.

#### Acceptance Criteria

1. THE System SHALL display a results count header showing "Found X relatives up to depth Y" or "Found X relatives at depth Y"
2. THE System SHALL display relatives in a responsive grid layout (1-4 columns based on screen width)
3. THE System SHALL load all results at once without pagination
4. THE System SHALL limit results to a maximum of 100 relatives
5. WHILE the search is in progress, THE System SHALL display skeleton loading cards
6. WHEN no relatives are found, THE System SHALL display an empty state message "No relatives found within depth X"
7. IF the search fails, THEN THE System SHALL display an error message

### Requirement 4: Relative Card Display

**User Story:** As a user, I want each relative card to show essential information, so that I can identify the person and their relationship distance.

#### Acceptance Criteria

1. THE Relative_Card SHALL display a gender-based avatar icon
2. THE Relative_Card SHALL display the person's first name and last name (truncated if too long)
3. THE Relative_Card SHALL display birth year and death year in format "YYYY - YYYY"
4. WHEN the person is alive, THE Relative_Card SHALL display only the birth year
5. THE Relative_Card SHALL display the district and locality combination (truncated if too long)
6. THE Relative_Card SHALL display a depth badge showing the relationship depth number
7. THE Relative_Card SHALL include a "View" button to open person details

### Requirement 5: View Person Details

**User Story:** As a user, I want to view detailed information about a relative, so that I can see their full profile.

#### Acceptance Criteria

1. WHEN a user clicks the "View" button on a Relative_Card, THE System SHALL open the PersonDetailsPanel
2. THE PersonDetailsPanel SHALL display the selected relative's full information
3. THE PersonDetailsPanel SHALL be reusable from existing FamilyTree components

### Requirement 6: Filter Panel - Depth Filters

**User Story:** As a user, I want to configure the relationship depth for my search, so that I can control how far into my family network to search.

#### Acceptance Criteria

1. THE Filter_Panel SHALL display a depth number input field
2. THE depth input SHALL accept values from 1 to the configured maximum (default 20)
3. THE Filter_Panel SHALL display a depth mode selector with options "Up to" and "Only at"
4. WHEN "Up to" is selected, THE System SHALL return all relatives from depth 1 to the specified depth
5. WHEN "Only at" is selected, THE System SHALL return only relatives exactly at the specified depth
6. THE System SHALL validate that depth does not exceed the configured maximum

### Requirement 7: Filter Panel - Address Filters

**User Story:** As a user, I want to filter relatives by location, so that I can create location-specific invitation lists.

#### Acceptance Criteria

1. THE Filter_Panel SHALL display cascading address dropdowns: Country, State, District, Sub-District, Locality
2. THE address filters SHALL be optional (no defaults applied)
3. WHEN a country is selected, THE System SHALL load and display states for that country
4. WHEN a state is selected, THE System SHALL load and display districts for that state
5. WHEN a district is selected, THE System SHALL load and display sub-districts for that district
6. WHEN a sub-district is selected, THE System SHALL load and display localities for that sub-district
7. WHEN an address filter is applied, THE System SHALL only return relatives matching that address

### Requirement 8: Filter Panel - Additional Filters

**User Story:** As a user, I want to filter by living status and gender, so that I can create appropriate invitation lists for different occasions.

#### Acceptance Criteria

1. THE Filter_Panel SHALL display a "Living only" checkbox (default: checked)
2. WHEN "Living only" is checked, THE System SHALL exclude deceased relatives from results
3. WHEN "Living only" is unchecked, THE System SHALL include both living and deceased relatives
4. THE Filter_Panel SHALL display a gender dropdown with options: Any, Male, Female
5. WHEN a gender is selected, THE System SHALL only return relatives of that gender

### Requirement 9: Filter Panel - Actions

**User Story:** As a user, I want to apply or reset my filters, so that I can control my search criteria.

#### Acceptance Criteria

1. THE Filter_Panel SHALL display an "Apply Filters" button
2. WHEN a user clicks "Apply Filters", THE System SHALL execute the search with current filter values
3. WHEN a user clicks "Apply Filters", THE System SHALL close the filter panel
4. THE Filter_Panel SHALL display a "Reset" button
5. WHEN a user clicks "Reset", THE System SHALL restore all filters to their default values
6. THE Filter_Panel SHALL slide out from the left side of the screen

### Requirement 10: Backend API

**User Story:** As a developer, I want a dedicated API endpoint for relatives network search, so that the frontend can retrieve filtered relatives data.

#### Acceptance Criteria

1. THE System SHALL expose a POST endpoint at `/api/v1/relatives-network/find`
2. THE endpoint SHALL accept person_id, depth, depth_mode, living_only, gender_id, and address filter parameters
3. THE endpoint SHALL use BFS algorithm to traverse relationships up to the specified depth
4. THE endpoint SHALL return a list of relatives with person details and depth information
5. THE endpoint SHALL limit results to a maximum of 100 relatives
6. THE endpoint SHALL exclude the requesting person from results
7. IF the person_id is not found, THEN THE endpoint SHALL return a 404 error

### Requirement 11: Configuration

**User Story:** As a system administrator, I want to configure the maximum allowed depth, so that I can control system performance.

#### Acceptance Criteria

1. THE System SHALL read maximum depth from configuration setting `RELATIVES_NETWORK_MAX_DEPTH`
2. THE default maximum depth SHALL be 20
3. THE System SHALL enforce the maximum depth limit on all requests

### Requirement 12: Code Organization

**User Story:** As a developer, I want the feature to be self-contained, so that it doesn't affect existing functionality.

#### Acceptance Criteria

1. THE frontend components SHALL be placed in a new `frontend/src/components/RelativesNetwork/` folder
2. THE route SHALL be placed in a new `frontend/src/routes/_layout/relatives-network.tsx` file
3. THE backend service SHALL be placed in a new `backend/app/services/relatives_network/` folder
4. THE backend route SHALL be placed in a new `backend/app/api/routes/relatives_network/` folder
5. THE backend schemas SHALL be placed in a new `backend/app/schemas/relatives_network/` folder
6. THE feature SHALL NOT modify any existing components or services
7. THE feature MAY reuse the existing PersonDetailsPanel component for viewing relative details
