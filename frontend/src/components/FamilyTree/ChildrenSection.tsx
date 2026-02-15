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
 * Always renders the row for consistent layout across own/other trees
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
  // Always render the row for consistent layout
  // When viewing own tree (showAddCard=true): show add card if no children
  // When viewing other's tree (showAddCard=false): show empty row if no children
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
