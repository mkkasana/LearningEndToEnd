import type {
  GenerationInfo,
  RishteNode,
  RishteEdge,
  TransformedPath,
} from "../types"
import { calculatePositions, getEdgeHandles } from "./layoutCalculator"
import type { LineagePathResponse, PersonNode as ApiPersonNode } from "@/client"

// Re-export layout constants for convenience
export {
  NODE_WIDTH,
  NODE_HEIGHT,
  HORIZONTAL_GAP,
  VERTICAL_GAP,
  SPOUSE_GAP,
} from "./layoutCalculator"

/**
 * Check if relationship indicates going UP the tree (child → parent)
 */
export function isChildRelationship(rel: string): boolean {
  return ["Son", "Daughter"].includes(rel)
}

/**
 * Check if relationship indicates going DOWN the tree (parent → child)
 */
export function isParentRelationship(rel: string): boolean {
  return ["Father", "Mother"].includes(rel)
}

/**
 * Check if relationship is a spouse relationship
 */
export function isSpouseRelationship(rel: string): boolean {
  return ["Spouse", "Husband", "Wife"].includes(rel)
}

/**
 * Build ordered path array from linked list graph structure
 * Starts from personAId and follows to_person pointers to build the path
 */
export function buildPathArray(
  graph: Record<string, ApiPersonNode>,
  personAId: string
): ApiPersonNode[] {
  const startNode = graph[personAId]

  if (!startNode) {
    return []
  }

  const path: ApiPersonNode[] = []
  let current: ApiPersonNode | undefined = startNode
  const visited = new Set<string>() // Prevent infinite loops

  while (current && !visited.has(current.person_id)) {
    visited.add(current.person_id)
    path.push(current)
    if (current.to_person && current.to_person.person_id) {
      current = graph[current.to_person.person_id]
    } else {
      current = undefined
    }
  }

  return path
}


/**
 * Assign generation levels and X-axis positions to each person in the path
 * Generation 0 is the oldest, increases downward
 * xOffset is calculated to keep related nodes close and avoid overlaps
 */
export function assignGenerations(
  path: ApiPersonNode[]
): Map<string, GenerationInfo> {
  const generations = new Map<string, GenerationInfo>()
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
      if (isChildRelationship(relationship) || isParentRelationship(relationship)) {
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
 * Create React Flow nodes from path data
 */
function createNodes(
  path: ApiPersonNode[],
  positions: Map<string, { x: number; y: number }>,
  personAId: string,
  personBId: string
): RishteNode[] {
  return path.map((person) => ({
    id: person.person_id,
    type: "personNode" as const,
    position: positions.get(person.person_id) || { x: 0, y: 0 },
    data: {
      personId: person.person_id,
      firstName: person.first_name,
      lastName: person.last_name,
      birthYear: person.birth_year ?? null,
      deathYear: person.death_year ?? null,
      isPersonA: person.person_id === personAId,
      isPersonB: person.person_id === personBId,
    },
  }))
}

/**
 * Create React Flow edges from path data
 */
function createEdges(
  path: ApiPersonNode[],
  positions: Map<string, { x: number; y: number }>
): RishteEdge[] {
  const edges: RishteEdge[] = []

  for (let i = 0; i < path.length - 1; i++) {
    const source = path[i]
    const target = path[i + 1]
    // Use source.to_person.relationship as it describes "what target is to source"
    const relationship = source.to_person?.relationship || ""
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
      type: "relationshipEdge",
      data: {
        relationship,
        isSpouseEdge: isSpouse,
      },
      animated: true,
    })
  }

  return edges
}

/**
 * Main transformation function: converts API response to React Flow elements
 */
export function transformApiResponse(
  response: LineagePathResponse,
  personAId: string,
  personBId: string
): TransformedPath {
  const graph = response.graph || {}
  
  if (!response.connection_found || Object.keys(graph).length === 0) {
    return { nodes: [], edges: [] }
  }

  // Step 1: Build ordered path array from linked list, starting from Person A
  const path = buildPathArray(graph, personAId)

  if (path.length === 0) {
    return { nodes: [], edges: [] }
  }

  // Step 2: Assign generation levels
  const generations = assignGenerations(path)

  // Step 3: Calculate positions
  const positions = calculatePositions(generations)

  // Step 4: Create React Flow elements
  const nodes = createNodes(path, positions, personAId, personBId)
  const edges = createEdges(path, positions)

  return { nodes, edges }
}

/**
 * Generate path summary string from path
 */
export function generatePathSummary(path: ApiPersonNode[]): string {
  return path.map((p) => p.first_name).join(" → ")
}

/**
 * Get person count from path
 */
export function getPersonCount(path: ApiPersonNode[]): number {
  return path.length
}
