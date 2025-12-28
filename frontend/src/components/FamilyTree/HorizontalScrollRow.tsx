import { memo } from "react"
import { PersonCard } from "./PersonCard"
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area"
import type { PersonDetails } from "@/client"
import { cn } from "@/lib/utils"

export interface HorizontalScrollRowProps {
  people: PersonDetails[]
  selectedPersonId?: string
  onPersonClick: (personId: string) => void
  variant: 'parent' | 'center' | 'child'
  colorCoding?: Map<string, 'sibling' | 'spouse'>
}

/**
 * HorizontalScrollRow component displays people in a horizontally scrollable row
 * Unified component for parents, center (siblings+selected+spouses), and children rows
 * 
 * Features:
 * - Horizontal scrolling with smooth touch support
 * - Color-coding for center row (siblings vs spouses)
 * - Responsive card sizing
 * - Scroll indicators
 * - Works consistently across all screen sizes
 * 
 * Requirements: 9.1, 9.2, 9.3, 9.4, 9.5
 */
export const HorizontalScrollRow = memo(function HorizontalScrollRow({
  people,
  selectedPersonId,
  onPersonClick,
  variant,
  colorCoding,
}: HorizontalScrollRowProps) {
  if (people.length === 0 && !selectedPersonId) {
    return null
  }

  // Determine card variant based on row variant and whether it's the selected person
  const getCardVariant = (personId: string): 'selected' | 'parent' | 'spouse' | 'sibling' | 'child' => {
    if (personId === selectedPersonId) {
      return 'selected'
    }
    
    if (variant === 'parent') {
      return 'parent'
    }
    
    if (variant === 'child') {
      return 'child'
    }
    
    // For center row, use color coding to determine variant
    if (variant === 'center' && colorCoding) {
      const type = colorCoding.get(personId)
      return type === 'sibling' ? 'sibling' : 'spouse'
    }
    
    return 'spouse' // Default for center row
  }

  // Get relationship type label
  const getRelationshipType = (personId: string): string | undefined => {
    if (personId === selectedPersonId) {
      return undefined
    }
    
    if (variant === 'parent') {
      return 'Parent'
    }
    
    if (variant === 'child') {
      return 'Child'
    }
    
    // For center row, use color coding
    if (variant === 'center' && colorCoding) {
      const type = colorCoding.get(personId)
      return type === 'sibling' ? 'Sibling' : 'Spouse'
    }
    
    return 'Spouse'
  }

  // Get background color for color-coding in center row
  const getCardBackgroundClass = (personId: string): string => {
    if (variant !== 'center' || !colorCoding || personId === selectedPersonId) {
      return ''
    }
    
    const type = colorCoding.get(personId)
    if (type === 'sibling') {
      return 'bg-blue-50/50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800'
    }
    if (type === 'spouse') {
      return 'bg-pink-50/50 dark:bg-pink-950/20 border-pink-200 dark:border-pink-800'
    }
    
    return ''
  }

  // Container styling based on variant
  const containerClass = cn(
    "w-full",
    variant === 'parent' && "mb-4 md:mb-6 lg:mb-8",
    variant === 'center' && "my-2 md:my-4",
    variant === 'child' && "mt-4 md:mt-6 lg:mt-8"
  )

  const ariaLabel = variant === 'parent' 
    ? 'Parents row' 
    : variant === 'child' 
    ? 'Children row' 
    : 'Center row with siblings and spouses'

  return (
    <div 
      className={containerClass}
      role="region"
      aria-label={ariaLabel}
    >
      <ScrollArea className="w-full whitespace-nowrap rounded-lg border border-border/50 bg-muted/10 p-2 md:p-3 lg:p-4">
        <div className="flex gap-3 md:gap-4 lg:gap-6 p-1 md:p-2 items-center justify-start">
          {people.map((person) => {
            const cardVariant = getCardVariant(person.id)
            const relationshipType = getRelationshipType(person.id)
            const backgroundClass = getCardBackgroundClass(person.id)
            
            return (
              <div 
                key={person.id} 
                className={cn(
                  "inline-block flex-shrink-0",
                  backgroundClass && "rounded-lg p-2",
                  backgroundClass
                )}
              >
                <PersonCard
                  person={person}
                  relationshipType={relationshipType}
                  variant={cardVariant}
                  onClick={onPersonClick}
                  showPhoto={true}
                />
              </div>
            )
          })}
        </div>
        <ScrollBar 
          orientation="horizontal" 
          className="h-2 touch-manipulation"
        />
      </ScrollArea>
    </div>
  )
})
