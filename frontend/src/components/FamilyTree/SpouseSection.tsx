import { PersonCard } from "./PersonCard"
import { SpouseCarousel } from "./SpouseCarousel"
import type { PersonDetails } from "@/client"

export interface SpouseSectionProps {
  spouses: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * SpouseSection component displays spouse card(s) horizontally adjacent to selected person
 * Uses SpouseCarousel for multiple spouses
 */
export function SpouseSection({ spouses, onPersonClick }: SpouseSectionProps) {
  if (spouses.length === 0) {
    return null
  }

  // For single spouse, display directly
  if (spouses.length === 1) {
    return (
      <div 
        className="flex items-center"
        role="region"
        aria-label="Spouse section"
      >
        <PersonCard
          person={spouses[0]}
          relationshipType="Spouse"
          variant="spouse"
          onClick={onPersonClick}
          showPhoto={true}
        />
      </div>
    )
  }

  // For multiple spouses, use SpouseCarousel
  return (
    <div 
      className="flex items-center"
      role="region"
      aria-label="Spouses section"
    >
      <SpouseCarousel spouses={spouses} onPersonClick={onPersonClick} />
    </div>
  )
}
