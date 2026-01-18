# Requirements Document

## Introduction

The Rishte (Relationship Visualizer) feature provides an interactive UI for discovering and visualizing the relationship path between any two persons in the family database. Users can select two people and see a dynamic, generation-based family tree diagram showing how they are connected through their lineage, with spouses displayed side-by-side and clear generational levels.

This feature is implemented as a completely standalone module with its own dedicated folder structure under `src/components/Rishte/` to maintain separation of concerns and avoid coupling with existing components.

## Glossary

- **Rishte_Page**: The main page component accessible from the sidebar that hosts the relationship finder functionality
- **Person_Selector**: A searchable dropdown component for selecting a person from the database
- **Lineage_Graph**: The React Flow-based interactive diagram displaying the relationship path
- **Person_Node**: A custom React Flow node component representing a single person, styled similar to the existing FamilyTree PersonCard
- **Relationship_Edge**: A custom React Flow edge component showing the relationship type (Son, Daughter, Father, Mother, Spouse, etc.)
- **Generation_Level**: A horizontal row in the graph representing people of the same generation
- **Path_Transformer**: The logic that converts the linear API response into a tree structure for rendering

## Requirements

### Requirement 1: Project Structure

**User Story:** As a developer, I want the Rishte feature to be self-contained in its own folder, so that it doesn't complicate existing components.

#### Acceptance Criteria

1. THE System SHALL create all Rishte components under `src/components/Rishte/` folder
2. THE System SHALL create the route file at `src/routes/_layout/rishte.tsx`
3. THE Rishte components SHALL NOT modify or extend existing FamilyTree components
4. THE Rishte feature SHALL use its own custom React Flow node and edge components

### Requirement 2: Sidebar Navigation

**User Story:** As a user, I want to access the Rishte feature from the main sidebar, so that I can easily find and use the relationship visualization tool.

#### Acceptance Criteria

1. THE Rishte_Page SHALL be accessible via a "Rishte" menu item in the main sidebar after the "Search" item
2. WHEN a user clicks the "Rishte" sidebar item, THE System SHALL navigate to the `/rishte` route
3. THE Sidebar SHALL display an appropriate icon (e.g., GitBranch or similar) for the Rishte menu item

### Requirement 3: Person Selection Interface

**User Story:** As a user, I want to select two persons to find their relationship, so that I can discover how they are connected.

#### Acceptance Criteria

1. THE Rishte_Page SHALL display two Person_Selector components labeled "Person A" and "Person B"
2. WHEN a user types in a Person_Selector, THE System SHALL search for matching persons using the existing person search functionality
3. THE Person_Selector SHALL display person results showing first name, last name, and birth year
4. WHEN a user selects a person, THE Person_Selector SHALL display the selected person's name
5. THE Rishte_Page SHALL display a "Find Relationship" button that is enabled only when both persons are selected
6. WHEN a user clicks "Find Relationship", THE System SHALL call the `/lineage-path/find` API with the selected person IDs

### Requirement 4: Loading and Error States

**User Story:** As a user, I want clear feedback during the search process, so that I know the system is working or if something went wrong.

#### Acceptance Criteria

1. WHILE the lineage path API is loading, THE System SHALL display a loading indicator
2. IF the API returns an error, THEN THE System SHALL display an error message to the user
3. IF no connection is found between the two persons, THEN THE System SHALL display a "No connection found" message
4. WHEN a connection is found, THE System SHALL render the Lineage_Graph with the path data

### Requirement 5: Graph Data Transformation

**User Story:** As a developer, I want the linear API response transformed into a tree structure, so that the graph can be rendered with proper generational layout.

#### Acceptance Criteria

1. THE Path_Transformer SHALL convert the linear linked-list response from the API into a tree structure
2. THE Path_Transformer SHALL identify generation levels based on parent-child relationships
3. THE Path_Transformer SHALL group spouse relationships at the same generation level
4. THE Path_Transformer SHALL handle paths that traverse multiple family trees (connected via marriage)
5. THE Path_Transformer SHALL calculate node positions with generations as horizontal rows

### Requirement 6: Generation-Based Graph Layout

**User Story:** As a user, I want to see the relationship path as a family tree with clear generations, so that I can understand the family structure at a glance.

#### Acceptance Criteria

1. THE Lineage_Graph SHALL render persons of the same generation on the same horizontal level
2. THE Lineage_Graph SHALL position spouse/husband/wife pairs side-by-side on the same level
3. THE Lineage_Graph SHALL position children below their parents
4. THE Lineage_Graph SHALL position siblings horizontally spread within their generation level
5. WHEN two family trees are connected via marriage, THE Lineage_Graph SHALL display them side-by-side with the spouse connection as a horizontal edge

### Requirement 7: Person Node Display

**User Story:** As a user, I want to see relevant information about each person in the path, so that I can identify them easily.

#### Acceptance Criteria

1. THE Person_Node SHALL display a circular avatar placeholder at the top with a gender-appropriate icon (male/female User icon)
2. THE Person_Node SHALL display the person's first name and last name below the avatar
3. THE Person_Node SHALL display the person's birth year, and death year if applicable (format: "1990 -" or "1990 - 2020")
4. THE Person_Node SHALL visually distinguish Person A (start) with a green border
5. THE Person_Node SHALL visually distinguish Person B (end) with a blue border
6. THE Person_Node SHALL follow similar styling to the existing FamilyTree PersonCard (Card component with Avatar, centered text)
7. THE Person_Node SHALL NOT include View or Explore buttons (simplified display for path visualization)

### Requirement 8: Relationship Edge Display

**User Story:** As a user, I want to see the relationship type between connected persons, so that I understand how they are related.

#### Acceptance Criteria

1. THE Relationship_Edge SHALL display the relationship label (Son, Daughter, Father, Mother, Spouse, Husband, Wife)
2. THE Relationship_Edge SHALL use vertical edges for parent-child relationships
3. THE Relationship_Edge SHALL use horizontal edges for spouse relationships
4. THE Relationship_Edge SHALL display arrows indicating the direction of the path from Person A to Person B
5. THE Relationship_Edge SHALL have distinct styling for spouse edges (e.g., double line or different color)

### Requirement 9: Graph Interactivity

**User Story:** As a user, I want to interact with the graph, so that I can explore the relationship path comfortably.

#### Acceptance Criteria

1. THE Lineage_Graph SHALL support zooming in and out
2. THE Lineage_Graph SHALL support panning/dragging to navigate the graph
3. THE Lineage_Graph SHALL provide a "Fit View" control to auto-fit the entire graph in the viewport
4. THE Lineage_Graph SHALL provide zoom controls (zoom in, zoom out buttons)
5. WHEN the graph is rendered, THE System SHALL automatically fit the view to show all nodes

### Requirement 10: Responsive Design

**User Story:** As a user, I want the Rishte page to work well on different screen sizes, so that I can use it on various devices.

#### Acceptance Criteria

1. THE Rishte_Page SHALL be responsive and work on desktop and tablet screen sizes
2. THE Person_Selector components SHALL stack vertically on smaller screens
3. THE Lineage_Graph SHALL fill the available viewport space below the selection controls

### Requirement 11: Path Summary

**User Story:** As a user, I want to see a summary of the relationship path, so that I can quickly understand the connection.

#### Acceptance Criteria

1. WHEN a connection is found, THE System SHALL display the total number of persons in the path
2. THE System SHALL display a text summary of the path (e.g., "sib1_son → sib1_self → father → self → spouse → son")
