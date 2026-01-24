# Requirements Document

## Introduction

This feature adds a "View" button to each person card (node) rendered in the Find Partner match graph. When clicked, it opens the same PersonDetailsPanel sliding panel used in the Family Tree view, providing a consistent user experience for viewing detailed person information across the application.

## Glossary

- **Match_Graph**: The React Flow graph visualization component that displays the relationship path between the seeker and potential matches in the Find Partner page
- **MatchPersonNode**: The custom React Flow node component that renders individual person cards within the Match_Graph
- **PersonDetailsPanel**: The existing sliding panel component that displays comprehensive person information including photo, name, dates, gender, address, religion, and life events
- **Seeker**: The person who is searching for potential marriage matches
- **Match**: A person identified as a potential marriage match for the seeker

## Requirements

### Requirement 1: Add View Button to MatchPersonNode

**User Story:** As a user viewing the partner match graph, I want to see a View button on each person card, so that I can quickly access detailed information about any person in the relationship path.

#### Acceptance Criteria

1. THE MatchPersonNode component SHALL display a View button with an Eye icon below the person's name and years
2. WHEN a user clicks the View button, THE MatchPersonNode SHALL emit an onViewClick callback with the person's ID
3. THE View button SHALL stop event propagation to prevent triggering any parent click handlers
4. THE View button SHALL be keyboard accessible, responding to Enter and Space key presses
5. THE View button SHALL have an aria-label of "View details for {firstName} {lastName}"

### Requirement 2: Integrate PersonDetailsPanel in Find Partner Page

**User Story:** As a user on the Find Partner page, I want to see the same person details panel as in the Family Tree, so that I have a consistent experience when viewing person information.

#### Acceptance Criteria

1. THE Find Partner page SHALL include the PersonDetailsPanel component
2. WHEN a View button is clicked on any MatchPersonNode, THE PersonDetailsPanel SHALL open with that person's details
3. THE PersonDetailsPanel SHALL slide in from the right side of the screen
4. THE PersonDetailsPanel SHALL display the same information as in Family Tree: photo, full name, birth/death years, gender, address, religion, and life events
5. WHEN the user closes the PersonDetailsPanel, THE panel SHALL close without affecting the match graph state

### Requirement 3: Pass View Click Handler Through Component Hierarchy

**User Story:** As a developer, I want the view click handler to be properly passed through the component hierarchy, so that the click event reaches the page component that manages the panel state.

#### Acceptance Criteria

1. THE MatchGraph component SHALL accept an optional onNodeViewClick callback prop
2. THE MatchGraph component SHALL pass the onNodeViewClick callback to each MatchPersonNode via node data
3. THE MatchPersonNode component SHALL call the onNodeViewClick callback when the View button is clicked
4. THE PartnerResultsDisplay component SHALL accept an optional onViewPerson callback prop
5. THE PartnerResultsDisplay component SHALL pass the onViewPerson callback to the MatchGraph component

### Requirement 4: Visual Consistency with Family Tree

**User Story:** As a user, I want the View button in the partner match graph to look similar to the View button in the Family Tree, so that the interface feels consistent.

#### Acceptance Criteria

1. THE View button SHALL use the outline variant styling
2. THE View button SHALL use the small (sm) size
3. THE View button SHALL display an Eye icon followed by the text "View"
4. THE View button SHALL have consistent spacing and positioning relative to other card content
