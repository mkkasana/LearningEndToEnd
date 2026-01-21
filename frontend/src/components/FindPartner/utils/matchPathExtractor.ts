/**
 * Match Path Extractor Utility
 * Extracts linear paths from BFS exploration graph for match visualization
 * Requirements: 3.1, 3.2, 3.3, 3.4, 1.4
 */

import type { MatchItem } from "../types"

/**
 * Connection info between two persons in the exploration graph
 */
export interface MatchConnectionInfo {
  person_id: string
  relationship: string
}

/**
 * A node in the partner match exploration graph
 * Matches the API response structure (with optional fields)
 */
export interface MatchGraphNode {
  person_id: string
  first_name: string
  last_name: string
  birth_year?: number | null
  death_year?: number | null
  address?: string
  religion?: string
  is_match?: boolean
  depth: number
  from_person?: MatchConnectionInfo | null
  to_persons?: MatchConnectionInfo[]
}

/**
 * Extract linear path from seeker to match by tracing from_person backwards
 *
 * Algorithm:
 * 1. Start at the match node
 * 2. Follow from_person pointers backwards until reaching seeker
 * 3. Build path array from seeker to match (reverse order)
 *
 * @param graph - The exploration graph from API response
 * @param seekerId - The seeker person ID
 * @param matchId - The selected match person ID
 * @returns Array of MatchGraphNode from seeker to match
 *
 * Requirements: 3.1, 3.2, 3.3, 3.4
 */
export function extractPathToMatch(
  graph: Record<string, MatchGraphNode>,
  seekerId: string,
  matchId: string,
): MatchGraphNode[] {
  const path: MatchGraphNode[] = []
  let current = graph[matchId]

  // Trace backwards from match to seeker
  while (current) {
    path.unshift(current) // Add to front of array

    if (current.person_id === seekerId) {
      break // Reached seeker
    }

    if (current.from_person) {
      current = graph[current.from_person.person_id]
    } else {
      break // No more parents (shouldn't happen if graph is valid)
    }
  }

  return path
}

/**
 * Build match items for dropdown from API response
 * Sorts matches by depth (closest relationship first)
 *
 * @param graph - The exploration graph from API response
 * @param matchIds - Array of match person IDs
 * @returns Array of MatchItem sorted by depth ascending
 *
 * Requirements: 1.4
 */
export function buildMatchItems(
  graph: Record<string, MatchGraphNode>,
  matchIds: string[],
): MatchItem[] {
  return matchIds
    .map((id) => {
      const node = graph[id]
      if (!node) return null
      return {
        personId: node.person_id,
        firstName: node.first_name,
        lastName: node.last_name,
        birthYear: node.birth_year ?? null,
        depth: node.depth,
      }
    })
    .filter((item): item is MatchItem => item !== null)
    .sort((a, b) => a.depth - b.depth) // Sort by depth (closest first)
}

/**
 * Generate path summary as array of first names
 * Used to display "Name1 → Name2 → Name3..." summary
 *
 * @param path - Array of MatchGraphNode from seeker to match
 * @returns Array of first names in path order
 *
 * Requirements: 4.1, 4.2, 4.3
 */
export function generateMatchPathSummary(path: MatchGraphNode[]): string[] {
  return path.map((node) => node.first_name)
}
