/**
 * Relatives Network Page - Main route for listing relatives
 * Requirements: 1.3, 1.4, 1.5, 2.1, 3.1, 3.3, 3.5, 3.6, 3.7, 5.1, 5.2
 *
 * Provides a dedicated page for users to list their relatives up to a
 * configurable relationship depth with filtering capabilities.
 */

import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Filter, Loader2, Users } from "lucide-react"
import { useCallback, useEffect, useState } from "react"

import { OpenAPI } from "@/client/core/OpenAPI"
import { request } from "@/client/core/request"
import { ActivePersonIndicator } from "@/components/Family/ActivePersonIndicator"
import { PersonDetailsPanel } from "@/components/FamilyTree/PersonDetailsPanel"
import {
  DEFAULT_FILTERS,
  RelativesFilterPanel,
  RelativesResultsGrid,
  type RelativeData,
  type RelativesFilters,
} from "@/components/RelativesNetwork"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"

export const Route = createFileRoute("/_layout/relatives-network" as any)({
  component: RelativesNetworkPage,
  head: () => ({
    meta: [
      {
        title: "Relatives Network - Family Network",
      },
    ],
  }),
})

/**
 * API Response types (matching backend schema)
 */
interface RelativesNetworkResponse {
  person_id: string
  total_count: number
  depth: number
  depth_mode: string
  relatives: RelativeData[]
}

interface RelativesNetworkRequest {
  person_id: string
  depth: number
  depth_mode: "up_to" | "only_at"
  living_only: boolean
  gender_id?: string
  country_id?: string
  state_id?: string
  district_id?: string
  sub_district_id?: string
  locality_id?: string
}

/**
 * Convert frontend filters to API request format
 */
function filtersToRequest(
  personId: string,
  filters: RelativesFilters,
): RelativesNetworkRequest {
  return {
    person_id: personId,
    depth: filters.depth,
    depth_mode: filters.depthMode,
    living_only: filters.livingOnly,
    gender_id: filters.genderId || undefined,
    country_id: filters.countryId || undefined,
    state_id: filters.stateId || undefined,
    district_id: filters.districtId || undefined,
    sub_district_id: filters.subDistrictId || undefined,
    locality_id: filters.localityId || undefined,
  }
}

/**
 * Check if filters differ from defaults (to show active indicator)
 */
function hasActiveFilters(filters: RelativesFilters): boolean {
  return (
    filters.depth !== DEFAULT_FILTERS.depth ||
    filters.depthMode !== DEFAULT_FILTERS.depthMode ||
    filters.livingOnly !== DEFAULT_FILTERS.livingOnly ||
    !!filters.genderId ||
    !!filters.countryId ||
    !!filters.stateId ||
    !!filters.districtId ||
    !!filters.subDistrictId ||
    !!filters.localityId
  )
}

/**
 * RelativesNetworkPage - Main page for relatives network listing
 *
 * Requirements:
 * - 1.3: Display header with title "Relatives Network"
 * - 1.4: Display "Filters" button in header
 * - 1.5: Show message when no active person is set
 * - 2.1: Auto-search on page load with defaults
 * - 3.1: Display results count header
 * - 3.3: Load all results without pagination
 * - 3.5: Display skeleton loading cards
 * - 3.6: Display empty state message
 * - 3.7: Display error message on failure
 * - 5.1: Open PersonDetailsPanel on View click
 * - 5.2: Display selected relative's full information
 */
function RelativesNetworkPage() {
  // Active person context
  const { activePersonId, isLoading: isContextLoading } =
    useActivePersonContext()

  // Filter state - Requirements: 2.2, 2.3, 2.4
  const [filters, setFilters] = useState<RelativesFilters>(DEFAULT_FILTERS)
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false)

  // Results state
  const [results, setResults] = useState<RelativesNetworkResponse | null>(null)

  // Person details panel state - Requirements: 5.1, 5.2
  const [detailsPanelPersonId, setDetailsPanelPersonId] = useState<
    string | null
  >(null)
  const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(false)

  // Search mutation - Requirements: 2.1, 10.2
  const searchMutation = useMutation({
    mutationFn: async (requestBody: RelativesNetworkRequest) => {
      const response = await request<RelativesNetworkResponse>(OpenAPI, {
        method: "POST",
        url: "/api/v1/relatives-network/find",
        body: requestBody,
      })
      return response
    },
    onSuccess: (data) => {
      setResults(data)
    },
    onError: () => {
      setResults(null)
    },
  })

  // Auto-search on page load with defaults - Requirements: 2.1
  useEffect(() => {
    if (activePersonId && !searchMutation.isPending && !results) {
      const requestBody = filtersToRequest(activePersonId, filters)
      searchMutation.mutate(requestBody)
    }
  }, [activePersonId]) // Only trigger on activePersonId change

  // Handle filter apply - Requirements: 9.1, 9.2, 9.3
  const handleApplyFilters = useCallback(
    (newFilters: RelativesFilters) => {
      setFilters(newFilters)
      if (activePersonId) {
        const requestBody = filtersToRequest(activePersonId, newFilters)
        searchMutation.mutate(requestBody)
      }
    },
    [activePersonId, searchMutation],
  )

  // Handle filter reset - Requirements: 9.4, 9.5
  const handleResetFilters = useCallback(() => {
    setFilters(DEFAULT_FILTERS)
    if (activePersonId) {
      const requestBody = filtersToRequest(activePersonId, DEFAULT_FILTERS)
      searchMutation.mutate(requestBody)
    }
  }, [activePersonId, searchMutation])

  // Handle View button click - Requirements: 5.1
  const handleViewRelative = useCallback((personId: string) => {
    setDetailsPanelPersonId(personId)
    setIsDetailsPanelOpen(true)
  }, [])

  // Loading state - context loading
  if (isContextLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading...</p>
      </div>
    )
  }

  // No active person state - Requirements: 1.5
  if (!activePersonId) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              Relatives Network
            </h1>
            <p className="text-muted-foreground">
              List your relatives for invitation planning
            </p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center text-center py-12">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">Complete your profile</h3>
          <p className="text-muted-foreground max-w-md">
            Please complete your profile to view your relatives network.
          </p>
        </div>
      </div>
    )
  }

  const showActiveIndicator = hasActiveFilters(filters)
  const isLoading = searchMutation.isPending
  const error = searchMutation.error

  return (
    <div className="flex flex-col gap-6">
      {/* Header - Requirements: 1.3, 1.4 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Relatives Network
          </h1>
          <p className="text-muted-foreground">
            List your relatives for invitation planning
          </p>
        </div>
        <Button
          variant="outline"
          size="default"
          onClick={() => setIsFilterPanelOpen(true)}
          className="relative"
        >
          <Filter className="h-4 w-4 mr-2" />
          Filters
          {showActiveIndicator && (
            <Badge
              variant="default"
              className="absolute -top-2 -right-2 h-5 w-5 p-0 flex items-center justify-center text-xs"
            >
              •
            </Badge>
          )}
        </Button>
      </div>

      {/* Active Person Indicator */}
      <ActivePersonIndicator />

      {/* Results count - Requirements: 3.1 */}
      {!isLoading && results && (
        <div className="text-sm text-muted-foreground">
          {results.total_count > 0 ? (
            <>
              Found {results.total_count} relative
              {results.total_count !== 1 ? "s" : ""}{" "}
              {results.depth_mode === "up_to"
                ? `up to depth ${results.depth}`
                : `at depth ${results.depth}`}
            </>
          ) : (
            `No relatives found ${results.depth_mode === "up_to" ? `within depth ${results.depth}` : `at depth ${results.depth}`}`
          )}
        </div>
      )}

      {/* Loading state - Requirements: 3.5 */}
      {isLoading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-[180px] w-full rounded-xl" />
          ))}
        </div>
      )}

      {/* Error state - Requirements: 3.7 */}
      {error && !isLoading && (
        <div className="flex flex-col items-center justify-center text-center py-12">
          <p className="text-destructive">Failed to load relatives</p>
          <p className="text-sm text-muted-foreground mt-2">
            {error instanceof Error ? error.message : "An error occurred"}
          </p>
        </div>
      )}

      {/* Results grid - Requirements: 3.2, 3.6 */}
      {!isLoading && !error && results && (
        <RelativesResultsGrid
          relatives={results.relatives}
          depth={results.depth}
          onViewRelative={handleViewRelative}
        />
      )}

      {/* Filter Panel - Requirements: 6.1-9.6 */}
      <RelativesFilterPanel
        open={isFilterPanelOpen}
        onOpenChange={setIsFilterPanelOpen}
        filters={filters}
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
      />

      {/* Person Details Panel - Requirements: 5.1, 5.2, 5.3 */}
      <PersonDetailsPanel
        personId={detailsPanelPersonId}
        open={isDetailsPanelOpen}
        onOpenChange={setIsDetailsPanelOpen}
      />
    </div>
  )
}
