import { PersonCard } from "./PersonCard"
import type { PersonDetails } from "@/client"

export interface ParentsSectionProps {
  parents: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * ParentsSection component displays parent cards above the selected person
 * Displays all parents without filtering - users can have any number of parents
 */
export function ParentsSection({ parents, onPersonClick }: ParentsSectionProps) {
  if (parents.length === 0) {
    return null
  }

  return (
    <div 
      className="flex flex-col items-center gap-2 md:gap-4 mb-4 md:mb-6 lg:mb-8"
      role="region"
      aria-label="Parents section"
    >
      <div className="flex flex-col md:flex-row gap-4 md:gap-6 lg:gap-8 justify-center items-center md:items-start flex-wrap">
        {parents.map((parent) => (
          <PersonCard
            key={parent.id}
            person={parent}
            relationshipType="Parent"
            variant="parent"
            onClick={onPersonClick}
            showPhoto={true}
          />
        ))}
      </div>
    </div>
  )
}
