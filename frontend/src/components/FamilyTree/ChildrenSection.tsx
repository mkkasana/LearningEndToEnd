import { HorizontalScrollRow } from "./HorizontalScrollRow"
import type { PersonDetails } from "@/client"

export interface ChildrenSectionProps {
  children: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * ChildrenSection component displays child cards below the selected person
 * with smaller styling compared to the selected person
 * Uses HorizontalScrollRow for consistent horizontal layout without vertical stacking
 * 
 * Note: This component displays ALL children of the selected person,
 * regardless of which spouse they are associated with (Requirement 6.5)
 * Requirements: 9.4
 */
export function ChildrenSection({ children, onPersonClick }: ChildrenSectionProps) {
  if (children.length === 0) {
    return null
  }

  return (
    <HorizontalScrollRow
      people={children}
      onPersonClick={onPersonClick}
      variant="child"
    />
  )
}
