# Requirements Document

## Introduction

This feature adds a "View" button to each person card (node) rendered in the Rishte relationship graph. When clicked, it opens the same PersonDetailsPanel sliding panel used in the Family Tree and Find Partner views, providing a consistent user experience for viewing detailed person information across the application.

The PersonDetailsPanel already includes an "Explore" button that navigates to the Family Tree with the selected person, so users will have access to both View and Explore functionality through this integration.

Note: This feature modifies the Rishte-specific `PersonNode` component directly rather than sharing components with Find Partner, keeping the codebases independent.

## Glossary

- **Rishte_Graph**: The React Flow graph visualization component that displays the relationship path between two selected persons in the Rishte page
- **PersonNode**: The custom React Flow node component (in `/components/Rishte/`) that renders individual person cards within the Rishte_Graph
- **PersonDetailsPanel**: The existing sliding panel component that displays comprehensive person information including photo, name, dates, gender, address, religion, life events, and an Explore button to navigate to Family Tree
- **Person_A**: The first person selected for relationship visualization (green border)
- **Person_B**: The second person selected for relationship visualization (blue border)

## Requirements

### Requirement 1: Add View Button to PersonNode

**User Story:** As a user viewing the Rishte relationship graph, I want to see a View button on each person card, so that I can quickly access detailed information about any person in the relationship path.

#### Acceptance Criteria

1. THE PersonNode component SHALL display a View button with an Eye icon below the person's name and years
2. WHEN a user clicks the View button, THE PersonNode SHALL emit an onViewClick callback with the person's ID
3. THE View button SHALL stop event propagation to prevent triggering any parent click handlers
4. THE View button SHALL be keyboard accessible, responding to Enter and Space key presses
5. THE View button SHALL have an aria-label of "View details for {firstName} {lastName}"

### Requirement 2: Integrate PersonDetailsPanel in Rishte Page

**User Story:** As a user on the Rishte page, I want to see the same person details panel as in the Family Tree and Find Partner pages, so that I have a consistent experience when viewing person information.

#### Acceptance Criteria

1. THE Rishte page SHALL include the PersonDetailsPanel component
2. WHEN a View button is clicked on any PersonNode, THE PersonDetailsPanel SHALL open with that person's details
3. THE PersonDetailsPanel SHALL slide in from the right side of the screen
4. THE PersonDetailsPanel SHALL display the same information as in Family Tree: photo, full name, birth/death years, gender, address, religion, and life events
5. WHEN the user closes the PersonDetailsPanel, THE panel SHALL close without affecting the Rishte graph state

### Requirement 3: Pass View Click Handler Through Component Hierarchy

**User Story:** As a developer, I want the view click handler to be properly passed through the component hierarchy, so that the click event reaches the page component that manages the panel state.

#### Acceptance Criteria

1. THE RishteGraph component SHALL accept an optional onNodeViewClick callback prop
2. THE RishteGraph component SHALL pass the onNodeViewClick callback to each PersonNode via node data
3. THE PersonNode component SHALL call the onNodeViewClick callback when the View button is clicked
4. THE PersonNodeData interface SHALL include an optional onViewClick callback property

### Requirement 4: Visual Consistency with Other Views

**User Story:** As a user, I want the View button in the Rishte graph to look identical to the View button in the Family Tree and Find Partner views, so that the interface feels consistent.

#### Acceptance Criteria

1. THE View button SHALL use the outline variant styling
2. THE View button SHALL use the small (sm) size
3. THE View button SHALL display an Eye icon followed by the text "View"
4. THE View button SHALL have consistent spacing and positioning relative to other card content
