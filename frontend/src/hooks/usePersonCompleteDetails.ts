import { useQuery } from "@tanstack/react-query"
import type { PersonCompleteDetailsResponse } from "@/client"
import { PersonService } from "@/client"

/**
 * Custom hook for fetching complete person details
 * @param personId - The ID of the person to fetch details for (null to disable query)
 * @returns Person complete details with loading and error states
 *
 * Performance optimizations:
 * - Data is cached for 5 minutes (staleTime) to avoid redundant API calls
 * - Cache is kept in memory for 10 minutes (gcTime) for quick navigation
 * - Query is disabled when personId is null
 */
export function usePersonCompleteDetails(personId: string | null) {
  const query = useQuery({
    queryKey: ["personCompleteDetails", personId],
    queryFn: async (): Promise<PersonCompleteDetailsResponse> => {
      if (!personId) {
        throw new Error("Person ID is required")
      }

      try {
        const response = await PersonService.getPersonCompleteDetails({
          personId,
        })
        return response
      } catch (error) {
        if (error instanceof Error) {
          throw new Error(`Failed to load person details: ${error.message}`)
        }
        throw new Error("Failed to load person details")
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
