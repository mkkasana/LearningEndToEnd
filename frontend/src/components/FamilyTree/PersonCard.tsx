import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { PersonDetails } from "@/client"
import { User } from "lucide-react"

export type PersonCardVariant = 'selected' | 'parent' | 'spouse' | 'sibling' | 'child'

export interface PersonCardProps {
  person: PersonDetails
  relationshipType?: string
  variant: PersonCardVariant
  onClick: (personId: string) => void
  showPhoto?: boolean
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
 * Get variant-specific styling classes
 */
function getVariantStyles(variant: PersonCardVariant): string {
  const baseStyles = "cursor-pointer transition-all hover:shadow-lg"
  
  switch (variant) {
    case 'selected':
      return cn(
        baseStyles,
        "border-2 border-primary shadow-md scale-105",
        "min-w-[200px]"
      )
    case 'parent':
      return cn(
        baseStyles,
        "border border-border",
        "min-w-[180px]"
      )
    case 'spouse':
      return cn(
        baseStyles,
        "border border-border",
        "min-w-[180px]"
      )
    case 'sibling':
      return cn(
        baseStyles,
        "border border-border opacity-75 scale-90",
        "min-w-[160px]"
      )
    case 'child':
      return cn(
        baseStyles,
        "border border-border scale-95",
        "min-w-[170px]"
      )
  }
}

/**
 * Get avatar size based on variant
 */
function getAvatarSize(variant: PersonCardVariant): string {
  switch (variant) {
    case 'selected':
      return "size-20"
    case 'parent':
    case 'spouse':
      return "size-16"
    case 'sibling':
      return "size-12"
    case 'child':
      return "size-14"
  }
}

/**
 * PersonCard component displays information about a person in the family tree
 */
export function PersonCard({
  person,
  relationshipType,
  variant,
  onClick,
  showPhoto = true,
}: PersonCardProps) {
  const yearsDisplay = formatYearsDisplay(person.date_of_birth, person.date_of_death)
  const displayName = `${person.first_name} ${person.last_name}`
  
  return (
    <Card
      className={cn(
        "flex flex-col items-center gap-3 p-4",
        getVariantStyles(variant)
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
      aria-label={`${displayName}, ${relationshipType || 'selected person'}`}
    >
      {showPhoto && (
        <Avatar className={getAvatarSize(variant)}>
          <AvatarImage src={undefined} alt={displayName} />
          <AvatarFallback>
            <User className="size-1/2" />
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className="flex flex-col items-center gap-1 text-center">
        <div className={cn(
          "font-semibold",
          variant === 'selected' ? "text-lg" : "text-sm"
        )}>
          {displayName}
        </div>
        
        <div className={cn(
          "text-muted-foreground",
          variant === 'selected' ? "text-sm" : "text-xs"
        )}>
          {yearsDisplay}
        </div>
        
        {relationshipType && variant !== 'selected' && (
          <div className="text-xs text-muted-foreground italic mt-1">
            {relationshipType}
          </div>
        )}
      </div>
    </Card>
  )
}
