import { Users } from "lucide-react"
import { memo } from "react"
import { cn } from "@/lib/utils"

export type EmptyRowPlaceholderVariant = "parent" | "center" | "child"

export interface EmptyRowPlaceholderProps {
  variant: EmptyRowPlaceholderVariant
}

/**
 * Get variant-specific styling classes with responsive sizing
 * Uses similar dimensions as PersonCard for visual consistency
 * Compact sizing to fit all three rows on screen
 */
function getVariantStyles(variant: EmptyRowPlaceholderVariant): string {
  const baseStyles = cn(
    "border border-dashed border-muted-foreground/20 bg-muted/10 rounded-lg",
    "flex flex-col items-center justify-center gap-1",
  )

  switch (variant) {
    case "parent":
      return cn(
        baseStyles,
        "min-w-[120px] md:min-w-[140px]",
        "min-h-[120px] md:min-h-[140px]",
      )
    case "center":
      return cn(
        baseStyles,
        "min-w-[120px] md:min-w-[140px]",
        "min-h-[120px] md:min-h-[140px]",
      )
    case "child":
      return cn(
        baseStyles,
        "min-w-[110px] md:min-w-[130px]",
        "min-h-[110px] md:min-h-[130px]",
      )
  }
}

/**
 * Get label text based on variant
 */
function getLabelText(variant: EmptyRowPlaceholderVariant): string {
  switch (variant) {
    case "parent":
      return "No parents added"
    case "center":
      return "No siblings or spouses"
    case "child":
      return "No children added"
  }
}

/**
 * EmptyRowPlaceholder - A subtle placeholder shown when viewing another person's
 * family tree and a row has no members.
 *
 * Visual Design:
 * - Same dimensions as PersonCard for the given variant
 * - Very subtle dashed border with muted background
 * - Centered icon and text indicating empty state
 * - Non-interactive (read-only indication)
 */
export const EmptyRowPlaceholder = memo(function EmptyRowPlaceholder({
  variant,
}: EmptyRowPlaceholderProps) {
  return (
    <div
      className={cn("p-2", getVariantStyles(variant))}
      role="status"
      aria-label={getLabelText(variant)}
    >
      <Users
        className="size-6 md:size-8 text-muted-foreground/30"
        aria-hidden="true"
      />
      <span className="text-xs text-muted-foreground/50 text-center">
        {getLabelText(variant)}
      </span>
    </div>
  )
})
