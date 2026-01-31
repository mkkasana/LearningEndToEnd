# Design Document: Contributions Page

## Overview

The Contributions Page feature adds a dedicated full-page view for users to see all persons they have created, along with engagement statistics. This enhances the existing contribution stats functionality (currently only accessible via a dialog) by providing a more prominent sidebar navigation entry and a spacious page layout.

This is primarily a frontend feature that:
1. Adds a new sidebar menu item
2. Creates a new route and page component
3. Reuses the existing `/api/v1/person/my-contributions` API endpoint
4. Retains the existing dialog access from the profile menu

No backend changes are required.

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     AppSidebar.tsx                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  baseItems array                                        │ │
│  │  + { icon: BarChart3, title: "My Contributions",       │ │
│  │      path: "/contributions" }                           │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Navigation
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              /contributions route                            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ContributionsPage.tsx                                  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Page Header: "My Contributions"                  │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Summary Stats: Total Contributions | Total Views │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │  Person Cards Grid (responsive)                   │  │ │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐            │  │ │
│  │  │  │ Card 1  │ │ Card 2  │ │ Card 3  │            │  │ │
│  │  │  └─────────┘ └─────────┘ └─────────┘            │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Call
                            ▼
┌─────────────────────────────────────────────────────────────┐
│           GET /api/v1/person/my-contributions                │
│           (existing endpoint - no changes)                   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User clicks "My Contributions" in sidebar
                    ↓
        Navigate to /contributions
                    ↓
        ContributionsPage mounts
                    ↓
        useQuery fetches GET /api/v1/person/my-contributions
                    ↓
        Display loading state while fetching
                    ↓
        Receive PersonContributionPublic[] response
                    ↓
        Calculate summary stats (total count, total views)
                    ↓
        Render page header + summary + person cards grid
```

## Components and Interfaces

### Sidebar Integration

```typescript
// frontend/src/components/Sidebar/AppSidebar.tsx

import {
  BarChart3,  // Add this import
  Bug,
  Calendar,
  // ... other imports
} from "lucide-react"

const baseItems: Item[] = [
  { icon: Home, title: "Dashboard", path: "/" },
  { icon: UsersRound, title: "Update Family", path: "/family" },
  { icon: Network, title: "Family View", path: "/family-tree" },
  { icon: Share2, title: "Relatives Network", path: "/relatives-network" },
  { icon: Calendar, title: "Life Events", path: "/life-events" },
  { icon: Search, title: "Search", path: "/search" },
  { icon: GitBranch, title: "Rishte", path: "/rishte" },
  { icon: Heart, title: "Find Partner", path: "/find-partner" },
  { icon: BarChart3, title: "My Contributions", path: "/contributions" },  // NEW
  { icon: Bug, title: "Report Ticket", path: "/support-tickets" },
]
```

### Route Configuration

```typescript
// frontend/src/routes/_layout/contributions.tsx

import { createFileRoute } from "@tanstack/react-router"
import ContributionsPage from "@/components/Contributions/ContributionsPage"

export const Route = createFileRoute("/_layout/contributions")({
  component: ContributionsPage,
})
```

### ContributionsPage Component

```typescript
// frontend/src/components/Contributions/ContributionsPage.tsx

import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import { 
  BarChart3, 
  Calendar, 
  Eye, 
  Loader2, 
  MapPin, 
  Network, 
  Users 
} from "lucide-react"
import { type PersonContributionPublic, PersonService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

/**
 * Format date range for display.
 * Shows "birthYear - deathYear" for deceased persons.
 * Shows "birthYear" only for living persons.
 */
function formatDateRange(
  birthDate: string,
  deathDate: string | null | undefined,
): string {
  const birthYear = new Date(birthDate).getFullYear()
  if (deathDate) {
    const deathYear = new Date(deathDate).getFullYear()
    return `${birthYear} - ${deathYear}`
  }
  return `${birthYear}`
}

/**
 * Navigate to family tree with a specific person selected.
 */
function handleExplorePerson(
  personId: string,
  navigate: ReturnType<typeof useNavigate>,
) {
  sessionStorage.setItem("familyTreeExplorePersonId", personId)
  navigate({ to: "/family-tree" })
  setTimeout(() => {
    window.dispatchEvent(
      new CustomEvent("familyTreeExplorePerson", { detail: { personId } }),
    )
  }, 100)
}

export default function ContributionsPage() {
  const navigate = useNavigate()

  const {
    data: contributions,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["myContributions"],
    queryFn: () => PersonService.getMyContributions(),
  })

  // Calculate summary stats
  const totalContributions = contributions?.length ?? 0
  const totalViews = contributions?.reduce(
    (sum, p) => sum + (p.total_views ?? 0), 
    0
  ) ?? 0

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <BarChart3 className="h-8 w-8" />
          My Contributions
        </h1>
        <p className="text-muted-foreground mt-2">
          View all persons you have created and their profile view statistics
        </p>
      </div>

      {/* Summary Stats */}
      {!isLoading && !error && contributions && (
        <div className="flex gap-6 mb-8">
          <Card className="flex-1">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Users className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{totalContributions}</p>
                  <p className="text-sm text-muted-foreground">
                    Total Contributions
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="flex-1">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Eye className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{totalViews}</p>
                  <p className="text-sm text-muted-foreground">Total Views</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="flex justify-center items-center py-16">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="text-center py-16">
          <p className="text-destructive text-lg">Failed to load contributions</p>
          <p className="text-muted-foreground mt-2">Please try again later</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && !error && contributions?.length === 0 && (
        <div className="text-center py-16">
          <Users className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <p className="text-lg text-muted-foreground">
            You haven't created any person profiles yet.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Start building your family tree to see your contributions here.
          </p>
          <Button 
            className="mt-6" 
            onClick={() => navigate({ to: "/family" })}
          >
            Add Family Members
          </Button>
        </div>
      )}

      {/* Person Cards Grid */}
      {!isLoading && !error && contributions && contributions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contributions.map((person: PersonContributionPublic) => (
            <Card 
              key={person.id} 
              className="hover:shadow-md transition-shadow"
            >
              <CardContent className="pt-6">
                {/* Name and Status */}
                <div className="flex items-center gap-2 mb-3">
                  <h3 className="font-semibold text-lg">
                    {person.first_name} {person.last_name}
                  </h3>
                  <div
                    className={`w-3 h-3 rounded-full ${
                      person.is_active
                        ? "bg-green-500"
                        : "bg-gray-300 border border-gray-400"
                    }`}
                    title={person.is_active ? "Active" : "Deactivated"}
                  />
                </div>

                {/* Date Range */}
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                  <Calendar className="h-4 w-4" />
                  <span>
                    {formatDateRange(person.date_of_birth, person.date_of_death)}
                  </span>
                </div>

                {/* Address */}
                {person.address && (
                  <div className="flex items-start gap-2 text-sm text-muted-foreground mb-3">
                    <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span className="line-clamp-2">{person.address}</span>
                  </div>
                )}

                {/* Footer: View Count and Explore */}
                <div className="flex items-center justify-between mt-4 pt-4 border-t">
                  <Badge variant="secondary" className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    <span>{person.total_views} views</span>
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExplorePerson(person.id, navigate)}
                  >
                    <Network className="h-4 w-4 mr-1" />
                    Explore
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
```

## Data Models

No new data models required. This feature reuses the existing `PersonContributionPublic` type:

```typescript
// Already exists in frontend/src/client/types.gen.ts
export interface PersonContributionPublic {
  id: string
  first_name: string
  last_name: string
  date_of_birth: string
  date_of_death: string | null
  is_active: boolean
  address: string
  total_views: number
  created_at: string
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

This feature primarily reuses existing backend logic and properties from the `contribution-stats` spec. The following properties from that spec apply:

- **Property 1**: Contribution Query Correctness (Requirements 1.1)
- **Property 2**: Name Display Format (Requirements 1.2)
- **Property 3**: Address Formatting (Requirements 1.3, 5.3)
- **Property 4**: Date Range Formatting for Living Persons (Requirements 1.4)
- **Property 5**: Date Range Formatting for Deceased Persons (Requirements 1.5)
- **Property 15**: Contributions Sorted by View Count (Requirements 5.5)

### Property 1: Summary Stats Calculation

*For any* list of contributions, the total contributions count should equal the length of the list, and the total views should equal the sum of all individual total_views values.

**Validates: Requirements 2.3**

## Error Handling

### API Errors

**Strategy**: Display user-friendly error message with retry option

```typescript
{error && (
  <div className="text-center py-16">
    <p className="text-destructive text-lg">Failed to load contributions</p>
    <p className="text-muted-foreground mt-2">Please try again later</p>
  </div>
)}
```

### Empty State

**Strategy**: Provide helpful guidance and action button

```typescript
{contributions?.length === 0 && (
  <div className="text-center py-16">
    <p>You haven't created any person profiles yet.</p>
    <Button onClick={() => navigate({ to: "/family" })}>
      Add Family Members
    </Button>
  </div>
)}
```

## Testing Strategy

### Unit Tests

Since this is primarily a frontend feature reusing existing backend logic, testing focuses on:

1. **Component rendering tests**:
   - Test loading state renders correctly
   - Test error state renders correctly
   - Test empty state renders correctly
   - Test person cards render with correct data

2. **Summary calculation tests**:
   - Test total contributions equals array length
   - Test total views equals sum of individual views
   - Test with empty array returns zeros

3. **Navigation tests**:
   - Test sidebar item navigates to /contributions
   - Test Explore button triggers navigation to family tree

### Integration Tests

1. **Route test**: Verify /contributions route loads ContributionsPage
2. **API integration**: Verify page fetches from correct endpoint
3. **Existing dialog**: Verify ContributionStatsDialog still works from profile menu

### Property-Based Tests

No new property-based tests required. Existing tests from `contribution-stats` spec cover the data formatting and sorting logic.

## Performance Considerations

1. **Query caching**: TanStack Query caches the contributions data, preventing redundant API calls
2. **Responsive images**: No images in this feature, keeping payload light
3. **Lazy loading**: Consider adding pagination for users with 50+ contributions (future enhancement)

## Security Considerations

1. **Authentication**: Route requires authenticated user (handled by `_layout` wrapper)
2. **Authorization**: API only returns persons created by the current user
3. **No sensitive data exposure**: Only displays data the user already has access to

