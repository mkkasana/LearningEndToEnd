import { HorizontalScrollRow } from "./HorizontalScrollRow"
import type { PersonDetails } from "@/client"

export interface ParentsSectionProps {
  parents: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * ParentsSection component displays parent cards above the selected person
 * Displays all parents without filtering - users can have any number of parents
 * Uses HorizontalScrollRow for consistent horizontal layout without vertical stacking
 * Requirements: 9.2
 */
export function ParentsSection({ parents, onPersonClick }: ParentsSectionProps) {
  if (parents.length === 0) {
    return null
  }

  return (
    <HorizontalScrollRow
      people={parents}
      onPersonClick={onPersonClick}
      variant="parent"
    />
  )
}
