import { useQuery } from "@tanstack/react-query"
import type { PersonDetails, PersonRelationshipWithDetails } from "@/client"
import { PersonService } from "@/client"

// Relationship type constants
export const RELATIONSHIP_TYPES = {
  FATHER: "rel-6a0ede824d101",
  MOTHER: "rel-6a0ede824d102",
  DAUGHTER: "rel-6a0ede824d103",
  SON: "rel-6a0ede824d104",
  WIFE: "rel-6a0ede824d105",
  HUSBAND: "rel-6a0ede824d106",
  SPOUSE: "rel-6a0ede824d107",
} as const

export const PARENT_TYPES = [
  RELATIONSHIP_TYPES.FATHER,
  RELATIONSHIP_TYPES.MOTHER,
]

export const SPOUSE_TYPES = [
  RELATIONSHIP_TYPES.WIFE,
  RELATIONSHIP_TYPES.HUSBAND,
  RELATIONSHIP_TYPES.SPOUSE,
]

export const CHILD_TYPES = [RELATIONSHIP_TYPES.DAUGHTER, RELATIONSHIP_TYPES.SON]

export interface CategorizedRelationships {
  parents: PersonDetails[]
  spouses: PersonDetails[]
  children: PersonDetails[]
  parentIds: string[]
}

export interface FamilyTreeData extends CategorizedRelationships {
  siblings: PersonDetails[]
  selectedPerson: PersonDetails
}

/**
 * Custom hook for fetching and processing family tree data
 * @param personId - The ID of the person to fetch relationships for (null for current user)
 * @returns Family tree data with loading and error states
 *
 * Performance optimizations:
 * - Data is cached for 5 minutes (staleTime) to avoid redundant API calls
 * - Cache is kept in memory for 10 minutes (gcTime) for quick navigation
 * - Previously viewed persons are served from cache instantly
 */
export function useFamilyTreeData(personId: string | null) {
  const query = useQuery({
    queryKey: ["familyTreeData", personId],
    queryFn: async () => {
      try {
        // Fetch relationship data - now returns selected person + relationships
        const response = personId
          ? await PersonService.getPersonRelationshipsWithDetails({ personId })
          : await PersonService.getMyRelationshipsWithDetails()

        // Categorize relationships
        const categorized = categorizeRelationships(response.relationships)

        // Calculate siblings - handle failures gracefully
        let siblings: PersonDetails[] = []
        try {
          siblings = await calculateSiblings(
            personId || "me",
            categorized.parentIds,
          )
        } catch (error) {
          console.error("Failed to calculate siblings:", error)
          // Continue with empty siblings array if calculation fails
        }

        return {
          ...categorized,
          siblings,
          selectedPerson: response.selected_person,
        }
      } catch (error) {
        // Re-throw with more descriptive error message
        if (error instanceof Error) {
          throw new Error(`Failed to load family tree data: ${error.message}`)
        }
        throw new Error("Failed to load family tree data")
      }
    },
    enabled: personId !== null,
    staleTime: 5 * 60 * 1000, // 5 minutes - data is considered fresh for this duration
    gcTime: 10 * 60 * 1000, // 10 minutes - cache is kept in memory for this duration
  })

  return {
    familyData: query.data,
    isLoading: query.isLoading,
    error: query.error,
    refetch: query.refetch,
  }
}

/**
 * Categorize relationships into parents, spouses, and children
 * @param relationships - Array of person relationships with details
 * @returns Categorized relationships with parent IDs
 */
export function categorizeRelationships(
  relationships: PersonRelationshipWithDetails[],
): CategorizedRelationships {
  const parents: PersonDetails[] = []
  const spouses: PersonDetails[] = []
  const children: PersonDetails[] = []
  const parentIds: string[] = []

  for (const rel of relationships) {
    const relType = rel.relationship.relationship_type

    if (PARENT_TYPES.includes(relType as any)) {
      parents.push(rel.person)
      parentIds.push(rel.person.id)
    } else if (SPOUSE_TYPES.includes(relType as any)) {
      spouses.push(rel.person)
    } else if (CHILD_TYPES.includes(relType as any)) {
      children.push(rel.person)
    }
  }

  return {
    parents,
    spouses,
    children,
    parentIds,
  }
}

/**
 * Calculate siblings by finding people who share the same parents
 * @param selectedPersonId - The ID of the selected person
 * @param parentIds - Array of parent IDs
 * @returns Array of sibling person details
 */
export async function calculateSiblings(
  selectedPersonId: string,
  parentIds: string[],
): Promise<PersonDetails[]> {
  if (parentIds.length === 0) {
    return []
  }

  const siblingMap = new Map<string, PersonDetails>()

  // For each parent, fetch their relationships to find their children
  for (const parentId of parentIds) {
    try {
      const parentRelationshipsResponse =
        await PersonService.getPersonRelationshipsWithDetails({
          personId: parentId,
        })

      // Find all children of this parent
      for (const rel of parentRelationshipsResponse.relationships) {
        const relType = rel.relationship.relationship_type

        if (CHILD_TYPES.includes(relType as any)) {
          const childId = rel.person.id

          // Exclude the selected person and avoid duplicates
          if (childId !== selectedPersonId && !siblingMap.has(childId)) {
            siblingMap.set(childId, rel.person)
          }
        }
      }
    } catch (error) {
      console.error(
        `Failed to fetch relationships for parent ${parentId}:`,
        error,
      )
      // Continue with other parents even if one fails
    }
  }

  return Array.from(siblingMap.values())
}
