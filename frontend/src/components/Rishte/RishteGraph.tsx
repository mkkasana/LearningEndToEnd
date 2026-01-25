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
import { memo, useCallback, useEffect, useMemo } from "react"
import { GraphControls } from "./GraphControls"
import { PersonNode } from "./PersonNode"
import { RelationshipEdge } from "./RelationshipEdge"
import type { RishteEdge, RishteNode } from "./types"

// Custom node types for React Flow
const nodeTypes = {
  personNode: PersonNode,
}

// Custom edge types for React Flow
const edgeTypes = {
  relationshipEdge: RelationshipEdge,
}

// Default edge options with arrow marker
const defaultEdgeOptions = {
  markerEnd: {
    type: MarkerType.ArrowClosed,
    width: 20,
    height: 20,
  },
}

interface RishteGraphInnerProps {
  nodes: RishteNode[]
  edges: RishteEdge[]
}

/**
 * Inner graph component that uses React Flow hooks
 * Must be wrapped in ReactFlowProvider
 */
const RishteGraphInner = memo(function RishteGraphInner({
  nodes: initialNodes,
  edges: initialEdges,
}: RishteGraphInnerProps) {
  const { fitView } = useReactFlow()
  const [nodes, setNodes, onNodesChange] =
    useNodesState<RishteNode>(initialNodes)
  const [edges, setEdges, onEdgesChange] =
    useEdgesState<RishteEdge>(initialEdges)

  // Update nodes and edges when props change
  useEffect(() => {
    setNodes(initialNodes)
    setEdges(initialEdges)
  }, [initialNodes, initialEdges, setNodes, setEdges])

  // Auto-fit view on initial render and when nodes change
  // Requirements: 9.5 - Auto-fit view on initial render
  useEffect(() => {
    if (nodes.length > 0) {
      const timer = setTimeout(() => {
        fitView({ duration: 300, padding: 0.2 })
      }, 200)
      return () => clearTimeout(timer)
    }
  }, [nodes.length, fitView])

  // Prevent node dragging for cleaner visualization
  const onNodeDragStart = useCallback(() => {}, [])

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
        onNodeDragStart={onNodeDragStart}
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
        <GraphControls />
      </div>
    </div>
  )
})

interface RishteGraphProps {
  nodes: RishteNode[]
  edges: RishteEdge[]
  onNodeViewClick?: (personId: string) => void
}

/**
 * RishteGraph component - Main React Flow container for relationship visualization
 *
 * Requirements:
 * - 6.1: Render persons of the same generation on the same horizontal level
 * - 6.2: Position spouse/husband/wife pairs side-by-side
 * - 6.3: Position children below their parents
 * - 6.4: Position siblings horizontally spread within their generation level
 * - 6.5: Display connected family trees side-by-side with spouse connection
 * - 9.1: Support zooming in and out
 * - 9.2: Support panning/dragging to navigate the graph
 * - 9.3: Provide "Fit View" control to auto-fit the entire graph
 * - 9.4: Provide zoom controls (zoom in, zoom out buttons)
 * - 9.5: Automatically fit the view to show all nodes on render
 */
export const RishteGraph = memo(function RishteGraph({
  nodes,
  edges,
  onNodeViewClick,
}: RishteGraphProps) {
  // Inject onViewClick callback into each node's data
  const nodesWithCallback = useMemo(() => {
    if (!onNodeViewClick) return nodes

    return nodes.map((node) => ({
      ...node,
      data: {
        ...node.data,
        onViewClick: onNodeViewClick,
      },
    }))
  }, [nodes, onNodeViewClick])

  return (
    <ReactFlowProvider>
      <RishteGraphInner nodes={nodesWithCallback} edges={edges} />
    </ReactFlowProvider>
  )
})
