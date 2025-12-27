import { SiblingsList } from "./SiblingsList"
import type { PersonDetails } from "@/client"

export interface SiblingsSectionProps {
  siblings: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * SiblingsSection component displays sibling cards near the selected person
 * with de-emphasized styling (smaller, reduced opacity)
 * Uses SiblingsList for horizontal scrolling when there are many siblings
 */
export function SiblingsSection({ siblings, onPersonClick }: SiblingsSectionProps) {
  if (siblings.length === 0) {
    return null
  }

  // Use SiblingsList for horizontal scrolling
  return (
    <div className="flex flex-col items-center gap-2">
      <SiblingsList siblings={siblings} onPersonClick={onPersonClick} />
    </div>
  )
}
