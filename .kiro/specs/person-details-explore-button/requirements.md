# Requirements Document

## Introduction

This feature adds an "Explore in Family Tree" button to the PersonDetailsPanel component. When users view a person's details (from Find Partner graph, Family Tree, or any other context), they will have the option to navigate to the Family Tree view with that person selected as the center of the tree. This provides a seamless way to explore a person's family network after viewing their details.

## Glossary

- **PersonDetailsPanel**: A sliding sheet component that displays comprehensive person information including photo, name, dates, gender, address, religion, and life events
- **Explore_Button**: A button with Network icon that navigates to the Family Tree view with a specific person selected
- **Family_Tree_View**: The `/family-tree` route that displays a visual family tree centered on a selected person
- **Session_Storage**: Browser storage used to pass the person ID between pages
- **Custom_Event**: A browser event (`familyTreeExplorePerson`) used to notify the Family Tree component of the selected person

## Requirements

### Requirement 1: Explore Button Display

**User Story:** As a user viewing person details, I want to see an "Explore in Family Tree" button, so that I can quickly navigate to view that person's family network.

#### Acceptance Criteria

1. WHEN the PersonDetailsPanel displays person details successfully, THE Explore_Button SHALL be rendered below the user avatar
2. THE Explore_Button SHALL display a Network icon followed by the text "Explore in Family Tree"
3. THE Explore_Button SHALL use the outline variant styling consistent with other action buttons
4. THE Explore_Button SHALL be visible in all contexts where PersonDetailsPanel is used (Find Partner, Family Tree, etc.)

### Requirement 2: Explore Button Interaction

**User Story:** As a user, I want to click the Explore button to navigate to the Family Tree view with the selected person, so that I can see their family relationships.

#### Acceptance Criteria

1. WHEN a user clicks the Explore_Button, THE system SHALL store the person ID in Session_Storage with key "familyTreeExplorePersonId"
2. WHEN a user clicks the Explore_Button, THE PersonDetailsPanel SHALL close automatically
3. WHEN a user clicks the Explore_Button, THE system SHALL navigate to the `/family-tree` route
4. WHEN navigation completes, THE system SHALL dispatch a Custom_Event with the person ID to notify the Family_Tree_View
5. THE Family_Tree_View SHALL receive the person ID and set it as the selected person, centering the tree on that person

### Requirement 3: Keyboard Accessibility

**User Story:** As a user who navigates with keyboard, I want to activate the Explore button using keyboard, so that I can use the feature without a mouse.

#### Acceptance Criteria

1. THE Explore_Button SHALL be focusable via keyboard navigation (Tab key)
2. WHEN the Explore_Button has focus and user presses Enter, THE system SHALL trigger the explore action
3. WHEN the Explore_Button has focus and user presses Space, THE system SHALL trigger the explore action
4. THE Explore_Button SHALL have an appropriate aria-label for screen readers

### Requirement 4: Loading and Error States

**User Story:** As a user, I want the Explore button to handle edge cases gracefully, so that I have a reliable experience.

#### Acceptance Criteria

1. WHILE the PersonDetailsPanel is in loading state, THE Explore_Button SHALL NOT be displayed
2. WHILE the PersonDetailsPanel is in error state, THE Explore_Button SHALL NOT be displayed
3. IF the person ID is null or undefined, THE Explore_Button SHALL NOT be displayed
