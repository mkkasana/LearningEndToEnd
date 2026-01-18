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
 */
export function getEdgeHandles(
  sourcePos: { x: number; y: number },
  targetPos: { x: number; y: number }
): EdgeHandles {
  const { x: sx, y: sy } = sourcePos
  const { x: tx, y: ty } = targetPos

  // Same column
  if (sx === tx) {
    if (sy < ty) {
      // Target is directly below source
      return { sourceHandle: "bottom", targetHandle: "top" }
    } else {
      // Target is directly above source
      return { sourceHandle: "top", targetHandle: "bottom" }
    }
  }

  // Same row
  if (sy === ty) {
    if (sx < tx) {
      // Target is to the right of source
      return { sourceHandle: "right", targetHandle: "left" }
    } else {
      // Target is to the left of source
      return { sourceHandle: "left", targetHandle: "right" }
    }
  }

  // Diagonal positions
  if (sx < tx) {
    // Target is to the right
    if (sy < ty) {
      // Target is south-east (below and right)
      return { sourceHandle: "bottom", targetHandle: "top" }
    } else {
      // Target is north-east (above and right)
      return { sourceHandle: "top", targetHandle: "left" }
    }
  } else {
    // Target is to the left
    if (sy < ty) {
      // Target is south-west (below and left)
      return { sourceHandle: "bottom", targetHandle: "top" }
    } else {
      // Target is north-west (above and left)
      return { sourceHandle: "top", targetHandle: "right" }
    }
  }
}
