/**
 * Property-Based Tests for Match Graph Transformer
 * Feature: partner-match-visualizer
 *
 * Property 4: Generation Layout Correctness
 * Validates: Requirements 5.1, 5.2, 5.3
 */

import * as fc from "fast-check"
import { describe, expect, it } from "vitest"
import {
  assignGenerations,
  calculatePositions,
  getEdgeHandles,
  isChildRelationship,
  isParentRelationship,
  isSpouseRelationship,
  transformMatchPath,
} from "./matchGraphTransformer"
import type { MatchGraphNode } from "./matchPathExtractor"

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
  "Wife",
)

/**
 * Generate a valid linear path with proper from_person relationships
 */
const validPathArbitrary = fc.integer({ min: 2, max: 6 }).chain((pathLength) =>
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
              const path: MatchGraphNode[] = []
              const seekerId = personIds[0]
              const matchId = personIds[pathLength - 1]

              for (let i = 0; i < pathLength; i++) {
                const fromPerson =
                  i === 0
                    ? null
                    : {
                        person_id: personIds[i - 1],
                        relationship: relationships[i - 1],
                      }

                path.push({
                  person_id: personIds[i],
                  first_name: firstNames[i],
                  last_name: `Last${i}`,
                  birth_year: 1990 + i,
                  death_year: null,
                  address: "",
                  religion: "",
                  is_match: personIds[i] === matchId,
                  depth: i,
                  from_person: fromPerson,
                  to_persons: [],
                })
              }

              return { path, seekerId, matchId, relationships }
            }),
        ),
    ),
)

/**
 * Generate a path with only parent-child relationships (no spouses)
 */
const parentChildPathArbitrary = fc
  .integer({ min: 2, max: 5 })
  .chain((pathLength) =>
    fc
      .array(fc.uuid(), { minLength: pathLength, maxLength: pathLength })
      .chain((personIds) =>
        fc
          .array(fc.constantFrom("Father", "Mother", "Son", "Daughter"), {
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
                const path: MatchGraphNode[] = []

                for (let i = 0; i < pathLength; i++) {
                  const fromPerson =
                    i === 0
                      ? null
                      : {
                          person_id: personIds[i - 1],
                          relationship: relationships[i - 1],
                        }

                  path.push({
                    person_id: personIds[i],
                    first_name: firstNames[i],
                    last_name: `Last${i}`,
                    birth_year: 1990 + i,
                    death_year: null,
                    address: "",
                    religion: "",
                    is_match: i === pathLength - 1,
                    depth: i,
                    from_person: fromPerson,
                    to_persons: [],
                  })
                }

                return { path, relationships }
              }),
          ),
      ),
  )

// ============================================
// Property-Based Tests
// ============================================

describe("matchGraphTransformer - Property-Based Tests", () => {
  /**
   * Feature: partner-match-visualizer, Property 4: Generation Layout Correctness
   * Validates: Requirements 5.1, 5.2, 5.3
   *
   * For any transformed path:
   * - All nodes with the same generation level SHALL have the same Y coordinate
   * - For any parent-child relationship, the child's Y coordinate SHALL be greater than the parent's
   * - For any spouse relationship, both nodes SHALL have the same Y coordinate but different X coordinates
   */
  describe("Property 4: Generation Layout Correctness", () => {
    it("should assign same Y coordinate to nodes with same generation level", () => {
      fc.assert(
        fc.property(validPathArbitrary, ({ path }) => {
          const generations = assignGenerations(path)
          const positions = calculatePositions(generations)

          // Group nodes by generation
          const genToPositions = new Map<number, { x: number; y: number }[]>()
          generations.forEach((info, personId) => {
            const pos = positions.get(personId)
            if (pos) {
              const existing = genToPositions.get(info.generation) || []
              existing.push(pos)
              genToPositions.set(info.generation, existing)
            }
          })

          // All nodes in same generation should have same Y
          genToPositions.forEach((positionsInGen) => {
            if (positionsInGen.length > 1) {
              const firstY = positionsInGen[0].y
              for (const pos of positionsInGen) {
                expect(pos.y).toBe(firstY)
              }
            }
          })
        }),
        { numRuns: 100 },
      )
    })

    it("should position children below parents (larger Y) for parent-child relationships", () => {
      fc.assert(
        fc.property(parentChildPathArbitrary, ({ path, relationships }) => {
          const generations = assignGenerations(path)
          const positions = calculatePositions(generations)

          // Check each parent-child relationship
          for (let i = 0; i < path.length - 1; i++) {
            const sourceId = path[i].person_id
            const targetId = path[i + 1].person_id
            const relationship = relationships[i]

            const sourcePos = positions.get(sourceId)
            const targetPos = positions.get(targetId)

            if (sourcePos && targetPos) {
              if (isParentRelationship(relationship)) {
                // Going from parent to child: child should be below (larger Y)
                expect(targetPos.y).toBeGreaterThan(sourcePos.y)
              } else if (isChildRelationship(relationship)) {
                // Going from child to parent: parent should be above (smaller Y)
                expect(targetPos.y).toBeLessThan(sourcePos.y)
              }
            }
          }
        }),
        { numRuns: 100 },
      )
    })

    it("should position spouses at same Y but different X coordinates", () => {
      // Create a path with a spouse relationship
      fc.assert(
        fc.property(
          fc.uuid(),
          fc.uuid(),
          fc.string({ minLength: 1, maxLength: 15 }),
          fc.string({ minLength: 1, maxLength: 15 }),
          fc.constantFrom("Spouse", "Husband", "Wife"),
          (personId, spouseId, name1, name2, spouseRel) => {
            const path: MatchGraphNode[] = [
              {
                person_id: personId,
                first_name: name1,
                last_name: "Person",
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
                person_id: spouseId,
                first_name: name2,
                last_name: "Spouse",
                birth_year: 1992,
                death_year: null,
                address: "",
                religion: "",
                is_match: true,
                depth: 1,
                from_person: { person_id: personId, relationship: spouseRel },
                to_persons: [],
              },
            ]

            const generations = assignGenerations(path)
            const positions = calculatePositions(generations)

            const personPos = positions.get(personId)
            const spousePos = positions.get(spouseId)

            expect(personPos).toBeDefined()
            expect(spousePos).toBeDefined()

            if (personPos && spousePos) {
              // Same Y (same generation)
              expect(spousePos.y).toBe(personPos.y)
              // Different X (side by side)
              expect(spousePos.x).not.toBe(personPos.x)
            }
          },
        ),
        { numRuns: 100 },
      )
    })

    it("should produce valid React Flow nodes and edges", () => {
      fc.assert(
        fc.property(validPathArbitrary, ({ path, seekerId, matchId }) => {
          const result = transformMatchPath(path, seekerId, matchId)

          // Should have same number of nodes as path length
          expect(result.nodes.length).toBe(path.length)

          // Should have path.length - 1 edges
          expect(result.edges.length).toBe(path.length - 1)

          // Exactly one node should be seeker
          const seekerNodes = result.nodes.filter((n) => n.data.isSeeker)
          expect(seekerNodes.length).toBe(1)
          expect(seekerNodes[0].id).toBe(seekerId)

          // Exactly one node should be match
          const matchNodes = result.nodes.filter((n) => n.data.isMatch)
          expect(matchNodes.length).toBe(1)
          expect(matchNodes[0].id).toBe(matchId)

          // All nodes should have type 'matchPersonNode'
          for (const node of result.nodes) {
            expect(node.type).toBe("matchPersonNode")
          }

          // All edges should have type 'matchRelationshipEdge'
          for (const edge of result.edges) {
            expect(edge.type).toBe("matchRelationshipEdge")
          }
        }),
        { numRuns: 100 },
      )
    })

    it("should not have overlapping nodes in the same generation", () => {
      fc.assert(
        fc.property(validPathArbitrary, ({ path }) => {
          const generations = assignGenerations(path)
          const positions = calculatePositions(generations)

          // Group positions by Y coordinate (generation)
          const yToPositions = new Map<
            number,
            { x: number; personId: string }[]
          >()
          positions.forEach((pos, personId) => {
            const existing = yToPositions.get(pos.y) || []
            existing.push({ x: pos.x, personId })
            yToPositions.set(pos.y, existing)
          })

          // No two nodes in the same row should have the same X
          yToPositions.forEach((positionsInRow) => {
            const xValues = positionsInRow.map((p) => p.x)
            const uniqueXValues = new Set(xValues)
            expect(uniqueXValues.size).toBe(xValues.length)
          })
        }),
        { numRuns: 100 },
      )
    })
  })
})

// ============================================
// Unit Tests for Relationship Helpers and Edge Cases
// ============================================

describe("matchGraphTransformer - Unit Tests", () => {
  describe("Relationship Type Helpers", () => {
    it("isChildRelationship should return true for Son and Daughter", () => {
      expect(isChildRelationship("Son")).toBe(true)
      expect(isChildRelationship("Daughter")).toBe(true)
      expect(isChildRelationship("Father")).toBe(false)
      expect(isChildRelationship("Spouse")).toBe(false)
    })

    it("isParentRelationship should return true for Father and Mother", () => {
      expect(isParentRelationship("Father")).toBe(true)
      expect(isParentRelationship("Mother")).toBe(true)
      expect(isParentRelationship("Son")).toBe(false)
      expect(isParentRelationship("Spouse")).toBe(false)
    })

    it("isSpouseRelationship should return true for Spouse, Husband, Wife", () => {
      expect(isSpouseRelationship("Spouse")).toBe(true)
      expect(isSpouseRelationship("Husband")).toBe(true)
      expect(isSpouseRelationship("Wife")).toBe(true)
      expect(isSpouseRelationship("Father")).toBe(false)
      expect(isSpouseRelationship("Son")).toBe(false)
    })
  })

  describe("getEdgeHandles", () => {
    it("should return bottom/top for vertical downward edges", () => {
      const result = getEdgeHandles({ x: 0, y: 0 }, { x: 0, y: 100 })
      expect(result.sourceHandle).toBe("bottom")
      expect(result.targetHandle).toBe("top")
    })

    it("should return top/bottom for vertical upward edges", () => {
      const result = getEdgeHandles({ x: 0, y: 100 }, { x: 0, y: 0 })
      expect(result.sourceHandle).toBe("top")
      expect(result.targetHandle).toBe("bottom")
    })

    it("should return right/left for horizontal rightward edges", () => {
      const result = getEdgeHandles({ x: 0, y: 0 }, { x: 100, y: 0 })
      expect(result.sourceHandle).toBe("right")
      expect(result.targetHandle).toBe("left")
    })

    it("should return left/right for horizontal leftward edges", () => {
      const result = getEdgeHandles({ x: 100, y: 0 }, { x: 0, y: 0 })
      expect(result.sourceHandle).toBe("left")
      expect(result.targetHandle).toBe("right")
    })
  })

  describe("transformMatchPath", () => {
    it("should return empty nodes and edges for empty path", () => {
      const result = transformMatchPath([], "seeker", "match")
      expect(result.nodes).toEqual([])
      expect(result.edges).toEqual([])
    })

    it("should handle single-node path", () => {
      const path: MatchGraphNode[] = [
        {
          person_id: "person1",
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
      ]

      const result = transformMatchPath(path, "person1", "person1")

      expect(result.nodes.length).toBe(1)
      expect(result.edges.length).toBe(0)
      expect(result.nodes[0].data.isSeeker).toBe(true)
      expect(result.nodes[0].data.isMatch).toBe(true)
    })

    it("should correctly set isSeeker and isMatch flags", () => {
      const path: MatchGraphNode[] = [
        {
          person_id: "seeker",
          first_name: "Seeker",
          last_name: "Person",
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
          person_id: "middle",
          first_name: "Middle",
          last_name: "Person",
          birth_year: 1985,
          death_year: null,
          address: "",
          religion: "",
          is_match: false,
          depth: 1,
          from_person: { person_id: "seeker", relationship: "Father" },
          to_persons: [],
        },
        {
          person_id: "match",
          first_name: "Match",
          last_name: "Person",
          birth_year: 1992,
          death_year: null,
          address: "",
          religion: "",
          is_match: true,
          depth: 2,
          from_person: { person_id: "middle", relationship: "Spouse" },
          to_persons: [],
        },
      ]

      const result = transformMatchPath(path, "seeker", "match")

      const seekerNode = result.nodes.find((n) => n.id === "seeker")
      const middleNode = result.nodes.find((n) => n.id === "middle")
      const matchNode = result.nodes.find((n) => n.id === "match")

      expect(seekerNode?.data.isSeeker).toBe(true)
      expect(seekerNode?.data.isMatch).toBe(false)

      expect(middleNode?.data.isSeeker).toBe(false)
      expect(middleNode?.data.isMatch).toBe(false)

      expect(matchNode?.data.isSeeker).toBe(false)
      expect(matchNode?.data.isMatch).toBe(true)
    })
  })

  describe("assignGenerations - Complex Path", () => {
    it("should correctly assign generations for path: child → parent → spouse → child", () => {
      const path: MatchGraphNode[] = [
        {
          person_id: "child1",
          first_name: "Child1",
          last_name: "Person",
          birth_year: 2000,
          death_year: null,
          address: "",
          religion: "",
          is_match: false,
          depth: 0,
          from_person: null,
          to_persons: [],
        },
        {
          person_id: "parent",
          first_name: "Parent",
          last_name: "Person",
          birth_year: 1970,
          death_year: null,
          address: "",
          religion: "",
          is_match: false,
          depth: 1,
          from_person: { person_id: "child1", relationship: "Son" }, // child1 is Son of parent
          to_persons: [],
        },
        {
          person_id: "spouse",
          first_name: "Spouse",
          last_name: "Person",
          birth_year: 1972,
          death_year: null,
          address: "",
          religion: "",
          is_match: false,
          depth: 2,
          from_person: { person_id: "parent", relationship: "Spouse" },
          to_persons: [],
        },
        {
          person_id: "child2",
          first_name: "Child2",
          last_name: "Person",
          birth_year: 1995,
          death_year: null,
          address: "",
          religion: "",
          is_match: true,
          depth: 3,
          from_person: { person_id: "spouse", relationship: "Mother" }, // spouse is Mother of child2
          to_persons: [],
        },
      ]

      const generations = assignGenerations(path)
      const positions = calculatePositions(generations)

      // After normalization:
      // parent and spouse should be at generation 0 (oldest)
      // child1 and child2 should be at generation 1 (younger)
      expect(generations.get("parent")?.generation).toBe(0)
      expect(generations.get("spouse")?.generation).toBe(0)
      expect(generations.get("child1")?.generation).toBe(1)
      expect(generations.get("child2")?.generation).toBe(1)

      // Parent and spouse should have same Y
      expect(positions.get("parent")?.y).toBe(positions.get("spouse")?.y)

      // Children should have same Y (both in generation 1)
      expect(positions.get("child1")?.y).toBe(positions.get("child2")?.y)

      // Children should be below parents
      expect(positions.get("child1")!.y).toBeGreaterThan(
        positions.get("parent")!.y,
      )
    })
  })
})
