import {
  BaseEdge,
  EdgeLabelRenderer,
  getBezierPath,
  getStraightPath,
  type EdgeProps,
} from "@xyflow/react"
import { memo } from "react"
import { cn } from "@/lib/utils"
import type { RelationshipEdgeData } from "./types"

type RelationshipEdgeProps = EdgeProps & {
  data?: RelationshipEdgeData
}

/**
 * RelationshipEdge component for React Flow graph
 * Displays relationship labels on edges with different styling for spouse vs parent-child
 * 
 * Requirements:
 * - 8.1: Display relationship label (Son, Daughter, Father, Mother, Spouse, etc.)
 * - 8.2: Vertical edges for parent-child relationships
 * - 8.3: Horizontal edges for spouse relationships
 * - 8.4: Arrow markers indicating direction
 * - 8.5: Distinct styling for spouse edges
 */
export const RelationshipEdge = memo(function RelationshipEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  markerEnd,
}: RelationshipEdgeProps) {
  const relationship = data?.relationship || ""
  const isSpouseEdge = data?.isSpouseEdge || false

  // Use straight path for spouse edges (horizontal), bezier for parent-child (vertical)
  const [edgePath, labelX, labelY] = isSpouseEdge
    ? getStraightPath({
        sourceX,
        sourceY,
        targetX,
        targetY,
      })
    : getBezierPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
      })

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd as string | undefined}
        className={cn(
          "!stroke-2",
          isSpouseEdge
            ? "!stroke-purple-400 dark:!stroke-purple-500"
            : "!stroke-muted-foreground"
        )}
        style={{
          strokeWidth: isSpouseEdge ? 3 : 2,
          strokeDasharray: isSpouseEdge ? "5,5" : undefined,
        }}
      />
      
      {/* Relationship label */}
      <EdgeLabelRenderer>
        <div
          className={cn(
            "absolute pointer-events-all nodrag nopan",
            "px-2 py-1 rounded-md text-xs font-medium",
            "transform -translate-x-1/2 -translate-y-1/2",
            isSpouseEdge
              ? "bg-purple-100 text-purple-700 dark:bg-purple-900/50 dark:text-purple-300 border border-purple-300 dark:border-purple-700"
              : "bg-background text-foreground border border-border shadow-sm"
          )}
          style={{
            left: labelX,
            top: labelY,
          }}
        >
          {relationship}
        </div>
      </EdgeLabelRenderer>
    </>
  )
})
