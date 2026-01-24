/**
 * PartnerResultsDisplay Component - Display partner match search results
 * Requirements: 10.1, 10.2, 10.3, 1.5, 1.6, 2.1, 2.2, 2.3
 *
 * Displays partner match results with interactive graph visualization:
 * - Match selector dropdown to choose which match to view
 * - Path summary showing the relationship path
 * - React Flow graph visualization of the path
 * - Loading state with spinner
 * - Error state with error message
 * - Empty results message
 */

import { AlertCircle, Loader2, Search, Users } from "lucide-react"
import { useEffect, useMemo, useState } from "react"
import type { PartnerMatchResponse } from "@/client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MatchGraph } from "./MatchGraph"
import { MatchPathSummary } from "./MatchPathSummary"
import { MatchSelector } from "./MatchSelector"
import type { PartnerResultsDisplayProps } from "./types"
import { transformMatchPath } from "./utils/matchGraphTransformer"
import {
  buildMatchItems,
  extractPathToMatch,
  generateMatchPathSummary,
} from "./utils/matchPathExtractor"

/**
 * PartnerResultsDisplay - Displays partner match search results
 *
 * Shows different states:
 * - Empty state (before search)
 * - Loading state (during search)
 * - Error state (on failure)
 * - No matches state (when total_matches = 0)
 * - Results with graph visualization (after successful search with matches)
 *
 * Requirements:
 * - 10.1: Replace raw JSON display with Match_Selector and Match_Graph
 * - 10.2: Display Match_Selector and Match_Graph when matches exist
 * - 10.3: Remove raw JSON pretty-print display
 * - 1.5: Auto-select first match on results load
 * - 1.6: Update graph when user selects a different match
 * - 2.1: Show "No matches found" message when total_matches = 0
 * - 2.2: Hide Match_Selector when no matches
 * - 2.3: Hide Match_Graph when no matches
 */
export function PartnerResultsDisplay({
  data,
  isLoading,
  error,
  totalMatches,
  onViewPerson,
}: PartnerResultsDisplayProps) {
  // State for selected match ID
  const [selectedMatchId, setSelectedMatchId] = useState<string | null>(null)

  // Cast data to PartnerMatchResponse for type safety
  const matchResponse = data as PartnerMatchResponse | null

  // Build match items for dropdown (sorted by depth)
  const matchItems = useMemo(() => {
    if (!matchResponse?.exploration_graph || !matchResponse?.matches) {
      return []
    }
    return buildMatchItems(
      matchResponse.exploration_graph,
      matchResponse.matches,
    )
  }, [matchResponse?.exploration_graph, matchResponse?.matches])

  // Auto-select first match when results load
  // Requirements: 1.5 - Auto-select first match by default
  useEffect(() => {
    if (matchItems.length > 0 && !selectedMatchId) {
      setSelectedMatchId(matchItems[0].personId)
    }
  }, [matchItems, selectedMatchId])

  // Reset selection when data changes (new search)
  useEffect(() => {
    if (matchItems.length > 0) {
      setSelectedMatchId(matchItems[0].personId)
    } else {
      setSelectedMatchId(null)
    }
    // Only reset when matchResponse changes (new search), not on every matchItems change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [matchResponse?.seeker_id])

  // Extract path for selected match
  const path = useMemo(() => {
    if (
      !matchResponse?.exploration_graph ||
      !matchResponse?.seeker_id ||
      !selectedMatchId
    ) {
      return []
    }
    return extractPathToMatch(
      matchResponse.exploration_graph,
      matchResponse.seeker_id,
      selectedMatchId,
    )
  }, [
    matchResponse?.exploration_graph,
    matchResponse?.seeker_id,
    selectedMatchId,
  ])

  // Generate path summary (array of names)
  const pathNames = useMemo(() => {
    return generateMatchPathSummary(path)
  }, [path])

  // Transform path to React Flow nodes and edges
  const { nodes, edges } = useMemo(() => {
    if (!matchResponse?.seeker_id || !selectedMatchId) {
      return { nodes: [], edges: [] }
    }
    return transformMatchPath(path, matchResponse.seeker_id, selectedMatchId)
  }, [path, matchResponse?.seeker_id, selectedMatchId])

  // Handle match selection change
  // Requirements: 1.6 - Update graph when user selects a different match
  const handleSelectMatch = (matchId: string) => {
    setSelectedMatchId(matchId)
  }

  // Loading state - show spinner
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-sm text-muted-foreground">
          Searching for partner matches...
        </p>
      </div>
    )
  }

  // Error state - show error message
  if (error) {
    return (
      <Alert variant="destructive" className="max-w-2xl mx-auto">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Search Failed</AlertTitle>
        <AlertDescription>
          {error.message || "An error occurred while searching for matches."}
        </AlertDescription>
      </Alert>
    )
  }

  // Empty state - before search or no data
  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-4 text-muted-foreground">
        <Search className="h-12 w-12" />
        <div className="text-center">
          <p className="text-lg font-medium">Ready to Search</p>
          <p className="text-sm">
            Configure your filters and click "Find Matches" to search for
            potential partners.
          </p>
        </div>
      </div>
    )
  }

  // No matches found
  // Requirements: 2.1, 2.2, 2.3 - Show message, hide selector and graph
  if (totalMatches === 0) {
    return (
      <Alert className="max-w-2xl mx-auto">
        <Users className="h-4 w-4" />
        <AlertTitle>No Matches Found</AlertTitle>
        <AlertDescription>
          No potential partners were found matching your criteria. Try adjusting
          your filters or increasing the search depth.
        </AlertDescription>
      </Alert>
    )
  }

  // Results display - show graph visualization
  // Requirements: 10.1, 10.2, 10.3 - Replace JSON with graph
  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Users className="h-5 w-5" />
          Search Results
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Match Selector - Requirements: 1.1, 1.2, 1.3, 1.4 */}
        <MatchSelector
          matches={matchItems}
          selectedMatchId={selectedMatchId}
          onSelectMatch={handleSelectMatch}
          totalMatches={totalMatches ?? 0}
        />

        {/* Path Summary - Requirements: 4.1, 4.2, 4.3 */}
        {selectedMatchId && pathNames.length > 0 && (
          <MatchPathSummary pathNames={pathNames} />
        )}

        {/* Match Graph - Requirements: 5.1-5.4, 8.1-8.5 */}
        {selectedMatchId && nodes.length > 0 && (
          <div className="rounded-md border">
            <MatchGraph
              nodes={nodes}
              edges={edges}
              onNodeViewClick={onViewPerson}
            />
          </div>
        )}
      </CardContent>
    </Card>
  )
}
