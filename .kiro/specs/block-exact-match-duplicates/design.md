# Design Document: Block Exact Match Duplicates

## Overview

This feature enhances the `ConnectExistingPersonStep` component to prevent users from creating duplicate person records when an exact match already exists. An exact match is defined as a person with:
- 100% name match score (perfect first name + last name match)
- Exact date of birth match

The implementation is primarily frontend-focused, as the backend already returns all necessary data (match_score, date_of_birth) in the search results.

## Architecture

### Current Flow
```
User enters data → Search API → Display results → User can "Connect" OR "Create New"
```

### New Flow
```
User enters data → Search API → Check for exact matches → 
    ├─ Exact match found → Block "Create New", show warning
    └─ No exact match → Allow "Connect" OR "Create New"
```

## Components and Interfaces

### Modified Component: ConnectExistingPersonStep

The `ConnectExistingPersonStep.tsx` component will be enhanced with exact match detection logic.

#### New Helper Function

```typescript
/**
 * Determines if a person match is an exact match.
 * An exact match requires:
 * - match_score === 100 (perfect name match)
 * - date_of_birth matches the search criteria exactly
 */
function isExactMatch(
  person: PersonMatchResult,
  searchDateOfBirth: string
): boolean {
  const isNameExactMatch = person.match_score === 100
  const isDateOfBirthMatch = person.date_of_birth === searchDateOfBirth
  return isNameExactMatch && isDateOfBirthMatch
}

/**
 * Finds all exact matches from the search results.
 */
function findExactMatches(
  persons: PersonMatchResult[],
  searchDateOfBirth: string
): PersonMatchResult[] {
  return persons.filter(person => isExactMatch(person, searchDateOfBirth))
}
```

#### New State Variables

```typescript
// Derived state from matchingPersons
const exactMatches = useMemo(() => 
  findExactMatches(matchingPersons, searchCriteria.dateOfBirth),
  [matchingPersons, searchCriteria.dateOfBirth]
)

const hasExactMatch = exactMatches.length > 0
const hasBlockingExactMatch = exactMatches.some(p => !p.is_already_connected)
const allExactMatchesConnected = hasExactMatch && exactMatches.every(p => p.is_already_connected)
```

### UI Changes

#### 1. Exact Match Warning Banner

When an exact match is detected, display a warning banner:

```tsx
{hasExactMatch && (
  <div className="bg-amber-50 border border-amber-200 rounded-md p-4">
    <div className="flex items-start gap-3">
      <AlertTriangle className="h-5 w-5 text-amber-600 mt-0.5" />
      <div>
        <p className="text-sm font-medium text-amber-800">
          Exact match found
        </p>
        <p className="text-sm text-amber-700 mt-1">
          {allExactMatchesConnected 
            ? "This person is already in your family. You cannot create a duplicate."
            : "A person with the same name and date of birth already exists. Please connect to the existing person instead of creating a duplicate."}
        </p>
      </div>
    </div>
  </div>
)}
```

#### 2. Exact Match Badge

Add a distinct badge for exact matches:

```tsx
{isExactMatch(person, searchCriteria.dateOfBirth) ? (
  <Badge variant="destructive" className="ml-2">
    Exact Match
  </Badge>
) : (
  <Badge variant="secondary" className="ml-2">
    {Math.round(person.match_score)}% match
  </Badge>
)}
```

#### 3. Disabled Create Button

Disable the "Create New" button when exact match exists:

```tsx
<Button
  type="button"
  onClick={onNext}
  disabled={isLoading || isFetching || hasBlockingExactMatch || allExactMatchesConnected}
>
  {hasExactMatch ? "Cannot Create (Exact Match Found)" : "Next: Create New"}
</Button>
```

#### 4. Sort Results with Exact Matches First

```typescript
const sortedPersons = useMemo(() => {
  return [...matchingPersons].sort((a, b) => {
    const aIsExact = isExactMatch(a, searchCriteria.dateOfBirth)
    const bIsExact = isExactMatch(b, searchCriteria.dateOfBirth)
    if (aIsExact && !bIsExact) return -1
    if (!aIsExact && bIsExact) return 1
    return b.match_score - a.match_score
  })
}, [matchingPersons, searchCriteria.dateOfBirth])
```

## Data Models

No changes to data models required. The existing `PersonMatchResult` already contains all necessary fields:

```typescript
interface PersonMatchResult {
  person_id: string
  first_name: string
  middle_name: string | null
  last_name: string
  date_of_birth: string  // Used for exact match comparison
  date_of_death: string | null
  address_display: string | null
  religion_display: string | null
  match_score: number    // Used for exact match comparison (100 = exact)
  name_match_score: number
  is_current_user: boolean
  is_already_connected: boolean
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Exact Match Detection Accuracy

*For any* person match result, the `isExactMatch` function SHALL return true if and only if match_score equals 100 AND date_of_birth matches the search criteria exactly.

**Validates: Requirements 1.1, 1.2**

### Property 2: All Exact Matches Identified

*For any* array of person match results, the `findExactMatches` function SHALL return all persons where match_score equals 100 AND date_of_birth matches the search criteria.

**Validates: Requirements 1.3**

### Property 3: Create Button Disabled for Blocking Exact Matches

*For any* search result containing at least one exact match that is not already connected, the "Create New" button SHALL be disabled.

**Validates: Requirements 2.1**

### Property 4: Create Button Enabled When No Exact Match

*For any* search result where no exact match exists (all results have score < 100 OR date_of_birth mismatch), the "Create New" button SHALL be enabled.

**Validates: Requirements 1.4, 2.4**

### Property 5: Exact Matches Sorted First

*For any* list of search results containing both exact and non-exact matches, all exact matches SHALL appear before all non-exact matches in the sorted list.

**Validates: Requirements 5.2**

### Property 6: Both Buttons Disabled for Already-Connected Exact Match

*For any* exact match that is already connected to the user, both the "Connect" button for that person AND the "Create New" button SHALL be disabled.

**Validates: Requirements 4.2**

### Property 7: Connect Button Enabled for Non-Connected Exact Match

*For any* exact match that is NOT already connected to the user, the "Connect" button for that person SHALL be enabled.

**Validates: Requirements 3.2**

## Error Handling

| Scenario | Handling |
|----------|----------|
| Search API fails | Show error message, allow retry or proceed to create |
| No matches found | Allow user to proceed with creation |
| Exact match found | Block creation, show warning, guide to connect |
| Exact match already connected | Block both connect and create, show info message |

## Testing Strategy

### Unit Tests

Unit tests verify specific examples and edge cases:

1. **isExactMatch function**
   - Test with score = 100 and matching DOB → returns true
   - Test with score = 100 and non-matching DOB → returns false
   - Test with score = 99 and matching DOB → returns false
   - Test with score = 0 and non-matching DOB → returns false

2. **findExactMatches function**
   - Test with empty array → returns empty array
   - Test with no exact matches → returns empty array
   - Test with one exact match → returns array with one item
   - Test with multiple exact matches → returns all exact matches

3. **UI State Tests**
   - Test warning banner renders when exact match exists
   - Test "Exact Match" badge renders for exact matches
   - Test "Create New" button text changes when exact match exists

### Property-Based Tests

Property-based tests validate universal properties across many generated inputs. Each test should run minimum 100 iterations.

**Testing Framework:** Vitest with fast-check

1. **Property 1: Exact Match Detection Accuracy**
   - Generate random PersonMatchResult with random scores (0-100) and random DOBs
   - Verify isExactMatch returns true iff score=100 AND DOB matches
   - **Feature: block-exact-match-duplicates, Property 1: Exact Match Detection Accuracy**

2. **Property 2: All Exact Matches Identified**
   - Generate arrays of random PersonMatchResults
   - Verify findExactMatches returns exactly those with score=100 AND matching DOB
   - **Feature: block-exact-match-duplicates, Property 2: All Exact Matches Identified**

3. **Property 3: Create Button Disabled for Blocking Exact Matches**
   - Generate scenarios with exact matches (not already connected)
   - Verify hasBlockingExactMatch is true
   - **Feature: block-exact-match-duplicates, Property 3: Create Button Disabled**

4. **Property 4: Create Button Enabled When No Exact Match**
   - Generate scenarios with no exact matches
   - Verify hasBlockingExactMatch is false
   - **Feature: block-exact-match-duplicates, Property 4: Create Button Enabled**

5. **Property 5: Exact Matches Sorted First**
   - Generate random arrays with mix of exact and non-exact matches
   - Verify after sorting, all exact matches have lower indices than non-exact matches
   - **Feature: block-exact-match-duplicates, Property 5: Exact Matches Sorted First**

6. **Property 6: Both Buttons Disabled for Already-Connected Exact Match**
   - Generate exact matches with is_already_connected = true
   - Verify allExactMatchesConnected is true when all exact matches are connected
   - **Feature: block-exact-match-duplicates, Property 6: Both Buttons Disabled**

7. **Property 7: Connect Button Enabled for Non-Connected Exact Match**
   - Generate exact matches with is_already_connected = false
   - Verify Connect button should be enabled for these
   - **Feature: block-exact-match-duplicates, Property 7: Connect Button Enabled**

### Integration Tests

1. Test full flow with exact match → verify creation blocked
2. Test full flow without exact match → verify creation allowed
3. Test exact match that is already connected → verify both actions blocked
4. Test connecting to an exact match → verify relationship created successfully
