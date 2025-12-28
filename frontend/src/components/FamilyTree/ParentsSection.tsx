import { PersonCard } from "./PersonCard"
import type { PersonDetails } from "@/client"

export interface ParentsSectionProps {
  parents: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * ParentsSection component displays parent cards above the selected person
 * Handles cases with 0, 1, or 2 parents
 */
export function ParentsSection({ parents, onPersonClick }: ParentsSectionProps) {
  if (parents.length === 0) {
    return null
  }

  // Separate mother and father if both exist
  const father = parents.find(p => {
    // We need to check the relationship type from the original data
    // For now, we'll use a simple heuristic based on gender_id
    // This will be refined when we have access to the relationship type
    return p.gender_id === 'gen-6a0ede824d101' // Male gender ID
  })
  
  const mother = parents.find(p => {
    return p.gender_id === 'gen-6a0ede824d102' // Female gender ID
  })

  return (
    <div className="flex flex-col items-center gap-2 md:gap-4 mb-4 md:mb-6 lg:mb-8">
      <div className="flex flex-col md:flex-row gap-4 md:gap-6 justify-center items-center md:items-start">
        {father && (
          <PersonCard
            person={father}
            relationshipType="Father"
            variant="parent"
            onClick={onPersonClick}
            showPhoto={true}
          />
        )}
        {mother && (
          <PersonCard
            person={mother}
            relationshipType="Mother"
            variant="parent"
            onClick={onPersonClick}
            showPhoto={true}
          />
        )}
        {/* Handle case where we have a parent but can't determine gender */}
        {parents.length === 1 && !father && !mother && (
          <PersonCard
            person={parents[0]}
            relationshipType="Parent"
            variant="parent"
            onClick={onPersonClick}
            showPhoto={true}
          />
        )}
      </div>
    </div>
  )
}
