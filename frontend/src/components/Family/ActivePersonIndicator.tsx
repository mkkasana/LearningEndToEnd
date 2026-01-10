import { ArrowLeft, UserCheck } from "lucide-react"

import { Button } from "@/components/ui/button"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import { cn } from "@/lib/utils"

export interface ActivePersonIndicatorProps {
  /** Additional CSS classes */
  className?: string
}

/**
 * ActivePersonIndicator - Shows a banner when assuming another person's role
 * 
 * Displays:
 * - Visual indicator that user is acting as another person
 * - The assumed person's name
 * - "Return to Primary" button to exit assumed state
 * - Primary person name for reference
 * 
 * _Requirements: 2.5, 4.1, 4.4_
 */
export function ActivePersonIndicator({ className }: ActivePersonIndicatorProps) {
  const { 
    isAssuming, 
    assumedPerson, 
    primaryPerson, 
    returnToPrimary 
  } = useActivePersonContext()

  // Only show when assuming another person
  if (!isAssuming || !assumedPerson) {
    return null
  }

  const assumedName = `${assumedPerson.first_name} ${assumedPerson.last_name}`
  const primaryName = primaryPerson 
    ? `${primaryPerson.first_name} ${primaryPerson.last_name}` 
    : "your profile"

  return (
    <div
      className={cn(
        "flex items-center justify-between gap-4 px-4 py-2",
        "bg-amber-100 dark:bg-amber-950/50 border-b border-amber-300 dark:border-amber-800",
        "text-amber-900 dark:text-amber-100",
        className
      )}
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center gap-2">
        <UserCheck className="h-4 w-4" aria-hidden="true" />
        <span className="text-sm font-medium">
          Acting as <strong>{assumedName}</strong>
        </span>
        <span className="text-xs text-amber-700 dark:text-amber-300">
          (Primary: {primaryName})
        </span>
      </div>

      <Button
        variant="outline"
        size="sm"
        onClick={returnToPrimary}
        className="bg-white dark:bg-amber-900 border-amber-400 dark:border-amber-700 hover:bg-amber-50 dark:hover:bg-amber-800"
        aria-label={`Return to ${primaryName}`}
      >
        <ArrowLeft className="h-3 w-3" />
        <span className="text-xs">Return to Primary</span>
      </Button>
    </div>
  )
}
