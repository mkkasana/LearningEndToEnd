# Design Document: Family Tree V2 — Expandable Tree Visualization

## Overview

Family Tree V2 replaces the fixed 3-row layout with a recursive, expandable tree inspired by the PhoneTool org chart. Users can expand any node upward (parents) or downward (children) to unlimited depth. The tree uses proper SVG connector lines and on-demand data loading.

This is a fully isolated feature — new backend endpoint, new frontend route, new component folder, new data hook. It reuses existing `PersonService` and `PersonRelationshipService` internally but does not modify any V1 code.

## Architecture

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       Frontend Layer                          │
│                                                               │
│  Route: /family-tree-v2                                       │
│  Components: frontend/src/components/FamilyTreeV2/            │
│  Hook: frontend/src/hooks/useFamilyTreeV2Data.ts              │
│                                                               │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  FamilyTreeV2View (Route Component)                      │ │
│  │  - Manages root person state                             │ │
│  │  - Search dialog integration                             │ │
│  │  - ActivePersonContext integration                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  TreeContainer                                           │ │
│  │  - Manages local expand/collapse state                   │ │
│  │  - Renders recursive TreeNode components                 │ │
│  │  - Handles scroll/pan for overflow                       │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  TreeNode (recursive)                                    │ │
│  │  - Renders person card + expand/collapse controls        │ │
│  │  - Renders ConnectorLines to children                    │ │
│  │  - Triggers on-demand data fetching                      │ │
│  └──────────────────────────────────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  ConnectorLines                                          │ │
│  │  - SVG-based parent-to-children lines                    │ │
│  │  - T-shaped branching for multiple children              │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                       Backend Layer                           │
│                                                               │
│  Routes: backend/app/api/routes/family_tree_v2/               │
│  Service: backend/app/services/family_tree_v2_service.py      │
│                                                               │
│  GET /api/v1/family-tree-v2/{person_id}                       │
│    → Returns root node + 1 level parents + 1 level children  │
│                                                               │
│  GET /api/v1/family-tree-v2/{person_id}/children              │
│    → Returns immediate children nodes for on-demand expand    │
│                                                               │
│  GET /api/v1/family-tree-v2/{person_id}/parents               │
│    → Returns immediate parent nodes for on-demand expand      │
│                                                               │
│  Internally reuses: PersonService, PersonRelationshipService  │
└──────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
FamilyTreeV2View
├── Header (title + Search Person button)
├── ActivePersonIndicator (reuse from V1)
├── TreeContainer
│   ├── ParentNodes (expanded upward from root)
│   │   ├── TreeNode (Grandparent) — recursively expandable upward
│   │   │   └── ExpandUpButton
│   │   └── ConnectorLines
│   ├── TreeNode (Root Person) — highlighted
│   │   ├── PersonCardV2 (avatar, name, years, spouse badge)
│   │   ├── ExpandUpButton (if has_parents & not expanded)
│   │   └── ExpandDownButton (if has_children & not expanded)
│   ├── ConnectorLines (root → children)
│   └── ChildrenRow
│       ├── TreeNode (Child 1) — recursively expandable downward
│       │   ├── PersonCardV2
│       │   ├── ExpandDownButton
│       │   ├── ConnectorLines
│       │   └── ChildrenRow (grandchildren, if expanded)
│       ├── TreeNode (Child 2)
│       └── ...
├── PersonDetailsPanel (reuse from V1)
└── SearchPersonDialog (reuse from V1)
```

## Components and Interfaces

### Backend

#### File Structure

```
backend/app/api/routes/family_tree_v2/
├── __init__.py          # Router definition
├── routes.py            # API endpoint handlers
backend/app/services/
├── family_tree_v2_service.py  # Business logic
backend/app/schemas/
├── family_tree_v2.py    # Pydantic response models
```

#### Response Schemas

```python
# backend/app/schemas/family_tree_v2.py

from pydantic import BaseModel

class SpouseSummary(BaseModel):
    id: str
    first_name: str
    last_name: str

class TreeNodeResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    date_of_birth: str
    date_of_death: str | None = None
    gender_id: str
    expanded_down: bool          # Are children currently included?
    expanded_up: bool            # Are parents currently included?
    has_children: bool           # Does this person have child relationships?
    has_parents: bool            # Does this person have parent relationships?
    children: list["TreeNodeResponse"] = []
    parents: list["TreeNodeResponse"] = []
    spouses: list[SpouseSummary] = []

class FamilyTreeV2Response(BaseModel):
    root: TreeNodeResponse

class ChildrenResponse(BaseModel):
    children: list[TreeNodeResponse]

class ParentsResponse(BaseModel):
    parents: list[TreeNodeResponse]
```

#### API Endpoints

```python
# backend/app/api/routes/family_tree_v2/routes.py

# GET /api/v1/family-tree-v2/{person_id}
# Returns: FamilyTreeV2Response
# - Root node with expanded_down=True (immediate children included)
# - Root node with expanded_up=True (immediate parents included)
# - Children/parents have expanded_down=False, expanded_up=False
#   but has_children/has_parents set correctly

# GET /api/v1/family-tree-v2/{person_id}/children
# Returns: ChildrenResponse
# - Each child node with has_children/has_parents set
# - Children not expanded (expanded_down=False, expanded_up=False)

# GET /api/v1/family-tree-v2/{person_id}/parents
# Returns: ParentsResponse
# - Each parent node with has_children/has_parents set
# - Parents not expanded (expanded_down=False, expanded_up=False)
```

#### Service Layer

```python
# backend/app/services/family_tree_v2_service.py

class FamilyTreeV2Service:
    """
    Builds recursive tree structures from existing relationship data.
    Reuses PersonService and PersonRelationshipService internally.
    """

    def get_tree(self, person_id: str) -> TreeNodeResponse:
        """
        Build tree for person with 1 level of parents and 1 level of children.
        1. Fetch person details
        2. Fetch relationships → categorize into parents, children, spouses
        3. For each parent: fetch their details, check if they have parents (has_parents)
        4. For each child: fetch their details, check if they have children (has_children)
        5. Return assembled tree
        """

    def get_children_nodes(self, person_id: str) -> list[TreeNodeResponse]:
        """
        Fetch immediate children as TreeNodeResponse objects.
        Each child includes has_children/has_parents flags but no nested data.
        """

    def get_parent_nodes(self, person_id: str) -> list[TreeNodeResponse]:
        """
        Fetch immediate parents as TreeNodeResponse objects.
        Each parent includes has_children/has_parents flags but no nested data.
        """
```

#### Router Registration

```python
# In backend/app/api/main.py, add:
from app.api.routes.family_tree_v2 import router as family_tree_v2_router

api_router.include_router(
    family_tree_v2_router, prefix="/family-tree-v2", tags=["family-tree-v2"]
)
```

### Frontend

#### File Structure

```
frontend/src/components/FamilyTreeV2/
├── TreeContainer.tsx        # Scrollable container, manages tree state
├── TreeNode.tsx             # Recursive node component
├── PersonCardV2.tsx         # Person card for V2 (avatar, name, years, spouse badge)
├── ConnectorLines.tsx       # SVG connector lines between parent and children
├── ExpandButton.tsx         # Expand/collapse button (up or down)
frontend/src/routes/_layout/
├── family-tree-v2.tsx       # Route component
frontend/src/hooks/
├── useFamilyTreeV2Data.ts   # Data fetching hook
```

#### Key Interfaces

```typescript
// Tree node as returned by API and managed in local state
interface TreeNode {
  id: string
  first_name: string
  last_name: string
  date_of_birth: string
  date_of_death: string | null
  gender_id: string
  expanded_down: boolean
  expanded_up: boolean
  has_children: boolean
  has_parents: boolean
  children: TreeNode[]
  parents: TreeNode[]
  spouses: SpouseSummary[]
}

interface SpouseSummary {
  id: string
  first_name: string
  last_name: string
}
```

#### TreeContainer

```typescript
interface TreeContainerProps {
  rootNode: TreeNode
  rootPersonId: string
  onPersonClick: (personId: string) => void  // Open details panel
}
```

Responsibilities:
- Maintains a mutable copy of the tree in local state (for expand/collapse toggling)
- Provides `expandDown(nodeId)` and `expandUp(nodeId)` callbacks that fetch data and merge into tree state
- Provides `collapseDown(nodeId)` and `collapseUp(nodeId)` callbacks that toggle visibility without API calls
- Wraps the tree in a scrollable/pannable container
- Centers the root node on initial render

#### TreeNode (Recursive)

```typescript
interface TreeNodeProps {
  node: TreeNode
  isRoot: boolean
  onExpandDown: (nodeId: string) => Promise<void>
  onExpandUp: (nodeId: string) => Promise<void>
  onCollapseDown: (nodeId: string) => void
  onCollapseUp: (nodeId: string) => void
  onPersonClick: (personId: string) => void
}
```

Rendering logic:
```
[ExpandUpButton] (if has_parents && !expanded_up)
[CollapseUpButton] (if expanded_up)
    │
[Parent nodes] (if expanded_up, rendered recursively)
    │
    ├── ConnectorLines (from parents down to this node)
    │
[PersonCardV2]  ← this node
    │
    ├── ConnectorLines (from this node down to children)
    │
[Children nodes] (if expanded_down, rendered recursively as horizontal row)
    │
[ExpandDownButton] (if has_children && !expanded_down)
[CollapseDownButton] (if expanded_down)
```

#### PersonCardV2

```typescript
interface PersonCardV2Props {
  node: TreeNode
  isRoot: boolean
  onClick: (personId: string) => void
}
```

Display:
- Avatar (gender-based placeholder using existing `MALE_GENDER_ID`/`FEMALE_GENDER_ID` constants)
- Full name: `first_name last_name`
- Years: `birth_year -` or `birth_year - death_year`
- Spouse badge(s): small text below name showing spouse name(s)
- Root node gets a highlighted border (e.g., `border-2 border-green-500`)

#### ConnectorLines

```typescript
interface ConnectorLinesProps {
  parentRef: React.RefObject<HTMLDivElement>  // Parent node element
  childRefs: React.RefObject<HTMLDivElement>[] // Child node elements
}
```

Implementation approach:
- Use CSS borders/pseudo-elements (simpler, more performant than SVG for this use case)
- Vertical line from parent center-bottom to a horizontal bar
- Horizontal bar spans from leftmost child to rightmost child
- Vertical drop-lines from horizontal bar to each child center-top
- For single child: just a straight vertical line

```
        [Parent]
            │              ← vertical line (CSS border-left on a div)
     ┌──────┼──────┐       ← horizontal bar (CSS border-top on a div)
     │      │      │       ← vertical drop-lines
  [Child1] [Child2] [Child3]
```

CSS approach (no SVG needed):
```css
/* Vertical line from parent */
.connector-vertical {
  border-left: 2px solid hsl(var(--muted-foreground) / 0.3);
  height: 24px;
  margin: 0 auto;
}

/* Horizontal bar spanning children */
.connector-horizontal {
  border-top: 2px solid hsl(var(--muted-foreground) / 0.3);
}

/* Drop line to each child */
.connector-drop {
  border-left: 2px solid hsl(var(--muted-foreground) / 0.3);
  height: 24px;
  margin: 0 auto;
}
```

#### ExpandButton

```typescript
interface ExpandButtonProps {
  direction: "up" | "down"
  isLoading: boolean
  isExpanded: boolean
  onClick: () => void
}
```

- Shows `ChevronDown`/`ChevronUp` icon when collapsed
- Shows `Minus` icon when expanded (to collapse)
- Shows `Loader2` spinner when loading
- Small circular button, muted styling

#### useFamilyTreeV2Data Hook

```typescript
function useFamilyTreeV2Data(rootPersonId: string | null) {
  // Fetches initial tree via GET /api/v1/family-tree-v2/{person_id}
  // Returns: { treeData, isLoading, error, refetch }
  // Uses TanStack Query with queryKey: ["familyTreeV2", rootPersonId]
  // staleTime: 5 minutes, gcTime: 10 minutes
}

function useExpandChildren(personId: string) {
  // Fetches children via GET /api/v1/family-tree-v2/{person_id}/children
  // Returns: { expandChildren, isLoading }
  // Uses TanStack Query mutation or lazy query
}

function useExpandParents(personId: string) {
  // Fetches parents via GET /api/v1/family-tree-v2/{person_id}/parents
  // Returns: { expandParents, isLoading }
}
```

### Tree State Management

The tree state is managed locally in `TreeContainer` using `useState`:

```typescript
const [tree, setTree] = useState<TreeNode>(initialTreeFromAPI)

// Expand down: fetch children, merge into tree
const expandDown = async (nodeId: string) => {
  const children = await fetchChildren(nodeId)
  setTree(prev => mergeChildrenIntoTree(prev, nodeId, children))
}

// Collapse down: toggle expanded_down flag, keep children in memory
const collapseDown = (nodeId: string) => {
  setTree(prev => toggleExpandedDown(prev, nodeId, false))
}

// Helper: recursively find node by ID and update it
function mergeChildrenIntoTree(
  tree: TreeNode, targetId: string, children: TreeNode[]
): TreeNode {
  if (tree.id === targetId) {
    return { ...tree, children, expanded_down: true }
  }
  return {
    ...tree,
    children: tree.children.map(c => mergeChildrenIntoTree(c, targetId, children)),
    parents: tree.parents.map(p => mergeChildrenIntoTree(p, targetId, children)),
  }
}
```

## Data Models

### Existing Models Reused Internally

The backend service reuses these existing models/services internally:
- `PersonService.get_person_by_id()` — fetch person details
- `PersonRelationshipService.get_relationships_by_person()` — fetch all relationships
- `RELATIONSHIP_TYPES` constants — categorize relationships into parents/children/spouses

### Relationship Type Mapping (same as V1)

```python
PARENT_TYPES = ["rel-6a0ede824d101", "rel-6a0ede824d102"]  # Father, Mother
CHILD_TYPES = ["rel-6a0ede824d103", "rel-6a0ede824d104"]    # Daughter, Son
SPOUSE_TYPES = ["rel-6a0ede824d105", "rel-6a0ede824d106", "rel-6a0ede824d107"]  # Wife, Husband, Spouse
```

## Correctness Properties

### Property 1: Tree Node Data Completeness

*For any* tree node returned by the API, the node SHALL contain all required fields (`id`, `first_name`, `last_name`, `date_of_birth`, `gender_id`, `has_children`, `has_parents`, `expanded_down`, `expanded_up`, `children`, `parents`, `spouses`).

**Validates: Requirement 2.3**

### Property 2: Expand Flag Consistency

*For any* tree node, if `expanded_down` is `false` then `children` SHALL be an empty array, and if `expanded_down` is `true` then `children` SHALL contain the actual child nodes. Same for `expanded_up` and `parents`.

**Validates: Requirement 2.4**

### Property 3: Has-Children/Has-Parents Accuracy

*For any* tree node, `has_children` SHALL be `true` if and only if the person has at least one child relationship in the database. Same for `has_parents`.

**Validates: Requirements 2.3, 2.4, 3.4, 3.5**

### Property 4: Expand Idempotency

*For any* node that is already expanded, calling expand again SHALL not duplicate children/parents or make additional API calls.

**Validates: Requirement 4.6**

### Property 5: Collapse Preserves Data

*For any* expanded node, collapsing it SHALL hide the children/parents from view but preserve them in memory, so re-expanding shows them instantly without an API call.

**Validates: Requirements 4.5, 4.6**

### Property 6: Connector Line Correctness

*For any* parent node with N expanded children (N ≥ 1), the connector lines SHALL connect the parent to exactly N children with no missing or extra connections.

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 7: Root Person Highlighting

*For any* tree rendering, exactly one node (the root person) SHALL have the highlighted/distinguished visual style.

**Validates: Requirement 3.2**

### Property 8: Initial Load Completeness

*For any* initial tree load, the root node SHALL have `expanded_down=true` with immediate children and `expanded_up=true` with immediate parents, all from a single API call.

**Validates: Requirements 2.2, 8.3**

### Property 9: Isolation from V1

*For any* code change in the `FamilyTreeV2` folder or `family_tree_v2` backend folder, no files in the V1 `FamilyTree` folder or existing person/relatives routes SHALL be modified.

**Validates: Requirement 10**

## Error Handling

| Scenario | Handling | UI |
|---|---|---|
| No person profile | Show prompt to complete profile | Alert with link to `/complete-profile` |
| Initial tree load fails | Show error with retry button | Alert with retry + "Return to Dashboard" |
| Expand API call fails | Show error toast, keep expand button | Toast notification, button stays visible |
| Person not found (404) | Show error, offer to return to own tree | Alert with "Return to My Tree" button |
| Network timeout | Show timeout message with retry | Toast with retry action |

## Testing Strategy

### Backend Tests

- Unit tests for `FamilyTreeV2Service` methods
- Test tree building with various relationship configurations (no parents, no children, multiple spouses, etc.)
- Test `has_children`/`has_parents` flag accuracy
- Test 404 handling for invalid person IDs
- Test authentication requirement

### Frontend Tests

- Unit tests for `TreeNode` rendering with different node states
- Unit tests for `ConnectorLines` with 1, 2, 3+ children
- Integration tests for expand/collapse flow (mock API)
- Test that collapse preserves data and re-expand is instant
- Test root person highlighting
- Test responsive card sizing at different breakpoints

### Property-Based Tests

- Tag format: `Feature: family-tree-v2, Property {number}: {property_text}`
- Use `fast-check` for generating random tree structures
- Minimum 100 iterations per property test

## Implementation Notes

### Styling

- Tailwind CSS consistent with existing codebase
- CSS-based connector lines (no external library needed)
- Smooth transitions using Tailwind's `animate-in`, `fade-in`, `duration-300`
- Dark mode support via Tailwind dark variants

### Shared Components (reused from V1 without modification)

- `PersonDetailsPanel` — sliding panel for person details
- `SearchPersonDialog` — multi-step search wizard
- `ActivePersonIndicator` — shows assumed person context
- `Avatar`, `Card`, `Button`, etc. — shadcn/ui primitives

### Performance

- Single API call for initial load (root + 1 up + 1 down)
- One API call per expand operation
- TanStack Query caching (5 min stale, 10 min gc)
- Local state for expand/collapse toggling (no API calls for collapse)
- React.memo on TreeNode to prevent unnecessary re-renders of unchanged branches
