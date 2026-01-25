# Design Document: Rishte View Button

## Overview

This feature adds a "View" button to each person node in the Rishte relationship graph, enabling users to view detailed person information in a sliding panel. The implementation reuses the existing `PersonDetailsPanel` component from the Family Tree feature to ensure a consistent user experience across the application.

**Key Design Decisions:**
- **Own Component**: We modify the Rishte-specific `PersonNode` component (`/components/Rishte/PersonNode.tsx`) directly rather than sharing with Find Partner's `MatchPersonNode`. This keeps the codebases independent and allows for future divergence if needed.
- **Explore via Panel**: The Explore button functionality is already built into `PersonDetailsPanel`, so users can navigate to Family Tree from within the panel after clicking View.

## Architecture

The feature follows the existing component hierarchy pattern, passing callbacks down through the component tree:

```
┌─────────────────────────────────────────────────────────────────┐
│                        RishtePage                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  State: detailsPanelPersonId, isDetailsPanelOpen        │   │
│  │  Handler: handleViewClick(personId)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    RishteGraph                           │   │
│  │  Props: onNodeViewClick?: (personId: string) => void    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PersonNode                            │   │
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

### PersonNode Updates

Add View button and callback handling to the Rishte-specific PersonNode component (`/components/Rishte/PersonNode.tsx`):

```typescript
// Updated PersonNodeData interface in /components/Rishte/types.ts
export interface PersonNodeData extends Record<string, unknown> {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  deathYear: number | null
  isPersonA: boolean
  isPersonB: boolean
  gender?: "male" | "female"
  onViewClick?: (personId: string) => void  // NEW
}

// Add imports to PersonNode.tsx
import { Eye } from "lucide-react"
import { Button } from "@/components/ui/button"

// View button click handler in PersonNode.tsx
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

// View button JSX (add after Person A/B label)
{data.onViewClick && (
  <Button
    variant="outline"
    size="sm"
    className="mt-1 nodrag nopan pointer-events-auto cursor-pointer"
    onClick={handleViewClick}
    onKeyDown={handleViewKeyDown}
    aria-label={`View details for ${firstName} ${lastName}`}
  >
    <Eye className="h-4 w-4" />
    <span>View</span>
  </Button>
)}
```

### RishteGraph Updates

Add callback prop and pass to nodes in `/components/Rishte/RishteGraph.tsx`:

```typescript
interface RishteGraphProps {
  nodes: RishteNode[]
  edges: RishteEdge[]
  onNodeViewClick?: (personId: string) => void  // NEW
}

// In RishteGraph component, inject callback into nodes
const nodesWithCallback = useMemo(() => {
  if (!onNodeViewClick) return nodes

  return nodes.map((node) => ({
    ...node,
    data: {
      ...node.data,
      onViewClick: onNodeViewClick,
    },
  }))
}, [nodes, onNodeViewClick])

// Pass nodesWithCallback to RishteGraphInner instead of nodes
```

### RishteGraphInner Updates

Update the inner component to receive nodes with callbacks:

```typescript
// No changes needed - it already receives nodes as props
// The callback is injected into node.data by RishteGraph
```

### RishtePage Updates

Add state and handler for the details panel in `/routes/_layout/rishte.tsx`:

```typescript
// Add import
import { PersonDetailsPanel } from "@/components/FamilyTree/PersonDetailsPanel"

// State for PersonDetailsPanel
const [detailsPanelPersonId, setDetailsPanelPersonId] = useState<string | null>(null)
const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(false)

// Handler for View button clicks
const handleViewClick = useCallback((personId: string) => {
  setDetailsPanelPersonId(personId)
  setIsDetailsPanelOpen(true)
}, [])

// Pass callback to RishteGraph
<RishteGraph
  nodes={transformedPath.nodes}
  edges={transformedPath.edges}
  onNodeViewClick={handleViewClick}  // NEW
/>

// Add PersonDetailsPanel at the end of the component
<PersonDetailsPanel
  personId={detailsPanelPersonId}
  open={isDetailsPanelOpen}
  onOpenChange={setIsDetailsPanelOpen}
/>
```

## Data Models

No changes to data models required. The feature reuses existing:
- `PersonNodeData` - Extended with optional `onViewClick` callback
- `PersonCompleteDetailsResponse` - Used by PersonDetailsPanel (unchanged)

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: View Button Callback Invocation

*For any* PersonNode with any valid person ID, when the View button is clicked, the onViewClick callback SHALL be invoked with exactly that person's ID.

**Validates: Requirements 1.2, 3.3**

### Property 2: Aria Label Correctness

*For any* PersonNode with any first name and last name combination, the View button's aria-label SHALL be exactly "View details for {firstName} {lastName}".

**Validates: Requirements 1.5**

### Property 3: Panel Opens With Correct Person ID

*For any* person ID passed to handleViewClick in RishtePage, the PersonDetailsPanel SHALL receive that exact person ID as its personId prop.

**Validates: Requirements 2.2**

### Property 4: Callback Injection to All Nodes

*For any* RishteGraph with any number of nodes and a provided onNodeViewClick callback, every node in the graph SHALL have the onViewClick callback in its data.

**Validates: Requirements 3.2**

## Error Handling

| Scenario | Handling |
|----------|----------|
| onViewClick callback is undefined | View button still renders but click does nothing |
| PersonDetailsPanel API call fails | Panel shows error state with retry button (existing behavior) |
| Invalid person ID passed | PersonDetailsPanel shows "Person not found" error (existing behavior) |

## Testing Strategy

### Unit Tests

1. **PersonNode renders View button** - Verify button with Eye icon and "View" text is present
2. **View button has correct aria-label** - Verify accessibility attribute format
3. **View button uses correct styling** - Verify outline variant and sm size
4. **Click stops propagation** - Verify stopPropagation is called
5. **Keyboard accessibility** - Verify Enter and Space trigger callback
6. **RishteGraph passes callback to nodes** - Verify nodes receive onViewClick in data
7. **RishtePage state management** - Verify panel opens/closes correctly

### Property-Based Tests

Property-based tests will use `fast-check` library to generate random inputs and verify properties hold for all cases.

1. **Property 1 test**: Generate random person IDs, verify callback receives exact ID
2. **Property 2 test**: Generate random first/last name strings, verify aria-label format
3. **Property 3 test**: Generate random person IDs, verify panel receives correct ID
4. **Property 4 test**: Generate random node arrays, verify all nodes receive callback

### Integration Tests

1. **End-to-end View flow**: Click View button → Panel opens → Shows correct person data → Close panel
2. **Multiple View clicks**: Click View on different nodes → Panel updates with new person each time
3. **Panel close doesn't affect graph**: Open panel → Close panel → Graph state unchanged
