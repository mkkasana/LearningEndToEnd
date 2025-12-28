import { PersonCard } from "./PersonCard"
import type { PersonDetails } from "@/client"

export interface ChildrenSectionProps {
  children: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * ChildrenSection component displays child cards below the selected person
 * with smaller styling compared to the selected person
 * 
 * Note: This component displays ALL children of the selected person,
 * regardless of which spouse they are associated with (Requirement 6.5)
 */
export function ChildrenSection({ children, onPersonClick }: ChildrenSectionProps) {
  if (children.length === 0) {
    return null
  }

  return (
    <div className="flex flex-col items-center gap-2 md:gap-4 mt-4 md:mt-6 lg:mt-8">
      <div className="flex flex-wrap gap-3 md:gap-4 justify-center items-start max-w-full md:max-w-3xl lg:max-w-4xl">
        {children.map((child) => (
          <PersonCard
            key={child.id}
            person={child}
            relationshipType="Child"
            variant="child"
            onClick={onPersonClick}
            showPhoto={true}
          />
        ))}
      </div>
    </div>
  )
}
