import { memo, useEffect, useRef } from "react"
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
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const selectedPersonRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to center the selected person when it changes or on initial render
  // Requirements: 9.8, 9.9
  useEffect(() => {
    if (variant === 'center' && selectedPersonId && selectedPersonRef.current && scrollContainerRef.current) {
      // Check if scrollIntoView is available (may not be in test environment)
      if (typeof selectedPersonRef.current.scrollIntoView === 'function') {
        // Use scrollIntoView with smooth behavior and center alignment
        selectedPersonRef.current.scrollIntoView({
          behavior: 'smooth',
          block: 'nearest',
          inline: 'center'
        })
      }
    }
  }, [selectedPersonId, variant])

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

  // Get background color for color-coding
  // Requirements: 9.2, 9.3, 9.4
  const getColorVariant = (personId: string): 'parent' | 'sibling' | 'spouse' | 'child' | 'selected' | undefined => {
    if (personId === selectedPersonId) {
      return 'selected'
    }
    
    if (variant === 'parent') {
      return 'parent'
    }
    
    if (variant === 'child') {
      return 'child'
    }
    
    // For center row, use color coding
    if (variant === 'center' && colorCoding) {
      return colorCoding.get(personId)
    }
    
    return undefined
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
      <ScrollArea 
        className="w-full whitespace-nowrap rounded-lg border border-border/50 bg-muted/10 p-2 md:p-3 lg:p-4"
        ref={scrollContainerRef}
      >
        <div className="flex gap-3 md:gap-4 lg:gap-6 p-1 md:p-2 items-center justify-start">
          {people.map((person) => {
            const cardVariant = getCardVariant(person.id)
            const relationshipType = getRelationshipType(person.id)
            const colorVariant = getColorVariant(person.id)
            const isSelected = person.id === selectedPersonId
            
            return (
              <div 
                key={person.id} 
                ref={isSelected ? selectedPersonRef : null}
                className="inline-block flex-shrink-0"
              >
                <PersonCard
                  person={person}
                  relationshipType={relationshipType}
                  variant={cardVariant}
                  onClick={onPersonClick}
                  showPhoto={true}
                  colorVariant={colorVariant}
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
