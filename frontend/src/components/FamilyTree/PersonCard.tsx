import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { PersonDetails } from "@/client"
import { User } from "lucide-react"
import { memo } from "react"

export type PersonCardVariant = 'selected' | 'parent' | 'spouse' | 'sibling' | 'child'

export interface PersonCardProps {
  person: PersonDetails
  relationshipType?: string
  variant: PersonCardVariant
  onClick: (personId: string) => void
  showPhoto?: boolean
  colorVariant?: 'parent' | 'sibling' | 'spouse' | 'child' | 'selected'
}

/**
 * Format birth and death years for display
 * @param dateOfBirth - ISO date string for birth date
 * @param dateOfDeath - ISO date string for death date (optional)
 * @returns Formatted string like "1990 -" or "1990 - 2020"
 */
export function formatYearsDisplay(dateOfBirth: string, dateOfDeath?: string | null): string {
  // Extract year directly from the date string to avoid timezone issues
  // Date strings are in format "YYYY-MM-DD"
  const birthYear = parseInt(dateOfBirth.split('-')[0])
  
  if (dateOfDeath) {
    const deathYear = parseInt(dateOfDeath.split('-')[0])
    return `${birthYear} - ${deathYear}`
  }
  
  return `${birthYear} -`
}

/**
 * Get variant-specific styling classes with responsive sizing
 * Requirements: 4.1 - Spouse cards have reduced opacity for visual hierarchy
 */
function getVariantStyles(variant: PersonCardVariant): string {
  const baseStyles = cn(
    "cursor-pointer transition-all duration-200 ease-in-out",
    "hover:shadow-xl hover:scale-[1.02] hover:border-primary/50",
    "touch-manipulation active:scale-95",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
  )
  
  switch (variant) {
    case 'selected':
      return cn(
        baseStyles,
        "border-2 border-green-500 shadow-lg scale-105 bg-card",
        "hover:shadow-2xl hover:border-green-600 hover:bg-card",
        "min-w-[160px] md:min-w-[180px] lg:min-w-[200px]",
        "min-h-[180px] md:min-h-[200px] lg:min-h-[220px]"
      )
    case 'parent':
      return cn(
        baseStyles,
        "border border-border shadow-sm bg-card",
        "hover:bg-accent/50",
        "min-w-[140px] md:min-w-[160px] lg:min-w-[180px]",
        "min-h-[160px] md:min-h-[180px] lg:min-h-[200px]"
      )
    case 'spouse':
      return cn(
        baseStyles,
        "border border-border shadow-sm bg-card opacity-40",
        "hover:bg-accent/50 hover:opacity-60",
        "min-w-[140px] md:min-w-[160px] lg:min-w-[180px]",
        "min-h-[160px] md:min-h-[180px] lg:min-h-[200px]"
      )
    case 'sibling':
      return cn(
        baseStyles,
        "border border-border opacity-75 scale-90 shadow-sm bg-card",
        "hover:opacity-90 hover:bg-accent/30",
        "min-w-[120px] md:min-w-[140px] lg:min-w-[160px]",
        "min-h-[140px] md:min-h-[160px] lg:min-h-[180px]"
      )
    case 'child':
      return cn(
        baseStyles,
        "border border-border scale-95 shadow-sm bg-card",
        "hover:bg-accent/50",
        "min-w-[130px] md:min-w-[150px] lg:min-w-[170px]",
        "min-h-[150px] md:min-h-[170px] lg:min-h-[190px]"
      )
  }
}

/**
 * Get color-coding classes based on relationship type
 * Requirements: 9.2, 9.3, 9.4, 9.10
 * 
 * Color Palette:
 * - Parents: Light amber/orange (bg-amber-100, border-amber-300)
 * - Siblings: Light blue/sky (bg-blue-100, border-blue-300)
 * - Spouses: Light purple/violet (bg-purple-100, border-purple-300)
 * - Children: Light pink/rose (bg-pink-100, border-pink-300)
 * - Selected: Light green with prominent border (bg-green-100, border-green-500)
 */
function getColorVariantClasses(colorVariant?: 'parent' | 'sibling' | 'spouse' | 'child' | 'selected'): string {
  if (!colorVariant || colorVariant === 'selected') {
    return ''
  }
  
  switch (colorVariant) {
    case 'parent':
      return 'bg-amber-100 dark:bg-amber-950/20 border-amber-300 dark:border-amber-800'
    case 'sibling':
      return 'bg-blue-100 dark:bg-blue-950/20 border-blue-300 dark:border-blue-800'
    case 'spouse':
      return 'bg-purple-100 dark:bg-purple-950/20 border-purple-300 dark:border-purple-800'
    case 'child':
      return 'bg-pink-100 dark:bg-pink-950/20 border-pink-300 dark:border-pink-800'
    default:
      return ''
  }
}

/**
 * Get avatar size based on variant with responsive sizing
 */
function getAvatarSize(variant: PersonCardVariant): string {
  switch (variant) {
    case 'selected':
      return "size-16 md:size-18 lg:size-20"
    case 'parent':
    case 'spouse':
      return "size-12 md:size-14 lg:size-16"
    case 'sibling':
      return "size-10 md:size-11 lg:size-12"
    case 'child':
      return "size-11 md:size-12 lg:size-14"
  }
}

/**
 * PersonCard component displays information about a person in the family tree
 * Accessibility: Supports keyboard navigation, ARIA labels, and focus management
 * Performance: Memoized to prevent unnecessary re-renders
 */
export const PersonCard = memo(function PersonCard({
  person,
  relationshipType,
  variant,
  onClick,
  showPhoto = true,
  colorVariant,
}: PersonCardProps) {
  const yearsDisplay = formatYearsDisplay(person.date_of_birth, person.date_of_death)
  const displayName = `${person.first_name} ${person.last_name}`
  const ariaLabel = variant === 'selected' 
    ? `${displayName}, currently selected, born ${yearsDisplay}`
    : `${displayName}, ${relationshipType || 'family member'}, born ${yearsDisplay}. Click to view their family tree.`
  
  const colorClasses = getColorVariantClasses(colorVariant)
  
  return (
    <Card
      className={cn(
        "flex flex-col items-center gap-2 md:gap-3 p-3 md:p-4",
        getVariantStyles(variant),
        colorClasses
      )}
      onClick={() => onClick(person.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          onClick(person.id)
        }
      }}
      aria-label={ariaLabel}
      aria-pressed={variant === 'selected'}
      data-person-id={person.id}
    >
      {showPhoto && (
        <Avatar className={getAvatarSize(variant)} aria-hidden="true">
          <AvatarImage src={undefined} alt="" />
          <AvatarFallback>
            <User className="size-1/2" aria-hidden="true" />
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className="flex flex-col items-center gap-1 text-center">
        <div className={cn(
          "font-semibold leading-tight",
          variant === 'selected' ? "text-lg md:text-xl" : "text-sm md:text-base"
        )}>
          {displayName}
        </div>
        
        <div className={cn(
          "text-muted-foreground font-medium",
          variant === 'selected' ? "text-sm md:text-base" : "text-xs md:text-sm"
        )}>
          {yearsDisplay}
        </div>
        
        {relationshipType && variant !== 'selected' && (
          <div className="text-xs md:text-sm text-muted-foreground/80 italic mt-0.5 font-light">
            {relationshipType}
          </div>
        )}
      </div>
    </Card>
  )
})
