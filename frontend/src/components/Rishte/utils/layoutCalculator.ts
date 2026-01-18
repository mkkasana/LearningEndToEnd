import type { GenerationInfo } from "../types"

// Layout constants
export const NODE_WIDTH = 180
export const NODE_HEIGHT = 200
export const HORIZONTAL_GAP = 100
export const VERTICAL_GAP = 150
export const SPOUSE_GAP = 50

/**
 * Sort nodes within a generation, placing spouses next to their partners
 */
function sortNodesInGeneration(
  nodeIds: string[],
  generations: Map<string, GenerationInfo>
): string[] {
  const nonSpouses: string[] = []
  const spouses: string[] = []

  for (const id of nodeIds) {
    const info = generations.get(id)
    if (info?.isSpouse) {
      spouses.push(id)
    } else {
      nonSpouses.push(id)
    }
  }

  // Build result: non-spouses first, then insert spouses after their partners
  const result: string[] = [...nonSpouses]

  for (const spouseId of spouses) {
    const info = generations.get(spouseId)
    if (info?.spouseOfId) {
      const partnerIndex = result.indexOf(info.spouseOfId)
      if (partnerIndex !== -1) {
        result.splice(partnerIndex + 1, 0, spouseId)
      } else {
        result.push(spouseId)
      }
    } else {
      result.push(spouseId)
    }
  }

  return result
}

/**
 * Calculate positions for all nodes based on generation levels
 * - Nodes in the same generation have the same Y coordinate
 * - Spouses are positioned side-by-side
 * - Children are positioned below parents
 */
export function calculatePositions(
  generations: Map<string, GenerationInfo>
): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>()

  // Group nodes by generation
  const genGroups = new Map<number, string[]>()
  generations.forEach((info, id) => {
    if (!genGroups.has(info.generation)) {
      genGroups.set(info.generation, [])
    }
    genGroups.get(info.generation)!.push(id)
  })

  // Calculate positions for each generation
  genGroups.forEach((nodeIds, gen) => {
    const y = gen * (NODE_HEIGHT + VERTICAL_GAP)

    // Sort nodes: non-spouses first, then spouses next to their partners
    const sorted = sortNodesInGeneration(nodeIds, generations)

    let currentX = 0
    for (const nodeId of sorted) {
      const info = generations.get(nodeId)!

      if (info.isSpouse && info.spouseOfId) {
        // Position spouse next to their partner with SPOUSE_GAP
        const spousePos = positions.get(info.spouseOfId)
        if (spousePos) {
          positions.set(nodeId, {
            x: spousePos.x + NODE_WIDTH + SPOUSE_GAP,
            y,
          })
          currentX = spousePos.x + NODE_WIDTH + SPOUSE_GAP + NODE_WIDTH + HORIZONTAL_GAP
        } else {
          positions.set(nodeId, { x: currentX, y })
          currentX += NODE_WIDTH + HORIZONTAL_GAP
        }
      } else {
        positions.set(nodeId, { x: currentX, y })
        currentX += NODE_WIDTH + HORIZONTAL_GAP
      }
    }
  })

  return positions
}

/**
 * Get the Y coordinate for a given generation level
 */
export function getGenerationY(generation: number): number {
  return generation * (NODE_HEIGHT + VERTICAL_GAP)
}

/**
 * Check if two nodes are at the same generation level based on their Y coordinates
 */
export function isSameGeneration(y1: number, y2: number): boolean {
  return y1 === y2
}

/**
 * Check if node1 is a parent of node2 based on Y coordinates
 * (parent has smaller Y, child has larger Y)
 */
export function isParentOf(parentY: number, childY: number): boolean {
  return parentY < childY
}

/**
 * Calculate the expected X offset for a spouse positioned next to their partner
 */
export function getSpouseXOffset(): number {
  return NODE_WIDTH + SPOUSE_GAP
}
