# Design Document: Assume Person Role

## Overview

This feature enables elevated users (SuperUser/Admin) to "assume" the role of any Person record they have created, allowing them to add direct relatives on behalf of that person. This solves the limitation where users can only add their own direct relatives, enabling the construction of multi-generational family trees.

**Dependency:** This feature builds on the **Person Context API Refactor** spec, which provides:
- APIs that accept explicit `person_id` parameters
- The `ActivePersonContext` in the frontend
- The `validate_person_access()` permission utility

This feature extends the `ActivePersonContext` to support assuming different persons and adds the UI controls for switching context.

## Architecture

```mermaid
flowchart TD
    subgraph Frontend
        A[User Login] --> B[Load Primary Person]
        B --> C{Is Elevated User?}
        C -->|No| D[Normal Family Tree View]
        C -->|Yes| E[Family Tree with Assume Controls]
        E --> F[Click Assume Role on Person Card]
        F --> G[Validate Permission via API]
        G -->|Success| H[Store Assumed Person in sessionStorage]
        H --> I[Update Active Person Context]
        I --> J[Re-render Tree Centered on Assumed Person]
        J --> K[Add Family Member Dialog]
        K --> L[Create Relative with Active Person Context]
    end
    
    subgraph Backend
        G --> M[GET /api/v1/persons/{person_id}/can-assume]
        L --> N[POST /api/v1/persons/{person_id}/relationships]
        N --> O[Validate created_by_user_id]
    end
    
    subgraph Session Storage
        H --> P[assumedPersonId]
        H --> Q[assumedPersonName]
    end
```

## Components and Interfaces

### Backend Components

#### 1. Permission Validation Endpoint

New endpoint to validate if a user can assume a specific person's role.

```python
# app/api/routes/person/person.py

@router.get("/{person_id}/can-assume", response_model=CanAssumeResponse)
def can_assume_person(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
) -> Any:
    """
    Check if current user can assume the role of a specific person.
    
    Requirements:
    - User must have SUPERUSER or ADMIN role
    - Person must have been created by this user (created_by_user_id matches)
    
    Returns:
        CanAssumeResponse with can_assume boolean and reason if denied
    """
    pass
```

#### 2. Relationship Creation with Context

Modify the relationship creation endpoint to accept an optional `acting_as_person_id` parameter.

```python
# app/api/routes/person/person.py

@router.post("/{person_id}/relationships", response_model=PersonRelationshipPublic)
def create_person_relationship(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    relationship_in: PersonRelationshipCreate,
) -> Any:
    """
    Create relationship for a specific person (when assuming their role).
    
    Authorization:
    - User must have SUPERUSER or ADMIN role
    - User must have created the person (created_by_user_id matches)
    
    The relationship is created FROM person_id TO relationship_in.related_person_id
    """
    pass
```

#### 3. Schema Definitions

```python
# app/schemas/person/person_assume.py

class CanAssumeResponse(SQLModel):
    """Response for can-assume check."""
    can_assume: bool
    reason: str | None = None
    person_name: str | None = None

class AssumedPersonContext(SQLModel):
    """Context information for assumed person."""
    person_id: uuid.UUID
    first_name: str
    last_name: str
    created_by_user_id: uuid.UUID
```

### Frontend Components

#### 1. Assumed Person Context Hook

New hook to manage the assumed person state.

```typescript
// src/hooks/useAssumedPerson.ts

interface AssumedPersonState {
  personId: string | null
  personName: string | null
}

interface UseAssumedPersonReturn {
  assumedPerson: AssumedPersonState | null
  primaryPerson: PersonDetails | null
  activePerson: PersonDetails | null  // Either assumed or primary
  isAssuming: boolean
  canAssume: boolean  // Based on user role
  assumePerson: (personId: string, personName: string) => Promise<void>
  returnToPrimary: () => void
  clearAssumedPerson: () => void
}

export function useAssumedPerson(): UseAssumedPersonReturn {
  // Implementation uses sessionStorage for persistence within session
}
```

#### 2. Assume Role Button Component

Button displayed on Person cards for eligible persons.

```typescript
// src/components/FamilyTree/AssumeRoleButton.tsx

interface AssumeRoleButtonProps {
  personId: string
  personName: string
  createdByUserId: string
  onAssumeSuccess?: () => void
}

export function AssumeRoleButton({
  personId,
  personName,
  createdByUserId,
  onAssumeSuccess,
}: AssumeRoleButtonProps): JSX.Element | null {
  // Only render for elevated users viewing persons they created
}
```

#### 3. Active Person Indicator

UI component showing current context (primary vs assumed).

```typescript
// src/components/FamilyTree/ActivePersonIndicator.tsx

interface ActivePersonIndicatorProps {
  primaryPerson: PersonDetails
  assumedPerson: AssumedPersonState | null
  onReturnToPrimary: () => void
}

export function ActivePersonIndicator({
  primaryPerson,
  assumedPerson,
  onReturnToPrimary,
}: ActivePersonIndicatorProps): JSX.Element {
  // Shows banner when in assumed role with return button
}
```

#### 4. Modified Family Tree View

Update the family tree view to use the active person context.

```typescript
// src/routes/_layout/family-tree.tsx

function FamilyTreeView() {
  const { user } = useAuth()
  const { 
    activePerson, 
    isAssuming, 
    canAssume,
    assumePerson,
    returnToPrimary 
  } = useAssumedPerson()
  
  // Use activePerson.id instead of myPerson.id for tree operations
  // Show assume controls only when canAssume is true
}
```

## Data Models

### Session Storage Schema

```typescript
// Stored in sessionStorage (cleared on tab close/logout)
interface AssumedPersonStorage {
  assumedPersonId: string      // UUID of assumed person
  assumedPersonName: string    // Display name for UI
  assumedAt: number           // Timestamp for debugging
}

// Key: "assumedPerson"
// Value: JSON.stringify(AssumedPersonStorage)
```

### API Response Models

```typescript
// GET /api/v1/persons/{person_id}/can-assume
interface CanAssumeResponse {
  can_assume: boolean
  reason?: string  // "not_elevated_user" | "not_creator" | "person_not_found"
  person_name?: string
}

// Extended PersonDetails to include created_by info
interface PersonDetailsExtended extends PersonDetails {
  created_by_user_id: string
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Role-Based Access Control

*For any* user with USER role (permission level 0), attempting to access assume person functionality SHALL result in a 403 Forbidden error, and the assume role UI controls SHALL NOT be visible.

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Creator-Only Assumption

*For any* Person record and any elevated user, the user can assume that Person's role if and only if `person.created_by_user_id === user.id`.

**Validates: Requirements 2.1, 2.4**

### Property 3: Session Scope Invariant

*For any* assumed person context, after logout and login, the Active_Person_Context SHALL equal the user's Primary_Person (assumed context is cleared).

**Validates: Requirements 3.1, 3.2**

### Property 4: Session Persistence on Refresh

*For any* assumed person context within an active session, after page refresh, the assumed person context SHALL be preserved and Active_Person_Context SHALL remain the Assumed_Person.

**Validates: Requirements 3.5**

### Property 5: Relationship Creation Context

*For any* relationship created while in assumed role, the relationship's `person_id` SHALL equal the Assumed_Person's ID, and the new Person's `created_by_user_id` SHALL equal the actual logged-in User's ID.

**Validates: Requirements 5.1, 5.3**

### Property 6: Return to Primary Idempotence

*For any* user, calling "Return to Primary" multiple times SHALL result in the same state as calling it once (Active_Person_Context equals Primary_Person).

**Validates: Requirements 4.2, 4.3**

### Property 7: Invalid Session Fallback

*For any* session containing an assumed Person ID that no longer exists (deleted), the system SHALL fall back to Primary_Person without error.

**Validates: Requirements 7.2, 7.3**

## Error Handling

### Backend Errors

| Error Condition | HTTP Status | Response |
|----------------|-------------|----------|
| User not elevated (USER role) | 403 Forbidden | `{"detail": "Insufficient permissions. SuperUser or Admin role required."}` |
| Person not found | 404 Not Found | `{"detail": "Person not found"}` |
| User didn't create person | 403 Forbidden | `{"detail": "Cannot assume role of person you did not create"}` |
| Invalid person_id format | 422 Unprocessable | `{"detail": "Invalid person ID format"}` |

### Frontend Error Handling

```typescript
// Error handling in useAssumedPerson hook
const assumePerson = async (personId: string, personName: string) => {
  try {
    // Validate with backend first
    const response = await PersonService.canAssumePerson({ personId })
    
    if (!response.can_assume) {
      showErrorToast(response.reason || "Cannot assume this person's role")
      return
    }
    
    // Store in sessionStorage
    sessionStorage.setItem("assumedPerson", JSON.stringify({
      assumedPersonId: personId,
      assumedPersonName: personName,
      assumedAt: Date.now()
    }))
    
    // Update state
    setAssumedPerson({ personId, personName })
    
  } catch (error) {
    // Handle network errors, invalid responses
    showErrorToast("Failed to assume person role. Please try again.")
    console.error("Assume person error:", error)
  }
}
```

### Session Recovery

```typescript
// On app initialization, validate stored assumed person
useEffect(() => {
  const stored = sessionStorage.getItem("assumedPerson")
  if (stored) {
    try {
      const { assumedPersonId } = JSON.parse(stored)
      // Validate the person still exists and user can still assume
      PersonService.canAssumePerson({ personId: assumedPersonId })
        .then(response => {
          if (!response.can_assume) {
            // Clear invalid session data
            sessionStorage.removeItem("assumedPerson")
            setAssumedPerson(null)
          }
        })
        .catch(() => {
          // On error, clear and fall back to primary
          sessionStorage.removeItem("assumedPerson")
          setAssumedPerson(null)
        })
    } catch {
      sessionStorage.removeItem("assumedPerson")
    }
  }
}, [])
```

## Testing Strategy

### Unit Tests

Unit tests verify specific examples and edge cases:

1. **Backend permission checks**
   - Test USER role gets 403
   - Test SUPERUSER can access
   - Test ADMIN can access
   - Test creator validation

2. **Frontend state management**
   - Test sessionStorage read/write
   - Test state updates on assume/return
   - Test logout clears state

3. **UI visibility**
   - Test assume button hidden for USER role
   - Test assume button shown for elevated users
   - Test button only on created persons

### Property-Based Tests

Property tests verify universal properties across all inputs using a property-based testing library (Hypothesis for Python, fast-check for TypeScript).

Each property test will:
- Run minimum 100 iterations
- Generate random valid inputs
- Verify the property holds for all generated cases

**Test Configuration:**
- Backend: pytest with hypothesis
- Frontend: vitest with fast-check
- Tag format: `Feature: assume-person-role, Property N: {property_text}`

### Integration Tests

1. **End-to-end assume flow**
   - Login as SuperUser
   - Navigate to family tree
   - Click assume on created person
   - Verify context switch
   - Add family member
   - Verify relationship created correctly

2. **Session persistence**
   - Assume a person
   - Refresh page
   - Verify still assuming same person

3. **Logout clears context**
   - Assume a person
   - Logout
   - Login again
   - Verify back to primary person
