/**
 * PartnerResultsDisplay Component - Display partner match search results
 * Requirements: 11.1, 11.2, 11.3, 11.4, 10.5, 10.6
 *
 * Displays the raw JSON response from the partner-match API with:
 * - Pretty-printed JSON formatting
 * - Total matches count
 * - Loading state with spinner
 * - Error state with error message
 * - Empty results message
 */

import { AlertCircle, Loader2, Search, Users } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { PartnerResultsDisplayProps } from "./types"

/**
 * PartnerResultsDisplay - Displays partner match search results
 *
 * Shows different states:
 * - Empty state (before search)
 * - Loading state (during search)
 * - Error state (on failure)
 * - Results (after successful search)
 */
export function PartnerResultsDisplay({
  data,
  isLoading,
  error,
  totalMatches,
}: PartnerResultsDisplayProps) {
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

  // Results display - show JSON with match count
  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Users className="h-5 w-5" />
          Search Results
          {totalMatches !== null && (
            <span className="ml-auto text-sm font-normal text-muted-foreground">
              {totalMatches} {totalMatches === 1 ? "match" : "matches"} found
            </span>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px] w-full rounded-md border">
          <pre className="p-4 text-xs font-mono whitespace-pre-wrap break-words">
            {JSON.stringify(data, null, 2)}
          </pre>
        </ScrollArea>
      </CardContent>
    </Card>
  )
}
