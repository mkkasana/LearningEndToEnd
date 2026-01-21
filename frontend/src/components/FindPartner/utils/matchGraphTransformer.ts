/**
 * Match Graph Transformer Utility
 * Transforms extracted path data into React Flow nodes and edges
 * Requirements: 5.1, 5.2, 5.3, 5.4
 */

import type {
  MatchEdge,
  MatchGenerationInfo,
  MatchNode,
  TransformedMatchPath,
} from "../types"
import type { MatchGraphNode } from "./matchPathExtractor"

// Layout constants
export const NODE_WIDTH = 180
export const NODE_HEIGHT = 200
export const HORIZONTAL_GAP = 100
export const VERTICAL_GAP = 150
export const SPOUSE_GAP = 50

/**
 * Check if relationship indicates going UP the tree (child → parent)
 * When from_person relationship is "Son" or "Daughter", we're going from child to parent
 */
export function isChildRelationship(rel: string): boolean {
  return ["Son", "Daughter"].includes(rel)
}

/**
 * Check if relationship indicates going DOWN the tree (parent → child)
 * When from_person relationship is "Father" or "Mother", we're going from parent to child
 */
export function isParentRelationship(rel: string): boolean {
  return ["Father", "Mother"].includes(rel)
}

/**
 * Check if relationship is a spouse relationship
 * Spouse relationships stay at the same generation level
 */
export function isSpouseRelationship(rel: string): boolean {
  return ["Spouse", "Husband", "Wife"].includes(rel)
}

/**
 * Assign generation levels and X-axis positions to each person in the path
 * Generation 0 is the oldest, increases downward
 * xOffset is calculated to keep related nodes close and avoid overlaps
 *
 * @param path - Array of MatchGraphNode from seeker to match
 * @returns Map of person_id to MatchGenerationInfo
 *
 * Requirements: 5.1, 5.2, 5.3, 5.4
 */
export function assignGenerations(
  path: MatchGraphNode[],
): Map<string, MatchGenerationInfo> {
  const generations = new Map<string, MatchGenerationInfo>()
  const generationToXAxis = new Map<number, number>() // Track max X per generation
  let currentGen = 0
  let currentXAxis = 0

  for (let i = 0; i < path.length; i++) {
    const node = path[i]
    const prevNode = i > 0 ? path[i - 1] : null
    const relationship = node.from_person?.relationship

    // Determine generation change based on relationship
    if (relationship) {
      if (isChildRelationship(relationship)) {
        // Going UP the tree (child → parent): generation decreases
        currentGen--
      } else if (isParentRelationship(relationship)) {
        // Going DOWN the tree (parent → child): generation increases
        currentGen++
      }
      // Spouse relationships stay at same generation
    }

    // Calculate X-axis position
    if (relationship) {
      if (
        isChildRelationship(relationship) ||
        isParentRelationship(relationship)
      ) {
        // Check if this generation already has nodes at or beyond currentXAxis
        const genXAxis = generationToXAxis.get(currentGen) ?? -1
        if (genXAxis >= currentXAxis) {
          // Shift right to avoid overlap with existing nodes in this generation
          currentXAxis = genXAxis + 1
        }
        // Update the generation's max X position
        generationToXAxis.set(currentGen, currentXAxis)
      } else if (isSpouseRelationship(relationship)) {
        // Spouse always shifts right (side-by-side positioning)
        currentXAxis++
        // Also update generation tracking to prevent overlaps with later nodes
        generationToXAxis.set(currentGen, currentXAxis)
      } else {
        // Unknown relationship, shift right to be safe
        currentXAxis++
        generationToXAxis.set(currentGen, currentXAxis)
      }
    } else {
      // First node (no relationship), set generation's X position
      generationToXAxis.set(currentGen, currentXAxis)
    }

    const isSpouse = isSpouseRelationship(relationship || "")

    generations.set(node.person_id, {
      personId: node.person_id,
      generation: currentGen,
      xOffset: currentXAxis,
      isSpouse,
      spouseOfId: isSpouse ? prevNode?.person_id : undefined,
    })
  }

  // Normalize generations (make minimum = 0)
  const genValues = Array.from(generations.values()).map((g) => g.generation)
  const minGen = Math.min(...genValues)

  generations.forEach((info) => {
    info.generation -= minGen
  })

  return generations
}

/**
 * Calculate pixel positions for all nodes based on generation levels and xOffset
 * - Y coordinate is determined by generation (row)
 * - X coordinate is determined by xOffset (column)
 *
 * @param generations - Map of person_id to MatchGenerationInfo
 * @returns Map of person_id to {x, y} position
 */
export function calculatePositions(
  generations: Map<string, MatchGenerationInfo>,
): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>()

  generations.forEach((info, id) => {
    const x = info.xOffset * (NODE_WIDTH + HORIZONTAL_GAP)
    const y = info.generation * (NODE_HEIGHT + VERTICAL_GAP)
    positions.set(id, { x, y })
  })

  return positions
}

/**
 * Edge handle positions
 */
export type HandlePosition = "top" | "bottom" | "left" | "right"

export interface EdgeHandles {
  sourceHandle: HandlePosition
  targetHandle: HandlePosition
}

/**
 * Determine the appropriate source and target handles based on node positions
 * This ensures edges connect from the most logical side of each node
 *
 * @param sourcePos - Position of source node
 * @param targetPos - Position of target node
 * @returns Object with sourceHandle and targetHandle positions
 */
export function getEdgeHandles(
  sourcePos: { x: number; y: number },
  targetPos: { x: number; y: number },
): EdgeHandles {
  const { x: sx, y: sy } = sourcePos
  const { x: tx, y: ty } = targetPos

  // Same column
  if (sx === tx) {
    if (sy < ty) {
      // Target is directly below source
      return { sourceHandle: "bottom", targetHandle: "top" }
    }
    // Target is directly above source
    return { sourceHandle: "top", targetHandle: "bottom" }
  }

  // Same row
  if (sy === ty) {
    if (sx < tx) {
      // Target is to the right of source
      return { sourceHandle: "right", targetHandle: "left" }
    }
    // Target is to the left of source
    return { sourceHandle: "left", targetHandle: "right" }
  }

  // Diagonal positions
  if (sx < tx) {
    // Target is to the right
    if (sy < ty) {
      // Target is south-east (below and right)
      return { sourceHandle: "bottom", targetHandle: "top" }
    }
    // Target is north-east (above and right)
    return { sourceHandle: "top", targetHandle: "left" }
  }
  // Target is to the left
  if (sy < ty) {
    // Target is south-west (below and left)
    return { sourceHandle: "bottom", targetHandle: "top" }
  }
  // Target is north-west (above and left)
  return { sourceHandle: "top", targetHandle: "right" }
}

/**
 * Main transformation function: converts path to React Flow nodes and edges
 *
 * @param path - Array of MatchGraphNode from seeker to match
 * @param seekerId - The seeker person ID
 * @param matchId - The selected match person ID
 * @returns TransformedMatchPath with nodes and edges for React Flow
 *
 * Requirements: 5.1, 5.2, 5.3, 5.4
 */
export function transformMatchPath(
  path: MatchGraphNode[],
  seekerId: string,
  matchId: string,
): TransformedMatchPath {
  if (path.length === 0) {
    return { nodes: [], edges: [] }
  }

  // Step 1: Assign generation levels
  const generations = assignGenerations(path)

  // Step 2: Calculate positions
  const positions = calculatePositions(generations)

  // Step 3: Create nodes
  const nodes: MatchNode[] = path.map((person) => ({
    id: person.person_id,
    type: "matchPersonNode" as const,
    position: positions.get(person.person_id) || { x: 0, y: 0 },
    data: {
      personId: person.person_id,
      firstName: person.first_name,
      lastName: person.last_name,
      birthYear: person.birth_year ?? null,
      deathYear: person.death_year ?? null,
      isSeeker: person.person_id === seekerId,
      isMatch: person.person_id === matchId,
    },
  }))

  // Step 4: Create edges
  const edges: MatchEdge[] = []
  for (let i = 0; i < path.length - 1; i++) {
    const source = path[i]
    const target = path[i + 1]
    // Find relationship from source's to_persons that points to target
    // This gives us "what target is to source" (e.g., "Father" if target is source's father)
    const toPersonConnection = source.to_persons?.find(
      (conn) => conn.person_id === target.person_id,
    )
    const relationship = toPersonConnection?.relationship || ""
    const isSpouse = isSpouseRelationship(relationship)

    // Get appropriate handles based on node positions
    const sourcePos = positions.get(source.person_id) || { x: 0, y: 0 }
    const targetPos = positions.get(target.person_id) || { x: 0, y: 0 }
    const { sourceHandle, targetHandle } = getEdgeHandles(sourcePos, targetPos)

    edges.push({
      id: `${source.person_id}-${target.person_id}`,
      source: source.person_id,
      target: target.person_id,
      sourceHandle,
      targetHandle,
      type: "matchRelationshipEdge",
      data: {
        relationship,
        isSpouseEdge: isSpouse,
      },
      animated: true,
    })
  }

  return { nodes, edges }
}
