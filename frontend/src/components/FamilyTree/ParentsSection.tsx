import type { PersonDetails } from "@/client"
import { HorizontalScrollRow } from "./HorizontalScrollRow"

export interface ParentsSectionProps {
  parents: PersonDetails[]
  onPersonClick: (personId: string) => void
  onViewClick?: (personId: string) => void
  showAddCard?: boolean
  onAddClick?: () => void
}

/**
 * ParentsSection component displays parent cards above the selected person
 * Displays all parents without filtering - users can have any number of parents
 * Uses HorizontalScrollRow for consistent horizontal layout without vertical stacking
 * Requirements: 1.1, 9.2
 */
export function ParentsSection({
  parents,
  onPersonClick,
  onViewClick,
  showAddCard,
  onAddClick,
}: ParentsSectionProps) {
  if (parents.length === 0 && !showAddCard) {
    return null
  }

  return (
    <HorizontalScrollRow
      people={parents}
      onPersonClick={onPersonClick}
      onViewClick={onViewClick}
      variant="parent"
      showAddCard={showAddCard}
      onAddClick={onAddClick}
    />
  )
}
