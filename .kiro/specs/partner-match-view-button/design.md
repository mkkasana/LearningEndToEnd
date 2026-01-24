# Design Document: Partner Match View Button

## Overview

This feature adds a "View" button to each person node in the Find Partner match graph, enabling users to view detailed person information in a sliding panel. The implementation reuses the existing `PersonDetailsPanel` component from the Family Tree feature to ensure a consistent user experience across the application.

## Architecture

The feature follows the existing component hierarchy pattern, passing callbacks down through the component tree:

```
┌─────────────────────────────────────────────────────────────────┐
│                      FindPartnerPage                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  State: detailsPanelPersonId, isDetailsPanelOpen        │   │
│  │  Handler: handleViewClick(personId)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PartnerResultsDisplay                       │   │
│  │  Props: onViewPerson?: (personId: string) => void       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MatchGraph                            │   │
│  │  Props: onNodeViewClick?: (personId: string) => void    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  MatchPersonNode                         │   │
│  │  Data: onViewClick?: (personId: string) => void         │   │
│  │  UI: View button with Eye icon                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              PersonDetailsPanel (existing)               │   │
│  │  Props: personId, open, onOpenChange                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### MatchPersonNode Updates

Add View button and callback handling to the existing node component:

```typescript
// Updated MatchPersonNodeData interface
interface MatchPersonNodeData {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  deathYear: number | null
  isSeeker: boolean
  isMatch: boolean
  onViewClick?: (personId: string) => void  // NEW
}

// View button click handler
const handleViewClick = (e: React.MouseEvent<HTMLButtonElement>) => {
  e.stopPropagation()
  if (data.onViewClick) {
    data.onViewClick(data.personId)
  }
}

// View button keyboard handler
const handleViewKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
  if (e.key === "Enter" || e.key === " ") {
    e.stopPropagation()
  }
}
```

### MatchGraph Updates

Add callback prop and pass to nodes:

```typescript
interface MatchGraphProps {
  nodes: MatchNode[]
  edges: MatchEdge[]
  onNodeViewClick?: (personId: string) => void  // NEW
}

// When creating nodes, inject the callback into node data
const nodesWithCallback = nodes.map(node => ({
  ...node,
  data: {
    ...node.data,
    onViewClick: onNodeViewClick
  }
}))
```

### PartnerResultsDisplay Updates

Add callback prop and pass to MatchGraph:

```typescript
interface PartnerResultsDisplayProps {
  data: PartnerMatchResponse | null
  isLoading: boolean
  error: Error | null
  totalMatches: number | null
  onViewPerson?: (personId: string) => void  // NEW
}
```

### FindPartnerPage Updates

Add state and handler for the details panel:

```typescript
// State for PersonDetailsPanel
const [detailsPanelPersonId, setDetailsPanelPersonId] = useState<string | null>(null)
const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(false)

// Handler for View button clicks
const handleViewClick = (personId: string) => {
  setDetailsPanelPersonId(personId)
  setIsDetailsPanelOpen(true)
}
```

## Data Models

No changes to data models required. The feature reuses existing:
- `MatchPersonNodeData` - Extended with optional `onViewClick` callback
- `PersonCompleteDetailsResponse` - Used by PersonDetailsPanel (unchanged)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: View Button Callback Invocation

*For any* MatchPersonNode with any valid person ID, when the View button is clicked, the onViewClick callback SHALL be invoked with exactly that person's ID.

**Validates: Requirements 1.2, 3.3**

### Property 2: Aria Label Correctness

*For any* MatchPersonNode with any first name and last name combination, the View button's aria-label SHALL be exactly "View details for {firstName} {lastName}".

**Validates: Requirements 1.5**

### Property 3: Panel Opens With Correct Person ID

*For any* person ID passed to handleViewClick in FindPartnerPage, the PersonDetailsPanel SHALL receive that exact person ID as its personId prop.

**Validates: Requirements 2.2**

## Error Handling

| Scenario | Handling |
|----------|----------|
| onViewClick callback is undefined | View button still renders but click does nothing |
| PersonDetailsPanel API call fails | Panel shows error state with retry button (existing behavior) |
| Invalid person ID passed | PersonDetailsPanel shows "Person not found" error (existing behavior) |

## Testing Strategy

### Unit Tests

1. **MatchPersonNode renders View button** - Verify button with Eye icon and "View" text is present
2. **View button has correct aria-label** - Verify accessibility attribute format
3. **View button uses correct styling** - Verify outline variant and sm size
4. **Click stops propagation** - Verify stopPropagation is called
5. **Keyboard accessibility** - Verify Enter and Space trigger callback
6. **MatchGraph passes callback to nodes** - Verify nodes receive onViewClick in data
7. **PartnerResultsDisplay passes callback** - Verify onViewPerson is passed to MatchGraph
8. **FindPartnerPage state management** - Verify panel opens/closes correctly

### Property-Based Tests

Property-based tests will use `fast-check` library to generate random inputs and verify properties hold for all cases.

1. **Property 1 test**: Generate random person IDs, verify callback receives exact ID
2. **Property 2 test**: Generate random first/last name strings, verify aria-label format
3. **Property 3 test**: Generate random person IDs, verify panel receives correct ID

### Integration Tests

1. **End-to-end View flow**: Click View button → Panel opens → Shows correct person data → Close panel
2. **Multiple View clicks**: Click View on different nodes → Panel updates with new person each time
3. **Panel close doesn't affect graph**: Open panel → Close panel → Graph state unchanged
