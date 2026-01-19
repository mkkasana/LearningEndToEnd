# Design Document: Find Partner UI

## Overview

This document describes the frontend implementation for the "Find Partner" feature. The feature provides a dedicated page accessible from the menu bar where users can search for potential marriage matches using a filter panel with smart defaults. The implementation reuses the existing `partner-match/find` backend API and displays results as raw JSON initially.

The design follows existing patterns from the Search page (`search.tsx`) and `SearchFilterPanel` component, adapting them for the partner match use case with multi-select tag inputs instead of single-select dropdowns for religion filters.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Find Partner Page                        │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                      Header + Filter Button                  ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │                    Main Content Area                         ││
│  │                                                              ││
│  │    - Empty state (before search)                            ││
│  │    - Loading state (during search)                          ││
│  │    - Results JSON (after search)                            ││
│  │    - Error state (on failure)                               ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              Partner Filter Panel (Sheet - slides from left)     │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Gender: [Dropdown - Male/Female]                           ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  Birth Year: [From] - [To]                                  ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  Include Religions: [Tag1 ×] [Tag2 ×] [+ dropdown]          ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  Include Categories: [Tag1 ×] [+ dropdown]                  ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  Include Sub-Categories: [+ dropdown]                       ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  Exclude Sub-Categories: [Tag1 ×] [Tag2 ×] [+ dropdown]     ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  Search Depth: [Dropdown 1-50, default 10]                  ││
│  ├─────────────────────────────────────────────────────────────┤│
│  │  [Reset Filters]              [Find Matches]                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### File Structure

```
frontend/src/
├── routes/_layout/
│   └── find-partner.tsx          # Main page route
└── components/FindPartner/
    ├── index.ts                   # Barrel export
    ├── types.ts                   # TypeScript interfaces
    ├── PartnerFilterPanel.tsx     # Filter panel component
    ├── TagInput.tsx               # Reusable multi-select tag input
    ├── PartnerResultsDisplay.tsx  # JSON results display
    └── utils/
        ├── defaultsCalculator.ts  # Smart defaults logic
        └── defaultsCalculator.test.ts
```

### TypeScript Interfaces

```typescript
// types.ts

/**
 * Selected tag item for multi-select inputs
 */
export interface TagItem {
  id: string
  name: string
}

/**
 * Partner filter state
 */
export interface PartnerFilters {
  genderId: string                    // Single select
  birthYearFrom: number | undefined   // Number input
  birthYearTo: number | undefined     // Number input
  includeReligions: TagItem[]         // Multi-select tags
  includeCategories: TagItem[]        // Multi-select tags
  includeSubCategories: TagItem[]     // Multi-select tags
  excludeSubCategories: TagItem[]     // Multi-select tags
  searchDepth: number                 // Dropdown 1-50
}

/**
 * Props for PartnerFilterPanel
 */
export interface PartnerFilterPanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  filters: PartnerFilters
  defaultFilters: PartnerFilters
  onApply: (filters: PartnerFilters) => void
  onReset: () => void
}

/**
 * Props for TagInput component
 */
export interface TagInputProps {
  label: string
  selectedItems: TagItem[]
  availableItems: TagItem[]
  onAdd: (item: TagItem) => void
  onRemove: (itemId: string) => void
  placeholder?: string
  disabled?: boolean
}

/**
 * Active person data needed for defaults
 */
export interface ActivePersonDefaults {
  genderId: string | null
  birthYear: number | null
  religionId: string | null
  religionName: string | null
  categoryId: string | null
  categoryName: string | null
  subCategoryId: string | null
  subCategoryName: string | null
}

/**
 * Lineage sub-categories for exclusion defaults
 */
export interface LineageSubCategories {
  selfSubCategory: TagItem | null
  motherSubCategory: TagItem | null
  grandmotherSubCategory: TagItem | null
}
```

### Component: TagInput

A reusable multi-select tag input component that displays selected items as removable tags and provides a dropdown to add more items.

```typescript
// TagInput.tsx (pseudocode)

function TagInput({
  label,
  selectedItems,
  availableItems,
  onAdd,
  onRemove,
  placeholder,
  disabled
}: TagInputProps) {
  // Filter available items to exclude already selected
  const unselectedItems = availableItems.filter(
    item => !selectedItems.some(selected => selected.id === item.id)
  )

  return (
    <div>
      <Label>{label}</Label>
      <div className="flex flex-wrap gap-2 p-2 border rounded">
        {/* Selected tags */}
        {selectedItems.map(item => (
          <Badge key={item.id} variant="secondary">
            {item.name}
            <button onClick={() => onRemove(item.id)}>×</button>
          </Badge>
        ))}
        
        {/* Add dropdown */}
        {unselectedItems.length > 0 && (
          <Select onValueChange={(id) => {
            const item = availableItems.find(i => i.id === id)
            if (item) onAdd(item)
          }}>
            <SelectTrigger className="w-auto">
              <Plus className="h-4 w-4" />
            </SelectTrigger>
            <SelectContent>
              {unselectedItems.map(item => (
                <SelectItem key={item.id} value={item.id}>
                  {item.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>
    </div>
  )
}
```

### Component: PartnerFilterPanel

The main filter panel component using the Sheet component pattern from the existing SearchFilterPanel.

```typescript
// PartnerFilterPanel.tsx (pseudocode structure)

function PartnerFilterPanel({
  open,
  onOpenChange,
  filters,
  defaultFilters,
  onApply,
  onReset
}: PartnerFilterPanelProps) {
  const [localFilters, setLocalFilters] = useState(filters)
  
  // Fetch metadata
  const { data: genders } = useQuery(['genders'], getGenders)
  const { data: religions } = useQuery(['religions'], getReligions)
  
  // Cascading: categories for selected religions
  const selectedReligionIds = localFilters.includeReligions.map(r => r.id)
  const { data: categories } = useQuery(
    ['categories', selectedReligionIds],
    () => getCategoriesForReligions(selectedReligionIds),
    { enabled: selectedReligionIds.length > 0 }
  )
  
  // Cascading: sub-categories for selected categories
  const selectedCategoryIds = localFilters.includeCategories.map(c => c.id)
  const { data: subCategories } = useQuery(
    ['subCategories', selectedCategoryIds],
    () => getSubCategoriesForCategories(selectedCategoryIds),
    { enabled: selectedCategoryIds.length > 0 }
  )
  
  // Handle cascading removal when religion is removed
  const handleRemoveReligion = (religionId: string) => {
    // Remove religion
    const newReligions = localFilters.includeReligions.filter(r => r.id !== religionId)
    
    // Remove orphaned categories (those belonging to removed religion)
    const validCategoryIds = categories
      ?.filter(c => newReligions.some(r => r.id === c.religionId))
      .map(c => c.id) || []
    const newCategories = localFilters.includeCategories.filter(
      c => validCategoryIds.includes(c.id)
    )
    
    // Remove orphaned sub-categories
    const validSubCategoryIds = subCategories
      ?.filter(sc => newCategories.some(c => c.id === sc.categoryId))
      .map(sc => sc.id) || []
    const newIncludeSubCategories = localFilters.includeSubCategories.filter(
      sc => validSubCategoryIds.includes(sc.id)
    )
    const newExcludeSubCategories = localFilters.excludeSubCategories.filter(
      sc => validSubCategoryIds.includes(sc.id)
    )
    
    setLocalFilters({
      ...localFilters,
      includeReligions: newReligions,
      includeCategories: newCategories,
      includeSubCategories: newIncludeSubCategories,
      excludeSubCategories: newExcludeSubCategories
    })
  }
  
  // Similar cascading logic for category removal...
  
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left">
        {/* Gender dropdown */}
        {/* Birth year inputs */}
        {/* Include Religions TagInput */}
        {/* Include Categories TagInput */}
        {/* Include Sub-Categories TagInput */}
        {/* Exclude Sub-Categories TagInput */}
        {/* Search Depth dropdown */}
        {/* Reset and Find Matches buttons */}
      </SheetContent>
    </Sheet>
  )
}
```

### Utility: defaultsCalculator

Pure functions for calculating smart defaults.

```typescript
// utils/defaultsCalculator.ts

/**
 * Calculate opposite gender ID
 * @param genderId - Active person's gender ID
 * @param genders - List of available genders
 * @returns Opposite gender ID or empty string if unknown
 */
export function calculateOppositeGender(
  genderId: string | null,
  genders: Array<{ genderId: string; genderCode: string }>
): string {
  if (!genderId || !genders.length) return ''
  
  const currentGender = genders.find(g => g.genderId === genderId)
  if (!currentGender) return ''
  
  const oppositeCode = currentGender.genderCode === 'MALE' ? 'FEMALE' : 'MALE'
  const oppositeGender = genders.find(g => g.genderCode === oppositeCode)
  
  return oppositeGender?.genderId || ''
}

/**
 * Calculate birth year range defaults
 * @param birthYear - Active person's birth year
 * @returns Object with fromYear and toYear, or undefined values if unknown
 */
export function calculateBirthYearRange(
  birthYear: number | null
): { fromYear: number | undefined; toYear: number | undefined } {
  if (!birthYear) {
    return { fromYear: undefined, toYear: undefined }
  }
  
  return {
    fromYear: birthYear - 2,
    toYear: birthYear + 5
  }
}

/**
 * Validate birth year range
 * @returns Error message or null if valid
 */
export function validateBirthYearRange(
  fromYear: number | undefined,
  toYear: number | undefined
): string | null {
  if (fromYear !== undefined && toYear !== undefined && fromYear > toYear) {
    return 'From year must be less than or equal to To year'
  }
  return null
}

/**
 * Build default filters from active person data and lineage
 */
export function buildDefaultFilters(
  activePersonDefaults: ActivePersonDefaults,
  lineageSubCategories: LineageSubCategories,
  genders: Array<{ genderId: string; genderCode: string }>
): PartnerFilters {
  const { fromYear, toYear } = calculateBirthYearRange(activePersonDefaults.birthYear)
  
  // Build include religions default
  const includeReligions: TagItem[] = []
  if (activePersonDefaults.religionId && activePersonDefaults.religionName) {
    includeReligions.push({
      id: activePersonDefaults.religionId,
      name: activePersonDefaults.religionName
    })
  }
  
  // Build include categories default
  const includeCategories: TagItem[] = []
  if (activePersonDefaults.categoryId && activePersonDefaults.categoryName) {
    includeCategories.push({
      id: activePersonDefaults.categoryId,
      name: activePersonDefaults.categoryName
    })
  }
  
  // Build exclude sub-categories from lineage (graceful if missing)
  const excludeSubCategories: TagItem[] = []
  if (lineageSubCategories.selfSubCategory) {
    excludeSubCategories.push(lineageSubCategories.selfSubCategory)
  }
  if (lineageSubCategories.motherSubCategory) {
    // Avoid duplicates
    if (!excludeSubCategories.some(sc => sc.id === lineageSubCategories.motherSubCategory!.id)) {
      excludeSubCategories.push(lineageSubCategories.motherSubCategory)
    }
  }
  if (lineageSubCategories.grandmotherSubCategory) {
    if (!excludeSubCategories.some(sc => sc.id === lineageSubCategories.grandmotherSubCategory!.id)) {
      excludeSubCategories.push(lineageSubCategories.grandmotherSubCategory)
    }
  }
  
  return {
    genderId: calculateOppositeGender(activePersonDefaults.genderId, genders),
    birthYearFrom: fromYear,
    birthYearTo: toYear,
    includeReligions,
    includeCategories,
    includeSubCategories: [], // Always starts empty
    excludeSubCategories,
    searchDepth: 10 // Default depth
  }
}
```

## Data Models

### API Request Mapping

The frontend filters map to the existing `PartnerMatchRequest` backend schema:

| Frontend Filter | Backend Field | Transformation |
|-----------------|---------------|----------------|
| `genderId` | `target_gender_code` | Lookup gender code from ID |
| `birthYearFrom` | `birth_year_min` | Direct mapping |
| `birthYearTo` | `birth_year_max` | Direct mapping |
| `includeReligions` | `include_religion_ids` | Extract IDs from TagItem[] |
| `includeCategories` | `include_category_ids` | Extract IDs from TagItem[] |
| `includeSubCategories` | `include_sub_category_ids` | Extract IDs from TagItem[] |
| `excludeSubCategories` | `exclude_sub_category_ids` | Extract IDs from TagItem[] |
| `searchDepth` | `max_depth` | Direct mapping |
| (from context) | `seeker_person_id` | Active person ID |

```typescript
function filtersToRequest(
  filters: PartnerFilters,
  activePersonId: string,
  genders: Array<{ genderId: string; genderCode: string }>
): PartnerMatchRequest {
  const gender = genders.find(g => g.genderId === filters.genderId)
  
  return {
    seeker_person_id: activePersonId,
    target_gender_code: gender?.genderCode || 'FEMALE',
    birth_year_min: filters.birthYearFrom,
    birth_year_max: filters.birthYearTo,
    include_religion_ids: filters.includeReligions.map(r => r.id),
    include_category_ids: filters.includeCategories.map(c => c.id),
    include_sub_category_ids: filters.includeSubCategories.length > 0 
      ? filters.includeSubCategories.map(sc => sc.id) 
      : undefined,
    exclude_sub_category_ids: filters.excludeSubCategories.map(sc => sc.id),
    max_depth: filters.searchDepth,
    prune_graph: true
  }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Gender defaults to opposite of active person

*For any* active person with a known gender, the gender filter should default to the opposite gender (Male → Female, Female → Male).

**Validates: Requirements 3.2, 3.3**

### Property 2: Birth year range defaults correctly

*For any* active person with a known birth year Y, the birth year filter should default to (Y - 2) for "From" and (Y + 5) for "To".

**Validates: Requirements 4.2, 4.3**

### Property 3: Birth year validation rejects invalid ranges

*For any* birth year range where "From" > "To", the validation should return an error message.

**Validates: Requirements 4.5**

### Property 4: Tag add/remove operations maintain correct count

*For any* tag input with N selected items, adding an item should result in N+1 items, and removing an item should result in N-1 items.

**Validates: Requirements 5.4, 5.6**

### Property 5: Cascading dropdown options are filtered by parent selections

*For any* set of selected religions R, the categories dropdown should only contain categories belonging to religions in R. Similarly, for any set of selected categories C, the sub-categories dropdown should only contain sub-categories belonging to categories in C.

**Validates: Requirements 6.3, 7.3, 8.5**

### Property 6: Cascading removal removes orphaned children

*For any* religion removed from the include list, all categories belonging to that religion should be removed from the categories list. Similarly, removing a category should remove all its sub-categories from both include and exclude lists.

**Validates: Requirements 6.4, 7.4, 8.6**

### Property 7: Reset restores all filters to defaults

*For any* modified filter state, clicking "Reset Filters" should restore all filter values to match the initial default values.

**Validates: Requirements 10.2**

### Property 8: API call includes all current filter values

*For any* filter state when "Find Matches" is clicked, the API request should contain all filter values correctly mapped to the backend schema.

**Validates: Requirements 9.3, 10.4**

## Error Handling

| Error Scenario | Handling Strategy |
|----------------|-------------------|
| Active person has no gender | Gender filter defaults to empty, user must select |
| Active person has no birth year | Birth year fields default to empty |
| Active person has no religion | Include religions starts empty |
| Mother not found in relationships | Skip mother's sub-category, continue with others |
| Grandmother not found | Skip grandmother's sub-category, continue with others |
| Religion metadata API fails | Show error toast, disable religion filters |
| Partner match API fails | Show error message in results area |
| Birth year validation fails | Show inline error, disable Find Matches button |

## Testing Strategy

### Unit Tests

Unit tests should cover:
- `calculateOppositeGender` function with various inputs
- `calculateBirthYearRange` function with various birth years
- `validateBirthYearRange` function with valid and invalid ranges
- `buildDefaultFilters` function with complete and partial data
- Tag add/remove logic in isolation

### Property-Based Tests

Property-based tests should use a library like `fast-check` to verify:
- Property 1: Gender opposite calculation (generate random genders)
- Property 2: Birth year range calculation (generate random years)
- Property 3: Birth year validation (generate random year pairs)
- Property 4: Tag operations (generate random tag lists and operations)
- Property 5: Cascading filter options (generate random religion/category hierarchies)
- Property 6: Cascading removal (generate random removal sequences)
- Property 7: Reset behavior (generate random filter modifications)
- Property 8: API mapping (generate random filter states)

Each property test should run minimum 100 iterations.

### Integration Tests

- Test filter panel opens and closes correctly
- Test default values are populated from active person context
- Test API call is made with correct parameters
- Test results are displayed as JSON
- Test error states are handled gracefully

