import { Handle, Position } from "@xyflow/react"
import { Eye, User } from "lucide-react"
import { memo } from "react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { PersonNodeData } from "./types"

interface PersonNodeProps {
  data: PersonNodeData
}

/**
 * Format birth and death years for display
 * @param birthYear - Birth year (number or null)
 * @param deathYear - Death year (number or null)
 * @returns Formatted string like "1990 -" or "1990 - 2020"
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
 * PersonNode component for React Flow graph
 * Displays a person card with avatar, name, and birth/death years
 *
 * Requirements:
 * - 7.1: Display circular avatar with User icon placeholder
 * - 7.2: Display first name + last name
 * - 7.3: Display birth year - death year
 * - 7.4: Green border for Person A (start)
 * - 7.5: Blue border for Person B (end)
 * - 7.6: Similar styling to FamilyTree PersonCard
 * - 7.7: No View or Explore buttons (simplified display)
 */
export const PersonNode = memo(function PersonNode({ data }: PersonNodeProps) {
  const { firstName, lastName, birthYear, deathYear, isPersonA, isPersonB, personId, onViewClick } =
    data

  const displayName = `${firstName} ${lastName}`
  const yearsDisplay = formatBirthDeathYears(birthYear, deathYear)

  // Handler for View button click - stops propagation to prevent parent handlers
  const handleViewClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation()
    if (onViewClick) {
      onViewClick(personId)
    }
  }

  // Handler for keyboard accessibility - Enter and Space keys
  const handleViewKeyDown = (e: React.KeyboardEvent<HTMLButtonElement>) => {
    if (e.key === "Enter" || e.key === " ") {
      e.stopPropagation()
    }
  }

  // Determine border color based on person type
  const getBorderClass = () => {
    if (isPersonA) {
      return "border-2 border-green-500 shadow-lg"
    }
    if (isPersonB) {
      return "border-2 border-blue-500 shadow-lg"
    }
    return "border border-border shadow-sm"
  }

  return (
    <>
      {/* Connection handles for edges */}
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

        {/* Visual indicator for Person A/B */}
        {(isPersonA || isPersonB) && (
          <div
            className={cn(
              "text-xs font-medium px-2 py-0.5 rounded-full",
              isPersonA &&
                "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
              isPersonB &&
                "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
            )}
          >
            {isPersonA ? "Person A" : "Person B"}
          </div>
        )}

        {/* View button - only rendered when onViewClick callback is provided */}
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
