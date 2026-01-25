# Design Document: Person Details Explore Button

## Overview

This feature adds an "Explore in Family Tree" button to the `PersonDetailsPanel` component. The button allows users to navigate from viewing a person's details to exploring their family network in the Family Tree view. The implementation reuses the existing explore pattern established in `ContributionStatsDialog` and the Search page.

## Architecture

The feature follows the existing architecture pattern for cross-page navigation with person selection:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PersonDetailsPanel                            │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Avatar                                                  │    │
│  │  [Explore in Family Tree] ← NEW BUTTON                  │    │
│  │  Name, Years, Gender, Address, Religion, Life Events    │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ onClick
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    handleExplorePerson()                         │
│  1. sessionStorage.setItem("familyTreeExplorePersonId", id)     │
│  2. onOpenChange(false) - close panel                           │
│  3. navigate({ to: "/family-tree" })                            │
│  4. setTimeout → dispatch CustomEvent                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Family Tree View                              │
│  - Listens for "familyTreeExplorePerson" event                  │
│  - Reads sessionStorage on mount (fallback)                     │
│  - Sets selectedPersonId → re-renders tree                      │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Modified Component: PersonDetailsPanel

Location: `frontend/src/components/FamilyTree/PersonDetailsPanel.tsx`

#### New Props

```typescript
export interface PersonDetailsPanelProps {
  personId: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
  // No new props needed - uses useNavigate hook internally
}
```

#### New Internal Function

```typescript
/**
 * Navigate to family tree with a specific person selected.
 * Uses custom event to notify the family tree component, plus sessionStorage as fallback.
 * Reuses the same pattern as ContributionStatsDialog.
 */
function handleExplorePerson(
  personId: string,
  navigate: ReturnType<typeof useNavigate>,
  onClose: () => void,
): void {
  // Store in sessionStorage as fallback for fresh page loads
  sessionStorage.setItem("familyTreeExplorePersonId", personId)
  // Close the panel
  onClose()
  // Navigate to family tree
  navigate({ to: "/family-tree" })
  // Dispatch custom event after a small delay to ensure navigation completes
  setTimeout(() => {
    window.dispatchEvent(
      new CustomEvent("familyTreeExplorePerson", { detail: { personId } }),
    )
  }, 100)
}
```

#### Button Placement

The Explore button will be added in the success state section, immediately after the Avatar component:

```tsx
{/* Person Details Content */}
{data && !isLoading && !error && (
  <div className="flex flex-col items-center gap-6 py-6">
    {/* Photo - Requirement 3.1 */}
    <Avatar className="h-24 w-24">
      {/* ... existing avatar code ... */}
    </Avatar>

    {/* NEW: Explore in Family Tree Button - Requirements 1.1, 1.2, 2.1-2.5 */}
    <Button
      variant="outline"
      className="flex items-center gap-2"
      onClick={() => handleExplorePerson(personId!, navigate, () => onOpenChange(false))}
      aria-label={`Explore ${data.first_name} ${data.last_name} in Family Tree`}
    >
      <Network className="h-4 w-4" />
      Explore in Family Tree
    </Button>

    {/* Name and Years - existing code continues... */}
  </div>
)}
```

## Data Models

No new data models required. The feature uses existing:
- `personId: string` - UUID of the person to explore
- `sessionStorage` key: `"familyTreeExplorePersonId"`
- Custom event: `"familyTreeExplorePerson"` with `{ detail: { personId: string } }`

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Session Storage Persistence

*For any* valid person ID displayed in the PersonDetailsPanel, when the Explore button is clicked, the sessionStorage SHALL contain that exact person ID under the key "familyTreeExplorePersonId".

**Validates: Requirements 2.1**

### Property 2: Custom Event Dispatch

*For any* valid person ID, when the Explore button is clicked and navigation completes, a CustomEvent named "familyTreeExplorePerson" SHALL be dispatched with the person ID in the event detail.

**Validates: Requirements 2.4**

### Property 3: Conditional Button Rendering

*For any* state where `data` is null, `isLoading` is true, or `error` is present, the Explore button SHALL NOT be rendered in the DOM.

**Validates: Requirements 4.1, 4.2, 4.3**

## Error Handling

| Scenario | Handling |
|----------|----------|
| Person ID is null | Button not rendered (guarded by `data && !isLoading && !error` condition) |
| Navigation fails | Browser handles navigation errors; sessionStorage provides fallback |
| Custom event not received | Family Tree reads from sessionStorage on mount as fallback |
| Panel already closed | No-op, navigation still proceeds |

## Testing Strategy

### Unit Tests

Unit tests will verify specific examples and edge cases:

1. **Button Rendering**
   - Button appears when data is loaded successfully
   - Button has correct text "Explore in Family Tree"
   - Button has Network icon
   - Button has appropriate aria-label

2. **Button Not Rendered**
   - Button not present during loading state
   - Button not present during error state
   - Button not present when personId is null

3. **Click Behavior**
   - Clicking button stores personId in sessionStorage
   - Clicking button closes the panel (onOpenChange called with false)
   - Clicking button triggers navigation to /family-tree

4. **Keyboard Accessibility**
   - Button is focusable
   - Enter key triggers click handler
   - Space key triggers click handler

### Property-Based Tests

Property tests will use a testing library (e.g., fast-check) to verify universal properties:

1. **Property 1 Test**: Generate random valid UUIDs, simulate click, verify sessionStorage contains the exact UUID
2. **Property 2 Test**: Generate random valid UUIDs, simulate click, verify CustomEvent is dispatched with correct detail
3. **Property 3 Test**: Generate random combinations of loading/error/data states, verify button presence matches expected condition

### Integration Tests

Integration tests will verify the end-to-end flow:

1. Open PersonDetailsPanel from Find Partner graph
2. Click Explore button
3. Verify navigation to /family-tree
4. Verify Family Tree shows the correct person selected

## Dependencies

### Imports to Add

```typescript
import { useNavigate } from "@tanstack/react-router"
import { Network } from "lucide-react"
```

### Existing Dependencies Used

- `@tanstack/react-router` - for navigation
- `lucide-react` - for Network icon
- `@/components/ui/button` - for Button component
- Browser APIs: `sessionStorage`, `CustomEvent`, `window.dispatchEvent`
