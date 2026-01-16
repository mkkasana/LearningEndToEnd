// @ts-nocheck

import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { Filter, Loader2, Search, Users } from "lucide-react"
import { useEffect, useState } from "react"

import type { PersonSearchFilterRequest } from "@/client"
import { PersonReligionService, PersonService } from "@/client"
import { ActivePersonIndicator } from "@/components/Family/ActivePersonIndicator"
import { PersonSearchCard } from "@/components/Search/PersonSearchCard"
import {
  SearchFilterPanel,
  type SearchFilters,
} from "@/components/Search/SearchFilterPanel"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationNext,
  PaginationPrevious,
} from "@/components/ui/pagination"
import { Skeleton } from "@/components/ui/skeleton"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import { usePersonSearch } from "@/hooks/usePersonSearch"

export const Route = createFileRoute("/_layout/search" as any)({
  component: SearchPage,
  head: () => ({
    meta: [
      {
        title: "Search - FastAPI Cloud",
      },
    ],
  }),
})

const ITEMS_PER_PAGE = 20

/**
 * Convert SearchFilters (frontend) to PersonSearchFilterRequest (API)
 */
function filtersToRequest(
  filters: SearchFilters,
  skip: number,
  limit: number,
): PersonSearchFilterRequest {
  return {
    first_name: filters.firstName || undefined,
    last_name: filters.lastName || undefined,
    country_id: filters.countryId,
    state_id: filters.stateId,
    district_id: filters.districtId,
    sub_district_id: filters.subDistrictId,
    locality_id: filters.localityId || undefined,
    religion_id: filters.religionId,
    religion_category_id: filters.religionCategoryId,
    religion_sub_category_id: filters.religionSubCategoryId || undefined,
    gender_id: filters.genderId || undefined,
    birth_year_from: filters.birthYearFrom || undefined,
    birth_year_to: filters.birthYearTo || undefined,
    skip,
    limit,
  }
}

/**
 * Check if filters are different from defaults (to show active indicator)
 */
function hasActiveFilters(
  filters: SearchFilters,
  defaultFilters: SearchFilters,
): boolean {
  return (
    filters.firstName !== defaultFilters.firstName ||
    filters.lastName !== defaultFilters.lastName ||
    filters.localityId !== defaultFilters.localityId ||
    filters.religionSubCategoryId !== defaultFilters.religionSubCategoryId ||
    filters.genderId !== defaultFilters.genderId ||
    filters.birthYearFrom !== defaultFilters.birthYearFrom ||
    filters.birthYearTo !== defaultFilters.birthYearTo
  )
}


function SearchPage() {
  const navigate = useNavigate()
  const { activePersonId, isLoading: isPersonLoading } = useActivePersonContext()

  // Filter panel state
  const [isFilterPanelOpen, setIsFilterPanelOpen] = useState(false)
  const [currentPage, setCurrentPage] = useState(0)

  // Default filters state (populated from user's address/religion)
  const [defaultFilters, setDefaultFilters] = useState<SearchFilters | null>(null)
  const [filters, setFilters] = useState<SearchFilters | null>(null)

  // Fetch user's address for default filters
  // _Requirements: 2.1, 5.7_
  const { data: myAddresses, isLoading: isAddressLoading } = useQuery({
    queryKey: ["personAddresses", activePersonId],
    queryFn: () => PersonService.getPersonAddresses({ personId: activePersonId! }),
    enabled: !!activePersonId,
  })

  // Fetch user's religion for default filters
  // _Requirements: 2.1, 6.5_
  const { data: myReligion, isLoading: isReligionLoading } = useQuery({
    queryKey: ["myReligion"],
    queryFn: () => PersonReligionService.getMyReligion(),
    enabled: !!activePersonId,
  })

  // Initialize default filters from user's address and religion
  // _Requirements: 2.1, 2.2_
  useEffect(() => {
    // Only proceed if we have both address and religion data loaded
    // Handle case where user may not have address or religion set up
    if (!isAddressLoading && !isReligionLoading && activePersonId) {
      // Get current address if available
      const currentAddress = myAddresses && myAddresses.length > 0
        ? (myAddresses.find((addr: any) => addr.is_current) || myAddresses[0])
        : null

      // Build default filters with safe null handling
      const newDefaultFilters: SearchFilters = {
        countryId: currentAddress?.country_id || "",
        stateId: currentAddress?.state_id || "",
        districtId: currentAddress?.district_id || "",
        subDistrictId: currentAddress?.sub_district_id || "",
        localityId: currentAddress?.locality_id || undefined,
        religionId: myReligion?.religion_id || "",
        religionCategoryId: myReligion?.religion_category_id || "",
        religionSubCategoryId: myReligion?.religion_sub_category_id || undefined,
      }
      
      setDefaultFilters(newDefaultFilters)
      if (!filters) {
        setFilters(newDefaultFilters)
      }
    }
  }, [myAddresses, myReligion, isAddressLoading, isReligionLoading, activePersonId])

  // Search query using the hook
  const searchRequest = filters
    ? filtersToRequest(filters, currentPage * ITEMS_PER_PAGE, ITEMS_PER_PAGE)
    : null

  const {
    results,
    total,
    isLoading: isSearchLoading,
    isFetching,
    error: searchError,
  } = usePersonSearch({
    filters: searchRequest,
    enabled: !!searchRequest,
  })

  /**
   * Handle explore button click - navigate to family tree with selected person
   * Uses sessionStorage + custom event pattern (same as ContributionStatsDialog)
   * _Requirements: 9.2_
   */
  const handleExplore = (personId: string) => {
    // Store in sessionStorage as fallback for fresh page loads
    sessionStorage.setItem("familyTreeExplorePersonId", personId)
    navigate({ to: "/family-tree" })
    // Dispatch custom event after a small delay to ensure navigation completes
    setTimeout(() => {
      window.dispatchEvent(
        new CustomEvent("familyTreeExplorePerson", { detail: { personId } }),
      )
    }, 100)
  }

  // Handle filter apply
  const handleApplyFilters = (newFilters: SearchFilters) => {
    setFilters(newFilters)
    setCurrentPage(0) // Reset to first page
  }

  // Handle filter reset
  const handleResetFilters = () => {
    if (defaultFilters) {
      setFilters(defaultFilters)
      setCurrentPage(0)
    }
  }

  // Pagination
  const totalPages = Math.ceil(total / ITEMS_PER_PAGE)
  const hasNextPage = currentPage < totalPages - 1
  const hasPrevPage = currentPage > 0

  // Loading state
  if (isPersonLoading || isAddressLoading || isReligionLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading...</p>
      </div>
    )
  }

  // No active person state - user must have a person profile
  // _Requirements: 2.4_
  if (!activePersonId) {
    return (
      <div className="flex flex-col gap-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Search</h1>
            <p className="text-muted-foreground">
              Find and explore persons in the system
            </p>
          </div>
        </div>
        <div className="flex flex-col items-center justify-center text-center py-12">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">Complete your profile</h3>
          <p className="text-muted-foreground max-w-md">
            Please complete your profile to start searching for persons.
          </p>
        </div>
      </div>
    )
  }

  // Still loading default filters
  if (!defaultFilters) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Initializing search...</p>
      </div>
    )
  }

  const showActiveIndicator =
    filters && defaultFilters && hasActiveFilters(filters, defaultFilters)

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Search</h1>
          <p className="text-muted-foreground">
            Find and explore persons in the system
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

      {/* Results count */}
      {/* _Requirements: 2.7, 9.5_ */}
      {!isSearchLoading && filters && (
        <div className="text-sm text-muted-foreground">
          {total > 0 ? (
            <>
              Showing {currentPage * ITEMS_PER_PAGE + 1}-
              {Math.min((currentPage + 1) * ITEMS_PER_PAGE, total)} of {total}{" "}
              results
            </>
          ) : (
            "No results found"
          )}
        </div>
      )}

      {/* Loading state */}
      {/* _Requirements: 2.6, 11.4_ */}
      {(isSearchLoading || isFetching) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-[180px] w-full rounded-xl" />
          ))}
        </div>
      )}

      {/* Error state */}
      {searchError && !isSearchLoading && (
        <div className="flex flex-col items-center justify-center text-center py-12">
          <p className="text-destructive">Failed to load search results</p>
          <p className="text-sm text-muted-foreground mt-2">
            {searchError.message}
          </p>
        </div>
      )}

      {/* Empty state */}
      {/* _Requirements: 9.4_ */}
      {!isSearchLoading && !isFetching && !searchError && results.length === 0 && (
        <div className="flex flex-col items-center justify-center text-center py-12">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Search className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">No results found</h3>
          <p className="text-muted-foreground max-w-md">
            Try adjusting your filters to find more persons
          </p>
        </div>
      )}

      {/* Results grid */}
      {/* _Requirements: 2.5, 9.1_ */}
      {!isSearchLoading && !isFetching && results.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {results.map((person) => (
            <PersonSearchCard
              key={person.person_id}
              person={person}
              onExplore={handleExplore}
            />
          ))}
        </div>
      )}

      {/* Pagination */}
      {/* _Requirements: 9.3_ */}
      {!isSearchLoading && totalPages > 1 && (
        <Pagination className="mt-4">
          <PaginationContent>
            <PaginationItem>
              <PaginationPrevious
                onClick={() => hasPrevPage && setCurrentPage((p) => p - 1)}
                className={!hasPrevPage ? "pointer-events-none opacity-50" : "cursor-pointer"}
              />
            </PaginationItem>
            <PaginationItem>
              <span className="px-4 text-sm text-muted-foreground">
                Page {currentPage + 1} of {totalPages}
              </span>
            </PaginationItem>
            <PaginationItem>
              <PaginationNext
                onClick={() => hasNextPage && setCurrentPage((p) => p + 1)}
                className={!hasNextPage ? "pointer-events-none opacity-50" : "cursor-pointer"}
              />
            </PaginationItem>
          </PaginationContent>
        </Pagination>
      )}

      {/* Filter Panel */}
      {/* _Requirements: 3.1-3.7_ */}
      {filters && defaultFilters && (
        <SearchFilterPanel
          open={isFilterPanelOpen}
          onOpenChange={setIsFilterPanelOpen}
          filters={filters}
          onApply={handleApplyFilters}
          onReset={handleResetFilters}
          defaultFilters={defaultFilters}
        />
      )}
    </div>
  )
}
