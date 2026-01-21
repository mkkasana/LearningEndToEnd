import { keepPreviousData, useQuery } from "@tanstack/react-query"
import type { PersonSearchFilterRequest, PersonSearchResponse } from "@/client"
import { PersonSearchService } from "@/client"

export interface UsePersonSearchParams {
  filters: PersonSearchFilterRequest | null
  enabled?: boolean
}

/**
 * Custom hook for searching persons with filters and pagination
 * Requirements: 11.2 - Wrap TanStack Query with proper query key
 *
 * Features:
 * - Caches search results using TanStack Query
 * - Handles loading and error states
 * - Uses keepPreviousData for smooth pagination transitions
 *
 * @param params - Search parameters including filters (can be null)
 * @returns Search results with loading and error states
 */
export function usePersonSearch({
  filters,
  enabled = true,
}: UsePersonSearchParams) {
  // Safely access filter properties with null checks
  const query = useQuery<PersonSearchResponse>({
    queryKey: [
      "personSearch",
      filters?.country_id ?? null,
      filters?.state_id ?? null,
      filters?.district_id ?? null,
      filters?.sub_district_id ?? null,
      filters?.locality_id ?? null,
      filters?.religion_id ?? null,
      filters?.religion_category_id ?? null,
      filters?.religion_sub_category_id ?? null,
      filters?.gender_id ?? null,
      filters?.birth_year_from ?? null,
      filters?.birth_year_to ?? null,
      filters?.first_name ?? null,
      filters?.last_name ?? null,
      filters?.skip ?? null,
      filters?.limit ?? null,
    ],
    queryFn: async () => {
      // This should never be called when filters is null due to enabled check
      if (!filters) {
        throw new Error("Filters are required for search")
      }
      const response = await PersonSearchService.searchPersons({
        requestBody: filters,
      })
      return response
    },
    enabled:
      enabled &&
      !!filters &&
      !!filters.country_id &&
      !!filters.state_id &&
      !!filters.district_id &&
      !!filters.sub_district_id &&
      !!filters.religion_id &&
      !!filters.religion_category_id,
    placeholderData: keepPreviousData,
    staleTime: 2 * 60 * 1000, // 2 minutes - search results are considered fresh
    gcTime: 5 * 60 * 1000, // 5 minutes - cache is kept in memory
  })

  return {
    results: query.data?.results ?? [],
    total: query.data?.total ?? 0,
    skip: query.data?.skip ?? 0,
    limit: query.data?.limit ?? 20,
    isLoading: query.isLoading,
    isFetching: query.isFetching,
    error: query.error,
    refetch: query.refetch,
  }
}
