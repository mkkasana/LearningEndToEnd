# Design Document: Rishte Person Search Wizard

## Overview

This design document describes the implementation of a user-friendly multi-step wizard for selecting persons in the Rishte (Relationship Visualizer) feature. The wizard replaces the current UUID-based input with a search-based approach that allows users to find persons using familiar criteria like name, address, and religion.

The implementation follows a self-contained architecture where all components reside within the `src/components/Rishte/` folder to maintain separation of concerns and avoid coupling with existing Family or Search components.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Rishte Page                                  │
│  ┌─────────────────┐              ┌─────────────────┐               │
│  │  Person A Card  │              │  Person B Card  │               │
│  │  [Select/Clear] │              │  [Select/Clear] │               │
│  └────────┬────────┘              └────────┬────────┘               │
│           │                                │                         │
│           └──────────┬─────────────────────┘                         │
│                      │                                               │
│           ┌──────────▼──────────┐                                   │
│           │ Find Relationship   │ (enabled when both selected)      │
│           └─────────────────────┘                                   │
└─────────────────────────────────────────────────────────────────────┘
                      │
                      ▼ (on button click)
┌─────────────────────────────────────────────────────────────────────┐
│              RishtePersonSearchDialog (Modal)                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ Progress: [●][○][○][○]  Step 1 of 4                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Step 1: RishteBasicInfoStep                                        │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │ First Name*: [___________]                                     │  │
│  │ Last Name:   [___________]                                     │  │
│  │ Gender:      [Dropdown   ▼]                                    │  │
│  │ Birth Year:  [From] - [To]                                     │  │
│  │                                          [Next →]              │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
│  Step 2: RishteAddressStep (defaults from active person)            │
│  Step 3: RishteReligionStep (defaults from active person)           │
│  Step 4: RishteResultsStep (search results with Select buttons)     │
└─────────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Component Hierarchy

```
src/components/Rishte/
├── index.ts                      # Barrel exports
├── types.ts                      # TypeScript interfaces (updated)
├── RishtePersonSearchDialog.tsx  # Main wizard dialog
├── RishteBasicInfoStep.tsx       # Step 1: Name, gender, birth year
├── RishteAddressStep.tsx         # Step 2: Address filters
├── RishteReligionStep.tsx        # Step 3: Religion filters
├── RishteResultsStep.tsx         # Step 4: Search results
├── RishtePersonButton.tsx        # Person A/B selection button
├── RishtePersonCard.tsx          # Selected person display card
├── PersonSelector.tsx            # (existing - to be replaced)
├── RishteGraph.tsx               # (existing)
├── PersonNode.tsx                # (existing)
├── RelationshipEdge.tsx          # (existing)
├── GraphControls.tsx             # (existing)
├── PathSummary.tsx               # (existing)
└── utils/
    ├── pathTransformer.ts        # (existing)
    └── layoutCalculator.ts       # (existing)
```

### TypeScript Interfaces

```typescript
// New types to add to types.ts

/**
 * Selected person data for display
 */
export interface SelectedPerson {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
}

/**
 * Basic info step form data
 */
export interface BasicInfoFormData {
  firstName: string        // Required
  lastName: string         // Required
  genderId?: string        // Optional
  birthYearFrom?: number   // Optional
  birthYearTo?: number     // Optional
}

/**
 * Address step form data
 */
export interface AddressFormData {
  countryId: string        // Required
  stateId: string          // Required
  districtId: string       // Required
  subDistrictId?: string   // Optional
  localityId?: string      // Optional
}

/**
 * Religion step form data
 */
export interface ReligionFormData {
  religionId: string           // Required
  religionCategoryId: string   // Required
  religionSubCategoryId?: string // Optional
}

/**
 * Combined search criteria from all steps
 */
export interface PersonSearchCriteria {
  basicInfo: BasicInfoFormData
  address: AddressFormData
  religion: ReligionFormData
}

/**
 * Wizard step enum
 */
export enum WizardStep {
  BASIC_INFO = 0,
  ADDRESS = 1,
  RELIGION = 2,
  RESULTS = 3,
}

/**
 * Props for RishtePersonSearchDialog
 */
export interface RishtePersonSearchDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  personLabel: "A" | "B"
  onPersonSelect: (person: SelectedPerson) => void
}

/**
 * Props for RishtePersonButton
 */
export interface RishtePersonButtonProps {
  label: "A" | "B"
  selectedPerson: SelectedPerson | null
  onSelect: () => void
  onClear: () => void
}
```

### Component Specifications

#### RishtePersonButton

Displays either a "Select Person X" button or a card showing the selected person.

```typescript
interface RishtePersonButtonProps {
  label: "A" | "B"
  selectedPerson: SelectedPerson | null
  onSelect: () => void
  onClear: () => void
}
```

**States:**
- Unselected: Shows button with UserPlus icon and "Select Person A/B" text
- Selected: Shows card with person name, birth year, and X button to clear

#### RishtePersonSearchDialog

Main wizard dialog managing the 4-step flow.

**State Management:**
- `currentStep: WizardStep` - Current wizard step
- `basicInfoData: BasicInfoFormData | null` - Step 1 data
- `addressData: AddressFormData | null` - Step 2 data
- `religionData: ReligionFormData | null` - Step 3 data

**Behavior:**
- Opens at Step 1 (BASIC_INFO)
- Fetches active person's address and religion on mount
- Passes defaults to Address and Religion steps
- Closes and calls `onPersonSelect` when user selects a person

#### RishteBasicInfoStep

Form for collecting basic search criteria.

**Fields:**
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| firstName | Input | Yes | min 1 char |
| lastName | Input | Yes |  min 1 char |
| genderId | Select | No | From genders API |
| birthYearFrom | Number | No | Valid year |
| birthYearTo | Number | No | >= birthYearFrom |

#### RishteAddressStep

Cascading dropdowns for address filtering.

**Fields:**
| Field | Type | Required | Cascade From |
|-------|------|----------|--------------|
| countryId | Select | Yes | - |
| stateId | Select | Yes | countryId |
| districtId | Select | Yes | stateId |
| subDistrictId | Select | No | districtId |
| localityId | Select | No | subDistrictId |

**Default Values:** Pre-populated from active person's current address.

#### RishteReligionStep

Cascading dropdowns for religion filtering.

**Fields:**
| Field | Type | Required | Cascade From |
|-------|------|----------|--------------|
| religionId | Select | Yes | - |
| religionCategoryId | Select | Yes | religionId |
| religionSubCategoryId | Select | No | religionCategoryId |

**Default Values:** Pre-populated from active person's religion.

#### RishteResultsStep

Displays search results with selection capability.

**API Call:**
Uses existing `PersonService.searchPersons()` with criteria from all steps.

**Display:**
- Loading spinner during search
- Grid of person cards with Select button
- Empty state message if no results
- Pagination for > 20 results

## Data Models

### Search Request Mapping

The wizard collects data across 3 steps and maps to the existing `PersonSearchFilterRequest`:

```typescript
function buildSearchRequest(criteria: PersonSearchCriteria): PersonSearchFilterRequest {
  return {
    first_name: criteria.basicInfo.firstName,
    last_name: criteria.basicInfo.lastName,
    gender_id: criteria.basicInfo.genderId || undefined,
    birth_year_from: criteria.basicInfo.birthYearFrom || undefined,
    birth_year_to: criteria.basicInfo.birthYearTo || undefined,
    country_id: criteria.address.countryId,
    state_id: criteria.address.stateId,
    district_id: criteria.address.districtId,
    sub_district_id: criteria.address.subDistrictId || undefined,
    locality_id: criteria.address.localityId || undefined,
    religion_id: criteria.religion.religionId,
    religion_category_id: criteria.religion.religionCategoryId,
    religion_sub_category_id: criteria.religion.religionSubCategoryId || undefined,
    skip: 0,
    limit: 20,
  }
}
```

### State Flow

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Basic Info  │────▶│   Address    │────▶│   Religion   │────▶│   Results    │
│   (Step 1)   │     │   (Step 2)   │     │   (Step 3)   │     │   (Step 4)   │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
  basicInfoData        addressData          religionData        API Search
       │                    │                    │                    │
       └────────────────────┴────────────────────┴────────────────────┘
                                    │
                                    ▼
                          PersonSearchFilterRequest
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Find Button Enabled State

*For any* combination of Person A and Person B selection states, the "Find Relationship" button SHALL be enabled if and only if both persons are selected (non-null).

**Validates: Requirements 7.1, 7.2, 7.3**

### Property 2: Selected Person Display

*For any* selected person with a valid personId, firstName, and lastName, the Person_Button SHALL display the person's full name (firstName + lastName).

**Validates: Requirements 2.3**

### Property 3: Name Field Validation

*For any* first name or last name string that is empty or contains only whitespace characters, the Basic_Info_Step validation SHALL reject it and prevent proceeding to the next step.

**Validates: Requirements 3.2, 3.3, 3.7**

### Property 4: Address Default Population

*For any* active person with a current address, when the Address_Step is rendered, all address fields SHALL be pre-populated with the active person's address values.

**Validates: Requirements 4.2, 9.3**

### Property 5: Religion Default Population

*For any* active person with a religion, when the Religion_Step is rendered, all religion fields SHALL be pre-populated with the active person's religion values.

**Validates: Requirements 5.2, 9.4**

### Property 6: Cascading Dropdown Reset

*For any* parent dropdown (country, state, district, religion, category) value change, all child dropdowns SHALL be reset to empty/default state.

**Validates: Requirements 4.6, 5.5**

### Property 7: Wizard Progress Indicator

*For any* wizard step (0-3), the progress indicator SHALL display the correct step number (step + 1) out of 4.

**Validates: Requirements 8.2**

### Property 8: Person Result Card Content

*For any* person search result, the result card SHALL display the person's full name, birth year (if available), address summary, and religion summary.

**Validates: Requirements 6.4**

## Error Handling

| Scenario | Handling |
|----------|----------|
| Active person has no address | Address step starts with empty fields |
| Active person has no religion | Religion step starts with empty fields |
| Search returns no results | Display "No persons found" message |
| Search API error | Display error message with retry option |
| Network timeout | Display timeout message |
| Invalid form data | Show inline validation errors |

## Testing Strategy

### Unit Tests

Unit tests verify specific examples and edge cases:

- Form validation for required fields
- Cascading dropdown behavior
- Button state management
- Empty state rendering
- Error state rendering

### Property-Based Tests

Property-based tests verify universal properties across all inputs using a property-based testing library (e.g., fast-check for TypeScript):

- **Property 1**: Find button state matches selection state
- **Property 3**: First name validation rejects empty/whitespace strings
- **Property 6**: Cascading dropdowns reset on parent change
- **Property 7**: Progress indicator shows correct step

Each property test should run minimum 100 iterations to ensure comprehensive coverage.

**Test Annotation Format:**
```typescript
// Feature: rishte-person-search-wizard, Property 1: Find Button Enabled State
// Validates: Requirements 7.1, 7.2, 7.3
```

