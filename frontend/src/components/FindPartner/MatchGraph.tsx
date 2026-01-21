/**
 * MatchGraph Component
 * React Flow container for rendering the match path visualization
 *
 * Requirements:
 * - 8.1: Support zooming in and out
 * - 8.2: Support panning/dragging to navigate the graph
 * - 8.3: Provide "Fit View" control to auto-fit the entire graph
 * - 8.4: Provide zoom controls (zoom in, zoom out buttons)
 * - 8.5: Automatically fit the view to show all nodes on render
 */

import {
  Background,
  BackgroundVariant,
  MarkerType,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
  useReactFlow,
} from "@xyflow/react"
import "@xyflow/react/dist/style.css"
import { memo, useEffect } from "react"
import { MatchGraphControls } from "./MatchGraphControls"
import { MatchPersonNode } from "./MatchPersonNode"
import { MatchRelationshipEdge } from "./MatchRelationshipEdge"
import type { MatchEdge, MatchGraphProps, MatchNode } from "./types"

// Custom node types for React Flow
const nodeTypes = {
  matchPersonNode: MatchPersonNode,
}

// Custom edge types for React Flow
const edgeTypes = {
  matchRelationshipEdge: MatchRelationshipEdge,
}

// Default edge options with arrow marker
const defaultEdgeOptions = {
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 20,
    height: 20,
  },
}

interface MatchGraphInnerProps {
  nodes: MatchNode[]
  edges: MatchEdge[]
}

/**
 * Inner graph component that uses React Flow hooks
 * Must be wrapped in ReactFlowProvider
 */
const MatchGraphInner = memo(function MatchGraphInner({
  nodes: initialNodes,
  edges: initialEdges,
}: MatchGraphInnerProps) {
  const { fitView } = useReactFlow()
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges)

  // Update nodes and edges when props change
  useEffect(() => {
    setNodes(initialNodes)
    setEdges(initialEdges)
  }, [initialNodes, initialEdges, setNodes, setEdges])

  // Auto-fit view on initial render and when nodes change
  // Requirements: 8.5 - Auto-fit view on initial render
  useEffect(() => {
    if (nodes.length > 0) {
      const timer = setTimeout(() => {
        fitView({ duration: 300, padding: 0.2 })
      }, 200)
      return () => clearTimeout(timer)
    }
  }, [nodes.length, fitView])

  return (
    <div className="relative" style={{ width: "100%", height: "500px" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        defaultEdgeOptions={defaultEdgeOptions}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        className="bg-background"
        style={{ width: "100%", height: "100%" }}
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          className="!bg-muted/30"
        />
      </ReactFlow>

      {/* Graph controls positioned at bottom-right */}
      <div className="absolute bottom-4 right-4 z-10">
        <MatchGraphControls />
      </div>
    </div>
  )
})

/**
 * MatchGraph component - Main React Flow container for match path visualization
 *
 * Requirements:
 * - 5.1: Render persons of the same generation on the same horizontal level
 * - 5.2: Position spouse/husband/wife pairs side-by-side on the same level
 * - 5.3: Position children below their parents
 * - 8.1: Support zooming in and out
 * - 8.2: Support panning/dragging to navigate the graph
 * - 8.3: Provide "Fit View" control to auto-fit the entire graph
 * - 8.4: Provide zoom controls (zoom in, zoom out buttons)
 * - 8.5: Automatically fit the view to show all nodes on render
 */
export const MatchGraph = memo(function MatchGraph({
  nodes,
  edges,
}: MatchGraphProps) {
  return (
    <ReactFlowProvider>
      <MatchGraphInner nodes={nodes} edges={edges} />
    </ReactFlowProvider>
  )
})
