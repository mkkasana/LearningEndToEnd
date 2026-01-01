# Design Document

## Overview

This feature adds an "Add Family Member" card (Add_Card) to each row of the Family Tree View. The Add_Card is a placeholder card with a "+" icon inside a circle, positioned at the rightmost end of each row. When clicked, it opens the existing Add Family Member flow (Discovery Dialog → Multi-step Wizard) allowing users to add family members directly from the tree visualization.

## Architecture

The feature integrates with the existing Family Tree View architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Family Tree View                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Parents Row: [Parent Cards...] [Add_Card]                   ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Center Row: [Siblings] [Selected] [Spouses] [Add_Card]      ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ Children Row: [Child Cards...] [Add_Card]                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼ (on Add_Card click)
┌─────────────────────────────────────────────────────────────────┐
│              Existing Add Family Member Flow                     │
│  Discovery Dialog → Multi-step Wizard → Success → Refresh Tree  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### New Component: AddFamilyMemberCard

```typescript
// frontend/src/components/FamilyTree/AddFamilyMemberCard.tsx

export interface AddFamilyMemberCardProps {
  variant: "parent" | "center" | "child"
  onClick: () => void
}

/**
 * AddFamilyMemberCard - A placeholder card with "+" icon for adding family members
 * 
 * Visual Design:
 * - Same dimensions as PersonCard for the given variant
 * - Dashed border with muted background
 * - Centered circle containing a "+" icon
 * - Hover effect: border color change, slight scale
 */
export function AddFamilyMemberCard({ variant, onClick }: AddFamilyMemberCardProps)
```

### Modified Components

#### HorizontalScrollRow.tsx
Add optional `showAddCard` prop and `onAddClick` callback:

```typescript
export interface HorizontalScrollRowProps {
  people: PersonDetails[]
  selectedPersonId?: string
  onPersonClick: (personId: string) => void
  onViewClick?: (personId: string) => void
  variant: "parent" | "center" | "child"
  colorCoding?: Map<string, "sibling" | "spouse">
  // New props
  showAddCard?: boolean
  onAddClick?: () => void
}
```

#### family-tree.tsx (Route)
Add state and handlers for the Add Family Member dialogs:

```typescript
// New state
const [showDiscoveryDialog, setShowDiscoveryDialog] = useState(false)
const [showAddDialog, setShowAddDialog] = useState(false)

// Handler for Add_Card click
const handleAddFamilyMember = () => {
  setShowDiscoveryDialog(true)
}

// Handler for skipping discovery
const handleSkipDiscovery = () => {
  setShowDiscoveryDialog(false)
  setShowAddDialog(true)
}

// Handler for discovery dialog close
const handleDiscoveryDialogClose = () => {
  setShowAddDialog(true)
}
```

## Data Models

No new data models required. The feature reuses existing:
- `PersonDetails` - For displaying family members
- `PersonRelationshipWithDetails` - For relationship data
- Existing relationship type constants from `useFamilyTreeData.ts`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Add Card Position Invariant

*For any* row in the Family Tree View with N family member cards (where N >= 0), the Add_Card SHALL appear at position N+1 (rightmost position).

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: Add Card Always Present

*For any* rendered Family Tree View, each row (Parents, Center, Children) SHALL contain exactly one Add_Card regardless of the number of existing family members.

**Validates: Requirements 1.1, 1.2, 1.3, 5.1**

## Error Handling

| Scenario | Handling |
|----------|----------|
| Add Family Member flow cancelled | Close dialogs, no data refresh, tree state unchanged |
| Add Family Member API error | Show error toast, keep dialog open for retry |
| Add Family Member success | Close dialogs, refresh family tree data, show success toast |

## Testing Strategy

### Unit Tests
- Verify AddFamilyMemberCard renders with correct styling for each variant
- Verify click handler is called when card is clicked
- Verify HorizontalScrollRow renders Add_Card when `showAddCard` is true

### Property-Based Tests
- **Property 1**: Generate random arrays of family members (0 to N), verify Add_Card is always at rightmost position
- **Property 2**: Generate random family tree states, verify each row has exactly one Add_Card

### Integration Tests
- Verify clicking Add_Card opens Discovery Dialog
- Verify successful addition refreshes the Family Tree
- Verify cancelled addition does not change tree state
