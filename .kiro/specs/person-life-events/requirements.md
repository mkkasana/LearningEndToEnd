# Requirements Document

## Introduction

This feature enables users to record and manage significant life events for themselves (their person record). Life events capture important milestones such as births, marriages, property purchases, achievements, and other meaningful moments. Events are displayed in a sorted list with full CRUD capabilities through a multi-step dialog flow.

## Glossary

- **Life_Event**: A significant occurrence in a person's life worth recording (e.g., birth of child, marriage, property purchase)
- **Person**: An individual in the system, linked to a user account
- **Event_Type**: A predefined category for classifying life events
- **System**: The Life Events management feature
- **User**: An authenticated person using the application

## Requirements

### Requirement 1: View Life Events

**User Story:** As a user, I want to view all my life events in a sorted list, so that I can see my life milestones chronologically.

#### Acceptance Criteria

1. WHEN a user navigates to the Life Events page, THE System SHALL display all life events for the user's person record
2. THE System SHALL sort life events by year (descending), then by month (descending), then by date (descending) - most recent first
3. WHEN no life events exist, THE System SHALL display an empty state message encouraging the user to add their first event
4. THE System SHALL display event type, title, year, and location for each event in the list

### Requirement 2: Create Life Event (Multi-Step Flow)

**User Story:** As a user, I want to add new life events through a guided multi-step process, so that I can record significant moments in my life with all relevant details.

#### Acceptance Criteria

**Step 1: Basic Information**
1. WHEN a user clicks the "Add Life Event" button, THE System SHALL display Step 1 of the multi-step dialog
2. THE System SHALL require the user to select an event type from predefined options: Birth, Marriage, Death, Purchase, Sale, Achievement, Education, Career, Health, Travel, Other
3. THE System SHALL require a title with a maximum of 100 characters
4. THE System SHALL require an event year
5. THE System SHALL allow optional event month (1-12) and event date
6. IF event date is provided, THEN THE System SHALL validate it against the provided month and year
7. THE System SHALL allow an optional description with a maximum of 500 characters
8. WHEN the user clicks "Next", THE System SHALL validate Step 1 fields and proceed to Step 2

**Step 2: Location Details**
9. THE System SHALL pre-populate address fields (country, state, district, sub-district, locality) with the person's default address
10. THE System SHALL allow the user to modify any address field
11. THE System SHALL allow an optional address details text field with a maximum of 30 characters
12. THE System SHALL provide a "Back" button to return to Step 1
13. WHEN the user clicks "Next", THE System SHALL proceed to Step 3

**Step 3: Review and Confirm**
14. THE System SHALL display a summary of all entered information for review
15. THE System SHALL provide a "Back" button to return to Step 2
16. WHEN the user clicks "Save", THE System SHALL create the life event and close the dialog
17. WHEN the life event is created successfully, THE System SHALL refresh the events list and show a success message
18. WHEN the form submission fails, THE System SHALL display an appropriate error message

**Progress Indicator**
19. THE System SHALL display a progress indicator showing the current step (1 of 3, 2 of 3, 3 of 3)

### Requirement 3: Edit Life Event

**User Story:** As a user, I want to edit my life events, so that I can correct or update event details.

#### Acceptance Criteria

1. WHEN a user clicks the edit action on a life event, THE System SHALL display the edit form pre-populated with existing data
2. THE System SHALL apply the same validation rules as event creation
3. WHEN the form is submitted with valid data, THE System SHALL update the life event and refresh the list
4. THE System SHALL only allow users to edit their own life events

### Requirement 4: Delete Life Event

**User Story:** As a user, I want to delete life events, so that I can remove incorrect or unwanted entries.

#### Acceptance Criteria

1. WHEN a user clicks the delete action on a life event, THE System SHALL display a confirmation dialog
2. WHEN the user confirms deletion, THE System SHALL remove the life event and refresh the list
3. WHEN the user cancels deletion, THE System SHALL close the confirmation dialog without changes
4. THE System SHALL only allow users to delete their own life events

### Requirement 5: Sidebar Navigation

**User Story:** As a user, I want to access Life Events from the sidebar, so that I can easily navigate to this feature.

#### Acceptance Criteria

1. THE System SHALL display a "Life Events" option in the sidebar navigation
2. WHEN a user clicks "Life Events" in the sidebar, THE System SHALL navigate to the Life Events page

### Requirement 6: Event Type Management

**User Story:** As a user, I want predefined event types, so that I can categorize my life events consistently.

#### Acceptance Criteria

1. THE System SHALL provide the following predefined event types: Birth, Marriage, Death, Purchase, Sale, Achievement, Education, Career, Health, Travel, Other
2. WHEN "Other" is selected, THE System SHALL allow the user to specify a custom event type in the title field
