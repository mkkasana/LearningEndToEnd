# Design Document: Family Tree View

## Overview

The Family Tree View feature provides an interactive, visual representation of family relationships centered on a selected person. The design focuses on displaying immediate family (parents, spouse, siblings, and children) in a clear, navigable tree layout that allows users to explore their family structure by clicking on different family members.

This feature leverages the existing bidirectional relationship system and the `/api/v1/person/{person_id}/relationships/with-details` endpoint to fetch relationship data. The frontend will be built using React with TanStack Router for routing and TanStack Query for data fetching, following the established patterns in the codebase.

The design emphasizes progressive loading (fetching data on-demand as users navigate) and responsive design to ensure the tree works well across desktop, tablet, and mobile devices.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Family Tree View Route                                │ │
│  │  - Navigation integration                              │ │
│  │  - Route: /_layout/family-tree                        │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  FamilyTreeView Component                             │ │
│  │  - Main container                                      │ │
│  │  - State management (selected person)                 │ │
│  │  - Data fetching orchestration                        │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Tree Layout Components                                │ │
│  │  - PersonCard (center, parents, spouse, children)     │ │
│  │  - RelationshipLines (visual connectors)              │ │
│  │  - SiblingsList (horizontal scrollable)               │ │
│  │  - SpouseCarousel (multiple spouses)                  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Data Processing Layer                                 │ │
│  │  - Relationship categorization                         │ │
│  │  - Sibling calculation                                 │ │
│  │  - Data caching                                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Existing API Endpoint                                 │ │
│  │  GET /api/v1/person/{person_id}/relationships/        │ │
│  │      with-details                                      │ │
│  │  - Returns PersonRelationshipWithDetails[]            │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
FamilyTreeView
├── FamilyTreeHeader
│   └── SelectedPersonInfo
├── FamilyTreeCanvas (3-row layout)
│   ├── ParentsRow (horizontally scrollable)
│   │   ├── PersonCard (Parent 1)
│   │   ├── PersonCard (Parent 2)
│   │   ├── ... (any number of parents)
│   │   └── RelationshipLines
│   ├── CenterRow (horizontally scrollable)
│   │   ├── PersonCard (Sibling 1) [color-coded]
│   │   ├── PersonCard (Sibling 2) [color-coded]
│   │   ├── PersonCard (Selected Person - emphasized)
│   │   ├── PersonCard (Spouse 1) [color-coded]
│   │   ├── PersonCard (Spouse 2) [color-coded]
│   │   ├── ... (any number of siblings/spouses)
│   │   └── RelationshipLines
│   └── ChildrenRow (horizontally scrollable)
│       ├── PersonCard (Child 1)
│       ├── PersonCard (Child 2)
│       ├── ... (any number of children)
│       └── RelationshipLines
└── LoadingOverlay
```

## Components and Interfaces

### Frontend Components

#### 1. FamilyTreeView (Main Container)

**Purpose**: Main container component that manages the overall state and orchestrates data fetching.

**State**:
```typescript
interface FamilyTreeViewState {
  selectedPersonId: string | null
  isLoading: boolean
  error: Error | null
}
```

**Props**: None (uses route parameters and auth context)

**Responsibilities**:
- Initialize with current user's person profile
- Manage selected person state
- Fetch relationship data using TanStack Query
- Handle navigation between family members
- Provide loading and error states

#### 2. PersonCard

**Purpose**: Display information about a single person in the tree.

**Props**:
```typescript
interface PersonCardProps {
  person: PersonDetails
  relationshipType?: string
  variant: 'selected' | 'parent' | 'spouse' | 'sibling' | 'child'
  onClick: (personId: string) => void
  showPhoto?: boolean
}
```

**Variants**:
- `selected`: Larger, prominent styling with border/shadow
- `parent`: Medium size, positioned above
- `spouse`: Medium size, positioned horizontally adjacent
- `sibling`: Smaller, de-emphasized with reduced opacity
- `child`: Medium Size, positioned below

**Display**:
- Profile photo or gender-based avatar placeholder
- First name and last name
- Birth year (formatted as "YYYY")
- Death year if applicable (formatted as "YYYY - YYYY" or "YYYY -")
- Relationship label (for non-selected cards)

#### 3. RelationshipLines

**Purpose**: Visual connectors showing relationships between people.

**Props**:
```typescript
interface RelationshipLinesProps {
  type: 'parent-child' | 'spouse' | 'sibling'
  fromPosition: { x: number; y: number }
  toPosition: { x: number; y: number }
}
```

**Implementation**:
- Use SVG for drawing lines
- Different line styles for different relationship types:
  - Parent-child: Vertical lines with branches
  - Spouse: Horizontal line
  - Sibling: Shared parent connection

#### 4. SiblingsList

**Purpose**: Display siblings in a horizontally scrollable list.

**Props**:
```typescript
interface SiblingsListProps {
  siblings: PersonDetails[]
  onSiblingClick: (personId: string) => void
}
```

**Features**:
- Horizontal scroll container
- Smaller card size
- De-emphasized styling
- Scroll indicators if overflow

#### 5. SpouseCarousel

**Purpose**: Display multiple spouses in a carousel/slideshow format.

**Props**:
```typescript
interface SpouseCarouselProps {
  spouses: PersonDetails[]
  onSpouseClick: (personId: string) => void
}
```

**Features**:
- Horizontal navigation (prev/next buttons)
- Indicator dots showing current spouse
- Smooth transitions between spouses

#### 6. HorizontalScrollRow (New Component for Improved Layout)

**Purpose**: Unified component for displaying any row of people (parents, center row with siblings+spouses, or children) in a horizontally scrollable container without vertical stacking.

**Props**:
```typescript
interface HorizontalScrollRowProps {
  people: PersonDetails[]
  selectedPersonId?: string // For highlighting the selected person in center row
  onPersonClick: (personId: string) => void
  variant: 'parent' | 'center' | 'child'
  colorCoding?: Map<string, 'sibling' | 'spouse'> // For center row differentiation
}
```

**Features**:
- Horizontal scroll container with smooth scrolling
- Responsive card sizing based on viewport
- Scroll indicators showing more content available
- Color-coded cards in center row (siblings vs spouses)
- Selected person prominently displayed in center row
- Touch-friendly scrolling on mobile devices
- Works consistently across all screen sizes (desktop, tablet, mobile)

**Layout Behavior**:
- **Parents Row**: All parents displayed horizontally, scrollable if many
- **Center Row**: Siblings (left) + Selected Person (center) + Spouses (right), all in one scrollable row with color coding
- **Children Row**: All children displayed horizontally, scrollable if many
- **No vertical stacking**: Cards never stack vertically within a row, only horizontal scrolling
- **Mobile-friendly**: Maintains horizontal layout even on small screens

### Data Processing Functions

#### 1. categorizeRelationships

**Purpose**: Categorize relationships into parents, spouses, siblings, and children.

**Signature**:
```typescript
function categorizeRelationships(
  relationships: PersonRelationshipWithDetails[],
  selectedPersonGenderId: string
): CategorizedRelationships

interface CategorizedRelationships {
  parents: PersonDetails[]
  spouses: PersonDetails[]
  children: PersonDetails[]
  parentIds: string[] // Used for sibling calculation
}
```

**Logic**:
- Parents: relationship_type in ['rel-6a0ede824d101' (Father), 'rel-6a0ede824d102' (Mother)]
- Spouses: relationship_type in ['rel-6a0ede824d105' (Wife), 'rel-6a0ede824d106' (Husband), 'rel-6a0ede824d107' (Spouse)]
- Children: relationship_type in ['rel-6a0ede824d103' (Daughter), 'rel-6a0ede824d104' (Son)]

#### 2. calculateSiblings

**Purpose**: Calculate siblings by finding people who share the same parents.

**Signature**:
```typescript
function calculateSiblings(
  selectedPersonId: string,
  parentIds: string[],
  allRelationshipsCache: Map<string, PersonRelationshipWithDetails[]>
): PersonDetails[]
```

**Logic**:
1. For each parent ID, fetch their relationships (from cache or API)
2. Find all children of those parents
3. Exclude the selected person
4. Deduplicate (same person might appear through both parents)
5. Return unique siblings

#### 3. useFamilyTreeData (Custom Hook)

**Purpose**: Encapsulate data fetching and caching logic.

**Signature**:
```typescript
function useFamilyTreeData(personId: string | null) {
  return {
    familyData: CategorizedRelationships & { siblings: PersonDetails[] }
    isLoading: boolean
    error: Error | null
    refetch: () => void
  }
}
```

**Implementation**:
- Use TanStack Query for data fetching
- Cache relationship data by person ID
- Handle loading and error states
- Provide refetch function for manual refresh

## Data Models

### Existing Backend Models (Used As-Is)

#### PersonRelationshipWithDetails
```typescript
interface PersonRelationshipWithDetails {
  relationship: PersonRelationshipPublic
  person: PersonDetails
}

interface PersonRelationshipPublic {
  id: string
  person_id: string
  related_person_id: string
  relationship_type: string
  relationship_type_label: string
  start_date: string | null
  end_date: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

interface PersonDetails {
  id: string
  first_name: string
  middle_name: string | null
  last_name: string
  gender_id: string
  date_of_birth: string
  date_of_death: string | null
  user_id: string | null
  created_by_user_id: string
  is_primary: boolean
  created_at: string
  updated_at: string
}
```

### Frontend-Specific Models

#### FamilyTreeData
```typescript
interface FamilyTreeData {
  selectedPerson: PersonDetails
  parents: PersonDetails[]
  spouses: PersonDetails[]
  siblings: PersonDetails[]
  children: PersonDetails[]
}
```

#### PersonCardData
```typescript
interface PersonCardData {
  person: PersonDetails
  relationshipLabel: string
  displayName: string
  birthYear: string
  deathYear: string | null
  yearsDisplay: string // "1990 -" or "1990 - 2020"
  hasPhoto: boolean
  photoUrl: string | null
}
```

### Relationship Type Constants

```typescript
const RELATIONSHIP_TYPES = {
  FATHER: 'rel-6a0ede824d101',
  MOTHER: 'rel-6a0ede824d102',
  DAUGHTER: 'rel-6a0ede824d103',
  SON: 'rel-6a0ede824d104',
  WIFE: 'rel-6a0ede824d105',
  HUSBAND: 'rel-6a0ede824d106',
  SPOUSE: 'rel-6a0ede824d107',
} as const

const PARENT_TYPES = [
  RELATIONSHIP_TYPES.FATHER,
  RELATIONSHIP_TYPES.MOTHER,
]

const SPOUSE_TYPES = [
  RELATIONSHIP_TYPES.WIFE,
  RELATIONSHIP_TYPES.HUSBAND,
  RELATIONSHIP_TYPES.SPOUSE,
]

const CHILD_TYPES = [
  RELATIONSHIP_TYPES.DAUGHTER,
  RELATIONSHIP_TYPES.SON,
]
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Person Information Formatting

*For any* person displayed in the family tree (selected person, parent, spouse, sibling, or child), the person card should display the person's first name and last name, and below the name should show "birth_year - death_year" if death year exists, otherwise "birth_year -".

**Validates: Requirements 2.2, 3.4, 4.3, 6.3**

### Property 2: Relationship Categorization

*For any* set of PersonRelationshipWithDetails returned from the API, the categorizeRelationships function should correctly categorize each relationship into exactly one category (parents, spouses, or children) based on the relationship_type, with no relationships miscategorized or lost.

**Validates: Requirements 9.3**

### Property 3: Sibling Calculation

*For any* person with parents, the calculateSiblings function should return all other people who share at least one parent with that person, excluding the person themselves, with no duplicates.

**Validates: Requirements 9.4**

### Property 4: Relationship Display

*For any* person with relationships of a given type (parents, spouses, siblings, or children), when that person is selected, the family tree should display all relationships of that type in the appropriate section.

**Validates: Requirements 3.1, 4.1, 5.1, 6.1**

### Property 5: Multiple Spouse Display

*For any* person with multiple spouse relationships, all spouses should be displayed in a horizontally scrollable container or carousel, with no spouses omitted.

**Validates: Requirements 4.4**

### Property 6: Multiple Sibling Display

*For any* person with more than a threshold number of siblings, all siblings should be displayed in a horizontally scrollable container, with no siblings omitted.

**Validates: Requirements 5.3**

### Property 7: All Children Display

*For any* person with children from multiple spouses, all children should be displayed regardless of which spouse they are associated with, with no children omitted.

**Validates: Requirements 6.5**

### Property 8: Person Selection Navigation

*For any* person card displayed in the family tree, when clicked, the system should update the selected person to that person, fetch that person's relationship data, and re-render the tree centered on the new person.

**Validates: Requirements 7.1, 7.2, 7.3**

### Property 9: Data Caching

*For any* person whose relationship data has been previously fetched, subsequent requests for that person's data should be served from cache without making additional API calls.

**Validates: Requirements 9.5**

### Property 10: Responsive Layout Adaptation

*For any* viewport size change, the family tree layout should adapt appropriately by adjusting card sizes, spacing, and section arrangement based on the current breakpoint (desktop, tablet, or mobile).

**Validates: Requirements 10.4**

### Property 11: Three-Row Horizontal Layout

*For any* person with relationships, the family tree should display exactly three horizontal rows (parents, center with siblings+spouses, children) where each row uses horizontal scrolling for overflow without vertical stacking of same-type relationships.

**Validates: Requirements 9.1, 9.2, 9.3, 9.4, 9.5**

## Error Handling

### Error Scenarios

1. **No Person Profile**
   - **Scenario**: User has no person profile associated with their account
   - **Handling**: Display a message prompting the user to complete their profile, with a link to the profile completion page
   - **UI**: Empty state with icon, message, and action button

2. **API Fetch Failure**
   - **Scenario**: Network error or server error when fetching relationship data
   - **Handling**: Display error message with retry button, preserve previous data if available
   - **UI**: Error toast notification with retry action

3. **Invalid Person ID**
   - **Scenario**: User navigates to a person ID that doesn't exist
   - **Handling**: Redirect to the user's own person profile or show error message
   - **UI**: Error message with navigation back to own profile

4. **Empty Relationship Data**
   - **Scenario**: Person has no relationships recorded
   - **Handling**: Display empty state for each section (no parents, no spouse, no children)
   - **UI**: Subtle placeholder text indicating no relationships in each section

5. **Partial Data**
   - **Scenario**: Some relationship data is missing or incomplete
   - **Handling**: Display available data, use placeholders for missing information
   - **UI**: Show "Unknown" or placeholder for missing names/dates

### Error Recovery

- **Retry Mechanism**: Provide retry buttons for failed API calls
- **Graceful Degradation**: Show partial data if some relationships fail to load
- **User Feedback**: Clear error messages explaining what went wrong and how to fix it
- **Fallback Navigation**: Always provide a way to return to the user's own profile

## Testing Strategy

### Dual Testing Approach

This feature will use both unit tests and property-based tests to ensure comprehensive coverage:

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across all inputs

Both types of tests are complementary and necessary for comprehensive coverage. Unit tests focus on specific scenarios and integration points, while property tests validate that core logic works correctly across a wide range of generated inputs.

### Unit Testing

Unit tests will focus on:

1. **Component Rendering**
   - PersonCard renders correctly with different variants
   - RelationshipLines render with correct SVG paths
   - SiblingsList and SpouseCarousel render with correct layout

2. **User Interactions**
   - Clicking a person card triggers selection change
   - Navigation between family members works correctly
   - Carousel navigation (prev/next) works for multiple spouses

3. **Edge Cases**
   - No person profile exists
   - Person has no relationships
   - Person has only one parent
   - Person has no photo (shows placeholder)
   - API fetch failures

4. **Integration Points**
   - API endpoint is called with correct parameters
   - TanStack Query caching works correctly
   - Route navigation works correctly

### Property-Based Testing

Property tests will focus on:

1. **Data Processing Properties**
   - Property 1: Person information formatting
   - Property 2: Relationship categorization
   - Property 3: Sibling calculation
   - Property 4: Relationship display
   - Property 5: Multiple spouse display
   - Property 6: Multiple sibling display
   - Property 7: All children display
   - Property 9: Data caching

2. **UI Behavior Properties**
   - Property 8: Person selection navigation
   - Property 10: Responsive layout adaptation

### Property Test Configuration

- **Library**: Use `fast-check` for TypeScript property-based testing
- **Iterations**: Minimum 100 iterations per property test
- **Tagging**: Each property test must reference its design document property
- **Tag format**: `Feature: family-tree-view, Property {number}: {property_text}`

### Test Data Generation

For property-based tests, we'll need generators for:

1. **PersonDetails Generator**
   - Random UUIDs for IDs
   - Random names (first, middle, last)
   - Random dates (birth, death)
   - Random gender IDs
   - Optional user IDs

2. **PersonRelationshipWithDetails Generator**
   - Random relationship types (from valid set)
   - Random person details
   - Random dates (start, end)
   - Active/inactive status

3. **Family Structure Generator**
   - Generate complete family structures with:
     - Parents (0-2)
     - Spouses (0-N)
     - Siblings (0-N, calculated through shared parents)
     - Children (0-N)

### Testing Tools

- **Unit Testing**: Vitest (already in use in the project)
- **Property Testing**: fast-check
- **Component Testing**: React Testing Library
- **API Mocking**: MSW (Mock Service Worker)

## Implementation Notes

### Navigation Integration

Add the Family Tree View link to the main navigation in the `_layout.tsx` component:

```typescript
const navigation = [
  { name: "Dashboard", to: "/" },
  { name: "Update Family", to: "/family" },
  { name: "Family View", to: "/family-tree" }, // New
  { name: "Items", to: "/items" },
  // ... other nav items
]
```

### Route Definition

Create a new route file at `frontend/src/routes/_layout/family-tree.tsx`:

```typescript
export const Route = createFileRoute("/_layout/family-tree")({
  component: FamilyTreeView,
  head: () => ({
    title: "Family Tree View",
  }),
})
```

### Styling Approach

- Use Tailwind CSS for styling (consistent with existing codebase)
- Use CSS Grid for main layout structure
- Use Flexbox for card layouts
- Use SVG for relationship lines
- Use Radix UI components for interactive elements (carousel, scroll area)

### Performance Considerations

1. **Data Caching**: Use TanStack Query's built-in caching to avoid redundant API calls
2. **Lazy Loading**: Only fetch relationship data when a person is selected
3. **Memoization**: Use React.memo for PersonCard components to avoid unnecessary re-renders
4. **Virtual Scrolling**: Consider virtual scrolling for large sibling/children lists (if needed)

### Accessibility

1. **Keyboard Navigation**: Ensure all person cards are keyboard accessible
2. **Screen Readers**: Provide appropriate ARIA labels for relationship sections
3. **Focus Management**: Manage focus when navigating between persons
4. **Color Contrast**: Ensure sufficient contrast for all text and visual elements

### Responsive Breakpoints

```typescript
const breakpoints = {
  mobile: '0-640px',    // Smaller cards, horizontal scrolling maintained
  tablet: '641-1024px', // Medium cards, horizontal scrolling maintained
  desktop: '1025px+',   // Larger cards, horizontal scrolling maintained
}
```

**Key Principle**: All screen sizes maintain the three-row horizontal layout. The only changes across breakpoints are card sizes and spacing—never vertical stacking of same-type relationships.

### Future Enhancements

The following features are mentioned in requirements but deferred to future iterations:

1. **Multi-Generation Expansion** (Requirement 8)
   - Expand to show grandparents, grandchildren
   - Progressive loading of additional generations
   - Collapse/expand controls

2. **Advanced Navigation**
   - Breadcrumb trail showing navigation path
   - "Back" button to return to previous person
   - Search functionality to jump to specific person

3. **Enhanced Visualizations**
   - Zoom in/out controls
   - Pan/drag to navigate large trees
   - Different layout algorithms (vertical, horizontal, radial)

4. **Export/Share**
   - Export tree as image
   - Share tree view with others
   - Print-friendly view
