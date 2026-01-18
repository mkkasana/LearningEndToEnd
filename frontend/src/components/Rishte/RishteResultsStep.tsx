// @ts-nocheck

import { useQuery } from "@tanstack/react-query"
import { Loader2, Search, User } from "lucide-react"
import { useState } from "react"
import type { PersonSearchResult } from "@/client"
import { PersonSearchService } from "@/client"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { RishteResultsStepProps } from "./types"
import {
  buildSearchRequest,
  extractBirthYear,
  formatPersonName,
  toSelectedPerson,
  calculateTotalPages,
} from "./utils/searchUtils"

/**
 * RishteResultsStep component - Step 4 of the Person Search Wizard
 * 
 * Displays search results and allows person selection:
 * - Calls person search API with collected criteria
 * - Shows loading indicator during search
 * - Displays person cards in scrollable grid
 * - Handles empty results with message
 * - Supports pagination for > 20 results
 * 
 * Requirements:
 * - 6.1: Call person search API with all collected criteria
 * - 6.2: Display loading indicator during search
 * - 6.3: Display matched persons in scrollable list
 * - 6.4: Each card shows name, birth year, address summary, religion summary
 * - 6.5: Each card has Select button
 * - 6.6: Close dialog and update Person_Button when selected
 * - 6.7: Display "No persons found" message if empty
 * - 6.8: Display Back button
 * - 6.9: Support pagination for > 20 results
 */
export function RishteResultsStep({
  searchCriteria,
  onSelect,
  onBack,
}: RishteResultsStepProps) {
  const [currentPage, setCurrentPage] = useState(0)
  const pageSize = 20

  // Build search request
  const searchRequest = buildSearchRequest(
    searchCriteria,
    currentPage * pageSize,
    pageSize
  )

  // Execute search query
  const {
    data: searchResponse,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["rishtePersonSearch", searchRequest],
    queryFn: () =>
      PersonSearchService.searchPersons({
        requestBody: searchRequest,
      }),
    enabled: true,
  })

  const results = searchResponse?.results ?? []
  const total = searchResponse?.total ?? 0
  const totalPages = calculateTotalPages(total, pageSize)

  /**
   * Handle person selection
   */
  const handleSelect = (person: PersonSearchResult) => {
    onSelect(toSelectedPerson(person))
  }

  /**
   * Handle pagination
   */
  const handlePreviousPage = () => {
    if (currentPage > 0) {
      setCurrentPage(currentPage - 1)
    }
  }

  const handleNextPage = () => {
    if (currentPage < totalPages - 1) {
      setCurrentPage(currentPage + 1)
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Searching for persons...</p>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-4">
        <p className="text-sm text-destructive">
          An error occurred while searching. Please try again.
        </p>
        <Button variant="outline" onClick={onBack}>
          Back
        </Button>
      </div>
    )
  }

  // Empty results state
  if (results.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 gap-4">
        <Search className="h-12 w-12 text-muted-foreground" />
        <div className="text-center">
          <p className="font-medium">No persons found</p>
          <p className="text-sm text-muted-foreground mt-1">
            Try adjusting your search criteria to find more results.
          </p>
        </div>
        <Button variant="outline" onClick={onBack}>
          Back to adjust criteria
        </Button>
      </div>
    )
  }

  // Results display
  return (
    <div className="flex flex-col gap-4 py-4">
      {/* Results count */}
      <div className="text-sm text-muted-foreground">
        Found {total} person{total !== 1 ? "s" : ""} matching your criteria
      </div>

      {/* Results grid */}
      <ScrollArea className="h-[350px] pr-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {results.map((person) => (
            <Card
              key={person.person_id}
              className="p-4 hover:border-primary/50 transition-colors"
            >
              <div className="flex flex-col gap-3">
                {/* Top row: Avatar and Person info */}
                <div className="flex items-start gap-3">
                  {/* Avatar */}
                  <Avatar className="h-10 w-10 shrink-0">
                    <AvatarFallback className="bg-muted">
                      <User className="h-5 w-5 text-muted-foreground" />
                    </AvatarFallback>
                  </Avatar>

                  {/* Person info */}
                  <div className="flex-1 min-w-0">
                    <div
                      className="font-medium text-sm"
                      title={formatPersonName(person)}
                    >
                      {formatPersonName(person)}
                    </div>

                    {/* Birth year */}
                    {person.date_of_birth && (
                      <div className="text-xs text-muted-foreground mt-0.5">
                        Born: {extractBirthYear(person.date_of_birth)}
                      </div>
                    )}

                    {/* Match score if available */}
                    {person.name_match_score !== null &&
                      person.name_match_score !== undefined && (
                        <div className="text-xs text-muted-foreground mt-0.5">
                          Match: {Math.round(person.name_match_score)}%
                        </div>
                      )}
                  </div>
                </div>

                {/* Select button at bottom */}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleSelect(person)}
                  className="w-full"
                >
                  Select
                </Button>
              </div>
            </Card>
          ))}
        </div>
      </ScrollArea>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={handlePreviousPage}
            disabled={currentPage === 0}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {currentPage + 1} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={handleNextPage}
            disabled={currentPage >= totalPages - 1}
          >
            Next
          </Button>
        </div>
      )}

      {/* Back button */}
      <div className="flex justify-start pt-2">
        <Button variant="outline" onClick={onBack}>
          Back
        </Button>
      </div>
    </div>
  )
}
