# Requirements Document

## Introduction

This feature adds an intelligent family member discovery system that proactively suggests potential family connections before the user enters the "Add Family Member" wizard. When a user clicks "Add Family Member", the system first searches for persons who are connected to the user's existing family members but not yet connected to the user. This helps users quickly discover and connect to extended family members without manually entering their information.

## Glossary

- **Person**: An individual record in the system containing biographical information
- **Family Member**: A person related to the current user through a relationship
- **Relationship**: A connection between two persons (e.g., Father, Mother, Spouse, Son, Daughter)
- **Direct Connection**: A relationship directly between the current user and another person
- **Indirect Connection**: A relationship path through one or more intermediate persons
- **Discovered Family Member**: A person who is connected to the user's family members but not directly connected to the user
- **Relationship Inference**: The process of determining the appropriate relationship type based on existing family connections

## Requirements

### Requirement 1

**User Story:** As a user clicking "Add Family Member", I want to see suggested family members who are already connected to my family, so that I can quickly connect to them without entering their information manually.

#### Acceptance Criteria

1. WHEN a user clicks "Add Family Member", THEN the system SHALL make an API call to discover potential family member suggestions
2. WHEN the API returns suggested family members, THEN the system SHALL display a "Discover Family Members" dialog with button to "Skip: Move to create new" button
3. WHEN a user clicks "Skip: Move to create new" then user should be taken to the multi-step wizard
4. WHEN the API returns no suggestions, THEN the system SHALL proceed directly to the multi-step "Add Family Member" wizard
5. WHEN the user closes the "Discover Family Members" dialog without connecting, THEN the system SHALL proceed to the multi-step "Add Family Member" wizard
6. WHEN the user successfully connects to a discovered family member, THEN the system SHALL close the dialog, show a success message, and refresh the family members list

### Requirement 2

**User Story:** As a user viewing discovered family members, I want to see relevant details about each suggested person and the inferred relationship, so that I can decide whether to connect to them.

#### Acceptance Criteria

1. WHEN displaying discovered family members, THEN the system SHALL show first name, middle name, last name, and date of birth for each person
2. WHEN displaying discovered family members, THEN the system SHALL show the inferred relationship type (e.g., "Son", "Daughter", "Father", "Mother", "Spouse")
3. WHEN displaying discovered family members, THEN the system SHALL show the connection path explaining why this person is suggested (e.g., "Connected to your spouse")
4. WHEN displaying discovered family members, THEN the system SHALL show the address in comma-separated format
5. WHEN displaying discovered family members, THEN the system SHALL show the religion in comma-separated format
6. WHEN displaying discovered family members, THEN the system SHALL present results in a vertically scrollable list
7. WHEN displaying discovered family members, THEN the system SHALL provide a "Connect as <potential relationship>" (Example : "Connect as Spouse") button for each suggested person 

### Requirement 3

**User Story:** As a user who finds a discovered family member, I want to connect to that person with a single action, so that I can quickly establish the family relationship.

#### Acceptance Criteria

1. WHEN a user clicks "Connect as <relation type>" (e.g., "Connect as Spouse") on a discovered family member, THEN the system SHALL display a confirmation dialog
2. WHEN the confirmation dialog is displayed, THEN the system SHALL show the person's full name and the inferred relationship type being created
3. WHEN the user confirms the connection, THEN the system SHALL create a relationship between the current user and the selected person with the inferred relationship type
4. WHEN the user cancels the connection, THEN the system SHALL close the confirmation dialog and return to the discovered family members list
5. WHEN the relationship is successfully created, THEN the system SHALL close the discovery dialog, show a success message, and refresh the family members list

### Requirement 4

**User Story:** As a system, Under discover relatives API call, I want to discover children of the user's spouse who are not connected to the user, so that I can suggest them as potential sons or daughters.

#### Acceptance Criteria

1. WHEN the user is connected to a spouse (relationship type: Wife, Husband, or Spouse), THEN the system SHALL find all persons connected to that spouse with relationship type Son or Daughter
2. WHEN a child of the spouse is found, THEN the system SHALL check if the user is already connected to that child
3. WHEN the user is not connected to the child, THEN the system SHALL include the child in the suggestions
4. WHEN suggesting a child, THEN the system SHALL infer the relationship type as "Son" if the child's gender is male
5. WHEN suggesting a child, THEN the system SHALL infer the relationship type as "Daughter" if the child's gender is female
6. WHEN suggesting a child, THEN the system SHALL include the connection path as "Connected to your spouse [spouse name]"

### Requirement 5

**User Story:** As a system, Under discover relatives API call, I want to discover the spouse of the user's parent who is not connected to the user, so that I can suggest them as a potential parent.

#### Acceptance Criteria

1. WHEN the user is connected to a parent (relationship type: Father or Mother), THEN the system SHALL find all persons connected to that parent with relationship type Wife, Husband, or Spouse
2. WHEN a spouse of the parent is found, THEN the system SHALL check if the user is already connected to that spouse
3. WHEN the user is not connected to the spouse, THEN the system SHALL include the spouse in the suggestions
4. WHEN suggesting a parent's spouse, THEN the system SHALL infer the relationship type as "Father" if the spouse's gender is male
5. WHEN suggesting a parent's spouse, THEN the system SHALL infer the relationship type as "Mother" if the spouse's gender is female
6. WHEN suggesting a parent's spouse, THEN the system SHALL include the connection path as "Connected to your parent [parent name]"

### Requirement 6

**User Story:** As a system, Under discover relatives API call, I want to discover the parent of the user's child who is not connected to the user, so that I can suggest them as a potential spouse.

#### Acceptance Criteria

1. WHEN the user is connected to a child (relationship type: Son or Daughter), THEN the system SHALL find all persons connected to that child with relationship type Father or Mother
2. WHEN a parent of the child is found, THEN the system SHALL check if the user is already connected to that parent
3. WHEN the user is not connected to the parent, THEN the system SHALL include the parent in the suggestions
4. WHEN suggesting a child's parent, THEN the system SHALL infer the relationship type as "Spouse"
5. WHEN suggesting a child's parent, THEN the system SHALL include the connection path as "Connected to your child [child name]"

### Requirement 7

**User Story:** As a system, Under discover relatives API call, I want to exclude persons who are already connected to the user, so that I don't suggest duplicate connections.

#### Acceptance Criteria

1. WHEN discovering family members, THEN the system SHALL exclude persons who already have an active relationship with the current user
2. WHEN discovering family members, THEN the system SHALL exclude the current user's own person record
3. WHEN all potential suggestions are already connected, THEN the system SHALL return an empty list
4. WHEN an empty list is returned, THEN the system SHALL proceed directly to the multi-step "Add Family Member" wizard
5. WHEN a person has multiple connection paths, THEN the system SHALL include them only once with the most direct connection path

### Requirement 8

**User Story:** As a developer, I want a dedicated API endpoint for discovering family members, so that the discovery logic is centralized and reusable.

#### Acceptance Criteria

1. WHEN the API is called, THEN the system SHALL accept the current user's ID as input
2. WHEN the API processes the discovery, THEN the system SHALL return a list of discovered family members with their details, inferred relationship types, and connection paths
3. WHEN the API encounters an error, THEN the system SHALL return appropriate HTTP status codes and error messages
4. WHEN the API is called, THEN the system SHALL require authentication and validate the current user's permissions
5. WHEN the API returns results, THEN the system SHALL include person ID, name, date of birth, gender, address details, religion details, inferred relationship type, and connection path for each result

### Requirement 9

**User Story:** As a user, I want the option to skip the discovery suggestions and manually add a family member, so that I can add someone who is not in the system yet.

#### Acceptance Criteria

1. WHEN the "Discover Family Members" dialog is displayed, THEN the system SHALL provide a "Skip and Add Manually" button
2. WHEN the user clicks "Skip and Add Manually", THEN the system SHALL close the discovery dialog and open the multi-step "Add Family Member" wizard
3. WHEN the user clicks the close button on the discovery dialog, THEN the system SHALL close the discovery dialog and open the multi-step "Add Family Member" wizard
4. WHEN the user connects to all suggested family members, THEN the system SHALL automatically close the discovery dialog
5. WHEN the discovery dialog closes after connecting to all suggestions, THEN the system SHALL NOT open the multi-step wizard

### Requirement 10

**User Story:** As a user, I want to see the most relevant family member suggestions first, so that I can quickly find the people I'm most likely to connect to.

#### Acceptance Criteria

1. WHEN displaying discovered family members, THEN the system SHALL sort suggestions by relationship proximity (direct connections first)
2. WHEN multiple suggestions have the same proximity, THEN the system SHALL sort by relationship type priority (children, then parents, then spouses)
3. WHEN multiple suggestions have the same relationship type, THEN the system SHALL sort alphabetically by first name
4. WHEN displaying discovered family members, THEN the system SHALL limit results to a maximum of 20 suggestions
5. WHEN more than 20 suggestions exist, THEN the system SHALL show the top 20 based on the sorting criteria

## Technical Notes

### Backend Implementation
- Create `GET /api/v1/person/discover-family-members` endpoint
- Implement `PersonDiscoveryService` with discovery logic for:
  - Spouse's children → User's children
  - Parent's spouse → User's parent
  - Child's parent → User's spouse
- Use SQL joins to efficiently traverse relationship graphs
- Return results with inferred relationship types and connection paths
- Implement sorting and limiting logic

### Frontend Implementation
- Create new `DiscoverFamilyMembersDialog.tsx` component
- Update "Add Family Member" button click handler to:
  1. Call discovery API
  2. Show discovery dialog if results found
  3. Show multi-step wizard if no results or user skips
- Reuse `ConnectConfirmationDialog.tsx` for connection confirmation
- Reuse styling and layout from `ConnectExistingPersonStep.tsx` for consistency

### Relationship Inference Rules
- **Spouse's Son/Daughter** → User's Son/Daughter (based on child's gender)
- **Parent's Spouse** → User's Father/Mother (based on spouse's gender)
- **Child's Father/Mother** → User's Spouse (gender-neutral)

### Performance Considerations
- Index person_relationship table on person_id and related_person_id for faster lookups
- Limit discovery depth to 2 degrees of separation (user → family member → discovered person)
- Cache discovery results for 5 minutes to avoid repeated API calls
- Use eager loading for person details to minimize database queries

### Edge Cases
- Handle cases where gender is not specified (default to "Spouse" for ambiguous relationships)
- Handle cases where multiple relationship types could apply (choose most specific)
- Handle cases where circular relationships exist (prevent infinite loops)
- Handle cases where deceased persons are discovered (include them in suggestions)
