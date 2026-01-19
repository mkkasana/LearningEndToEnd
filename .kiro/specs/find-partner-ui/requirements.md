# Requirements Document

## Introduction

This feature provides a "Find Partner" UI accessible from the menu bar. It allows users to search for potential marriage matches within their family network using a filter panel with smart defaults based on the active person's profile and family lineage. The feature uses the existing partner-match backend API and displays results as raw JSON initially, with plans for enhanced UI in the future.

## Glossary

- **Active_Person**: The currently selected person context (can be the logged-in user or an assumed role)
- **Filter_Panel**: A sliding sidebar panel containing all search filter controls
- **Tag_Input**: A multi-select input that displays selected items as removable tags with "×" buttons
- **Seeker**: The person for whom partner matches are being searched (always the Active_Person)
- **Gotra**: Sub-category in religion hierarchy, traditionally excluded from same lineage for marriage
- **Cascading_Filter**: A filter whose options depend on selections in a parent filter

## Requirements

### Requirement 1: Menu Bar Entry Point

**User Story:** As a user, I want to access the Find Partner feature from the menu bar, so that I can easily search for potential matches.

#### Acceptance Criteria

1. THE Menu_Bar SHALL display a "Find Partner" menu item
2. WHEN a user clicks "Find Partner", THE System SHALL navigate to a dedicated Find Partner page
3. WHEN the Find Partner page loads, THE System SHALL display an empty main content area with a filter panel

### Requirement 2: Filter Panel Layout

**User Story:** As a user, I want a filter panel to configure my search criteria, so that I can customize the partner search.

#### Acceptance Criteria

1. THE Filter_Panel SHALL display as a sliding sidebar on the Find Partner page
2. THE Filter_Panel SHALL contain filters in this order: Gender, Birth Year Range, Include Religions, Include Categories, Include Sub-Categories, Exclude Sub-Categories, Search Depth
3. THE Filter_Panel SHALL display "Reset Filters" and "Find Matches" action buttons at the bottom
4. WHEN the page loads, THE Filter_Panel SHALL initialize all filters with smart defaults based on Active_Person

### Requirement 3: Gender Filter

**User Story:** As a user, I want the gender filter to default to the opposite gender, so that I can quickly search for compatible matches.

#### Acceptance Criteria

1. THE Gender_Filter SHALL display as a single-select dropdown with options "Male" and "Female"
2. WHEN the Active_Person is Male, THE Gender_Filter SHALL default to "Female"
3. WHEN the Active_Person is Female, THE Gender_Filter SHALL default to "Male"
4. IF the Active_Person's gender is unknown, THEN THE Gender_Filter SHALL default to empty (user must select)

### Requirement 4: Birth Year Range Filter

**User Story:** As a user, I want the birth year range to have sensible defaults, so that I can find age-appropriate matches.

#### Acceptance Criteria

1. THE Birth_Year_Filter SHALL display two number inputs: "From Year" and "To Year"
2. WHEN the Active_Person has a birth year, THE "From Year" SHALL default to (Active_Person birth year - 2)
3. WHEN the Active_Person has a birth year, THE "To Year" SHALL default to (Active_Person birth year + 5)
4. IF the Active_Person's birth year is unknown, THEN THE Birth_Year_Filter SHALL default to empty
5. THE Birth_Year_Filter SHALL validate that "From Year" is not greater than "To Year"

### Requirement 5: Include Religions Filter (Tag Input)

**User Story:** As a user, I want to select multiple religions to include in my search, so that I can find matches from compatible religious backgrounds.

#### Acceptance Criteria

1. THE Include_Religions_Filter SHALL display as a Tag_Input with a dropdown for adding religions
2. WHEN the page loads, THE Include_Religions_Filter SHALL pre-populate with Active_Person's religion as a tag
3. THE Tag_Input SHALL display each selected religion as a removable tag with "×" button
4. WHEN a user clicks "×" on a tag, THE System SHALL remove that religion from the selection
5. THE dropdown SHALL list all available religions from the religions API
6. WHEN a user selects a religion from dropdown, THE System SHALL add it as a new tag
7. IF Active_Person has no religion data, THEN THE Include_Religions_Filter SHALL start empty

### Requirement 6: Include Categories Filter (Tag Input with Cascading)

**User Story:** As a user, I want to select religion categories that depend on my selected religions, so that I can narrow down compatible matches.

#### Acceptance Criteria

1. THE Include_Categories_Filter SHALL display as a Tag_Input with a dropdown for adding categories
2. WHEN the page loads, THE Include_Categories_Filter SHALL pre-populate with Active_Person's category as a tag
3. THE dropdown SHALL only list categories belonging to the currently selected religions in Include_Religions_Filter
4. WHEN a religion is removed from Include_Religions_Filter, THE System SHALL remove any categories belonging to that religion from Include_Categories_Filter
5. THE Tag_Input SHALL display each selected category as a removable tag with "×" button
6. IF Active_Person has no category data, THEN THE Include_Categories_Filter SHALL start empty

### Requirement 7: Include Sub-Categories Filter (Tag Input with Cascading)

**User Story:** As a user, I want to optionally include specific sub-categories in my search, so that I can find matches from preferred gotras.

#### Acceptance Criteria

1. THE Include_SubCategories_Filter SHALL display as a Tag_Input with a dropdown for adding sub-categories
2. WHEN the page loads, THE Include_SubCategories_Filter SHALL start empty (no defaults)
3. THE dropdown SHALL only list sub-categories belonging to the currently selected categories in Include_Categories_Filter
4. WHEN a category is removed from Include_Categories_Filter, THE System SHALL remove any sub-categories belonging to that category from Include_SubCategories_Filter
5. THE Tag_Input SHALL display each selected sub-category as a removable tag with "×" button

### Requirement 8: Exclude Sub-Categories Filter (Tag Input with Cascading)

**User Story:** As a user, I want to exclude certain gotras (sub-categories) from my search based on family lineage, so that I can respect traditional marriage customs.

#### Acceptance Criteria

1. THE Exclude_SubCategories_Filter SHALL display as a Tag_Input with a dropdown for adding sub-categories to exclude
2. WHEN the page loads, THE System SHALL attempt to fetch Active_Person's sub-category, mother's sub-category, and maternal grandmother's sub-category
3. THE Exclude_SubCategories_Filter SHALL pre-populate with successfully fetched sub-categories as tags
4. IF any lineage sub-category cannot be fetched, THEN THE System SHALL continue without that sub-category (graceful degradation)
5. THE dropdown SHALL only list sub-categories belonging to the currently selected categories in Include_Categories_Filter
6. WHEN a category is removed from Include_Categories_Filter, THE System SHALL remove any excluded sub-categories belonging to that category
7. THE Tag_Input SHALL display each excluded sub-category as a removable tag with "×" button

### Requirement 9: Search Depth Filter

**User Story:** As a user, I want to control how many relationship hops to search, so that I can balance between finding more matches and search performance.

#### Acceptance Criteria

1. THE Search_Depth_Filter SHALL display as a dropdown with values 1 through 50
2. WHEN the page loads, THE Search_Depth_Filter SHALL default to 10
3. WHEN a user selects a depth value, THE System SHALL use that value for the max_depth parameter in the search

### Requirement 10: Action Buttons

**User Story:** As a user, I want to reset filters or execute the search, so that I can control the search workflow.

#### Acceptance Criteria

1. THE Filter_Panel SHALL display a "Reset Filters" button
2. WHEN a user clicks "Reset Filters", THE System SHALL restore all filters to their initial default values
3. THE Filter_Panel SHALL display a "Find Matches" button
4. WHEN a user clicks "Find Matches", THE System SHALL call the partner-match/find API with the current filter values
5. WHILE the search is in progress, THE System SHALL display a loading indicator
6. IF the search fails, THEN THE System SHALL display an error message

### Requirement 11: Results Display

**User Story:** As a user, I want to see the search results, so that I can review potential matches.

#### Acceptance Criteria

1. WHEN the partner-match/find API returns successfully, THE System SHALL display the raw JSON response in the main content area
2. THE JSON display SHALL be formatted for readability (pretty-printed)
3. THE System SHALL display the total number of matches found
4. WHEN no matches are found, THE System SHALL display a "No matches found" message

### Requirement 12: Isolated Component Structure

**User Story:** As a developer, I want the Find Partner feature in its own folder structure, so that it doesn't interfere with existing code.

#### Acceptance Criteria

1. THE frontend components SHALL be placed in a new `frontend/src/components/FindPartner/` folder
2. THE route SHALL be placed in a new `frontend/src/routes/_layout/find-partner.tsx` file
3. THE feature SHALL not modify any existing Rishte components
4. THE feature SHALL reuse the existing partner-match backend API without modifications

