import { cn } from "@/lib/utils"

export type RelationshipLineType = 'parent-child' | 'spouse' | 'sibling' | 'generation'

export interface Position {
  x: number
  y: number
}

export interface RelationshipLinesProps {
  type: RelationshipLineType
  fromPosition: Position
  toPosition: Position
  className?: string
}

export interface GenerationLinesProps {
  connections: Array<{
    from: Position
    to: Position
  }>
  className?: string
}

/**
 * Calculate SVG path for generation connecting lines
 * Creates vertical lines from one generation to another
 */
function calculateGenerationPath(from: Position, to: Position): string {
  // Simple vertical line from parent row to child row
  return `M ${from.x} ${from.y} L ${to.x} ${to.y}`
}

/**
 * Calculate SVG path for parent-child relationship
 * Creates a vertical line with a horizontal branch at the top
 */
function calculateParentChildPath(from: Position, to: Position): string {
  // Vertical line from parent to child
  // We'll use a simple straight line for now, can be enhanced with curves
  const midY = (from.y + to.y) / 2
  
  // Path: Start at parent bottom, go down to midpoint, then to child top
  return `M ${from.x} ${from.y} L ${from.x} ${midY} L ${to.x} ${midY} L ${to.x} ${to.y}`
}

/**
 * Calculate SVG path for spouse relationship
 * Creates a horizontal line between spouses
 */
function calculateSpousePath(from: Position, to: Position): string {
  // Simple horizontal line
  return `M ${from.x} ${from.y} L ${to.x} ${to.y}`
}

/**
 * Calculate SVG path for sibling relationship
 * Creates lines showing shared parent connection
 */
function calculateSiblingPath(from: Position, to: Position): string {
  // For siblings, we show a connection through their shared parent
  // This creates an inverted U shape
  const midY = Math.min(from.y, to.y) - 30 // Go up 30px above the higher sibling
  
  // Path: Start at first sibling, go up, across, then down to second sibling
  return `M ${from.x} ${from.y} L ${from.x} ${midY} L ${to.x} ${midY} L ${to.x} ${to.y}`
}

/**
 * Get line style based on relationship type
 */
function getLineStyle(type: RelationshipLineType): {
  stroke: string
  strokeWidth: number
  strokeDasharray?: string
} {
  switch (type) {
    case 'generation':
      return {
        stroke: 'currentColor',
        strokeWidth: 2,
      }
    case 'parent-child':
      return {
        stroke: 'currentColor',
        strokeWidth: 2,
      }
    case 'spouse':
      return {
        stroke: 'currentColor',
        strokeWidth: 2,
        strokeDasharray: '5,5', // Dashed line for spouse
      }
    case 'sibling':
      return {
        stroke: 'currentColor',
        strokeWidth: 1,
        strokeDasharray: '3,3', // Dotted line for siblings
      }
  }
}

/**
 * Calculate the bounding box for the SVG container
 */
function calculateViewBox(from: Position, to: Position, type: RelationshipLineType): {
  x: number
  y: number
  width: number
  height: number
} {
  const minX = Math.min(from.x, to.x)
  const maxX = Math.max(from.x, to.x)
  const minY = Math.min(from.y, to.y)
  const maxY = Math.max(from.y, to.y)
  
  // Add padding
  const padding = type === 'sibling' ? 40 : 20
  
  return {
    x: minX - padding,
    y: minY - padding,
    width: maxX - minX + padding * 2,
    height: maxY - minY + padding * 2,
  }
}

/**
 * Calculate bounding box for multiple connections
 */
function calculateMultiViewBox(connections: Array<{ from: Position; to: Position }>): {
  x: number
  y: number
  width: number
  height: number
} {
  if (connections.length === 0) {
    return { x: 0, y: 0, width: 0, height: 0 }
  }
  
  let minX = Infinity
  let maxX = -Infinity
  let minY = Infinity
  let maxY = -Infinity
  
  connections.forEach(({ from, to }) => {
    minX = Math.min(minX, from.x, to.x)
    maxX = Math.max(maxX, from.x, to.x)
    minY = Math.min(minY, from.y, to.y)
    maxY = Math.max(maxY, from.y, to.y)
  })
  
  const padding = 20
  
  return {
    x: minX - padding,
    y: minY - padding,
    width: maxX - minX + padding * 2,
    height: maxY - minY + padding * 2,
  }
}

/**
 * RelationshipLines component renders SVG lines showing relationships between people
 * 
 * Supports four types of relationships:
 * - generation: Vertical lines connecting generations (parents to children)
 * - parent-child: Vertical lines with branches
 * - spouse: Horizontal dashed lines
 * - sibling: Lines showing shared parent connection
 */
export function RelationshipLines({
  type,
  fromPosition,
  toPosition,
  className,
}: RelationshipLinesProps) {
  // Calculate the path based on relationship type
  let path: string
  switch (type) {
    case 'generation':
      path = calculateGenerationPath(fromPosition, toPosition)
      break
    case 'parent-child':
      path = calculateParentChildPath(fromPosition, toPosition)
      break
    case 'spouse':
      path = calculateSpousePath(fromPosition, toPosition)
      break
    case 'sibling':
      path = calculateSiblingPath(fromPosition, toPosition)
      break
  }
  
  const lineStyle = getLineStyle(type)
  const viewBox = calculateViewBox(fromPosition, toPosition, type)
  
  return (
    <svg
      className={cn(
        "absolute pointer-events-none text-muted-foreground/30",
        className
      )}
      style={{
        left: viewBox.x,
        top: viewBox.y,
        width: viewBox.width,
        height: viewBox.height,
      }}
      viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`}
      preserveAspectRatio="none"
    >
      <path
        d={path}
        fill="none"
        stroke={lineStyle.stroke}
        strokeWidth={lineStyle.strokeWidth}
        strokeDasharray={lineStyle.strokeDasharray}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

/**
 * GenerationLines component renders multiple vertical lines connecting generations
 * Used for connecting parents to children across rows
 * 
 * Requirements: 3.3, 6.2
 */
export function GenerationLines({
  connections,
  className,
}: GenerationLinesProps) {
  if (connections.length === 0) {
    return null
  }
  
  const lineStyle = getLineStyle('generation')
  const viewBox = calculateMultiViewBox(connections)
  
  return (
    <svg
      className={cn(
        "absolute pointer-events-none text-muted-foreground/30 z-0",
        className
      )}
      style={{
        left: viewBox.x,
        top: viewBox.y,
        width: viewBox.width,
        height: viewBox.height,
      }}
      viewBox={`${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`}
      preserveAspectRatio="none"
    >
      {connections.map((connection, index) => {
        const path = calculateGenerationPath(connection.from, connection.to)
        return (
          <path
            key={index}
            d={path}
            fill="none"
            stroke={lineStyle.stroke}
            strokeWidth={lineStyle.strokeWidth}
            strokeDasharray={lineStyle.strokeDasharray}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        )
      })}
    </svg>
  )
}
