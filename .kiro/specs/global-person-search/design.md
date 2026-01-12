# Design Document: Global Person Search

## Overview

This design document describes the implementation of a dedicated Search page accessible from the sidebar navigation. The feature allows users to browse and search for persons in the system with advanced filtering capabilities. By default, it displays persons from the user's locality, with a slide-out filter panel for refined searching.

## Architecture

The feature follows the existing full-stack architecture:
- **Frontend**: React with TanStack Router and TanStack Query
- **Backend**: FastAPI with SQLModel and PostgreSQL
- **Pattern**: RESTful API with typed request/response models

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
├─────────────────────────────────────────────────────────────────┤
│  AppSidebar.tsx    │  search.tsx (route)  │  SearchFilterPanel  │
│  (nav item)        │  (main page)         │  (slide-out)        │
├─────────────────────────────────────────────────────────────────┤
│                    TanStack Query (caching)                      │
├─────────────────────────────────────────────────────────────────┤
│                    OpenAPI Generated Client                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Backend                                  │
├─────────────────────────────────────────────────────────────────┤
│  search_person.py  │  PersonSearchService  │  PersonRepository  │
│  (API routes)      │  (business logic)     │  (data access)     │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Frontend Components

#### 1. AppSidebar Update
**File**: `frontend/src/components/Sidebar/AppSidebar.tsx`

Add new navigation item:
```typescript
const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: Briefcase, title: "Items", path: "/items" },
  { icon: UsersRound, title: "Update Family", path: "/family" },
  { icon: Network, title: "Family View", path: "/family-tree" },
  { icon: Calendar, title: "Life Events", path: "/life-events" },
  { icon: Search, title: "Search", path: "/search" },  // NEW
  { icon: Bug, title: "Report Ticket", path: "/support-tickets" },
]
```

#### 2. Search Page Route
**File**: `frontend/src/routes/_layout/search.tsx`

Main page component with:
- Header with title and filter icon button
- Results grid displaying PersonSearchCard components
- Pagination controls
- Loading and empty states

```typescript
interface SearchPageState {
  filters: SearchFilters
  isFilterPanelOpen: boolean
  page: number
}
```

#### 3. SearchFilterPanel Component
**File**: `frontend/src/components/Search/SearchFilterPanel.tsx`

Slide-out panel using shadcn/ui Sheet component:
- Name section: First Name, Last Name inputs
- Address section: Cascading dropdowns (Country → State → District → Sub-District → Locality)
- Religion section: Cascading dropdowns (Religion → Category → Sub-Category)
- Demographics section: Gender dropdown, Birth Year From/To inputs
- Action buttons: Apply Filters, Reset

```typescript
interface SearchFilterPanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  filters: SearchFilters
  onApply: (filters: SearchFilters) => void
  onReset: () => void
  defaultFilters: SearchFilters
}

interface SearchFilters {
  firstName?: string
  lastName?: string
  countryId: string
  stateId: string
  districtId: string
  subDistrictId: string
  localityId?: string
  religionId: string
  religionCategoryId: string
  religionSubCategoryId?: string
  genderId?: string
  birthYearFrom?: number
  birthYearTo?: number
}
```

#### 4. PersonSearchCard Component
**File**: `frontend/src/components/Search/PersonSearchCard.tsx`

Card displaying person summary:
- Full name (first + middle + last)
- Birth year
- Explore button to navigate to family tree

```typescript
interface PersonSearchCardProps {
  person: PersonSearchResult
  onExplore: (personId: string) => void
}
```

#### 5. usePersonSearch Hook
**File**: `frontend/src/hooks/usePersonSearch.ts`

Custom hook wrapping TanStack Query:
```typescript
function usePersonSearch(filters: SearchFilters, page: number, limit: number) {
  return useQuery({
    queryKey: ['personSearch', filters, page, limit],
    queryFn: () => PersonSearchService.searchPersons({
      requestBody: { ...filters, skip: page * limit, limit }
    }),
    keepPreviousData: true,
  })
}
```

### Backend Components

#### 1. Search Route File
**File**: `backend/app/api/routes/person/search_person.py`

New route file for search endpoints:
```python
router = APIRouter()

@router.post("/search", response_model=PersonSearchResponse)
def search_persons(
    session: SessionDep,
    current_user: CurrentUser,
    request: PersonSearchFilterRequest,
) -> PersonSearchResponse:
    """Search for persons with optional filters and pagination."""
    service = PersonSearchService(session)
    return service.search_persons(request)
```

#### 2. Request/Response Schemas
**File**: `backend/app/schemas/person/person_search.py` (extend existing)

```python
class PersonSearchFilterRequest(SQLModel):
    """Request schema for person search with filters."""
    # Name filters (optional)
    first_name: str | None = None
    last_name: str | None = None
    
    # Address filters (required for filtering)
    country_id: uuid.UUID
    state_id: uuid.UUID
    district_id: uuid.UUID
    sub_district_id: uuid.UUID
    locality_id: uuid.UUID | None = None
    
    # Religion filters (required for filtering)
    religion_id: uuid.UUID
    religion_category_id: uuid.UUID
    religion_sub_category_id: uuid.UUID | None = None
    
    # Demographics (optional)
    gender_id: uuid.UUID | None = None
    birth_year_from: int | None = None
    birth_year_to: int | None = None
    
    # Pagination
    skip: int = 0
    limit: int = Field(default=20, le=100)


class PersonSearchResult(SQLModel):
    """Individual person result in search."""
    person_id: uuid.UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    date_of_birth: date
    name_match_score: float | None = None  # Only present when name filter used


class PersonSearchResponse(SQLModel):
    """Response schema for person search."""
    results: list[PersonSearchResult]
    total: int
    skip: int
    limit: int
```

#### 3. PersonSearchService
**File**: `backend/app/services/person/person_search_service.py`

New service for search logic:
```python
class PersonSearchService:
    def __init__(self, session: Session):
        self.session = session
        self.person_repo = PersonRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)
    
    def search_persons(self, request: PersonSearchFilterRequest) -> PersonSearchResponse:
        """Search persons with filters and pagination."""
        # 1. Find persons by address
        # 2. Find persons by religion
        # 3. Intersect results
        # 4. Apply gender filter if provided
        # 5. Apply birth year range filter if provided
        # 6. Apply name fuzzy matching if provided
        # 7. Apply pagination
        # 8. Return results with total count
```

## Data Models

### Database Queries

The search uses existing tables:
- `person` - Main person data
- `person_address` - Address associations
- `person_religion` - Religion associations

Query strategy:
1. Filter by address (required): `person_address` table
2. Filter by religion (required): `person_religion` table
3. Intersect person IDs from both queries
4. Apply additional filters on `person` table
5. Use EXTRACT(YEAR FROM date_of_birth) for birth year filtering

### Indexes

Existing indexes should be sufficient:
- `person_address`: Composite index on (country_id, state_id, district_id)
- `person_religion`: Index on religion_id
- `person`: Index on gender_id, date_of_birth

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Address Filter Intersection
*For any* search request with address filters (country_id, state_id, district_id, sub_district_id, and optionally locality_id), all returned persons SHALL have at least one address record matching all specified address criteria. When locality_id is provided, it must also match; when omitted, any locality (or none) is acceptable.
**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

### Property 2: Religion Filter Intersection
*For any* search request with religion filters (religion_id, religion_category_id, and optionally religion_sub_category_id), all returned persons SHALL have at least one religion record matching all specified religion criteria. When sub_category_id is provided, it must also match; when omitted, any sub-category (or none) is acceptable.
**Validates: Requirements 6.1, 6.2, 6.3**

### Property 3: Birth Year Range Bounds
*For any* search request with birth year filters, all returned persons SHALL have a birth year satisfying the range constraints: (1) when both birth_year_from and birth_year_to are provided, birth_year_from <= person.birth_year <= birth_year_to; (2) when only birth_year_from is provided, person.birth_year >= birth_year_from; (3) when only birth_year_to is provided, person.birth_year <= birth_year_to.
**Validates: Requirements 8.3, 8.4, 8.5**

### Property 4: Pagination Consistency
*For any* search request with pagination parameters (skip, limit), the response SHALL satisfy: (1) results.length <= limit; (2) results.length <= 100 (max page size); (3) skip + results.length <= total; (4) total represents the actual count of all matching persons regardless of pagination.
**Validates: Requirements 10.4, 10.5, 10.6, 10.8**

### Property 5: Name Matching Threshold
*For any* search request with name filters (first_name and/or last_name provided), all returned persons SHALL have a name_match_score >= 40 using the rapidfuzz algorithm with weighted average (40% first name, 60% last name).
**Validates: Requirements 4.3, 4.4**

### Property 6: Optional Gender Filter Behavior
*For any* search request where gender_id is not provided (null or omitted), the search results SHALL include persons of all genders that match other filter criteria. When gender_id is provided, only persons with matching gender SHALL be returned.
**Validates: Requirements 7.3**

## Error Handling

### Frontend Errors
- **Network errors**: Display toast notification with retry option
- **Validation errors**: Show inline error messages on form fields
- **Empty results**: Display friendly empty state with suggestions

### Backend Errors
- **400 Bad Request**: Invalid filter combinations (e.g., birth_year_from > birth_year_to)
- **401 Unauthorized**: User not authenticated
- **500 Internal Server Error**: Database or unexpected errors

## Testing Strategy

### Unit Tests

**Backend**:
- `test_person_search_service.py`: Test search logic with various filter combinations
- `test_person_search_schemas.py`: Test request/response validation

**Frontend**:
- `SearchFilterPanel.test.tsx`: Test filter form validation and submission
- `PersonSearchCard.test.tsx`: Test card rendering

### Property-Based Tests

Using pytest with Hypothesis for backend:
- Generate random valid filter combinations
- Verify all results match filter criteria
- Verify pagination bounds

### Integration Tests

- `test_person_search_api.py`: End-to-end API tests with database
- Frontend E2E with Playwright: Full search flow testing

### Test Configuration

- Property tests: Minimum 100 iterations
- Each test tagged with: **Feature: global-person-search, Property {number}: {description}**
