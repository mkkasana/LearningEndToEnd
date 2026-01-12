# Requirements Document

## Introduction

This feature adds a dedicated "Search" page accessible from the sidebar navigation. The page allows users to browse and search for persons in the system with advanced filtering capabilities. By default, it displays all persons from the user's locality, with a slide-out filter panel for refined searching.

## Glossary

- **Search_Page**: The main page component that displays search results and filter controls
- **Filter_Panel**: A slide-out sidebar panel containing all search filter options
- **Person_Card**: A card component displaying person information in search results
- **Search_Service**: Backend service handling person search with filters
- **Active_Person**: The currently logged-in user's person profile (or assumed person)

## Requirements

### Requirement 1: Sidebar Navigation

**User Story:** As a user, I want to access the Search feature from the sidebar, so that I can easily find and browse persons in the system.

#### Acceptance Criteria

1. THE Sidebar SHALL display a "Search" navigation item with a Search icon
2. WHEN a user clicks the "Search" navigation item, THE System SHALL navigate to the `/search` route
3. THE Search navigation item SHALL appear after "Life Events" in the sidebar menu order

### Requirement 2: Default Search Results

**User Story:** As a user, I want to see persons from my locality by default when I open the Search page, so that I can discover people near me without manual filtering.

#### Acceptance Criteria

1. WHEN the Search_Page loads, THE System SHALL fetch the Active_Person's address details (locality, sub-district, district, state, country) and religion details
2. WHEN the Active_Person has a locality defined, THE System SHALL display all persons from that locality by default
3. IF the Active_Person does not have a locality defined, THEN THE System SHALL display persons from the Active_Person's sub-district
4. IF the Active_Person does not have address information, THEN THE System SHALL display an empty state with a message prompting the user to complete their profile
5. THE Search_Page SHALL display results in a grid layout with Person_Cards
6. THE Search_Page SHALL show a loading state while fetching results
7. THE Search_Page SHALL display the total count of results found

### Requirement 3: Filter Panel UI

**User Story:** As a user, I want to access advanced filters through a slide-out panel, so that I can refine my search without cluttering the main view.

#### Acceptance Criteria

1. THE Search_Page SHALL display a filter icon button in the header area
2. WHEN a user clicks the filter icon, THE Filter_Panel SHALL slide in from the left side of the screen
3. THE Filter_Panel SHALL contain all filter input fields organized in logical sections
4. THE Filter_Panel SHALL have a "Apply Filters" button to execute the search
5. THE Filter_Panel SHALL have a "Reset" button to clear all filters and return to default search
6. THE Filter_Panel SHALL have a close button or allow clicking outside to dismiss
7. WHEN filters are active (different from default), THE filter icon SHALL display a visual indicator (badge or highlight)

### Requirement 4: Name Filters

**User Story:** As a user, I want to filter persons by name, so that I can find specific individuals.

#### Acceptance Criteria

1. THE Filter_Panel SHALL provide a "First Name" text input field (optional)
2. THE Filter_Panel SHALL provide a "Last Name" text input field (optional)
3. WHEN name filters are provided, THE Search_Service SHALL use fuzzy matching to find persons with similar names
4. THE name matching SHALL use the same algorithm as the existing person matching service (rapidfuzz with 40% threshold)

### Requirement 5: Address Filters

**User Story:** As a user, I want to filter persons by location, so that I can find people from specific areas.

#### Acceptance Criteria

1. THE Filter_Panel SHALL provide a "Country" dropdown (required when filtering)
2. THE Filter_Panel SHALL provide a "State" dropdown (required when filtering)
3. THE Filter_Panel SHALL provide a "District" dropdown (required when filtering)
4. THE Filter_Panel SHALL provide a "Sub-District" dropdown (required when filtering)
5. THE Filter_Panel SHALL provide a "Locality" dropdown (optional)
6. WHEN a parent location is selected, THE System SHALL load child locations dynamically (cascading dropdowns)
7. THE address dropdowns SHALL be pre-populated with the Active_Person's address values by default

### Requirement 6: Religion Filters

**User Story:** As a user, I want to filter persons by religion, so that I can find people with similar religious backgrounds.

#### Acceptance Criteria

1. THE Filter_Panel SHALL provide a "Religion" dropdown (required when filtering)
2. THE Filter_Panel SHALL provide a "Category" dropdown (required when filtering)
3. THE Filter_Panel SHALL provide a "Sub-Category" dropdown (optional)
4. WHEN a parent religion option is selected, THE System SHALL load child options dynamically (cascading dropdowns)
5. THE religion dropdowns SHALL be pre-populated with the Active_Person's religion values by default

### Requirement 7: Gender Filter

**User Story:** As a user, I want to filter persons by gender, so that I can narrow down search results.

#### Acceptance Criteria

1. THE Filter_Panel SHALL provide a "Gender" dropdown (optional)
2. THE Gender dropdown SHALL display all available gender options from the system
3. WHEN no gender is selected, THE Search_Service SHALL return persons of all genders

### Requirement 8: Birth Year Range Filter

**User Story:** As a user, I want to filter persons by birth year range, so that I can find people of similar age groups.

#### Acceptance Criteria

1. THE Filter_Panel SHALL provide a "Birth Year From" number input (optional)
2. THE Filter_Panel SHALL provide a "Birth Year To" number input (optional)
3. WHEN both birth year values are provided, THE Search_Service SHALL return persons born within that range (inclusive)
4. WHEN only "Birth Year From" is provided, THE Search_Service SHALL return persons born on or after that year
5. WHEN only "Birth Year To" is provided, THE Search_Service SHALL return persons born on or before that year
6. IF "Birth Year From" is greater than "Birth Year To", THEN THE System SHALL display a validation error

### Requirement 9: Search Results Display

**User Story:** As a user, I want to see search results in an organized manner, so that I can easily browse and find persons of interest.

#### Acceptance Criteria

1. THE Search_Page SHALL display results in a responsive grid (1 column on mobile, 2 on tablet, 3-4 on desktop)
2. EACH Person_Card SHALL display: full name, birth year.
3. THE Search_Page SHALL support pagination or infinite scroll for large result sets
4. WHEN no results match the filters, THE System SHALL display an appropriate empty state message
5. THE Search_Page SHALL display the current filter summary above the results

### Requirement 10: Backend Search API

**User Story:** As a developer, I want a flexible search API endpoint, so that the frontend can perform various search queries.

#### Acceptance Criteria

1. THE System SHALL create a new `search_person.py` route file to keep search-related endpoints separate from the main `person.py` file
2. THE System SHALL provide a `POST /api/v1/persons/search` endpoint
3. THE endpoint SHALL accept a request model containing optional filters: first_name, last_name, country_id, state_id, district_id, sub_district_id, locality_id, religion_id, religion_category_id, religion_sub_category_id, gender_id, birth_year_from, birth_year_to
4. THE endpoint SHALL return paginated results with person details
5. THE endpoint SHALL support pagination parameters: skip (offset) and limit in the request model
6. THE endpoint SHALL return total count of matching results for pagination UI
7. WHEN no name filters are provided, THE Search_Service SHALL skip name matching and return all persons matching other criteria
8. THE endpoint SHALL limit results to a maximum of 100 per page for performance

### Requirement 11: Performance and Caching

**User Story:** As a user, I want the search to be fast and responsive, so that I can quickly find the persons I'm looking for.

#### Acceptance Criteria

1. THE Search_Service SHALL use database indexes for efficient querying
2. THE frontend SHALL cache search results using TanStack Query
3. THE frontend SHALL debounce filter changes to avoid excessive API calls
4. THE Search_Page SHALL show a loading indicator during searches
