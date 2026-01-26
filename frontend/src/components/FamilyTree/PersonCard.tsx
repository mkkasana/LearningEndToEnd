import { Eye, User } from "lucide-react"
import { memo } from "react"
import type { PersonDetails } from "@/client"
import { AssumeRoleButton } from "@/components/Family/AssumeRoleButton"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

// Known gender IDs from the system
const MALE_GENDER_ID = "4eb743f7-0a50-4da2-a20d-3473b3b3db83"
const FEMALE_GENDER_ID = "691fde27-f82c-4a84-832f-4243acef4b95"

export type PersonCardVariant =
  | "selected"
  | "parent"
  | "spouse"
  | "sibling"
  | "child"

export interface PersonCardProps {
  person: PersonDetails
  relationshipType?: string
  variant: PersonCardVariant
  onClick: (personId: string) => void
  onViewClick?: (personId: string) => void
  showPhoto?: boolean
  colorVariant?: "parent" | "sibling" | "spouse" | "child" | "selected"
}

/**
 * Format birth and death years for display
 * @param dateOfBirth - ISO date string for birth date
 * @param dateOfDeath - ISO date string for death date (optional)
 * @returns Formatted string like "1990 -" or "1990 - 2020"
 */
export function formatYearsDisplay(
  dateOfBirth: string,
  dateOfDeath?: string | null,
): string {
  // Extract year directly from the date string to avoid timezone issues
  // Date strings are in format "YYYY-MM-DD"
  const birthYear = parseInt(dateOfBirth.split("-")[0], 10)

  if (dateOfDeath) {
    const deathYear = parseInt(dateOfDeath.split("-")[0], 10)
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
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
  )

  switch (variant) {
    case "selected":
      return cn(
        baseStyles,
        "border-2 border-green-500 shadow-lg scale-105 bg-card",
        "hover:shadow-2xl hover:border-green-600 hover:bg-card",
        "w-[160px] md:w-[180px] lg:w-[200px]",
        "min-h-[180px] md:min-h-[200px] lg:min-h-[220px]",
      )
    case "parent":
      return cn(
        baseStyles,
        "border border-border shadow-sm bg-card",
        "hover:bg-accent/50",
        "w-[140px] md:w-[160px] lg:w-[180px]",
        "min-h-[160px] md:min-h-[180px] lg:min-h-[200px]",
      )
    case "spouse":
      return cn(
        baseStyles,
        "border border-border shadow-sm bg-card opacity-40",
        "hover:bg-accent/50 hover:opacity-60",
        "w-[140px] md:w-[160px] lg:w-[180px]",
        "min-h-[160px] md:min-h-[180px] lg:min-h-[200px]",
      )
    case "sibling":
      return cn(
        baseStyles,
        "border border-border opacity-75 scale-90 shadow-sm bg-card",
        "hover:opacity-90 hover:bg-accent/30",
        "w-[120px] md:w-[140px] lg:w-[160px]",
        "min-h-[140px] md:min-h-[160px] lg:min-h-[180px]",
      )
    case "child":
      return cn(
        baseStyles,
        "border border-border scale-95 shadow-sm bg-card",
        "hover:bg-accent/50",
        "w-[130px] md:w-[150px] lg:w-[170px]",
        "min-h-[150px] md:min-h-[170px] lg:min-h-[190px]",
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
function getColorVariantClasses(
  colorVariant?: "parent" | "sibling" | "spouse" | "child" | "selected",
): string {
  if (!colorVariant || colorVariant === "selected") {
    return ""
  }

  switch (colorVariant) {
    case "parent":
      return "bg-amber-100 dark:bg-amber-950/20 border-amber-300 dark:border-amber-800"
    case "sibling":
      return "bg-blue-100 dark:bg-blue-950/20 border-blue-300 dark:border-blue-800"
    case "spouse":
      return "bg-purple-100 dark:bg-purple-950/20 border-purple-300 dark:border-purple-800"
    case "child":
      return "bg-pink-100 dark:bg-pink-950/20 border-pink-300 dark:border-pink-800"
    default:
      return ""
  }
}

/**
 * Get avatar size based on variant with responsive sizing
 */
function getAvatarSize(variant: PersonCardVariant): string {
  switch (variant) {
    case "selected":
      return "size-16 md:size-18 lg:size-20"
    case "parent":
    case "spouse":
      return "size-12 md:size-14 lg:size-16"
    case "sibling":
      return "size-10 md:size-11 lg:size-12"
    case "child":
      return "size-11 md:size-12 lg:size-14"
  }
}

/**
 * Get View button size based on variant
 * Requirements: 1.1, 1.2 - View button styled appropriately for each variant
 */
function getViewButtonSize(variant: PersonCardVariant): "sm" | "default" {
  switch (variant) {
    case "selected":
      return "default"
    case "sibling":
      return "sm"
    default:
      return "sm"
  }
}

/**
 * Get avatar background color based on gender
 * Male: blue tones, Female: pink tones, Unknown: gray
 */
function getGenderAvatarClass(genderId: string): string {
  if (genderId === MALE_GENDER_ID) {
    return "bg-blue-100 dark:bg-blue-950/30 text-blue-600 dark:text-blue-400"
  }
  if (genderId === FEMALE_GENDER_ID) {
    return "bg-pink-100 dark:bg-pink-950/30 text-pink-600 dark:text-pink-400"
  }
  return "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
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
  onViewClick,
  showPhoto = true,
  colorVariant,
}: PersonCardProps) {
  const yearsDisplay = formatYearsDisplay(
    person.date_of_birth,
    person.date_of_death,
  )
  const displayName = `${person.first_name} ${person.last_name}`
  const ariaLabel =
    variant === "selected"
      ? `${displayName}, currently selected, born ${yearsDisplay}`
      : `${displayName}, ${relationshipType || "family member"}, born ${yearsDisplay}. Click to view their family tree.`

  const colorClasses = getColorVariantClasses(colorVariant)

  /**
   * Handle View button click
   * Requirements: 1.4 - Stop event propagation to prevent card navigation
   */
  const handleViewClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    if (onViewClick) {
      onViewClick(person.id)
    }
  }

  /**
   * Handle View button keyboard events
   * Requirements: 1.3 - Keyboard accessibility
   */
  const handleViewKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.stopPropagation()
    }
  }

  return (
    <Card
      className={cn(
        "flex flex-col items-center gap-2 md:gap-3 p-3 md:p-4",
        getVariantStyles(variant),
        colorClasses,
      )}
      onClick={() => onClick(person.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onClick(person.id)
        }
      }}
      aria-label={ariaLabel}
      aria-pressed={variant === "selected"}
    >
      {showPhoto && (
        <Avatar
          className={cn(getAvatarSize(variant), getGenderAvatarClass(person.gender_id))}
          aria-hidden="true"
        >
          <AvatarImage src={undefined} alt="" />
          <AvatarFallback className={getGenderAvatarClass(person.gender_id)}>
            <User className="size-1/2" aria-hidden="true" />
          </AvatarFallback>
        </Avatar>
      )}

      <div className="flex flex-col items-center gap-1 text-center w-full px-1">
        <div
          className={cn(
            "font-semibold leading-tight truncate w-full",
            variant === "selected"
              ? "text-lg md:text-xl"
              : "text-sm md:text-base",
          )}
          title={displayName}
        >
          {displayName}
        </div>

        <div
          className={cn(
            "text-muted-foreground font-medium",
            variant === "selected"
              ? "text-sm md:text-base"
              : "text-xs md:text-sm",
          )}
        >
          {yearsDisplay}
        </div>

        {relationshipType && variant !== "selected" && (
          <div className="text-xs md:text-sm text-muted-foreground/80 italic mt-0.5 font-light">
            {relationshipType}
          </div>
        )}
      </div>

      {/* View Button - Requirements: 1.1, 1.2, 1.3, 1.4 */}
      {onViewClick && (
        <Button
          variant="outline"
          size={getViewButtonSize(variant)}
          className={cn(
            "mt-1",
            variant === "sibling" && "text-xs px-2 py-1 h-7",
          )}
          onClick={handleViewClick}
          onKeyDown={handleViewKeyDown}
          aria-label={`View details for ${displayName}`}
        >
          <Eye className={cn(variant === "sibling" ? "h-3 w-3" : "h-4 w-4")} />
          <span className={cn(variant === "sibling" && "text-xs")}>View</span>
        </Button>
      )}

      {/* Assume Role Button - Requirements: 6.1, 6.2 (assume-person-role) */}
      {/* Only shows for elevated users who created this person */}
      <AssumeRoleButton
        personId={person.id}
        personName={displayName}
        createdByUserId={person.created_by_user_id}
        size={variant === "sibling" ? "sm" : "sm"}
        className={cn("mt-1", variant === "sibling" && "text-xs px-2 py-1 h-7")}
      />
    </Card>
  )
})
