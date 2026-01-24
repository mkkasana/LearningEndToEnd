/**
 * Find Partner Page - Main route for partner match search
 * Requirements: 1.2, 1.3, 10.4
 *
 * Provides a dedicated page for searching potential marriage matches
 * using the partner-match API with configurable filters.
 */

import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Filter, Heart, Loader2 } from "lucide-react"
import { useCallback, useEffect, useState } from "react"
import { type PartnerMatchResponse, PartnerMatchService } from "@/client"
import { ActivePersonIndicator } from "@/components/Family/ActivePersonIndicator"
import {
  PartnerFilterPanel,
  type PartnerFilters,
  PartnerResultsDisplay,
  usePartnerDefaults,
} from "@/components/FindPartner"
import { PersonDetailsPanel } from "@/components/FamilyTree/PersonDetailsPanel"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useActivePersonContext } from "@/contexts"

export const Route = createFileRoute("/_layout/find-partner" as any)({
  component: FindPartnerPage,
  head: () => ({
    meta: [
      {
        title: "Find Partner - Partner Match Search",
      },
    ],
  }),
})

/**
 * FindPartnerPage - Main page for partner match search
 *
 * Requirements:
 * - 1.2: Navigate to dedicated Find Partner page
 * - 1.3: Display empty main content area with filter panel
 * - 10.4: Call partner-match/find API with current filter values
 */
function FindPartnerPage() {
  // Active person context for seeker ID
  const {
    activePersonId,
    activePerson,
    isLoading: isContextLoading,
  } = useActivePersonContext()

  // Filter panel state
  const [filterPanelOpen, setFilterPanelOpen] = useState(false)

  // Get default filters from active person
  const {
    defaultFilters,
    isLoading: isDefaultsLoading,
    genders,
  } = usePartnerDefaults()

  // Current filter state
  const [filters, setFilters] = useState<PartnerFilters | null>(null)

  // Search results state
  const [searchResults, setSearchResults] =
    useState<PartnerMatchResponse | null>(null)

  // State for PersonDetailsPanel - Requirements: 2.1
  const [detailsPanelPersonId, setDetailsPanelPersonId] = useState<
    string | null
  >(null)
  const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(false)

  // Initialize filters when defaults are loaded
  useEffect(() => {
    if (!isDefaultsLoading && defaultFilters && !filters) {
      setFilters(defaultFilters)
    }
  }, [isDefaultsLoading, defaultFilters, filters])

  // Partner match mutation
  const findMatchesMutation = useMutation({
    mutationFn: async (currentFilters: PartnerFilters) => {
      if (!activePersonId) {
        throw new Error("No active person selected")
      }

      // Find gender code from gender ID
      const gender = genders?.find(
        (g) => g.genderId === currentFilters.genderId,
      )
      const targetGenderCode = gender?.genderCode || "FEMALE"

      // Filter out any empty IDs and only include arrays with valid UUIDs
      const includeReligionIds = currentFilters.includeReligions
        .map((r) => r.id)
        .filter((id) => id && id.length > 0)
      const includeCategoryIds = currentFilters.includeCategories
        .map((c) => c.id)
        .filter((id) => id && id.length > 0)
      const includeSubCategoryIds = currentFilters.includeSubCategories
        .map((sc) => sc.id)
        .filter((id) => id && id.length > 0)
      const excludeSubCategoryIds = currentFilters.excludeSubCategories
        .map((sc) => sc.id)
        .filter((id) => id && id.length > 0)

      const response = await PartnerMatchService.findPartnerMatches({
        requestBody: {
          seeker_person_id: activePersonId,
          target_gender_code: targetGenderCode,
          birth_year_min: currentFilters.birthYearFrom,
          birth_year_max: currentFilters.birthYearTo,
          include_religion_ids:
            includeReligionIds.length > 0 ? includeReligionIds : undefined,
          include_category_ids:
            includeCategoryIds.length > 0 ? includeCategoryIds : undefined,
          include_sub_category_ids:
            includeSubCategoryIds.length > 0
              ? includeSubCategoryIds
              : undefined,
          exclude_sub_category_ids:
            excludeSubCategoryIds.length > 0
              ? excludeSubCategoryIds
              : undefined,
          max_depth: currentFilters.searchDepth,
        },
      })
      return response
    },
    onSuccess: (data) => {
      setSearchResults(data)
    },
    onError: () => {
      setSearchResults(null)
    },
  })

  // Handle filter apply - triggers search
  const handleApplyFilters = useCallback(
    (newFilters: PartnerFilters) => {
      setFilters(newFilters)
      findMatchesMutation.mutate(newFilters)
    },
    [findMatchesMutation],
  )

  // Handle filter reset
  // Requirements: 10.2 - Restore all filters to initial default values
  const handleResetFilters = useCallback(() => {
    if (defaultFilters) {
      setFilters(defaultFilters)
      setSearchResults(null)
    }
  }, [defaultFilters])

  // Handle open filter panel
  const handleOpenFilters = useCallback(() => {
    setFilterPanelOpen(true)
  }, [])

  // Handle View button click on person node - Requirements: 2.2
  const handleViewClick = useCallback((personId: string) => {
    setDetailsPanelPersonId(personId)
    setIsDetailsPanelOpen(true)
  }, [])

  // Loading state - context or defaults loading
  if (isContextLoading || isDefaultsLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading...</p>
      </div>
    )
  }

  // No active person
  if (!activePersonId || !activePerson) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Alert className="max-w-md">
          <Heart className="h-4 w-4" />
          <AlertTitle>Profile Required</AlertTitle>
          <AlertDescription>
            Please complete your profile to use the partner search feature.
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-4 sm:gap-6 h-full">
      {/* Active Person Indicator - Shows when assuming another person's role */}
      <ActivePersonIndicator />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
        <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-primary/10 shrink-0">
          <Heart className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1">
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
            Find Partner
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Search for potential marriage matches within your family network
          </p>
        </div>
        <Button onClick={handleOpenFilters} variant="outline" className="gap-2">
          <Filter className="h-4 w-4" />
          Filters
        </Button>
      </div>

      {/* Active Person Info */}
      <Card className="p-3 sm:p-4">
        <div className="flex items-center gap-3">
          <div className="text-sm text-muted-foreground">Searching as:</div>
          <div className="font-medium">
            {activePerson.first_name} {activePerson.last_name}
          </div>
        </div>
      </Card>

      {/* Filter Panel */}
      {filters && (
        <PartnerFilterPanel
          open={filterPanelOpen}
          onOpenChange={setFilterPanelOpen}
          filters={filters}
          defaultFilters={defaultFilters}
          onApply={handleApplyFilters}
          onReset={handleResetFilters}
        />
      )}

      {/* Results Display */}
      <div className="flex-1">
        <PartnerResultsDisplay
          data={searchResults}
          isLoading={findMatchesMutation.isPending}
          error={findMatchesMutation.error as Error | null}
          totalMatches={searchResults?.total_matches ?? null}
          onViewPerson={handleViewClick}
        />
      </div>

      {/* Person Details Panel - Requirements: 2.1, 2.3, 2.4, 2.5 */}
      <PersonDetailsPanel
        personId={detailsPanelPersonId}
        open={isDetailsPanelOpen}
        onOpenChange={setIsDetailsPanelOpen}
      />
    </div>
  )
}
