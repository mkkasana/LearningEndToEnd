import type { GenerationInfo } from "../types"

// Layout constants
export const NODE_WIDTH = 180
export const NODE_HEIGHT = 200
export const HORIZONTAL_GAP = 100
export const VERTICAL_GAP = 150
export const SPOUSE_GAP = 50

/**
 * Calculate pixel positions for all nodes based on generation levels and xOffset
 * - Y coordinate is determined by generation (row)
 * - X coordinate is determined by xOffset (column)
 */
export function calculatePositions(
  generations: Map<string, GenerationInfo>
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
