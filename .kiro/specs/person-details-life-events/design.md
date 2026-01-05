# Design Document: Life Events in Person Details Panel

## Overview

This design extends the Person Details Panel to include a Life Events section, allowing users to view significant life milestones for any person in the Family Tree. The implementation adds a new backend API endpoint and enhances the frontend PersonDetailsPanel component.

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend Layer                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  PersonDetailsPanel Component                          │ │
│  │  - Existing person details (photo, name, etc.)        │ │
│  │  - NEW: Life Events Section                           │ │
│  │  - Uses usePersonLifeEvents hook                      │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           │ TanStack Query                   │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LifeEventsService (Auto-generated Client)            │ │
│  │  - getPersonLifeEvents(personId)                      │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ HTTP GET
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend Layer                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Life Events API Routes                                │ │
│  │  - GET /api/v1/life-events/person/{person_id}         │ │
│  │  - NEW endpoint for fetching any person's events      │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LifeEventService                                      │ │
│  │  - get_life_events(person_id) [EXISTING]              │ │
│  │  - Reuses existing service method                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  LifeEventRepository                                   │ │
│  │  - get_by_person(person_id) [EXISTING]                │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Database: person_life_event table                     │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Backend Implementation

### New API Endpoint

**File**: `backend/app/api/routes/life_events.py`

Add new endpoint:

```python
@router.get("/person/{person_id}", response_model=LifeEventsPublic)
@log_route
def get_person_life_events(
    session: SessionDep,
    current_user: CurrentUser,
    person_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get life events for a specific person by person ID.
    
    Accessible to all authenticated users - allows viewing life events
    for any person visible in the Family Tree.
    
    Returns life events sorted by date (most recent first):
    - Year descending
    - Month descending (nulls last)
    - Date descending (nulls last)
    """
    # Verify person exists
    person_service = PersonService(session)
    person = person_service.get_person_by_id(person_id)
    
    if not person:
        raise HTTPException(
            status_code=404,
            detail="Person not found"
        )
    
    # Get life events for the person
    life_event_service = LifeEventService(session)
    events, count = life_event_service.get_life_events(
        person_id, skip=skip, limit=limit
    )
    
    return LifeEventsPublic(data=events, count=count)
```

**Key Design Decisions**:
- Reuses existing `LifeEventService.get_life_events()` method - no new service logic needed
- No special authorization beyond authentication - if you can see someone in Family Tree, you can see their life events
- Returns same `LifeEventsPublic` schema as `/me` endpoint for consistency
- Validates person exists before querying events

### Service Layer

**No changes needed** - the existing `LifeEventService.get_life_events(person_id)` method already provides all required functionality.

## Frontend Implementation

### 1. Custom Hook: usePersonLifeEvents

**File**: `frontend/src/hooks/usePersonLifeEvents.ts`

```typescript
import { useQuery } from "@tanstack/react-query"
import { LifeEventsService } from "@/client"

export function usePersonLifeEvents(personId: string | null) {
  return useQuery({
    queryKey: ["personLifeEvents", personId],
    queryFn: () => {
      if (!personId) {
        throw new Error("Person ID is required")
      }
      return LifeEventsService.getPersonLifeEvents({
        personId,
        skip: 0,
        limit: 100,
      })
    },
    enabled: !!personId,
  })
}
```

**Key Features**:
- Only fetches when personId is provided
- Uses TanStack Query for caching and state management
- Follows same pattern as `usePersonCompleteDetails`

### 2. Enhanced PersonDetailsPanel Component

**File**: `frontend/src/components/FamilyTree/PersonDetailsPanel.tsx`

Add Life Events section after existing details:

```typescript
import { usePersonLifeEvents } from "@/hooks/usePersonLifeEvents"
import { LifeEventsList } from "@/components/LifeEvents/LifeEventsList"

export function PersonDetailsPanel({
  personId,
  open,
  onOpenChange,
}: PersonDetailsPanelProps) {
  const { data, isLoading, error, refetch } = usePersonCompleteDetails(personId)
  
  // NEW: Fetch life events for the person
  const {
    data: lifeEventsData,
    isLoading: isLoadingEvents,
    error: eventsError,
    refetch: refetchEvents,
  } = usePersonLifeEvents(personId)

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-md overflow-y-auto">
        {/* Existing person details content */}
        {data && !isLoading && !error && (
          <div className="flex flex-col items-center gap-6 py-6">
            {/* Photo, Name, Gender, Address, Religion - EXISTING */}
            
            {/* NEW: Life Events Section */}
            <div className="w-full border-t pt-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Life Events
              </h3>
              
              {isLoadingEvents && (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              )}
              
              {eventsError && !isLoadingEvents && (
                <div className="text-center py-4">
                  <p className="text-sm text-destructive">
                    Failed to load life events
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2"
                    onClick={() => refetchEvents()}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retry
                  </Button>
                </div>
              )}
              
              {lifeEventsData && !isLoadingEvents && !eventsError && (
                <>
                  {lifeEventsData.data.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      No life events recorded
                    </p>
                  ) : (
                    <LifeEventsList events={lifeEventsData.data} compact />
                  )}
                </>
              )}
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
```

### 3. Reusable LifeEventsList Component

**File**: `frontend/src/components/LifeEvents/LifeEventsList.tsx`

```typescript
import { Calendar, MapPin } from "lucide-react"
import type { LifeEventPublic } from "@/client"
import { getEventTypeIcon } from "@/components/LifeEvents/eventTypeIcons"

interface LifeEventsListProps {
  events: LifeEventPublic[]
  compact?: boolean // Compact mode for side panel
}

export function LifeEventsList({ events, compact = false }: LifeEventsListProps) {
  return (
    <div className={compact ? "space-y-3" : "space-y-4"}>
      {events.map((event) => (
        <LifeEventCard key={event.id} event={event} compact={compact} />
      ))}
    </div>
  )
}

interface LifeEventCardProps {
  event: LifeEventPublic
  compact?: boolean
}

function LifeEventCard({ event, compact }: LifeEventCardProps) {
  const EventIcon = getEventTypeIcon(event.event_type)
  const formattedDate = formatEventDate(
    event.event_year,
    event.event_month,
    event.event_date
  )
  const location = formatEventLocation(event)

  return (
    <div className={cn(
      "flex gap-3 p-3 rounded-lg border bg-card",
      compact && "text-sm"
    )}>
      <div className="flex-shrink-0">
        <EventIcon className={cn(
          "text-muted-foreground",
          compact ? "h-4 w-4" : "h-5 w-5"
        )} />
      </div>
      
      <div className="flex-1 min-w-0">
        <h4 className={cn(
          "font-medium",
          compact ? "text-sm" : "text-base"
        )}>
          {event.title}
        </h4>
        
        <p className={cn(
          "text-muted-foreground flex items-center gap-1 mt-1",
          compact ? "text-xs" : "text-sm"
        )}>
          <Calendar className="h-3 w-3" />
          {formattedDate}
        </p>
        
        {location && (
          <p className={cn(
            "text-muted-foreground flex items-center gap-1 mt-1",
            compact ? "text-xs" : "text-sm"
          )}>
            <MapPin className="h-3 w-3" />
            {location}
          </p>
        )}
        
        {event.description && !compact && (
          <p className="text-sm text-muted-foreground mt-2">
            {event.description}
          </p>
        )}
      </div>
    </div>
  )
}

function formatEventDate(
  year: number,
  month: number | null,
  date: number | null
): string {
  if (month && date) {
    const monthName = new Date(year, month - 1).toLocaleString('default', { month: 'long' })
    return `${monthName} ${date}, ${year}`
  }
  if (month) {
    const monthName = new Date(year, month - 1).toLocaleString('default', { month: 'long' })
    return `${monthName} ${year}`
  }
  return `${year}`
}

function formatEventLocation(event: LifeEventPublic): string | null {
  const parts: string[] = []
  
  if (event.locality_name) parts.push(event.locality_name)
  if (event.sub_district_name) parts.push(event.sub_district_name)
  if (event.district_name) parts.push(event.district_name)
  if (event.state_name) parts.push(event.state_name)
  if (event.country_name) parts.push(event.country_name)
  
  return parts.length > 0 ? parts.join(", ") : null
}
```

### 4. Event Type Icons Helper

**File**: `frontend/src/components/LifeEvents/eventTypeIcons.ts`

```typescript
import {
  Baby,
  Heart,
  Cross,
  Home,
  DollarSign,
  Trophy,
  GraduationCap,
  Briefcase,
  Activity,
  Plane,
  Calendar,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

export function getEventTypeIcon(eventType: string): LucideIcon {
  const iconMap: Record<string, LucideIcon> = {
    birth: Baby,
    marriage: Heart,
    death: Cross,
    purchase: Home,
    sale: DollarSign,
    achievement: Trophy,
    education: GraduationCap,
    career: Briefcase,
    health: Activity,
    travel: Plane,
    other: Calendar,
  }
  
  return iconMap[eventType] || Calendar
}
```

## Data Flow

### Viewing Life Events Flow

1. **User clicks View button** on person card in Family Tree
2. **PersonDetailsPanel opens** with personId
3. **Parallel data fetching**:
   - `usePersonCompleteDetails(personId)` fetches person details
   - `usePersonLifeEvents(personId)` fetches life events
4. **Person details render immediately** when available
5. **Life Events section shows loading** while fetching
6. **Life events render** when data arrives
7. **User sees complete profile** with life events

### Error Handling

- Person details error: Shows error for entire panel (existing behavior)
- Life events error: Shows error only in Life Events section with retry button
- Person not found: Backend returns 404, frontend shows appropriate message
- Network error: TanStack Query handles retries automatically

## UI/UX Design

### Layout

```
┌─────────────────────────────────────┐
│  Person Details Panel         [X]   │
├─────────────────────────────────────┤
│                                     │
│         [Person Photo]              │
│                                     │
│         John Doe                    │
│         📅 1990 -                   │
│                                     │
│  👤 Gender                          │
│     Male                            │
│                                     │
│  📍 Address                         │
│     City, State, Country            │
│                                     │
│  ❤️  Religion                       │
│     Religion Name                   │
│                                     │
├─────────────────────────────────────┤ ← Border separator
│                                     │
│  📅 Life Events                     │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 🎓 Graduated College          │ │
│  │ 📅 May 2012                   │ │
│  │ 📍 Boston, MA, USA            │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 💼 Started First Job          │ │
│  │ 📅 June 2012                  │ │
│  │ 📍 New York, NY, USA          │ │
│  └───────────────────────────────┘ │
│                                     │
│  ┌───────────────────────────────┐ │
│  │ 💍 Got Married                │ │
│  │ 📅 September 15, 2015         │ │
│  │ 📍 San Francisco, CA, USA     │ │
│  └───────────────────────────────┘ │
│                                     │
└─────────────────────────────────────┘
```

### Styling Guidelines

- **Compact mode**: Smaller text, reduced spacing for side panel
- **Icons**: Use lucide-react icons matching event types
- **Colors**: Use muted colors for secondary information
- **Spacing**: Clear visual separation between events
- **Responsive**: Scrollable if many events

## Testing Strategy

### Backend Tests

**File**: `backend/tests/api/routes/test_life_events.py`

Add tests:
- `test_get_person_life_events_success` - Verify endpoint returns events
- `test_get_person_life_events_not_found` - Verify 404 for invalid person_id
- `test_get_person_life_events_empty` - Verify empty list for person with no events
- `test_get_person_life_events_pagination` - Verify skip/limit parameters
- `test_get_person_life_events_sorting` - Verify correct date sorting
- `test_get_person_life_events_unauthorized` - Verify authentication required

### Frontend Tests

**File**: `frontend/tests/life-events-in-panel.spec.ts`

E2E tests:
- Open person details panel and verify life events section appears
- Verify life events are displayed in correct order
- Verify empty state when no events exist
- Verify loading state while fetching
- Verify error state and retry functionality
- Verify date formatting for different date combinations
- Verify location formatting

### Unit Tests

**File**: `frontend/src/components/LifeEvents/LifeEventsList.test.tsx`

- Test date formatting function with various inputs
- Test location formatting with partial address data
- Test event type icon mapping
- Test compact vs normal mode rendering

## Performance Considerations

1. **Parallel Loading**: Person details and life events load simultaneously
2. **Query Caching**: TanStack Query caches results, avoiding redundant API calls
3. **Limit Results**: Default limit of 100 events prevents slow queries
4. **Optimistic UI**: Person details show immediately, life events load progressively
5. **Error Isolation**: Life events errors don't break person details display

## Security Considerations

1. **Authentication Required**: All users must be authenticated
2. **No Special Authorization**: Any authenticated user can view any person's life events (same as Family Tree visibility)
3. **Person Validation**: Backend validates person exists before querying events
4. **SQL Injection Protection**: Using SQLModel ORM with parameterized queries
5. **Rate Limiting**: Existing API rate limiting applies

## Migration and Rollout

### Phase 1: Backend (Can deploy independently)
1. Add new API endpoint
2. Add backend tests
3. Deploy backend changes

### Phase 2: Frontend (Requires backend deployed)
1. Regenerate OpenAPI client to include new endpoint
2. Create usePersonLifeEvents hook
3. Create LifeEventsList component
4. Update PersonDetailsPanel component
5. Add frontend tests
6. Deploy frontend changes

### Rollback Plan
- Frontend: Remove Life Events section from PersonDetailsPanel
- Backend: Remove new endpoint (no breaking changes to existing features)

## Future Enhancements (Out of Scope)

1. Edit life events directly from panel
2. Add new life events from panel
3. Filter/search life events
4. Pagination for more than 100 events
5. Privacy controls to hide specific events
6. Rich media attachments (photos, documents)
7. Event sharing/commenting features
