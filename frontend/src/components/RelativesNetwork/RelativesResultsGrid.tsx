/**
 * RelativesResultsGrid Component
 * Displays relatives in a responsive grid layout
 * Requirements: 3.2, 3.6
 */

import { Search } from "lucide-react"
import { memo } from "react"

import { RelativeCard } from "./RelativeCard"

/**
 * Relative data structure matching the API response
 */
export interface RelativeData {
  person_id: string
  first_name: string
  last_name: string
  gender_id: string
  birth_year: number | null
  death_year: number | null
  district_name: string | null
  locality_name: string | null
  depth: number
}

export interface RelativesResultsGridProps {
  /** List of relatives to display */
  relatives: RelativeData[]
  /** Depth value used in the search (for empty state message) */
  depth: number
  /** Callback when View button is clicked on a relative card */
  onViewRelative: (personId: string) => void
}

/**
 * Empty state component when no relatives are found
 * Requirements: 3.6
 */
function EmptyState({ depth }: { depth: number }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <Search className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="text-lg font-semibold mb-2">No relatives found</h3>
      <p className="text-muted-foreground max-w-md">
        No relatives found within depth {depth}. Try increasing the depth or
        adjusting your filters.
      </p>
    </div>
  )
}

/**
 * RelativesResultsGrid displays relatives in a responsive grid
 * - 1 column on mobile
 * - 2 columns on small screens
 * - 3 columns on medium screens
 * - 4 columns on large screens
 * Requirements: 3.2, 3.6
 */
export const RelativesResultsGrid = memo(function RelativesResultsGrid({
  relatives,
  depth,
  onViewRelative,
}: RelativesResultsGridProps) {
  // Handle empty state - Requirements: 3.6
  if (!relatives || relatives.length === 0) {
    return <EmptyState depth={depth} />
  }

  // Render responsive grid - Requirements: 3.2
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {relatives.map((relative) => (
        <RelativeCard
          key={relative.person_id}
          personId={relative.person_id}
          firstName={relative.first_name}
          lastName={relative.last_name}
          genderId={relative.gender_id}
          birthYear={relative.birth_year}
          deathYear={relative.death_year}
          districtName={relative.district_name}
          localityName={relative.locality_name}
          depth={relative.depth}
          onView={onViewRelative}
        />
      ))}
    </div>
  )
})
