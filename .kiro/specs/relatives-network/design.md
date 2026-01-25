# Design Document

## Overview

This document describes the design for the "Relatives Network" feature, which provides a dedicated page for users to list their relatives up to a configurable relationship depth. The feature uses a BFS (Breadth-First Search) algorithm to traverse family relationships and supports filtering by depth mode, address, gender, and living status.

The implementation is completely independent from existing features (PartnerMatch, Search) to avoid breaking changes, with all components in dedicated folders.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
├─────────────────────────────────────────────────────────────────┤
│  AppSidebar.tsx    │  relatives-network.tsx  │  FilterPanel     │
│  (nav item)        │  (main page route)      │  (slide-out)     │
├─────────────────────────────────────────────────────────────────┤
│  RelativeCard      │  ResultsGrid            │  PersonDetails   │
│  (person display)  │  (card layout)          │  (reused panel)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│  POST /api/v1/relatives-network/find                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│  RelativesNetworkService                                         │
│  - BFS traversal from person_id                                  │
│  - Depth filtering (up_to / only_at)                            │
│  - Address filtering                                             │
│  - Gender and living status filtering                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Layer                              │
│  Person, PersonRelationship, PersonAddress tables                │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Backend Components

#### 1.1 Schemas (`backend/app/schemas/relatives_network/`)

**File:** `relatives_network_schemas.py`

```python
class RelativesNetworkRequest(BaseModel):
    """Request body for relatives network search."""
    person_id: uuid.UUID
    depth: int = Field(default=3, ge=1, description="Search depth")
    depth_mode: str = Field(default="up_to", description="'up_to' or 'only_at'")
    living_only: bool = Field(default=True, description="Exclude deceased")
    gender_id: int | None = Field(default=None, description="Filter by gender")
    # Address filters (all optional)
    country_id: uuid.UUID | None = None
    state_id: uuid.UUID | None = None
    district_id: uuid.UUID | None = None
    sub_district_id: uuid.UUID | None = None
    locality_id: uuid.UUID | None = None

class RelativeInfo(BaseModel):
    """Information about a single relative."""
    person_id: uuid.UUID
    first_name: str
    last_name: str
    gender_id: int
    birth_year: int | None
    death_year: int | None
    district_name: str | None
    locality_name: str | None
    depth: int

class RelativesNetworkResponse(BaseModel):
    """Response for relatives network search."""
    person_id: uuid.UUID
    total_count: int
    depth: int
    depth_mode: str
    relatives: list[RelativeInfo]
```

#### 1.2 Service (`backend/app/services/relatives_network/`)

**File:** `relatives_network_service.py`

```python
class RelativesNetworkService:
    """Service for finding relatives within a family network using BFS."""
    
    def __init__(self, session: Session):
        self.session = session
        self.max_depth = settings.RELATIVES_NETWORK_MAX_DEPTH
    
    def find_relatives(self, request: RelativesNetworkRequest) -> RelativesNetworkResponse:
        """Find relatives up to or at specified depth."""
        # 1. Validate person exists
        # 2. Validate and cap depth
        # 3. Run BFS traversal
        # 4. Apply filters (living, gender, address)
        # 5. Build response with relative info
        pass
    
    def _bfs_traverse(self, person_id: uuid.UUID, max_depth: int) -> dict[uuid.UUID, int]:
        """BFS traversal returning {person_id: depth} mapping."""
        # Uses deque for level-by-level traversal
        # Tracks visited nodes to avoid cycles
        # Returns all reachable persons with their depth
        pass
    
    def _filter_by_depth_mode(self, depth_map: dict, depth: int, mode: str) -> list[uuid.UUID]:
        """Filter persons by depth mode (up_to or only_at)."""
        pass
    
    def _apply_filters(self, person_ids: list, request: RelativesNetworkRequest) -> list[uuid.UUID]:
        """Apply living, gender, and address filters."""
        pass
    
    def _enrich_relative_info(self, person_id: uuid.UUID, depth: int) -> RelativeInfo:
        """Fetch person details and build RelativeInfo."""
        pass
```

#### 1.3 API Route (`backend/app/api/routes/relatives_network/`)

**File:** `find_relatives.py`

```python
router = APIRouter()

@router.post("/find", response_model=RelativesNetworkResponse)
def find_relatives(
    request: RelativesNetworkRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> RelativesNetworkResponse:
    """Find relatives within the family network."""
    service = RelativesNetworkService(session)
    return service.find_relatives(request)
```

#### 1.4 Configuration

**File:** `backend/app/core/config.py` (add setting)

```python
RELATIVES_NETWORK_MAX_DEPTH: int = 20
```

### 2. Frontend Components

#### 2.1 File Structure

```
frontend/src/
├── routes/_layout/
│   └── relatives-network.tsx      # Main page route
└── components/RelativesNetwork/
    ├── index.ts                   # Barrel export
    ├── types.ts                   # TypeScript interfaces
    ├── RelativeCard.tsx           # Individual relative card
    ├── RelativesResultsGrid.tsx   # Grid layout for cards
    └── RelativesFilterPanel.tsx   # Filter slide-out panel
```

#### 2.2 Types (`types.ts`)

```typescript
export interface RelativesFilters {
  depth: number
  depthMode: 'up_to' | 'only_at'
  livingOnly: boolean
  genderId?: string
  countryId?: string
  stateId?: string
  districtId?: string
  subDistrictId?: string
  localityId?: string
}

export const DEFAULT_FILTERS: RelativesFilters = {
  depth: 3,
  depthMode: 'up_to',
  livingOnly: true,
}
```

#### 2.3 RelativeCard Component

```typescript
interface RelativeCardProps {
  relative: RelativeInfo
  onView: (personId: string) => void
}

// Displays:
// - Gender-based avatar (User icon with color based on gender_id)
// - Name: "{firstName} {lastName}" (truncated)
// - Years: "YYYY - YYYY" or "YYYY" if alive
// - Location: "{district}, {locality}" (truncated)
// - Depth badge: number in corner
// - View button
```

#### 2.4 RelativesFilterPanel Component

Slide-out sheet from left side containing:

1. **Depth Section**
   - Number input (1 to max_depth)
   - Radio/Toggle: "Up to" | "Only at"

2. **Filters Section**
   - Living only checkbox (default: checked)
   - Gender dropdown (Any, Male, Female)

3. **Address Section** (cascading dropdowns)
   - Country → State → District → Sub-District → Locality
   - All optional, no defaults

4. **Actions**
   - Reset button
   - Apply Filters button

#### 2.5 Main Page Route (`relatives-network.tsx`)

```typescript
function RelativesNetworkPage() {
  // State
  const [filters, setFilters] = useState<RelativesFilters>(DEFAULT_FILTERS)
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false)
  const [detailsPersonId, setDetailsPersonId] = useState<string | null>(null)
  
  // Get active person from context
  const { activePersonId } = useActivePersonContext()
  
  // Query for relatives
  const { data, isLoading, error } = useQuery({
    queryKey: ['relatives-network', activePersonId, filters],
    queryFn: () => RelativesNetworkService.findRelatives({
      person_id: activePersonId,
      ...filtersToRequest(filters),
    }),
    enabled: !!activePersonId,
  })
  
  // Render: Header, Results count, Grid/Loading/Empty/Error states
  // Filter panel, PersonDetailsPanel
}
```

## Data Models

### Request/Response Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Frontend       │     │  API            │     │  Service        │
│  RelativesFilters│ ──▶ │  Request        │ ──▶ │  BFS + Filter   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  RelativeCard[] │ ◀── │  Response       │ ◀── │  RelativeInfo[] │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### BFS Algorithm

```
Input: person_id, max_depth
Output: dict[person_id -> depth]

1. Initialize:
   - visited = {person_id: 0}
   - queue = deque([person_id])
   - current_depth = 0

2. While queue is not empty AND current_depth < max_depth:
   a. Process all nodes at current level
   b. For each node, get all relationships
   c. For each related person not in visited:
      - Add to visited with depth = current_depth + 1
      - Add to queue
   d. Increment current_depth

3. Return visited (excluding original person_id)
```

### Depth Mode Logic

```
depth_mode = "up_to":
  Return all persons where depth <= requested_depth

depth_mode = "only_at":
  Return all persons where depth == requested_depth
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Self Exclusion
*For any* person_id and any depth/filter combination, the requesting person SHALL NOT appear in the results list.
**Validates: Requirements 2.7, 10.6**

### Property 2: Depth Bounds - Up To Mode
*For any* search with depth_mode="up_to" and depth=N, all returned relatives SHALL have depth values between 1 and N (inclusive).
**Validates: Requirements 6.4**

### Property 3: Depth Bounds - Only At Mode
*For any* search with depth_mode="only_at" and depth=N, all returned relatives SHALL have depth value exactly equal to N.
**Validates: Requirements 6.5**

### Property 4: Max Depth Enforcement
*For any* request with depth > RELATIVES_NETWORK_MAX_DEPTH, the service SHALL cap the depth to RELATIVES_NETWORK_MAX_DEPTH.
**Validates: Requirements 6.6, 11.3**

### Property 5: Living Filter Correctness
*For any* search with living_only=true, all returned relatives SHALL have death_year=None (no deceased persons).
**Validates: Requirements 8.2**

### Property 6: Gender Filter Correctness
*For any* search with a specific gender_id, all returned relatives SHALL have that gender_id.
**Validates: Requirements 8.5**

### Property 7: Results Limit
*For any* search, the number of returned relatives SHALL NOT exceed 100.
**Validates: Requirements 3.4, 10.5**

### Property 8: Depth Consistency
*For any* relative in the results, the depth value SHALL equal the minimum number of relationship hops from the requesting person to that relative.
**Validates: Requirements 4.6**

## Error Handling

| Error Condition | HTTP Status | Message |
|-----------------|-------------|---------|
| Person not found | 404 | "Person not found" |
| Invalid depth (< 1) | 400 | "Depth must be at least 1" |
| Invalid depth_mode | 400 | "Invalid depth mode. Use 'up_to' or 'only_at'" |
| No active person (frontend) | - | Display "Complete your profile" message |

## Testing Strategy

### Unit Tests

1. **Service Layer Tests**
   - BFS traversal correctness
   - Depth mode filtering (up_to vs only_at)
   - Living/gender/address filter application
   - Max depth capping
   - Self exclusion

2. **API Route Tests**
   - Valid request handling
   - Error responses (404, 400)
   - Authentication requirement

3. **Frontend Component Tests**
   - RelativeCard rendering with various data
   - Filter panel state management
   - Results grid layout

### Property-Based Tests

Using `pytest` with `hypothesis` for backend:

1. **Property 1**: Self exclusion - generate random person_id and filters, verify self not in results
2. **Property 2**: Up-to depth bounds - generate random depth, verify all results have depth <= N
3. **Property 3**: Only-at depth bounds - generate random depth, verify all results have depth == N
4. **Property 4**: Max depth enforcement - generate depth > max, verify capping
5. **Property 5**: Living filter - generate with living_only=true, verify no death_year in results
6. **Property 6**: Gender filter - generate with gender_id, verify all results match
7. **Property 7**: Results limit - generate large graphs, verify <= 100 results

### Integration Tests

1. End-to-end flow: Page load → Filter → Results display
2. Filter panel interactions
3. View button → PersonDetailsPanel opening

## Future Improvements

1. **Export functionality**: CSV/Excel export of relatives list with contact info
2. **Print-friendly view**: Formatted list for printing
3. **Bulk actions**: Copy all addresses, send bulk messages
4. **Relationship path**: Show the relationship path (e.g., "Father's Brother's Son")
5. **Grouping by depth**: Visual grouping of relatives by depth level
