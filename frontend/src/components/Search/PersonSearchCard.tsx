import { Compass, User } from "lucide-react"
import { memo } from "react"
import type { PersonSearchResult } from "@/client"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export interface PersonSearchCardProps {
  person: PersonSearchResult
  onExplore: (personId: string) => void
}

/**
 * Format full name from first, middle, and last name
 * @param firstName - First name
 * @param middleName - Middle name (optional)
 * @param lastName - Last name
 * @returns Full name string
 */
export function formatFullName(
  firstName: string,
  middleName: string | null | undefined,
  lastName: string,
): string {
  if (middleName) {
    return `${firstName} ${middleName} ${lastName}`
  }
  return `${firstName} ${lastName}`
}

/**
 * Extract birth year from date string
 * @param dateOfBirth - ISO date string (YYYY-MM-DD)
 * @returns Birth year as number
 */
export function extractBirthYear(dateOfBirth: string): number {
  return parseInt(dateOfBirth.split("-")[0], 10)
}

/**
 * PersonSearchCard component displays a person's summary in search results
 * Requirements: 9.2 - Display full name, birth year, and Explore button
 * 
 * Accessibility: Supports keyboard navigation and ARIA labels
 * Performance: Memoized to prevent unnecessary re-renders
 */
export const PersonSearchCard = memo(function PersonSearchCard({
  person,
  onExplore,
}: PersonSearchCardProps) {
  const fullName = formatFullName(
    person.first_name,
    person.middle_name,
    person.last_name,
  )
  const birthYear = extractBirthYear(person.date_of_birth)

  const handleExploreClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    onExplore(person.person_id)
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.stopPropagation()
    }
  }

  return (
    <Card
      className={cn(
        "flex flex-col items-center gap-3 p-4",
        "cursor-pointer transition-all duration-200 ease-in-out",
        "hover:shadow-lg hover:scale-[1.02] hover:border-primary/50",
        "touch-manipulation active:scale-95",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
        "w-full min-h-[160px]",
      )}
      onClick={() => onExplore(person.person_id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onExplore(person.person_id)
        }
      }}
      aria-label={`${fullName}, born ${birthYear}. Click to explore their family tree.`}
    >
      <Avatar className="size-14" aria-hidden="true">
        <AvatarImage src={undefined} alt="" />
        <AvatarFallback>
          <User className="size-1/2" aria-hidden="true" />
        </AvatarFallback>
      </Avatar>

      <div className="flex flex-col items-center gap-1 text-center w-full px-1">
        <div
          className="font-semibold leading-tight truncate w-full text-base"
          title={fullName}
        >
          {fullName}
        </div>

        <div className="text-sm text-muted-foreground font-medium">
          Born {birthYear}
        </div>
      </div>

      <Button
        variant="outline"
        size="sm"
        className="mt-auto"
        onClick={handleExploreClick}
        onKeyDown={handleKeyDown}
        aria-label={`Explore family tree for ${fullName}`}
      >
        <Compass className="h-4 w-4" />
        <span>Explore</span>
      </Button>
    </Card>
  )
})
