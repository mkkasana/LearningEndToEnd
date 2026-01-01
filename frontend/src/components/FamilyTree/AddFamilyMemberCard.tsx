import { Plus } from "lucide-react"
import { memo } from "react"
import { Card } from "@/components/ui/card"
import { cn } from "@/lib/utils"

export type AddFamilyMemberCardVariant = "parent" | "center" | "child"

export interface AddFamilyMemberCardProps {
  variant: AddFamilyMemberCardVariant
  onClick: () => void
}

/**
 * Get variant-specific styling classes with responsive sizing
 * Uses same dimensions as PersonCard for visual consistency
 */
function getVariantStyles(variant: AddFamilyMemberCardVariant): string {
  const baseStyles = cn(
    "cursor-pointer transition-all duration-200 ease-in-out",
    "border-2 border-dashed border-muted-foreground/30 bg-muted/20",
    "hover:border-primary/50 hover:scale-[1.02] hover:bg-muted/30",
    "touch-manipulation active:scale-95",
    "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2",
  )

  switch (variant) {
    case "parent":
      return cn(
        baseStyles,
        "min-w-[140px] md:min-w-[160px] lg:min-w-[180px]",
        "min-h-[160px] md:min-h-[180px] lg:min-h-[200px]",
      )
    case "center":
      return cn(
        baseStyles,
        "min-w-[140px] md:min-w-[160px] lg:min-w-[180px]",
        "min-h-[160px] md:min-h-[180px] lg:min-h-[200px]",
      )
    case "child":
      return cn(
        baseStyles,
        "min-w-[130px] md:min-w-[150px] lg:min-w-[170px]",
        "min-h-[150px] md:min-h-[170px] lg:min-h-[190px]",
      )
  }
}

/**
 * Get circle size based on variant
 */
function getCircleSize(variant: AddFamilyMemberCardVariant): string {
  switch (variant) {
    case "parent":
    case "center":
      return "size-14 md:size-16 lg:size-18"
    case "child":
      return "size-12 md:size-14 lg:size-16"
  }
}

/**
 * Get icon size based on variant
 */
function getIconSize(variant: AddFamilyMemberCardVariant): string {
  switch (variant) {
    case "parent":
    case "center":
      return "size-6 md:size-7 lg:size-8"
    case "child":
      return "size-5 md:size-6 lg:size-7"
  }
}

/**
 * AddFamilyMemberCard - A placeholder card with "+" icon for adding family members
 *
 * Visual Design:
 * - Same dimensions as PersonCard for the given variant
 * - Dashed border with muted background
 * - Centered circle containing a "+" icon
 * - Hover effect: border color change, slight scale
 *
 * Requirements: 1.5, 1.6
 */
export const AddFamilyMemberCard = memo(function AddFamilyMemberCard({
  variant,
  onClick,
}: AddFamilyMemberCardProps) {
  const ariaLabel = `Add family member to ${variant === "parent" ? "parents" : variant === "child" ? "children" : "siblings and spouses"} row`

  return (
    <Card
      className={cn(
        "flex flex-col items-center justify-center gap-2 md:gap-3 p-3 md:p-4",
        getVariantStyles(variant),
      )}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onClick()
        }
      }}
      aria-label={ariaLabel}
      data-testid="add-family-member-card"
    >
      <div
        className={cn(
          "flex items-center justify-center rounded-full",
          "border-2 border-dashed border-muted-foreground/40",
          "bg-muted/30",
          "hover:border-primary/60 hover:bg-muted/50",
          "transition-all duration-200",
          getCircleSize(variant),
        )}
      >
        <Plus
          className={cn("text-muted-foreground/60", getIconSize(variant))}
          aria-hidden="true"
        />
      </div>
    </Card>
  )
})
