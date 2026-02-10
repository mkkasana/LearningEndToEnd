/**
 * MatchCard - Card component for displaying potential duplicate person matches
 * during the profile completion duplicate check step.
 *
 * Requirements: 10.3, 10.4, 10.5
 * - Display person name, DOB, address, religion
 * - Display match score with color coding
 * - Add "This is me" button
 * - Handle click to select match
 */

import { Calendar, Church, MapPin, User, UserCircle } from "lucide-react"
import { memo } from "react"
import type { PersonMatchResult } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export interface MatchCardProps {
  /** The person match result to display */
  match: PersonMatchResult
  /** Callback when user clicks "This is me" button */
  onSelect: () => void
  /** Whether the card is in a loading/disabled state */
  isLoading?: boolean
}

/**
 * Format full name from first, middle, and last name
 */
function formatFullName(
  firstName: string,
  middleName: string | null | undefined,
  lastName: string
): string {
  if (middleName) {
    return `${firstName} ${middleName} ${lastName}`
  }
  return `${firstName} ${lastName}`
}

/**
 * Format date for display (e.g., "Jan 15, 1990")
 * Uses UTC to avoid timezone conversion issues
 */
function formatDate(dateString: string): string {
  const date = new Date(dateString + "T00:00:00")
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

/**
 * Get badge styling based on match score
 * - High (>= 80%): Green
 * - Medium (>= 60%): Yellow/Amber
 * - Low (< 60%): Gray/Default
 */
function getScoreBadgeClass(score: number): string {
  if (score >= 80) {
    return "bg-green-100 text-green-700 border-green-200 dark:bg-green-950/30 dark:text-green-400 dark:border-green-800"
  }
  if (score >= 60) {
    return "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-950/30 dark:text-amber-400 dark:border-amber-800"
  }
  return "bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-700"
}

/**
 * MatchCard component displays a potential duplicate person match
 * with their details and a "This is me" button.
 *
 * Accessibility: Supports keyboard navigation and ARIA labels
 * Performance: Memoized to prevent unnecessary re-renders
 */
export const MatchCard = memo(function MatchCard({
  match,
  onSelect,
  isLoading = false,
}: MatchCardProps) {
  const fullName = formatFullName(
    match.first_name,
    match.middle_name,
    match.last_name
  )

  const handleSelectClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    if (!isLoading) {
      onSelect()
    }
  }

  const handleCardClick = () => {
    if (!isLoading) {
      onSelect()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.key === "Enter" || e.key === " ") && !isLoading) {
      e.preventDefault()
      onSelect()
    }
  }

  return (
    <Card
      className={cn(
        "hover:shadow-md transition-all cursor-pointer",
        "hover:border-primary/50",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
        isLoading && "opacity-50 cursor-not-allowed"
      )}
      onClick={handleCardClick}
      role="button"
      tabIndex={isLoading ? -1 : 0}
      onKeyDown={handleKeyDown}
      aria-label={`${fullName}, born ${formatDate(match.date_of_birth)}. ${Math.round(match.match_score)}% match. Click to select this person.`}
      aria-disabled={isLoading}
    >
      <CardContent className="pt-6">
        {/* Header: Name */}
        <div className="flex items-center gap-2 mb-2">
          <User className="h-4 w-4 text-primary flex-shrink-0" />
          <h4 className="font-semibold text-base truncate" title={fullName}>
            {fullName}
          </h4>
        </div>

        {/* Match Score Badge */}
        <div className="mb-3">
          <Badge
            className={cn(getScoreBadgeClass(match.match_score))}
          >
            {Math.round(match.match_score)}% match
          </Badge>
        </div>

        {/* Date of Birth */}
        <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
          <Calendar className="h-4 w-4 flex-shrink-0" />
          <span>Born {formatDate(match.date_of_birth)}</span>
          {match.date_of_death && (
            <span className="text-muted-foreground">
              • Died {formatDate(match.date_of_death)}
            </span>
          )}
        </div>

        {/* Gender */}
        {match.gender && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <UserCircle className="h-4 w-4 flex-shrink-0" />
            <span>{match.gender}</span>
          </div>
        )}

        {/* Address */}
        <div className="flex items-start gap-2 text-sm text-muted-foreground mb-2">
          <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
          <span className="line-clamp-2">{match.address_display || "No address"}</span>
        </div>

        {/* Religion */}
        {match.religion_display && (
          <div className="flex items-start gap-2 text-sm text-muted-foreground mb-4">
            <Church className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <span className="line-clamp-1">{match.religion_display}</span>
          </div>
        )}

        {/* This is me button */}
        <Button
          className="w-full"
          onClick={handleSelectClick}
          disabled={isLoading}
          aria-label={`Select ${fullName} as my existing record`}
        >
          This is me
        </Button>
      </CardContent>
    </Card>
  )
})
