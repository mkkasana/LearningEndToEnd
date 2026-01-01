import type { PersonDetails } from "@/client"
import { HorizontalScrollRow } from "./HorizontalScrollRow"

export interface ChildrenSectionProps {
  children: PersonDetails[]
  onPersonClick: (personId: string) => void
  onViewClick?: (personId: string) => void
  showAddCard?: boolean
  onAddClick?: () => void
}

/**
 * ChildrenSection component displays child cards below the selected person
 * with smaller styling compared to the selected person
 * Uses HorizontalScrollRow for consistent horizontal layout without vertical stacking
 *
 * Note: This component displays ALL children of the selected person,
 * regardless of which spouse they are associated with (Requirement 6.5)
 * Requirements: 1.3, 9.4
 */
export function ChildrenSection({
  children,
  onPersonClick,
  onViewClick,
  showAddCard,
  onAddClick,
}: ChildrenSectionProps) {
  if (children.length === 0 && !showAddCard) {
    return null
  }

  return (
    <HorizontalScrollRow
      people={children}
      onPersonClick={onPersonClick}
      onViewClick={onViewClick}
      variant="child"
      showAddCard={showAddCard}
      onAddClick={onAddClick}
    />
  )
}
