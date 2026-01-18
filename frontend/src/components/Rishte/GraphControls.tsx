import { useReactFlow } from "@xyflow/react"
import { Maximize2, Minus, Plus } from "lucide-react"
import { memo, useCallback } from "react"
import { Button } from "@/components/ui/button"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

/**
 * GraphControls component provides zoom and fit view controls for the React Flow graph
 * 
 * Requirements:
 * - 9.1: Support zooming in and out
 * - 9.2: Support panning/dragging (handled by React Flow)
 * - 9.3: Provide "Fit View" control to auto-fit the entire graph
 * - 9.4: Provide zoom controls (zoom in, zoom out buttons)
 */
export const GraphControls = memo(function GraphControls() {
  const { zoomIn, zoomOut, fitView } = useReactFlow()

  const handleZoomIn = useCallback(() => {
    zoomIn({ duration: 200 })
  }, [zoomIn])

  const handleZoomOut = useCallback(() => {
    zoomOut({ duration: 200 })
  }, [zoomOut])

  const handleFitView = useCallback(() => {
    fitView({ duration: 300, padding: 0.2 })
  }, [fitView])

  return (
    <TooltipProvider>
      <div className="flex items-center gap-1 p-1 bg-background border rounded-lg shadow-sm">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomIn}
              className="h-8 w-8 p-0"
              aria-label="Zoom in"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Zoom In</p>
          </TooltipContent>
        </Tooltip>

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleZoomOut}
              className="h-8 w-8 p-0"
              aria-label="Zoom out"
            >
              <Minus className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Zoom Out</p>
          </TooltipContent>
        </Tooltip>

        <div className="w-px h-6 bg-border" />

        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleFitView}
              className="h-8 w-8 p-0"
              aria-label="Fit view"
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top">
            <p>Fit View</p>
          </TooltipContent>
        </Tooltip>
      </div>
    </TooltipProvider>
  )
})
