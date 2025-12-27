import { cn } from "@/lib/utils"

export type RelationshipLineType = 'parent-child' | 'spouse' | 'sibling'

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
 * RelationshipLines component renders SVG lines showing relationships between people
 * 
 * Supports three types of relationships:
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
