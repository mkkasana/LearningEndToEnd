import { useQuery } from "@tanstack/react-query"
import type { LifeEventsPublic } from "@/client"
import { LifeEventsService } from "@/client"

/**
 * Custom hook for fetching life events for a specific person
 * @param personId - The ID of the person to fetch life events for (null to disable query)
 * @returns Life events with loading and error states
 *
 * Performance optimizations:
 * - Data is cached for 5 minutes (staleTime) to avoid redundant API calls
 * - Cache is kept in memory for 10 minutes (gcTime) for quick navigation
 * - Query is disabled when personId is null
 */
export function usePersonLifeEvents(personId: string | null) {
  const query = useQuery({
    queryKey: ["personLifeEvents", personId],
    queryFn: async (): Promise<LifeEventsPublic> => {
      if (!personId) {
        throw new Error("Person ID is required")
      }

      try {
        const response = await LifeEventsService.getPersonLifeEvents({
          personId,
          skip: 0,
          limit: 100,
        })
        return response
      } catch (error) {
        if (error instanceof Error) {
          throw new Error(`Failed to load life events: ${error.message}`)
        }
        throw new Error("Failed to load life events")
      }
    },
    enabled: personId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes - data is considered fresh for this duration
    gcTime: 10 * 60 * 1000, // 10 minutes - cache is kept in memory for this duration
  })

  return {
    data: query.data,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  }
}
