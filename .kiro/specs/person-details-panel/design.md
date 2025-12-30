# Design Document: Person Details Panel

## Overview

This design document describes the implementation of a sliding panel that displays comprehensive person details when users click a "View" button on person cards in the Family Tree view. The feature requires a new backend API endpoint to fetch complete person details with resolved names for gender, address locations, and religion.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Family Tree View                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  PersonCard                                                  ││
│  │  ┌─────────────┐                                            ││
│  │  │   Avatar    │                                            ││
│  │  │   Name      │                                            ││
│  │  │   Years     │                                            ││
│  │  │ [View] btn  │ ──────────────────────────────────────┐    ││
│  │  └─────────────┘                                       │    ││
│  └────────────────────────────────────────────────────────│────┘│
│                                                           │     │
│  ┌────────────────────────────────────────────────────────▼────┐│
│  │              PersonDetailsPanel (Sheet)                     ││
│  │  ┌─────────────────────────────────────────────────────────┐││
│  │  │  [X] Close                                              │││
│  │  │                                                         │││
│  │  │         ┌──────────┐                                    │││
│  │  │         │  Photo   │                                    │││
│  │  │         │ (circle) │                                    │││
│  │  │         └──────────┘                                    │││
│  │  │                                                         │││
│  │  │      Full Name (First Middle Last)                      │││
│  │  │           1990 - 2020 (or 1990 -)                       │││
│  │  │                                                         │││
│  │  │  Gender: Male                                           │││
│  │  │  Address: Locality, Sub-District, District, State, ...  │││
│  │  │  Religion: Hinduism, Vaishnavism, ISKCON                │││
│  │  └─────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Frontend Components

#### 1. PersonCard (Modified)

**Changes Required:**
- Add "View" button that opens the details panel
- Button click should stop propagation to prevent card navigation

```typescript
interface PersonCardProps {
  person: PersonDetails
  relationshipType?: string
  variant: PersonCardVariant
  onClick: (personId: string) => void
  onViewClick?: (personId: string) => void  // NEW: Handler for View button
  showPhoto?: boolean
  colorVariant?: 'parent' | 'sibling' | 'spouse' | 'child' | 'selected'
}
```

#### 2. PersonDetailsPanel (New Component)

**Purpose:** Sliding panel that displays comprehensive person information.

**Location:** `frontend/src/components/FamilyTree/PersonDetailsPanel.tsx`

```typescript
interface PersonDetailsPanelProps {
  personId: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
}
```

**Internal State:**
- Uses TanStack Query to fetch person complete details
- Manages loading and error states internally

#### 3. usePersonCompleteDetails (New Hook)

**Purpose:** Fetch complete person details from the API.

**Location:** `frontend/src/hooks/usePersonCompleteDetails.ts`

```typescript
interface PersonCompleteDetails {
  id: string
  first_name: string
  middle_name: string | null
  last_name: string
  date_of_birth: string  // ISO date
  date_of_death: string | null  // ISO date
  gender_name: string
  address: {
    locality_name: string | null
    sub_district_name: string | null
    district_name: string | null
    state_name: string | null
    country_name: string
    address_line: string | null
  } | null
  religion: {
    religion_name: string
    category_name: string | null
    sub_category_name: string | null
  } | null
}

function usePersonCompleteDetails(personId: string | null) {
  return {
    data: PersonCompleteDetails | undefined
    isLoading: boolean
    error: Error | null
    refetch: () => void
  }
}
```

### Backend API

#### New Endpoint: GET /api/v1/person/{person_id}/complete-details

**Purpose:** Returns complete person information with all related names resolved.

**Response Schema:**

```python
class PersonCompleteDetailsResponse(SQLModel):
    """Complete person details with resolved names."""
    
    id: uuid.UUID
    first_name: str
    middle_name: str | None
    last_name: str
    date_of_birth: date
    date_of_death: date | None
    gender_name: str
    address: PersonAddressDetails | None
    religion: PersonReligionDetails | None


class PersonAddressDetails(SQLModel):
    """Address details with resolved location names."""
    
    locality_name: str | None
    sub_district_name: str | None
    district_name: str | None
    state_name: str | None
    country_name: str
    address_line: str | None


class PersonReligionDetails(SQLModel):
    """Religion details with resolved names."""
    
    religion_name: str
    category_name: str | None
    sub_category_name: str | None
```

**Implementation Logic:**

```python
def get_person_complete_details(person_id: uuid.UUID) -> PersonCompleteDetailsResponse:
    # 1. Fetch person by ID
    person = person_repo.get_by_id(person_id)
    
    # 2. Fetch and resolve gender name
    gender = gender_repo.get_by_id(person.gender_id)
    gender_name = gender.name if gender else "Unknown"
    
    # 3. Fetch current address and resolve location names
    addresses = address_repo.get_by_person_id(person_id)
    current_address = next((a for a in addresses if a.is_current), None)
    address_details = None
    if current_address:
        address_details = resolve_address_names(current_address)
    
    # 4. Fetch religion and resolve names
    person_religion = religion_repo.get_by_person_id(person_id)
    religion_details = None
    if person_religion:
        religion_details = resolve_religion_names(person_religion)
    
    # 5. Return complete response
    return PersonCompleteDetailsResponse(...)
```

## Data Models

### Frontend Types

```typescript
// frontend/src/client/types.gen.ts (auto-generated)
interface PersonCompleteDetailsResponse {
  id: string
  first_name: string
  middle_name: string | null
  last_name: string
  date_of_birth: string
  date_of_death: string | null
  gender_name: string
  address: PersonAddressDetails | null
  religion: PersonReligionDetails | null
}

interface PersonAddressDetails {
  locality_name: string | null
  sub_district_name: string | null
  district_name: string | null
  state_name: string | null
  country_name: string
  address_line: string | null
}

interface PersonReligionDetails {
  religion_name: string
  category_name: string | null
  sub_category_name: string | null
}
```

### Backend Schemas

**Location:** `backend/app/schemas/person/person_complete_details.py`

```python
from datetime import date
import uuid
from sqlmodel import SQLModel


class PersonAddressDetails(SQLModel):
    """Address details with resolved location names."""
    
    locality_name: str | None = None
    sub_district_name: str | None = None
    district_name: str | None = None
    state_name: str | None = None
    country_name: str
    address_line: str | None = None


class PersonReligionDetails(SQLModel):
    """Religion details with resolved names."""
    
    religion_name: str
    category_name: str | None = None
    sub_category_name: str | None = None


class PersonCompleteDetailsResponse(SQLModel):
    """Complete person details with resolved names."""
    
    id: uuid.UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    date_of_birth: date
    date_of_death: date | None = None
    gender_name: str
    address: PersonAddressDetails | None = None
    religion: PersonReligionDetails | None = None
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: View Button Event Isolation

*For any* person card with a View button, clicking the View button SHALL NOT trigger the card's navigation click handler.

**Validates: Requirements 1.4**

### Property 2: Panel Open/Close State Consistency

*For any* PersonDetailsPanel, the panel's open state SHALL match the `open` prop value, and calling `onOpenChange(false)` SHALL close the panel.

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 3: API Response Completeness

*For any* valid person ID, the complete-details API SHALL return all core person fields (id, first_name, last_name, date_of_birth, gender_name) with non-null values.

**Validates: Requirements 4.1, 4.2**

### Property 4: Address Name Resolution

*For any* person with a current address, the API response SHALL include the country_name as a non-null string, and other location names SHALL be resolved from their respective IDs.

**Validates: Requirements 4.3, 4.5**

### Property 5: Religion Name Resolution

*For any* person with religion data, the API response SHALL include religion_name as a non-null string, with category and sub-category names resolved when present.

**Validates: Requirements 4.4, 4.6**

## Error Handling

### Frontend Error Handling

1. **API Fetch Errors:**
   - Display error message in panel with retry button
   - Log error to console for debugging
   - Allow user to close panel even during error state

2. **Missing Data:**
   - Display "Not available" or similar placeholder for missing fields
   - Gracefully handle null values in address and religion

### Backend Error Handling

1. **Person Not Found:**
   - Return 404 with message "Person not found"

2. **Database Errors:**
   - Log error and return 500 with generic message
   - Don't expose internal error details

3. **Missing Related Data:**
   - Return null for address/religion if not found
   - Continue processing even if some lookups fail

## Testing Strategy

### Unit Tests

1. **PersonCard View Button:**
   - Test button renders correctly
   - Test click handler is called with correct person ID
   - Test event propagation is stopped

2. **PersonDetailsPanel:**
   - Test renders loading state
   - Test renders error state with retry
   - Test renders all person details correctly
   - Test close button works
   - Test escape key closes panel

3. **usePersonCompleteDetails Hook:**
   - Test successful data fetch
   - Test error handling
   - Test loading state

4. **Backend API:**
   - Test successful response with all data
   - Test response with missing address
   - Test response with missing religion
   - Test 404 for invalid person ID

### Property-Based Tests

Property tests should verify:
- View button isolation (Property 1)
- Panel state consistency (Property 2)
- API response completeness (Property 3)
- Address resolution (Property 4)
- Religion resolution (Property 5)

### Integration Tests

1. **End-to-End Flow:**
   - Click View button on person card
   - Verify panel opens with correct data
   - Verify panel closes on X button click
   - Verify panel closes on escape key

## File Structure

```
frontend/src/
├── components/
│   └── FamilyTree/
│       ├── PersonCard.tsx (modified)
│       └── PersonDetailsPanel.tsx (new)
├── hooks/
│   └── usePersonCompleteDetails.ts (new)
└── client/
    └── types.gen.ts (auto-generated)

backend/app/
├── api/
│   └── routes/
│       └── person/
│           └── person.py (modified - add new endpoint)
├── schemas/
│   └── person/
│       └── person_complete_details.py (new)
└── services/
    └── person/
        └── person_service.py (modified - add new method)
```
