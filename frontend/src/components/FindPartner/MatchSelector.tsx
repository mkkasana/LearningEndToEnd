/**
 * MatchSelector Component
 * Dropdown to select which match's relationship path to display
 * Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
 */

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { MatchSelectorProps } from "./types"

/**
 * MatchSelector displays a dropdown to select a match from the list
 * Shows total matches count and allows selection of individual matches
 *
 * Requirements:
 * - 1.1: Display Match_Selector dropdown when matches are returned
 * - 1.2: Display total number of matches found
 * - 1.3: List all matches showing first name, last name, and birth year
 * - 1.4: Sort matches by depth (closest relationship first) - handled by buildMatchItems
 * - 1.5: Auto-select first match by default - handled by parent component
 * - 1.6: Update graph when user selects a different match
 */
export function MatchSelector({
  matches,
  selectedMatchId,
  onSelectMatch,
  totalMatches,
}: MatchSelectorProps) {
  return (
    <div className="flex items-center gap-4">
      <span className="text-sm text-muted-foreground">
        {totalMatches} {totalMatches === 1 ? "match" : "matches"} found
      </span>

      <Select
        value={selectedMatchId || undefined}
        onValueChange={onSelectMatch}
      >
        <SelectTrigger className="w-[300px]">
          <SelectValue placeholder="Select a match" />
        </SelectTrigger>
        <SelectContent>
          {matches.map((match) => (
            <SelectItem key={match.personId} value={match.personId}>
              {match.firstName} {match.lastName} ({match.birthYear || "N/A"})
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
