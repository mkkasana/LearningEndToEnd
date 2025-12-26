# Design Document

## Overview

This feature adds an intelligent person matching system to the "Add Family Member" wizard. After users enter basic details, address, and religion information, the system searches for existing persons with matching attributes and presents them as connection options. This prevents duplicate person records and helps users discover existing family members already in the system.

The feature introduces a new conditional step in the wizard that appears only when potential matches are found, allowing users to either connect to an existing person or proceed with creating a new one.

## Architecture

### High-Level Flow

```
User Flow:
1. Basic Info Step → 2. Address Step → 3. Religion Step
                                              ↓
                                    [Search API Call]
                                              ↓
                                    ┌─────────┴─────────┐
                                    │                   │
                            Matches Found        No Matches
                                    │                   │
                                    ↓                   ↓
                    4. Connect Existing Step    5. Confirmation Step
                                    │                   │
                            ┌───────┴────────┐          │
                            │                │          │
                    Connect Button    Next Button      │
                            │                │          │
                            ↓                ↓          ↓
                    [Create Relationship]  [Create New Person]
```

### Component Architecture

**Backend:**
- New API endpoint: `POST /api/v1/person/search-matches`
- New service: `PersonMatchingService`
- New schema: `PersonSearchRequest`, `PersonMatchResult`
- Fuzzy matching utility using `rapidfuzz` library

**Frontend:**
- New component: `ConnectExistingPersonStep.tsx`
- Updated component: `AddFamilyMemberDialog.tsx` (conditional step logic)
- New dialog: `ConnectConfirmationDialog.tsx`
- Updated wizard state management for 5-step flow

## Components and Interfaces

### Backend Components

#### 1. PersonMatchingService

```python
class PersonMatchingService:
    """Service for finding and scoring person matches."""
    
    def __init__(self, session: Session):
        self.session = session
        self.person_repo = PersonRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)
        self.relationship_repo = PersonRelationshipRepository(session)
    
    def search_matching_persons(
        self,
        current_user_id: UUID,
        search_criteria: PersonSearchRequest
    ) -> List[PersonMatchResult]:
        """
        Search for persons matching the provided criteria.
        
        Steps:
        1. Find persons with matching address
        2. Find persons with matching religion
        3. Compute intersection
        4. Filter by gender
        5. Apply fuzzy name matching and score
        6. Exclude already-connected persons
        7. Sort by match score
        """
        pass
    
    def calculate_name_match_score(
        self,
        search_first: str,
        search_last: str,
        person_first: str,
        person_last: str
    ) -> float:
        """Calculate fuzzy match score for names (0-100)."""
        pass
```

#### 2. API Endpoint

```python
@router.post("/search-matches", response_model=List[PersonMatchResult])
def search_matching_persons(
    session: SessionDep,
    current_user: CurrentUser,
    search_request: PersonSearchRequest
) -> Any:
    """
    Search for existing persons matching the provided criteria.
    Returns list of potential matches with scores.
    """
    pass
```

### Frontend Components

#### 1. ConnectExistingPersonStep Component

```typescript
interface ConnectExistingPersonStepProps {
  searchCriteria: PersonSearchCriteria
  relationshipType: string
  onConnect: (personId: string) => void
  onNext: () => void
  onBack: () => void
}

export function ConnectExistingPersonStep({
  searchCriteria,
  relationshipType,
  onConnect,
  onNext,
  onBack
}: ConnectExistingPersonStepProps) {
  // Fetch matching persons
  // Display scrollable list
  // Handle connect button clicks
  // Handle next button click
}
```

#### 2. Updated AddFamilyMemberDialog

```typescript
// New state management
const [currentStep, setCurrentStep] = useState(1)
const [matchingPersons, setMatchingPersons] = useState<PersonMatch[]>([])
const [showMatchingStep, setShowMatchingStep] = useState(false)

// Step progression logic
const handleReligionStepNext = async (data) => {
  // Save religion data
  // Call search API
  const matches = await searchMatches(...)
  
  if (matches.length > 0) {
    setMatchingPersons(matches)
    setShowMatchingStep(true)
    setCurrentStep(4) // Go to matching step
  } else {
    setCurrentStep(5) // Skip to confirmation
  }
}
```

## Data Models

### Backend Schemas

#### PersonSearchRequest

```python
class PersonSearchRequest(SQLModel):
    """Request schema for person matching search."""
    
    first_name: str = Field(description="First name to search")
    last_name: str = Field(description="Last name to search")
    middle_name: str | None = Field(default=None, description="Middle name (optional)")
    gender_id: UUID = Field(description="Gender ID")
    date_of_birth: date = Field(description="Date of birth")
    
    # Address criteria
    country_id: UUID
    state_id: UUID
    district_id: UUID
    sub_district_id: UUID | None = None
    locality_id: UUID | None = None
    
    # Religion criteria
    religion_id: UUID
    religion_category_id: UUID | None = None
    religion_sub_category_id: UUID | None = None
```

#### PersonMatchResult

```python
class PersonMatchResult(SQLModel):
    """Result schema for person match."""
    
    person_id: UUID
    first_name: str
    middle_name: str | None
    last_name: str
    date_of_birth: date
    date_of_death: date | None
    
    # Address display
    address_display: str  # Comma-separated
    
    # Religion display
    religion_display: str  # Comma-separated
    
    # Match scoring
    match_score: float = Field(description="Match score 0-100")
    name_match_score: float = Field(description="Name similarity score")
```

### Frontend Types

```typescript
interface PersonSearchCriteria {
  firstName: string
  lastName: string
  middleName?: string
  genderId: string
  dateOfBirth: string
  
  countryId: string
  stateId: string
  districtId: string
  subDistrictId?: string
  localityId?: string
  
  religionId: string
  religionCategoryId?: string
  religionSubCategoryId?: string
}

interface PersonMatch {
  personId: string
  firstName: string
  middleName?: string
  lastName: string
  dateOfBirth: string
  dateOfDeath?: string
  addressDisplay: string
  religionDisplay: string
  matchScore: number
  nameMatchScore: number
}
```

## Search Algorithm

### Step-by-Step Process

```python
def search_matching_persons(self, current_user_id, search_criteria):
    # Step 1: Find persons with matching address
    address_person_ids = self._find_persons_by_address(
        country_id=search_criteria.country_id,
        state_id=search_criteria.state_id,
        district_id=search_criteria.district_id,
        sub_district_id=search_criteria.sub_district_id,
        locality_id=search_criteria.locality_id
    )
    
    # Step 2: Find persons with matching religion
    religion_person_ids = self._find_persons_by_religion(
        religion_id=search_criteria.religion_id,
        category_id=search_criteria.religion_category_id,
        sub_category_id=search_criteria.religion_sub_category_id
    )
    
    # Step 3: Compute intersection
    matching_person_ids = set(address_person_ids) & set(religion_person_ids)
    
    # Step 4: Filter by gender
    persons = self.person_repo.get_by_ids(list(matching_person_ids))
    persons = [p for p in persons if p.gender_id == search_criteria.gender_id]
    
    # Step 5: Exclude already-connected persons
    current_person = self.person_repo.get_by_user_id(current_user_id)
    connected_ids = self.relationship_repo.get_related_person_ids(current_person.id)
    persons = [p for p in persons if p.id not in connected_ids and p.id != current_person.id]
    
    # Step 6: Calculate match scores
    results = []
    for person in persons:
        name_score = self.calculate_name_match_score(
            search_criteria.first_name,
            search_criteria.last_name,
            person.first_name,
            person.last_name
        )
        
        # Only include if name similarity is above threshold (e.g., 60%)
        if name_score >= 60:
            result = self._build_match_result(person, name_score)
            results.append(result)
    
    # Step 7: Sort by match score
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    # Limit to top 10 results
    return results[:10]
```

### Fuzzy Name Matching

```python
from rapidfuzz import fuzz

def calculate_name_match_score(self, search_first, search_last, person_first, person_last):
    """
    Calculate fuzzy match score using token sort ratio.
    Returns score 0-100.
    """
    # Normalize names (lowercase, strip whitespace)
    search_first = search_first.lower().strip()
    search_last = search_last.lower().strip()
    person_first = person_first.lower().strip()
    person_last = person_last.lower().strip()
    
    # Calculate individual scores
    first_name_score = fuzz.ratio(search_first, person_first)
    last_name_score = fuzz.ratio(search_last, person_last)
    
    # Weighted average (last name more important)
    match_score = (first_name_score * 0.4) + (last_name_score * 0.6)
    
    return round(match_score, 2)
```

## Error Handling

### Backend Error Scenarios

1. **Invalid search criteria**: Return 422 with validation errors
2. **Database connection error**: Return 500 with generic error message
3. **User not found**: Return 404 with "Person profile not found"
4. **Search timeout**: Return 504 with timeout message

### Frontend Error Handling

1. **API call fails**: Show error toast, allow retry
2. **No matches found**: Skip to confirmation step automatically
3. **Connection fails**: Show error toast, stay on matching step
4. **Network timeout**: Show retry button

## Testing Strategy

### Backend Unit Tests

```python
def test_search_matching_persons_with_exact_match():
    """Test finding person with exact name, address, and religion match."""
    pass

def test_search_matching_persons_with_fuzzy_name():
    """Test finding person with similar but not exact name."""
    pass

def test_search_excludes_already_connected():
    """Test that already-connected persons are excluded from results."""
    pass

def test_search_excludes_current_user():
    """Test that current user's person is excluded from results."""
    pass

def test_calculate_name_match_score_exact():
    """Test name matching with exact match returns 100."""
    pass

def test_calculate_name_match_score_similar():
    """Test name matching with similar names returns appropriate score."""
    pass
```

### Frontend Component Tests

```typescript
describe('ConnectExistingPersonStep', () => {
  it('displays matching persons in a scrollable list', () => {})
  it('shows match score for each person', () => {})
  it('calls onConnect when Connect button is clicked', () => {})
  it('calls onNext when Next button is clicked', () => {})
  it('calls onBack when Back button is clicked', () => {})
})

describe('AddFamilyMemberDialog with matching', () => {
  it('shows matching step when matches are found', () => {})
  it('skips matching step when no matches are found', () => {})
  it('creates relationship when connecting to existing person', () => {})
  it('creates new person when proceeding from matching step', () => {})
})
```

### Integration Tests

1. **End-to-end wizard flow with matches**: Complete wizard, find matches, connect
2. **End-to-end wizard flow without matches**: Complete wizard, no matches, create new
3. **Search API with various criteria**: Test different combinations of search parameters
4. **Performance test**: Search with large dataset (1000+ persons)

## Performance Considerations

### Database Optimization

1. **Indexes**: Ensure indexes on:
   - `person_address.person_id`
   - `person_address.country_id, state_id, district_id`
   - `person_religion.person_id`
   - `person_religion.religion_id, religion_category_id`
   - `person.gender_id`

2. **Query Optimization**:
   - Use `IN` clauses for batch lookups
   - Limit results to top 10 matches
   - Use `EXISTS` for relationship exclusion

3. **Caching**:
   - Cache metadata (countries, states, religions) in frontend
   - Consider caching search results during wizard session

### Frontend Optimization

1. **Lazy Loading**: Load matching step component only when needed
2. **Debouncing**: If adding real-time search, debounce API calls
3. **Pagination**: If showing more than 10 results, implement pagination

## Security Considerations

1. **Authentication**: Require valid user session for search API
2. **Authorization**: Only return persons user has permission to see
3. **Data Privacy**: Don't expose sensitive person data in search results
4. **Rate Limiting**: Limit search API calls to prevent abuse
5. **Input Validation**: Sanitize all search inputs to prevent injection

## Dependencies

### Backend
- `rapidfuzz>=3.0.0` - Fast fuzzy string matching library
- Existing SQLModel, FastAPI, SQLAlchemy dependencies

### Frontend
- Existing React, TanStack Query, Radix UI dependencies
- No new dependencies required

## Migration Plan

1. **Phase 1**: Deploy backend changes (API endpoint, service, schemas)
2. **Phase 2**: Deploy frontend changes (new step component, updated dialog)
3. **Phase 3**: Monitor usage and match success rates
4. **Phase 4**: Tune fuzzy matching thresholds based on feedback

## Future Enhancements

1. **Machine Learning**: Use ML model for better match scoring
2. **Partial Matches**: Allow matching on subset of criteria
3. **Match Confidence**: Show confidence levels (High, Medium, Low)
4. **User Feedback**: Allow users to report incorrect matches
5. **Batch Matching**: Find matches for multiple family members at once
