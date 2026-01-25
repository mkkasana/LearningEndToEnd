/**
 * RelativeCard Component
 * Displays individual relative information in a card format
 * Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7
 */

import { Eye, User } from "lucide-react"
import { memo } from "react"

import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

// Known gender IDs from the system
const MALE_GENDER_ID = "4eb743f7-0a50-4da2-a20d-3473b3b3db83"
const FEMALE_GENDER_ID = "691fde27-f82c-4a84-832f-4243acef4b95"

export interface RelativeCardProps {
  personId: string
  firstName: string
  lastName: string
  genderId: string
  birthYear: number | null
  deathYear: number | null
  districtName: string | null
  localityName: string | null
  depth: number
  onView: (personId: string) => void
}

/**
 * Format birth and death years for display
 * Requirements: 4.3, 4.4
 * @returns "YYYY - YYYY" for deceased, "YYYY" for living
 */
function formatYearsDisplay(
  birthYear: number | null,
  deathYear: number | null,
): string {
  if (!birthYear) {
    return "Unknown"
  }

  if (deathYear) {
    return `${birthYear} - ${deathYear}`
  }

  return `${birthYear}`
}

/**
 * Format location display
 * Requirements: 4.5
 * @returns "District, Locality" or just one if other is missing
 */
function formatLocationDisplay(
  districtName: string | null,
  localityName: string | null,
): string {
  if (districtName && localityName) {
    return `${districtName}, ${localityName}`
  }
  if (districtName) {
    return districtName
  }
  if (localityName) {
    return localityName
  }
  return ""
}

/**
 * Get avatar background color based on gender
 * Requirements: 4.1
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
 * RelativeCard component displays information about a relative
 * Requirements: 4.1-4.7
 */
export const RelativeCard = memo(function RelativeCard({
  personId,
  firstName,
  lastName,
  genderId,
  birthYear,
  deathYear,
  districtName,
  localityName,
  depth,
  onView,
}: RelativeCardProps) {
  const displayName = `${firstName} ${lastName}`
  const yearsDisplay = formatYearsDisplay(birthYear, deathYear)
  const locationDisplay = formatLocationDisplay(districtName, localityName)
  const isDeceased = deathYear !== null

  const handleViewClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    onView(personId)
  }

  return (
    <Card
      className={cn(
        "relative flex flex-col items-center gap-2 p-4",
        "w-full min-h-[180px]",
        "border border-border shadow-sm bg-card",
        "transition-all duration-200 ease-in-out",
        "hover:shadow-lg hover:border-primary/30",
        isDeceased && "opacity-75",
      )}
    >
      {/* Depth Badge - Requirements: 4.6 */}
      <Badge
        variant="secondary"
        className="absolute top-2 right-2 text-xs font-medium"
      >
        {depth}
      </Badge>

      {/* Gender-based Avatar - Requirements: 4.1 */}
      <Avatar className={cn("size-14", getGenderAvatarClass(genderId))}>
        <AvatarFallback className={getGenderAvatarClass(genderId)}>
          <User className="size-7" aria-hidden="true" />
        </AvatarFallback>
      </Avatar>

      {/* Name Display - Requirements: 4.2 */}
      <div
        className="font-semibold text-sm text-center leading-tight truncate w-full px-2"
        title={displayName}
      >
        {displayName}
      </div>

      {/* Years Display - Requirements: 4.3, 4.4 */}
      <div className="text-xs text-muted-foreground font-medium">
        {yearsDisplay}
      </div>

      {/* Location Display - Requirements: 4.5 */}
      {locationDisplay && (
        <div
          className="text-xs text-muted-foreground/80 text-center truncate w-full px-2"
          title={locationDisplay}
        >
          {locationDisplay}
        </div>
      )}

      {/* View Button - Requirements: 4.7 */}
      <Button
        variant="outline"
        size="sm"
        className="mt-auto"
        onClick={handleViewClick}
        aria-label={`View details for ${displayName}`}
      >
        <Eye className="h-4 w-4" />
        <span>View</span>
      </Button>
    </Card>
  )
})
