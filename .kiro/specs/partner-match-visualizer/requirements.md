# Requirements Document

## Introduction

This feature enhances the existing Find Partner UI by replacing the raw JSON results display with an interactive graph visualization. When partner matches are found, users can select a match from a dropdown list and see a visual relationship path from the seeker to the selected match, rendered as a generation-based family tree diagram.

This feature is implemented entirely within the existing `FindPartner/` folder structure to maintain isolation from the Rishte components. All graph components are duplicated (not shared) to avoid coupling and prevent breaking existing functionality.

## Glossary

- **Seeker**: The active person for whom partner matches are being searched
- **Match**: A person identified as an eligible partner candidate by the API
- **Match_Selector**: A dropdown component displaying all matches for user selection
- **Match_Graph**: The React Flow-based interactive diagram displaying the relationship path from Seeker to selected Match
- **Match_Person_Node**: A custom React Flow node component representing a single person in the path
- **Match_Relationship_Edge**: A custom React Flow edge component showing the relationship type between connected persons
- **Path_Extractor**: The logic that extracts a linear path from the BFS exploration graph by tracing from match back to seeker
- **Generation_Level**: A horizontal row in the graph representing people of the same generation

## Requirements

### Requirement 1: Match Selector Display

**User Story:** As a user, I want to see a dropdown list of all matches after searching, so that I can select which match's relationship path to view.

#### Acceptance Criteria

1. WHEN the partner-match API returns with matches, THE System SHALL display a Match_Selector dropdown
2. THE Match_Selector SHALL display the total number of matches found (e.g., "5 matches found")
3. THE Match_Selector dropdown SHALL list all matches showing first name, last name, and birth year
4. THE Match_Selector SHALL sort matches by depth (closest relationship first)
5. WHEN matches are returned, THE Match_Selector SHALL auto-select the first match by default
6. WHEN a user selects a different match, THE System SHALL update the graph to show the path to the newly selected match

### Requirement 2: No Matches State

**User Story:** As a user, I want clear feedback when no matches are found, so that I know the search completed but found no results.

#### Acceptance Criteria

1. WHEN the partner-match API returns with zero matches, THE System SHALL display a "No matches found" message
2. WHEN no matches are found, THE System SHALL NOT display the Match_Selector dropdown
3. WHEN no matches are found, THE System SHALL NOT display the Match_Graph

### Requirement 3: Path Extraction from BFS Graph

**User Story:** As a developer, I want to extract a linear path from the BFS exploration graph, so that I can render the relationship path from seeker to match.

#### Acceptance Criteria

1. THE Path_Extractor SHALL trace backwards from the selected match using `from_person` pointers until reaching the seeker
2. THE Path_Extractor SHALL produce an ordered array of persons from seeker to match
3. THE Path_Extractor SHALL handle cases where the match is directly connected to the seeker (single hop)
4. THE Path_Extractor SHALL handle multi-hop paths through the family tree

### Requirement 4: Path Summary Display

**User Story:** As a user, I want to see a text summary of the relationship path, so that I can quickly understand the connection.

#### Acceptance Criteria

1. WHEN a match is selected, THE System SHALL display a path summary showing the sequence of names
2. THE path summary SHALL use "→" as separator between names (e.g., "John → Ram → Shyam → Priya")
3. THE path summary SHALL display names in order from seeker to match

### Requirement 5: Generation-Based Graph Layout

**User Story:** As a user, I want to see the relationship path as a family tree with clear generations, so that I can understand the family structure at a glance.

#### Acceptance Criteria

1. THE Match_Graph SHALL render persons of the same generation on the same horizontal level
2. THE Match_Graph SHALL position spouse/husband/wife pairs side-by-side on the same level
3. THE Match_Graph SHALL position children below their parents
4. THE Match_Graph SHALL calculate generation levels based on parent-child relationships in the path

### Requirement 6: Match Person Node Display

**User Story:** As a user, I want to see relevant information about each person in the path, so that I can identify them easily.

#### Acceptance Criteria

1. THE Match_Person_Node SHALL display a circular avatar placeholder with a User icon
2. THE Match_Person_Node SHALL display the person's first name and last name below the avatar
3. THE Match_Person_Node SHALL display the person's birth year, and death year if applicable (format: "1990 -" or "1990 - 2020")
4. THE Match_Person_Node SHALL visually distinguish the Seeker with a green border and "Seeker" label
5. THE Match_Person_Node SHALL visually distinguish the Match with a blue border and "Match" label
6. THE Match_Person_Node SHALL NOT include View or Explore buttons (simplified display)

### Requirement 7: Match Relationship Edge Display

**User Story:** As a user, I want to see the relationship type between connected persons, so that I understand how they are related.

#### Acceptance Criteria

1. THE Match_Relationship_Edge SHALL display the relationship label (Son, Daughter, Father, Mother, Spouse, Husband, Wife)
2. THE Match_Relationship_Edge SHALL use vertical edges for parent-child relationships
3. THE Match_Relationship_Edge SHALL use horizontal edges for spouse relationships
4. THE Match_Relationship_Edge SHALL display arrows indicating the direction of the path
5. THE Match_Relationship_Edge SHALL have distinct styling for spouse edges (dashed line, different color)

### Requirement 8: Graph Interactivity

**User Story:** As a user, I want to interact with the graph, so that I can explore the relationship path comfortably.

#### Acceptance Criteria

1. THE Match_Graph SHALL support zooming in and out
2. THE Match_Graph SHALL support panning/dragging to navigate the graph
3. THE Match_Graph SHALL provide a "Fit View" control to auto-fit the entire graph in the viewport
4. THE Match_Graph SHALL provide zoom controls (zoom in, zoom out buttons)
5. WHEN the graph is rendered, THE System SHALL automatically fit the view to show all nodes

### Requirement 9: Component Isolation

**User Story:** As a developer, I want all new components in the FindPartner folder, so that Rishte components remain unchanged and unaffected.

#### Acceptance Criteria

1. THE System SHALL create all new graph components under `frontend/src/components/FindPartner/`
2. THE new components SHALL NOT import from or depend on any Rishte components
3. THE new components SHALL NOT modify any existing Rishte component files
4. THE existing FindPartner components (PartnerFilterPanel, TagInput, etc.) SHALL remain unchanged

### Requirement 10: Replace JSON Display

**User Story:** As a user, I want to see a visual graph instead of raw JSON, so that I can easily understand the match relationships.

#### Acceptance Criteria

1. THE System SHALL replace the current raw JSON display in PartnerResultsDisplay with the new Match_Selector and Match_Graph
2. WHEN matches exist, THE System SHALL display the Match_Selector and Match_Graph
3. THE System SHALL remove the raw JSON pretty-print display

