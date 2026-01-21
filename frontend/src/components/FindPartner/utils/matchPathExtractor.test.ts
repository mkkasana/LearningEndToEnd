/**
 * Property-Based Tests for Match Path Extractor
 * Feature: partner-match-visualizer
 * 
 * Property 1: Path Extraction Correctness
 * Property 2: Match Sorting by Depth
 * Validates: Requirements 3.1, 3.2, 1.4
 */

import * as fc from "fast-check"
import { describe, expect, it } from "vitest"
import {
  extractPathToMatch,
  buildMatchItems,
  generateMatchPathSummary,
  type MatchGraphNode,
} from "./matchPathExtractor"

// ============================================
// Generators for property-based testing
// ============================================

/**
 * Generate a random relationship type
 */
const relationshipTypeArbitrary = fc.constantFrom(
  "Father",
  "Mother",
  "Son",
  "Daughter",
  "Spouse",
  "Husband",
  "Wife"
)

/**
 * Generate a valid linear path graph from seeker to match
 * Returns { graph, seekerId, matchId, pathLength }
 */
const validPathGraphArbitrary = fc
  .integer({ min: 2, max: 6 })
  .chain((pathLength) =>
    fc
      .array(fc.uuid(), { minLength: pathLength, maxLength: pathLength })
      .chain((personIds) =>
        fc
          .array(relationshipTypeArbitrary, {
            minLength: pathLength - 1,
            maxLength: pathLength - 1,
          })
          .chain((relationships) =>
            fc
              .array(fc.string({ minLength: 1, maxLength: 15 }), {
                minLength: pathLength,
                maxLength: pathLength,
              })
              .map((firstNames) => {
                const graph: Record<string, MatchGraphNode> = {}
                const seekerId = personIds[0]
                const matchId = personIds[pathLength - 1]

                // Build the graph with proper from_person pointers
                for (let i = 0; i < pathLength; i++) {
                  const personId = personIds[i]
                  const fromPerson =
                    i === 0
                      ? null
                      : {
                          person_id: personIds[i - 1],
                          relationship: relationships[i - 1],
                        }

                  graph[personId] = {
                    person_id: personId,
                    first_name: firstNames[i],
                    last_name: `Last${i}`,
                    birth_year: 1990 + i,
                    death_year: null,
                    address: "",
                    religion: "",
                    is_match: personId === matchId,
                    depth: i,
                    from_person: fromPerson,
                    to_persons: [],
                  }
                }

                return { graph, seekerId, matchId, pathLength, personIds, firstNames }
              })
          )
      )
  )

/**
 * Generate multiple matches with different depths
 */
const multipleMatchesArbitrary = fc
  .integer({ min: 2, max: 5 })
  .chain((numMatches) =>
    fc
      .array(fc.uuid(), { minLength: numMatches, maxLength: numMatches })
      .chain((matchIds) =>
        fc
          .array(fc.integer({ min: 1, max: 10 }), {
            minLength: numMatches,
            maxLength: numMatches,
          })
          .chain((depths) =>
            fc
              .array(fc.string({ minLength: 1, maxLength: 15 }), {
                minLength: numMatches,
                maxLength: numMatches,
              })
              .chain((firstNames) =>
                fc
                  .array(fc.string({ minLength: 1, maxLength: 15 }), {
                    minLength: numMatches,
                    maxLength: numMatches,
                  })
                  .chain((lastNames) =>
                    fc
                      .array(
                        fc.option(fc.integer({ min: 1900, max: 2024 }), {
                          nil: null,
                        }),
                        { minLength: numMatches, maxLength: numMatches }
                      )
                      .map((birthYears) => {
                        const graph: Record<string, MatchGraphNode> = {}

                        for (let i = 0; i < numMatches; i++) {
                          graph[matchIds[i]] = {
                            person_id: matchIds[i],
                            first_name: firstNames[i],
                            last_name: lastNames[i],
                            birth_year: birthYears[i],
                            death_year: null,
                            address: "",
                            religion: "",
                            is_match: true,
                            depth: depths[i],
                            from_person: null,
                            to_persons: [],
                          }
                        }

                        return { graph, matchIds, depths }
                      })
                  )
              )
          )
      )
  )

// ============================================
// Property-Based Tests
// ============================================

describe("matchPathExtractor - Property-Based Tests", () => {
  /**
   * Feature: partner-match-visualizer, Property 1: Path Extraction Correctness
   * Validates: Requirements 3.1, 3.2
   *
   * For any valid BFS exploration graph containing a path from seeker to match,
   * the extractPathToMatch function SHALL:
   * - Return an array where the first element has person_id equal to seekerId
   * - Return an array where the last element has person_id equal to matchId
   * - Return an array where each consecutive pair satisfies: path[i+1].from_person.person_id === path[i].person_id
   */
  describe("Property 1: Path Extraction Correctness", () => {
    it("should extract path with seeker as first element and match as last element", () => {
      fc.assert(
        fc.property(validPathGraphArbitrary, ({ graph, seekerId, matchId }) => {
          const path = extractPathToMatch(graph, seekerId, matchId)

          // First element should be seeker
          expect(path[0].person_id).toBe(seekerId)

          // Last element should be match
          expect(path[path.length - 1].person_id).toBe(matchId)
        }),
        { numRuns: 100 }
      )
    })

    it("should maintain correct from_person chain in extracted path", () => {
      fc.assert(
        fc.property(validPathGraphArbitrary, ({ graph, seekerId, matchId }) => {
          const path = extractPathToMatch(graph, seekerId, matchId)

          // Each consecutive pair should satisfy: path[i+1].from_person.person_id === path[i].person_id
          for (let i = 0; i < path.length - 1; i++) {
            const current = path[i]
            const next = path[i + 1]

            expect(next.from_person).not.toBeNull()
            expect(next.from_person?.person_id).toBe(current.person_id)
          }
        }),
        { numRuns: 100 }
      )
    })

    it("should return path with correct length matching the graph depth", () => {
      fc.assert(
        fc.property(
          validPathGraphArbitrary,
          ({ graph, seekerId, matchId, pathLength }) => {
            const path = extractPathToMatch(graph, seekerId, matchId)

            // Path length should match expected length
            expect(path.length).toBe(pathLength)
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should handle single-hop paths (direct connection)", () => {
      fc.assert(
        fc.property(
          fc.uuid(),
          fc.uuid(),
          relationshipTypeArbitrary,
          fc.string({ minLength: 1, maxLength: 15 }),
          fc.string({ minLength: 1, maxLength: 15 }),
          (seekerId, matchId, relationship, seekerName, matchName) => {
            const graph: Record<string, MatchGraphNode> = {
              [seekerId]: {
                person_id: seekerId,
                first_name: seekerName,
                last_name: "Seeker",
                birth_year: 1990,
                death_year: null,
                address: "",
                religion: "",
                is_match: false,
                depth: 0,
                from_person: null,
                to_persons: [],
              },
              [matchId]: {
                person_id: matchId,
                first_name: matchName,
                last_name: "Match",
                birth_year: 1992,
                death_year: null,
                address: "",
                religion: "",
                is_match: true,
                depth: 1,
                from_person: { person_id: seekerId, relationship },
                to_persons: [],
              },
            }

            const path = extractPathToMatch(graph, seekerId, matchId)

            expect(path.length).toBe(2)
            expect(path[0].person_id).toBe(seekerId)
            expect(path[1].person_id).toBe(matchId)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  /**
   * Feature: partner-match-visualizer, Property 2: Match Sorting by Depth
   * Validates: Requirements 1.4
   *
   * For any list of match items with depth values, the buildMatchItems function
   * SHALL return items sorted in ascending order by depth (closest matches first).
   */
  describe("Property 2: Match Sorting by Depth", () => {
    it("should sort matches by depth in ascending order", () => {
      fc.assert(
        fc.property(multipleMatchesArbitrary, ({ graph, matchIds }) => {
          const result = buildMatchItems(graph, matchIds)

          // Verify sorted by depth ascending
          for (let i = 0; i < result.length - 1; i++) {
            expect(result[i].depth).toBeLessThanOrEqual(result[i + 1].depth)
          }
        }),
        { numRuns: 100 }
      )
    })

    it("should include all valid matches in the result", () => {
      fc.assert(
        fc.property(multipleMatchesArbitrary, ({ graph, matchIds }) => {
          const result = buildMatchItems(graph, matchIds)

          // All matches should be included
          expect(result.length).toBe(matchIds.length)

          // All match IDs should be present
          const resultIds = result.map((item) => item.personId)
          for (const matchId of matchIds) {
            expect(resultIds).toContain(matchId)
          }
        }),
        { numRuns: 100 }
      )
    })

    it("should correctly extract person data for each match", () => {
      fc.assert(
        fc.property(multipleMatchesArbitrary, ({ graph, matchIds }) => {
          const result = buildMatchItems(graph, matchIds)

          for (const item of result) {
            const node = graph[item.personId]
            expect(item.firstName).toBe(node.first_name)
            expect(item.lastName).toBe(node.last_name)
            expect(item.birthYear).toBe(node.birth_year)
            expect(item.depth).toBe(node.depth)
          }
        }),
        { numRuns: 100 }
      )
    })

    it("should filter out matches not found in graph", () => {
      fc.assert(
        fc.property(
          multipleMatchesArbitrary,
          fc.uuid(),
          ({ graph, matchIds }, nonExistentId) => {
            // Add a non-existent ID to the match list
            const matchIdsWithInvalid = [...matchIds, nonExistentId]

            const result = buildMatchItems(graph, matchIdsWithInvalid)

            // Should only include valid matches
            expect(result.length).toBe(matchIds.length)
            expect(result.map((item) => item.personId)).not.toContain(
              nonExistentId
            )
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})

// ============================================
// Unit Tests for Edge Cases
// ============================================

describe("matchPathExtractor - Unit Tests", () => {
  describe("extractPathToMatch", () => {
    it("should return empty array when match not found in graph", () => {
      const graph: Record<string, MatchGraphNode> = {}
      const result = extractPathToMatch(graph, "seeker-id", "non-existent-id")
      expect(result).toEqual([])
    })

    it("should handle seeker being the same as match", () => {
      const personId = "same-person"
      const graph: Record<string, MatchGraphNode> = {
        [personId]: {
          person_id: personId,
          first_name: "John",
          last_name: "Doe",
          birth_year: 1990,
          death_year: null,
          address: "",
          religion: "",
          is_match: true,
          depth: 0,
          from_person: null,
          to_persons: [],
        },
      }

      const result = extractPathToMatch(graph, personId, personId)

      expect(result.length).toBe(1)
      expect(result[0].person_id).toBe(personId)
    })
  })

  describe("buildMatchItems", () => {
    it("should return empty array for empty match list", () => {
      const graph: Record<string, MatchGraphNode> = {}
      const result = buildMatchItems(graph, [])
      expect(result).toEqual([])
    })
  })

  describe("generateMatchPathSummary", () => {
    it("should return empty array for empty path", () => {
      const result = generateMatchPathSummary([])
      expect(result).toEqual([])
    })

    it("should return array of first names in order", () => {
      const path: MatchGraphNode[] = [
        {
          person_id: "1",
          first_name: "John",
          last_name: "Doe",
          birth_year: 1990,
          death_year: null,
          address: "",
          religion: "",
          is_match: false,
          depth: 0,
          from_person: null,
          to_persons: [],
        },
        {
          person_id: "2",
          first_name: "Jane",
          last_name: "Doe",
          birth_year: 1992,
          death_year: null,
          address: "",
          religion: "",
          is_match: false,
          depth: 1,
          from_person: { person_id: "1", relationship: "Father" },
          to_persons: [],
        },
        {
          person_id: "3",
          first_name: "Bob",
          last_name: "Smith",
          birth_year: 1994,
          death_year: null,
          address: "",
          religion: "",
          is_match: true,
          depth: 2,
          from_person: { person_id: "2", relationship: "Spouse" },
          to_persons: [],
        },
      ]

      const result = generateMatchPathSummary(path)

      expect(result).toEqual(["John", "Jane", "Bob"])
    })
  })
})
