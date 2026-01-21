import { UserPlus, X } from "lucide-react"
import { memo } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"
import type { RishtePersonButtonProps, SelectedPerson } from "./types"

/**
 * Format the display name for a selected person
 */
function formatDisplayName(person: SelectedPerson): string {
  return `${person.firstName} ${person.lastName}`
}

/**
 * RishtePersonButton component for selecting Person A or Person B
 *
 * Displays either:
 * - A "Select Person X" button with UserPlus icon when no person is selected
 * - A card showing the selected person's name with a clear button when selected
 *
 * Requirements:
 * - 2.1: Display two Person_Buttons labeled "Select Person A" and "Select Person B"
 * - 2.2: Display "Select Person A/B" with user-plus icon when no person selected
 * - 2.3: Transform into Selected_Person_Card showing person's full name when selected
 * - 2.4: Display small "x" button to clear the selection
 * - 2.5: Open Person_Search_Wizard dialog when clicked
 * - 2.6: Styled consistently with existing UI design system
 */
export const RishtePersonButton = memo(function RishtePersonButton({
  label,
  selectedPerson,
  onSelect,
  onClear,
}: RishtePersonButtonProps) {
  const isSelected = selectedPerson !== null
  const buttonLabel = `Select Person ${label}`

  // Determine border color based on person label
  const getBorderClass = () => {
    if (label === "A") {
      return "border-green-500"
    }
    return "border-blue-500"
  }

  const getBadgeClass = () => {
    if (label === "A") {
      return "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
    }
    return "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
  }

  // Unselected state: Show button with UserPlus icon
  if (!isSelected) {
    return (
      <Button
        variant="outline"
        className={cn(
          "h-auto min-h-[80px] w-full flex flex-col gap-2 py-4",
          "border-2 border-dashed hover:border-solid",
          getBorderClass(),
        )}
        onClick={onSelect}
        aria-label={buttonLabel}
      >
        <UserPlus className="size-6" aria-hidden="true" />
        <span className="font-medium">{buttonLabel}</span>
      </Button>
    )
  }

  // Selected state: Show card with person info and clear button
  return (
    <Card
      className={cn(
        "relative min-h-[80px] w-full p-4",
        "border-2 transition-all duration-200",
        getBorderClass(),
      )}
    >
      {/* Clear button */}
      <Button
        variant="ghost"
        size="icon-sm"
        className="absolute top-2 right-2 h-6 w-6 p-0 hover:bg-destructive/10"
        onClick={(e) => {
          e.stopPropagation()
          onClear()
        }}
        aria-label={`Clear Person ${label} selection`}
      >
        <X className="h-4 w-4" aria-hidden="true" />
      </Button>

      {/* Person info */}
      <div className="flex flex-col gap-2 pr-8">
        {/* Person label badge */}
        <span
          className={cn(
            "text-xs font-medium px-2 py-0.5 rounded-full w-fit",
            getBadgeClass(),
          )}
        >
          Person {label}
        </span>

        {/* Person name */}
        <div
          className="font-semibold text-sm leading-tight truncate"
          title={formatDisplayName(selectedPerson)}
        >
          {formatDisplayName(selectedPerson)}
        </div>

        {/* Birth year if available */}
        {selectedPerson.birthYear && (
          <div className="text-xs text-muted-foreground">
            Born: {selectedPerson.birthYear}
          </div>
        )}
      </div>

      {/* Clickable overlay to re-select */}
      <button
        type="button"
        className="absolute inset-0 cursor-pointer opacity-0"
        onClick={onSelect}
        aria-label={`Change Person ${label} selection`}
      />
    </Card>
  )
})
