import { PersonCard } from "./PersonCard"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import type { PersonDetails } from "@/client"

export interface SiblingsListProps {
  siblings: PersonDetails[]
  onPersonClick: (personId: string) => void
}

/**
 * SiblingsList component displays siblings in a horizontally scrollable container
 * with scroll indicators if overflow occurs
 */
export function SiblingsList({ siblings, onPersonClick }: SiblingsListProps) {
  if (siblings.length === 0) {
    return null
  }

  return (
    <div className="w-full max-w-xs md:max-w-md lg:max-w-2xl">
      <ScrollArea className="w-full whitespace-nowrap">
        <div className="flex gap-2 md:gap-3 p-1 md:p-2">
          {siblings.map((sibling) => (
            <div key={sibling.id} className="inline-block">
              <PersonCard
                person={sibling}
                relationshipType="Sibling"
                variant="sibling"
                onClick={onPersonClick}
                showPhoto={true}
              />
            </div>
          ))}
        </div>
        <ScrollBar orientation="horizontal" />
      </ScrollArea>
    </div>
  )
}
