# Requirements Document

## Introduction

This document specifies the requirements for Family Tree V2 — an expandable, multi-generational tree visualization that replaces the fixed 3-row layout of V1. Inspired by the PhoneTool org chart (`phonetool.amazon.com/users/{alias}/org`), V2 renders a recursive tree where users can expand any node upward (parents/ancestors) or downward (children/descendants) to unlimited depth. Each node shows a person card with key details, and proper SVG connector lines visually link parent-to-child relationships.

This is a **new, standalone feature** with its own backend API endpoint, frontend route, components folder, and data hook — no modifications to the existing Family Tree V1 code.

## Glossary

- **System**: The full-stack FastAPI application with React frontend
- **User**: An authenticated person using the application
- **Root Person**: The person at the initial center/root of the tree when the page loads
- **Node**: A single person rendered in the tree, containing a person card and expand/collapse controls
- **Expand Upward**: Loading and displaying a node's parents above it
- **Expand Downward**: Loading and displaying a node's children below it
- **Connector Line**: An SVG line (vertical + horizontal branches) connecting a parent node to its child nodes
- **Tree Data**: The recursive data structure returned by the backend representing the expandable tree
- **Collapsed Node**: A node whose children/parents are not currently visible but can be loaded on demand
- **Expanded Node**: A node whose children or parents are currently visible in the tree

## Requirements

### Requirement 1: Navigation & Route

**User Story:** As a user, I want to access Family Tree V2 from the sidebar navigation, so that I can use the new expandable tree visualization.

#### Acceptance Criteria

1. WHEN the application loads THEN the System SHALL display a "Family View V2" menu item in the sidebar navigation with a distinct icon (e.g., `GitBranch` or `TreePine`)
2. WHEN a user clicks "Family View V2" THEN the System SHALL navigate to the `/family-tree-v2` route
3. WHEN the route loads THEN the System SHALL display the tree rooted on the current user's person profile (via `ActivePersonContext`)
4. WHEN the user has no person profile THEN the System SHALL display a message prompting profile completion with a link to `/complete-profile`
5. WHEN the user is assuming another person's role THEN the System SHALL root the tree on the assumed person

### Requirement 2: Backend API — Tree Data Endpoint

**User Story:** As a frontend developer, I want a dedicated backend API that returns a recursive tree structure for a given person, so that the frontend can render an expandable tree without multiple round-trip calls.

#### Acceptance Criteria

1. THE System SHALL expose a new endpoint `GET /api/v1/family-tree-v2/{person_id}` that returns a recursive tree structure
2. WHEN called with a valid `person_id` THEN the System SHALL return the person as the root node with their immediate children (1 level down) pre-expanded and their parents (1 level up) pre-expanded
3. WHEN returning each node THEN the System SHALL include: `id`, `first_name`, `last_name`, `date_of_birth`, `date_of_death`, `gender_id`, `expanded` (boolean), `children` (array of child nodes), `parents` (array of parent nodes), `spouses` (array of spouse details), and `has_children` (boolean indicating if unexpanded children exist), `has_parents` (boolean indicating if unexpanded parents exist)
4. WHEN a node is not expanded THEN the System SHALL return an empty `children`/`parents` array but set `has_children`/`has_parents` to `true` if relationships exist
5. THE System SHALL expose `GET /api/v1/family-tree-v2/{person_id}/children` that returns only the immediate children nodes for on-demand expansion
6. THE System SHALL expose `GET /api/v1/family-tree-v2/{person_id}/parents` that returns only the immediate parent nodes for on-demand expansion
7. WHEN the `person_id` does not exist THEN the System SHALL return a 404 error
8. ALL endpoints SHALL require authentication (current user must be logged in)
9. THE backend code SHALL be in a new folder `backend/app/api/routes/family_tree_v2/` with its own router, service, and schemas — no modifications to existing person or relatives routes

### Requirement 3: Tree Node Rendering

**User Story:** As a user, I want each person in the tree displayed as a card with their key information, so that I can quickly identify family members.

#### Acceptance Criteria

1. WHEN rendering a tree node THEN the System SHALL display a card containing: avatar (gender-based placeholder or photo), full name (first + last), and years display ("birth_year -" or "birth_year - death_year")
2. WHEN the node is the root person THEN the System SHALL visually distinguish it with a highlighted border or background (e.g., green border like V1)
3. WHEN a node has spouses THEN the System SHALL display spouse name(s) as a subtle label or small badge below the person's name on the same card
4. WHEN a node has unexpanded children (`has_children=true` and `children` is empty) THEN the System SHALL display an expand-down button/icon (e.g., chevron-down or "+" icon) below the node
5. WHEN a node has unexpanded parents (`has_parents=true` and `parents` is empty) THEN the System SHALL display an expand-up button/icon (e.g., chevron-up or "+" icon) above the node
6. WHEN a node has expanded children THEN the System SHALL display a collapse button/icon to hide the children
7. WHEN a node has expanded parents THEN the System SHALL display a collapse button/icon to hide the parents
8. WHEN a user clicks on a person's name/avatar area THEN the System SHALL open the PersonDetailsPanel (reuse from V1) showing full details for that person

### Requirement 4: Expand & Collapse Behavior

**User Story:** As a user, I want to expand any person's parents or children on demand, so that I can explore the family tree to unlimited depth without loading everything upfront.

#### Acceptance Criteria

1. WHEN a user clicks the expand-down button on a node THEN the System SHALL call `GET /api/v1/family-tree-v2/{person_id}/children` and render the returned children below that node
2. WHEN a user clicks the expand-up button on a node THEN the System SHALL call `GET /api/v1/family-tree-v2/{person_id}/parents` and render the returned parents above that node
3. WHEN expanding THEN the System SHALL show a loading spinner on the expand button while the API call is in progress
4. WHEN expansion completes THEN the System SHALL animate the new nodes appearing with a smooth fade-in/slide transition
5. WHEN a user clicks the collapse button on an expanded node THEN the System SHALL hide all descendants/ancestors of that node without making an API call (data stays in memory)
6. WHEN a user re-expands a previously collapsed node THEN the System SHALL show the cached data immediately without making another API call
7. WHEN an expand API call fails THEN the System SHALL show an error toast and keep the expand button visible for retry
8. THE System SHALL support expanding multiple branches simultaneously (e.g., expand grandparent's parents while also expanding a child's children)

### Requirement 5: Connector Lines

**User Story:** As a user, I want to see clear visual lines connecting parents to their children in the tree, so that I can understand the family relationships at a glance.

#### Acceptance Criteria

1. WHEN a parent node has expanded children THEN the System SHALL draw a vertical line downward from the parent node
2. WHEN a parent has multiple children THEN the System SHALL draw a horizontal line spanning all children, with vertical drop-lines to each child (T-shaped connector)
3. WHEN a parent has a single child THEN the System SHALL draw a single straight vertical line from parent to child
4. WHEN a node has expanded parents THEN the System SHALL draw vertical lines upward from the node to each parent
5. WHEN connector lines are rendered THEN the System SHALL use SVG or CSS-based lines that are responsive and scale with the tree layout
6. WHEN the tree is collapsed/expanded THEN the System SHALL animate the connector lines appearing/disappearing in sync with the nodes
7. THE connector lines SHALL use a muted color (e.g., `border-muted-foreground/30`) that is visible but not distracting

### Requirement 6: Tree Layout

**User Story:** As a user, I want the tree to be laid out in a clear top-down hierarchy, so that I can visually follow generational relationships.

#### Acceptance Criteria

1. WHEN the tree renders THEN the System SHALL use a top-down vertical layout where parents appear above and children appear below
2. WHEN a node has multiple children THEN the System SHALL display them horizontally side-by-side below the parent
3. WHEN the tree is wider than the viewport THEN the System SHALL allow horizontal scrolling/panning
4. WHEN the tree is taller than the viewport THEN the System SHALL allow vertical scrolling
5. WHEN the tree initially loads THEN the System SHALL center the root person in the visible viewport
6. WHEN a new branch is expanded THEN the System SHALL smoothly scroll to keep the expanded area visible
7. THE tree layout SHALL be responsive — on mobile, cards become smaller but maintain the same hierarchical structure
8. WHEN siblings are displayed THEN the System SHALL space them evenly with consistent gaps

### Requirement 7: Search & Navigate

**User Story:** As a user, I want to search for any person and re-root the tree on them, so that I can explore any family's tree.

#### Acceptance Criteria

1. WHEN the Family Tree V2 page renders THEN the System SHALL display a "Search Person" button in the header area
2. WHEN a user clicks "Search Person" THEN the System SHALL open the existing SearchPersonDialog (reuse from V1)
3. WHEN a user selects a person from search results THEN the System SHALL re-root the entire tree on that person (collapse all, fetch new tree data)
4. WHEN the tree is re-rooted THEN the System SHALL reset all expand/collapse state and start fresh with the new root person's immediate family

### Requirement 8: Performance & Caching

**User Story:** As a user, I want the tree to feel fast and responsive even with many expanded nodes, so that exploring large families is a smooth experience.

#### Acceptance Criteria

1. THE System SHALL cache expanded node data using TanStack Query with a 5-minute stale time (consistent with V1)
2. WHEN navigating back to a previously expanded node THEN the System SHALL serve data from cache without an API call
3. THE initial tree load (root + 1 level up + 1 level down) SHALL complete in a single API call
4. EACH subsequent expand operation SHALL require exactly one API call
5. THE frontend SHALL maintain a local tree state (expanded/collapsed flags) separate from the server data cache
6. WHEN more than 50 nodes are visible THEN the System SHOULD consider virtualizing off-screen nodes for performance (P2/optional)

### Requirement 9: Responsive Design

**User Story:** As a user, I want the expandable tree to work well on all screen sizes, so that I can explore family trees on any device.

#### Acceptance Criteria

1. WHEN on desktop (>1024px) THEN the System SHALL display full-size person cards with avatar, name, years, and spouse info
2. WHEN on tablet (641-1024px) THEN the System SHALL display medium-size cards with name and years
3. WHEN on mobile (<640px) THEN the System SHALL display compact cards with name only, expandable to show details on tap
4. WHEN on any screen size THEN the System SHALL support touch gestures for scrolling/panning the tree
5. WHEN the tree overflows the viewport THEN the System SHALL show scroll indicators or a minimap hint (P2/optional)

### Requirement 10: Isolation from V1

**User Story:** As a developer, I want V2 to be completely isolated from V1, so that changes to V2 never break the existing family tree.

#### Acceptance Criteria

1. THE frontend code SHALL live in a new folder `frontend/src/components/FamilyTreeV2/` with no imports from `frontend/src/components/FamilyTree/` (except shared UI components like PersonDetailsPanel)
2. THE frontend route SHALL be a new file `frontend/src/routes/_layout/family-tree-v2.tsx`
3. THE data hook SHALL be a new file `frontend/src/hooks/useFamilyTreeV2Data.ts`
4. THE backend API SHALL be in a new folder `backend/app/api/routes/family_tree_v2/` with its own service layer in `backend/app/services/family_tree_v2_service.py`
5. THE backend SHALL reuse existing `PersonService` and `PersonRelationshipService` internally but expose its own endpoint and response schemas
6. THE sidebar SHALL show both "Family View" (V1) and "Family View V2" side by side so users can compare
