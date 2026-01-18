# Requirements Document

## Introduction

This feature enhances the Rishte (Relationship Visualizer) page by replacing the UUID-based person input with a user-friendly multi-step search wizard. Users can search for persons using familiar criteria (name, address, religion) rather than requiring technical person IDs. The wizard follows a similar flow to the "Add Family Member" feature but is self-contained within the Rishte folder to maintain separation of concerns.

## Glossary

- **Person_Search_Wizard**: A multi-step dialog for searching and selecting a person using human-readable criteria
- **Person_Button**: A clickable button displaying "Select Person A" or "Select Person B" that opens the wizard
- **Selected_Person_Card**: A compact card showing the selected person's name and basic info
- **Basic_Info_Step**: Step 1 - Collects first name (required), last name (optional), gender (optional), birth year range (optional)
- **Address_Step**: Step 2 - Collects address filters defaulting to active person's address
- **Religion_Step**: Step 3 - Collects religion filters defaulting to active person's religion
- **Results_Step**: Step 4 - Displays matched persons sorted by relevance with selection capability
- **Active_Person**: The currently logged-in user's person profile from ActivePersonContext

## Requirements

### Requirement 1: Self-Contained Component Structure

**User Story:** As a developer, I want all person search wizard components to be contained within the Rishte folder, so that changes don't affect other features.

#### Acceptance Criteria

1. THE System SHALL create all wizard components under `src/components/Rishte/` folder
2. THE Wizard components SHALL NOT import from or modify existing Family or Search components
3. THE Wizard SHALL have its own step components: `RishteBasicInfoStep.tsx`, `RishteAddressStep.tsx`, `RishteReligionStep.tsx`, `RishteResultsStep.tsx`
4. THE Wizard SHALL have its own dialog component: `RishtePersonSearchDialog.tsx`

### Requirement 2: Person Selection Buttons

**User Story:** As a user, I want to click buttons to select Person A and Person B, so that I can easily initiate the search process.

#### Acceptance Criteria

1. THE Rishte_Page SHALL display two Person_Buttons labeled "Select Person A" and "Select Person B"
2. WHEN no person is selected, THE Person_Button SHALL display "Select Person A" or "Select Person B" with a user-plus icon
3. WHEN a person is selected, THE Person_Button SHALL transform into a Selected_Person_Card showing the person's full name
4. THE Selected_Person_Card SHALL display a small "x" button to clear the selection
5. WHEN a user clicks a Person_Button, THE System SHALL open the Person_Search_Wizard dialog
6. THE Person_Buttons SHALL be styled consistently with the existing UI design system

### Requirement 3: Basic Info Step (Step 1)

**User Story:** As a user, I want to enter basic search criteria like name and birth year, so that I can find the person I'm looking for.

#### Acceptance Criteria

1. THE Basic_Info_Step SHALL display a form with first name, last name, gender, and birth year range fields
2. THE First_Name field SHALL be required with minimum 1 character
3. THE Last_Name field SHALL be required with minimum 1 character
4. THE Gender field SHALL be optional and display a dropdown with options from the genders API
5. THE Birth_Year_From and Birth_Year_To fields SHALL be optional number inputs for specifying a year range
6. THE Basic_Info_Step SHALL display a "Next" button to proceed to the Address step
7. WHEN the user clicks "Next" without entering first name, THE System SHALL display a validation error

### Requirement 4: Address Step (Step 2)

**User Story:** As a user, I want to filter by address with my current address as default, so that I can find persons from specific locations.

#### Acceptance Criteria

1. THE Address_Step SHALL display cascading dropdowns for Country, State, District, Sub-District, and Locality
2. THE Address_Step SHALL pre-populate with the Active_Person's current address as default values
3. THE Country and State fields SHALL be required
4. THE District field SHALL be required
5. THE Sub_District and Locality fields SHALL be optional
6. WHEN a parent location changes, THE System SHALL reset and reload child location options
7. THE Address_Step SHALL display "Back" and "Next" buttons for navigation

### Requirement 5: Religion Step (Step 3)

**User Story:** As a user, I want to filter by religion with my religion as default, so that I can find persons of specific religious backgrounds.

#### Acceptance Criteria

1. THE Religion_Step SHALL display cascading dropdowns for Religion, Category, and Sub-Category
2. THE Religion_Step SHALL pre-populate with the Active_Person's religion as default values
3. THE Religion and Category fields SHALL be required
4. THE Sub_Category field SHALL be optional
5. WHEN a parent religion field changes, THE System SHALL reset and reload child options
6. THE Religion_Step SHALL display "Back" and "Search" buttons
7. WHEN the user clicks "Search", THE System SHALL proceed to the Results step and trigger the search

### Requirement 6: Results Step (Step 4)

**User Story:** As a user, I want to see matching persons sorted by relevance, so that I can select the right person.

#### Acceptance Criteria

1. THE Results_Step SHALL call the person search API with all collected criteria
2. THE Results_Step SHALL display a loading indicator while the search is in progress
3. THE Results_Step SHALL display matched persons in a scrollable list sorted by most matched at top
4. EACH person result SHALL display as a card showing full name, birth year, address summary, and religion summary
5. EACH person result card SHALL have a "Select" button
6. WHEN a user clicks "Select", THE System SHALL close the dialog and update the corresponding Person_Button with the selected person
7. IF no results are found, THE System SHALL display a "No persons found" message with suggestion to adjust criteria
8. THE Results_Step SHALL display a "Back" button to return to the Religion step
9. THE Results_Step SHALL support pagination if more than 20 results are returned

### Requirement 7: Find Relationship Button State

**User Story:** As a user, I want the Find Relationship button to be enabled only when both persons are selected, so that I know when I can search.

#### Acceptance Criteria

1. THE "Find Relationship" button SHALL be disabled when Person A is not selected
2. THE "Find Relationship" button SHALL be disabled when Person B is not selected
3. THE "Find Relationship" button SHALL be enabled when both Person A and Person B are selected
4. WHEN the user clicks "Find Relationship", THE System SHALL call the lineage-path API with the selected person IDs

### Requirement 8: Wizard Dialog Behavior

**User Story:** As a user, I want a smooth wizard experience with clear progress indication, so that I know where I am in the process.

#### Acceptance Criteria

1. THE Person_Search_Wizard SHALL display as a modal dialog
2. THE Wizard SHALL display a progress indicator showing current step (1 of 4, 2 of 4, etc.)
3. THE Wizard SHALL display a title indicating which person is being selected ("Select Person A" or "Select Person B")
4. WHEN the user closes the dialog without selecting, THE System SHALL preserve any previously selected person
5. THE Wizard SHALL reset to Step 1 when opened for a new selection

### Requirement 9: Default Values from Active Person

**User Story:** As a user, I want my address and religion to be pre-filled, so that I can search faster for persons similar to me.

#### Acceptance Criteria

1. WHEN the wizard opens, THE System SHALL fetch the Active_Person's current address
2. WHEN the wizard opens, THE System SHALL fetch the Active_Person's religion
3. THE Address_Step SHALL use the fetched address as default values for all address fields
4. THE Religion_Step SHALL use the fetched religion as default values for all religion fields
5. IF the Active_Person has no address, THE Address_Step SHALL start with empty fields
6. IF the Active_Person has no religion, THE Religion_Step SHALL start with empty fields

### Requirement 10: Responsive Design

**User Story:** As a user, I want the wizard to work well on different screen sizes, so that I can use it on various devices.

#### Acceptance Criteria

1. THE Person_Search_Wizard dialog SHALL be responsive and work on desktop and tablet screens
2. THE Person_Buttons SHALL stack vertically on smaller screens
3. THE Results_Step cards SHALL display in a responsive grid layout

