/**
 * MatchPathSummary Component
 * Displays the relationship path as "Name1 → Name2 → Name3..."
 * Requirements: 4.1, 4.2, 4.3
 */

import type { MatchPathSummaryProps } from './types'

/**
 * MatchPathSummary displays a text summary of the relationship path
 * Shows the sequence of names from seeker to match with arrow separators
 * 
 * Requirements:
 * - 4.1: Display path summary showing the sequence of names when match is selected
 * - 4.2: Use "→" as separator between names
 * - 4.3: Display names in order from seeker to match
 */
export function MatchPathSummary({ pathNames }: MatchPathSummaryProps) {
  if (pathNames.length === 0) {
    return null
  }

  return (
    <div className="text-sm text-muted-foreground">
      <span className="font-medium">Path: </span>
      {pathNames.join(' → ')}
    </div>
  )
}
