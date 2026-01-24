/**
 * MatchPersonNode Component
 * Custom React Flow node for displaying persons in the match path graph
 *
 * Requirements:
 * - 6.1: Display circular avatar placeholder with User icon
 * - 6.2: Display first name + last name below the avatar
 * - 6.3: Display birth year - death year (format: "1990 -" or "1990 - 2020")
 * - 6.4: Apply green border + "Seeker" label for seeker
 * - 6.5: Apply blue border + "Match" label for match
 * - 6.6: Add React Flow handles (top, bottom, left, right)
 */

import { Handle, Position } from "@xyflow/react"
import { Eye, User } from "lucide-react"
import { memo } from "react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { MatchPersonNodeData } from "./types"

interface MatchPersonNodeProps {
  data: MatchPersonNodeData
}

/**
 * Format birth and death years for display
 * @param birthYear - Birth year (number or null)
 * @param deathYear - Death year (number or null)
 * @returns Formatted string like "1990 -" or "1990 - 2020" or empty string
 */
export function formatBirthDeathYears(
  birthYear: number | null,
  deathYear: number | null,
): string {
  if (birthYear === null) {
    return ""
  }

  if (deathYear !== null) {
    return `${birthYear} - ${deathYear}`
  }

  return `${birthYear} -`
}

/**
 * MatchPersonNode component for React Flow graph
 * Displays a person card with avatar, name, birth/death years, and seeker/match labels
 */
export const MatchPersonNode = memo(function MatchPersonNode({
  data,
}: MatchPersonNodeProps) {
  const {
    personId,
    firstName,
    lastName,
    birthYear,
    deathYear,
    isSeeker,
    isMatch,
    onViewClick,
  } = data

  const displayName = `${firstName} ${lastName}`
  const yearsDisplay = formatBirthDeathYears(birthYear, deathYear)

  // Determine border color based on person type
  const getBorderClass = () => {
    if (isSeeker) {
      return "border-2 border-green-500 shadow-lg"
    }
    if (isMatch) {
      return "border-2 border-blue-500 shadow-lg"
    }
    return "border border-border shadow-sm"
  }

  /**
   * Handle View button click
   * Requirements: 1.2, 1.3 - Stop event propagation and call callback
   */
  const handleViewClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    if (onViewClick) {
      onViewClick(personId)
    }
  }

  /**
   * Handle View button keyboard events
   * Requirements: 1.4 - Keyboard accessibility for Enter and Space keys
   */
  const handleViewKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.stopPropagation()
    }
  }

  return (
    <>
      {/* Connection handles for edges - top, bottom, left, right */}
      <Handle
        type="target"
        position={Position.Top}
        id="top"
        className="!bg-muted-foreground !w-2 !h-2"
      />
      <Handle
        type="source"
        position={Position.Top}
        id="top"
        className="!bg-muted-foreground !w-2 !h-2"
      />
      <Handle
        type="target"
        position={Position.Bottom}
        id="bottom"
        className="!bg-muted-foreground !w-2 !h-2"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
        className="!bg-muted-foreground !w-2 !h-2"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        className="!bg-muted-foreground !w-2 !h-2"
      />
      <Handle
        type="source"
        position={Position.Left}
        id="left"
        className="!bg-muted-foreground !w-2 !h-2"
      />
      <Handle
        type="target"
        position={Position.Right}
        id="right"
        className="!bg-muted-foreground !w-2 !h-2"
      />
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        className="!bg-muted-foreground !w-2 !h-2"
      />

      <Card
        className={cn(
          "flex flex-col items-center gap-2 p-4 bg-card",
          "w-[160px] min-h-[140px]",
          "transition-all duration-200",
          getBorderClass(),
        )}
      >
        {/* Avatar with User icon */}
        <Avatar className="size-14" aria-hidden="true">
          <AvatarFallback className="bg-muted">
            <User className="size-7 text-muted-foreground" aria-hidden="true" />
          </AvatarFallback>
        </Avatar>

        {/* Name and years */}
        <div className="flex flex-col items-center gap-1 text-center w-full">
          <div
            className="font-semibold text-sm leading-tight truncate w-full"
            title={displayName}
          >
            {displayName}
          </div>

          {yearsDisplay && (
            <div className="text-xs text-muted-foreground font-medium">
              {yearsDisplay}
            </div>
          )}
        </div>

        {/* Visual indicator for Seeker/Match */}
        {(isSeeker || isMatch) && (
          <div
            className={cn(
              "text-xs font-medium px-2 py-0.5 rounded-full",
              isSeeker &&
                "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
              isMatch &&
                "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
            )}
          >
            {isSeeker ? "Seeker" : "Match"}
          </div>
        )}

        {/* View Button - Requirements: 1.1, 1.5, 4.1, 4.2, 4.3, 4.4 */}
        {onViewClick && (
          <Button
            variant="outline"
            size="sm"
            className="mt-1 nodrag nopan pointer-events-auto cursor-pointer"
            onClick={handleViewClick}
            onKeyDown={handleViewKeyDown}
            aria-label={`View details for ${firstName} ${lastName}`}
          >
            <Eye className="h-4 w-4" />
            <span>View</span>
          </Button>
        )}
      </Card>
    </>
  )
})
