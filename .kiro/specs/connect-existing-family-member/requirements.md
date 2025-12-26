# Requirements Document

## Introduction

This feature adds an intelligent person matching step to the "Add Family Member" wizard to prevent duplicate person records. When a user enters basic details, address, and religion information for a new family member, the system will search for existing persons with matching attributes and allow the user to connect to an existing person instead of creating a duplicate.

## Glossary

- **Person**: An individual record in the system containing biographical information
- **Family Member**: A person related to the current user through a relationship
- **Relationship**: A connection between two persons (e.g., Father, Mother, Spouse)
- **Person Matching**: The process of finding existing person records that match provided criteria
- **Fuzzy Matching**: Approximate string matching that accounts for minor variations in names
- **Match Score**: A numerical value indicating how closely a person matches the search criteria

## Requirements

### Requirement 1

**User Story:** As a user adding a family member, I want to see if a person with similar details already exists in the system, so that I can connect to them instead of creating a duplicate record.

#### Acceptance Criteria

1. WHEN a user completes the Religion step (Step 3) and clicks "Next", THEN the system SHALL search for existing persons matching the provided criteria
2. WHEN matching persons are found, THEN the system SHALL display a "Connect Existing Person" step before the Confirmation step
3. WHEN no matching persons are found, THEN the system SHALL proceed directly to the Confirmation step
4. WHEN the user navigates back from the "Connect Existing Person" step, THEN the system SHALL return to the Religion step with data preserved
5. WHEN the user clicks "Next: Create New" on the "Connect Existing Person" step, THEN the system SHALL proceed to the Confirmation step for creating a new person

### Requirement 2

**User Story:** As a user viewing potential matches, I want to see relevant details about each matching person, so that I can identify if they are the person I'm trying to add.

#### Acceptance Criteria

1. WHEN displaying matching persons, THEN the system SHALL show first name, middle name, last name, date of birth, and match score for each person
2. WHEN displaying matching persons, THEN the system SHALL show the address in comma-separated format
3. WHEN displaying matching persons, THEN the system SHALL show the religion in comma-separated format
4. WHEN displaying matching persons, THEN the system SHALL present results in a scrollable list
5. WHEN displaying matching persons, THEN the system SHALL sort results by match score in descending order

### Requirement 3

**User Story:** As a user who finds an existing person match, I want to connect to that person with a single action, so that I can quickly establish the family relationship without creating duplicate data.

#### Acceptance Criteria

1. WHEN a user clicks "Connect" on a matching person, THEN the system SHALL display a confirmation dialog
2. WHEN the confirmation dialog is displayed, THEN the system SHALL show the person's full name and the relationship type being created
3. WHEN the user confirms the connection, THEN the system SHALL create a relationship between the current user and the selected person
4. WHEN the user cancels the connection, THEN the system SHALL close the dialog and return to the matching persons list
5. WHEN the relationship is successfully created, THEN the system SHALL close the wizard, show a success message, and refresh the family members list

### Requirement 4

**User Story:** As a system, I want to search for existing persons using multiple criteria, so that I can find accurate matches and prevent duplicate records.

#### Acceptance Criteria

1. WHEN searching for matching persons, THEN the system SHALL find persons with the exact same address (country, state, district, sub-district, locality)
2. WHEN searching for matching persons, THEN the system SHALL find persons with the exact same religion details (religion, category, sub-category)
3. WHEN searching for matching persons, THEN the system SHALL compute the intersection of persons matching both address and religion criteria
4. WHEN filtering results, THEN the system SHALL include only persons with the same gender as specified in the search criteria
5. WHEN computing match scores, THEN the system SHALL use fuzzy matching on first name and last name to calculate similarity

### Requirement 5

**User Story:** As a system, I want to calculate match scores for potential person matches, so that users can see the most relevant matches first.

#### Acceptance Criteria

1. WHEN calculating match scores, THEN the system SHALL assign higher scores to persons with closer name matches
2. WHEN calculating match scores, THEN the system SHALL use a fuzzy string matching algorithm (e.g., Levenshtein distance)
3. WHEN calculating match scores, THEN the system SHALL return scores as a percentage (0-100)
4. WHEN first name and last name both match exactly, THEN the system SHALL assign a score of 100
5. WHEN names have minor variations, THEN the system SHALL assign proportional scores based on similarity

### Requirement 6

**User Story:** As a user, I want the system to exclude persons I'm already connected to from the matching results, so that I don't see duplicate suggestions.

#### Acceptance Criteria

1. WHEN searching for matching persons, THEN the system SHALL exclude persons who already have a relationship with the current user
2. WHEN searching for matching persons, THEN the system SHALL exclude the current user's own person record
3. WHEN no matches remain after filtering, THEN the system SHALL proceed directly to the Confirmation step
4. WHEN all potential matches are already connected, THEN the system SHALL display a message indicating no new matches were found
5. WHEN the user is already connected to all matching persons, THEN the system SHALL allow proceeding to create a new person

### Requirement 7

**User Story:** As a developer, I want a dedicated API endpoint for person matching, so that the search logic is centralized and reusable.

#### Acceptance Criteria

1. WHEN the API receives a person search request, THEN the system SHALL accept basic details (first name, last name, gender, date of birth), address IDs, and religion IDs as input
2. WHEN the API processes the search, THEN the system SHALL return a list of matching persons with their details and match scores
3. WHEN the API encounters an error, THEN the system SHALL return appropriate HTTP status codes and error messages
4. WHEN the API is called, THEN the system SHALL require authentication and validate the current user's permissions
5. WHEN the API returns results, THEN the system SHALL include person ID, name, date of birth, address details, religion details, and match score for each result

### Requirement 8

**User Story:** As a user, I want the wizard to maintain my entered data when navigating between steps, so that I don't lose information if I go back to review or change details.

#### Acceptance Criteria

1. WHEN navigating from "Connect Existing Person" step to Religion step, THEN the system SHALL preserve all previously entered data
2. WHEN navigating from "Connect Existing Person" step to Confirmation step, THEN the system SHALL preserve all previously entered data
3. WHEN returning to "Connect Existing Person" step from Confirmation, THEN the system SHALL re-display the same matching results
4. WHEN the user edits data in previous steps and returns to "Connect Existing Person", THEN the system SHALL re-run the search with updated criteria
5. WHEN the wizard is closed without completing, THEN the system SHALL discard all entered data

## Technical Notes

### Backend Implementation
- Create `POST /api/v1/person/search-matches` endpoint
- Implement fuzzy matching using a library like `fuzzywuzzy` or `rapidfuzz` in Python
- Use SQL joins to efficiently find persons matching address and religion criteria
- Return results sorted by match score

### Frontend Implementation
- Add new `ConnectExistingPersonStep.tsx` component
- Update `AddFamilyMemberDialog.tsx` to conditionally show the new step
- Implement confirmation dialog for connecting to existing person
- Handle two different completion flows: create new vs. connect existing

### Performance Considerations
- Index person_address and person_religion tables on person_id for faster lookups
- Limit search results to top 10 matches to avoid overwhelming the user
- Consider caching search results during the wizard session
