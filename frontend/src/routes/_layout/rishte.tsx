import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { AlertCircle, GitBranch, Loader2, Search } from "lucide-react"
import { useState, useCallback, useMemo } from "react"
import { LineagePathService, type LineagePathResponse } from "@/client"
import {
  PersonSelector,
  PathSummary,
  RishteGraph,
  transformApiResponse,
  buildPathArray,
  generatePathSummary,
  getPersonCount,
} from "@/components/Rishte"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

export const Route = createFileRoute("/_layout/rishte" as any)({
  component: RishtePage,
  head: () => ({
    meta: [
      {
        title: "Rishte - Relationship Visualizer",
      },
    ],
  }),
})

/**
 * RishtePage - Main page for visualizing relationship paths between two persons
 * 
 * Requirements:
 * - 3.1: Display two PersonSelector components labeled "Person A" and "Person B"
 * - 3.5: Display "Find Relationship" button enabled only when both persons are selected
 * - 3.6: Call /lineage-path/find API when button is clicked
 * - 4.1: Display loading indicator while API is loading
 * - 4.2: Display error message if API returns an error
 * - 4.3: Display "No connection found" message if no connection exists
 * - 4.4: Render Lineage_Graph when connection is found
 */
function RishtePage() {
  // Person selection state (simplified to just store person IDs)
  const [personAId, setPersonAId] = useState<string | null>(null)
  const [personBId, setPersonBId] = useState<string | null>(null)

  // API response state
  const [apiResponse, setApiResponse] = useState<LineagePathResponse | null>(null)

  // Find relationship mutation
  const findRelationshipMutation = useMutation({
    mutationFn: async () => {
      if (!personAId || !personBId) {
        throw new Error("Both person IDs must be entered")
      }
      const response = await LineagePathService.findLineagePath({
        requestBody: {
          person_a_id: personAId,
          person_b_id: personBId,
        },
      })
      return response
    },
    onSuccess: (data) => {
      setApiResponse(data)
    },
    onError: () => {
      setApiResponse(null)
    },
  })

  // Handle find relationship button click
  const handleFindRelationship = useCallback(() => {
    if (personAId && personBId) {
      findRelationshipMutation.mutate()
    }
  }, [personAId, personBId, findRelationshipMutation])

  // Handle person A change - reset results when selection changes
  const handlePersonAChange = useCallback((personId: string | null) => {
    setPersonAId(personId)
    setApiResponse(null)
  }, [])

  // Handle person B change - reset results when selection changes
  const handlePersonBChange = useCallback((personId: string | null) => {
    setPersonBId(personId)
    setApiResponse(null)
  }, [])

  // Check if Find button should be enabled
  // Requirements: 3.5 - Button enabled only when both persons are selected
  const isFindButtonEnabled = personAId !== null && personBId !== null

  // Transform API response to React Flow elements
  const transformedPath = useMemo(() => {
    if (!apiResponse?.connection_found || !personAId || !personBId) {
      return null
    }
    return transformApiResponse(apiResponse, personAId, personBId)
  }, [apiResponse, personAId, personBId])

  // Generate path summary
  const pathSummaryData = useMemo(() => {
    if (!apiResponse?.connection_found || !apiResponse.graph || !personAId) {
      return null
    }
    const path = buildPathArray(apiResponse.graph, personAId)
    return {
      personCount: getPersonCount(path),
      pathSummary: generatePathSummary(path),
    }
  }, [apiResponse, personAId])

  const isLoading = findRelationshipMutation.isPending
  const error = findRelationshipMutation.error
  const showNoConnection = apiResponse && !apiResponse.connection_found
  const showGraph = transformedPath && transformedPath.nodes.length > 0

  return (
    <div className="flex flex-col gap-4 sm:gap-6 h-full">
      {/* Header */}
      {/* Requirements: 10.1 - Responsive design for desktop and tablet */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
        <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-primary/10 shrink-0">
          <GitBranch className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">Rishte</h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Discover how two people are connected through their family lineage
          </p>
        </div>
      </div>

      {/* Person Selection */}
      {/* Requirements: 10.2 - Stack PersonSelectors vertically on smaller screens */}
      <Card className="p-3 sm:p-4">
        <div className="flex flex-col gap-3 sm:gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
            <PersonSelector
              label="Person A"
              value={personAId}
              onChange={handlePersonAChange}
              placeholder="Enter Person A's ID (UUID)..."
            />
            <PersonSelector
              label="Person B"
              value={personBId}
              onChange={handlePersonBChange}
              placeholder="Enter Person B's ID (UUID)..."
            />
          </div>
          
          <div className="flex justify-center">
            <Button
              onClick={handleFindRelationship}
              disabled={!isFindButtonEnabled || isLoading}
              className="w-full sm:w-auto sm:min-w-[200px]"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Finding...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Find Relationship
                </>
              )}
            </Button>
          </div>
        </div>
      </Card>

      {/* Loading State */}
      {/* Requirements: 4.1 - Display loading indicator */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="mt-4 text-muted-foreground">
            Searching for connection...
          </p>
        </div>
      )}

      {/* Error State */}
      {/* Requirements: 4.2 - Display error message */}
      {error && !isLoading && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error instanceof Error ? error.message : "Failed to find relationship. Please try again."}
          </AlertDescription>
        </Alert>
      )}

      {/* No Connection State */}
      {/* Requirements: 4.3 - Display "No connection found" message */}
      {showNoConnection && !isLoading && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>No Connection Found</AlertTitle>
          <AlertDescription>
            {apiResponse.message || "These two persons do not appear to be connected through family relationships."}
          </AlertDescription>
        </Alert>
      )}

      {/* Path Summary */}
      {/* Requirements: 11.1, 11.2 - Display path summary */}
      {pathSummaryData && showGraph && !isLoading && (
        <PathSummary
          personCount={pathSummaryData.personCount}
          pathSummary={pathSummaryData.pathSummary}
        />
      )}

      {/* Graph */}
      {/* Requirements: 4.4 - Render Lineage_Graph when connection found */}
      {/* Requirements: 10.3 - Graph fills available viewport space */}
      {showGraph && !isLoading && (
        <div className="flex-1 min-h-[400px] border rounded-lg overflow-hidden">
          <RishteGraph
            nodes={transformedPath.nodes}
            edges={transformedPath.edges}
          />
        </div>
      )}

      {/* Empty State - No search performed yet */}
      {!isLoading && !error && !apiResponse && (
        <div className="flex flex-col items-center justify-center py-8 sm:py-12 text-center px-4">
          <div className="rounded-full bg-muted p-3 sm:p-4 mb-3 sm:mb-4">
            <GitBranch className="h-6 w-6 sm:h-8 sm:w-8 text-muted-foreground" />
          </div>
          <h3 className="text-base sm:text-lg font-semibold">Find Family Connections</h3>
          <p className="text-sm sm:text-base text-muted-foreground max-w-md">
            Select two persons above and click "Find Relationship" to discover how they are connected through their family lineage.
          </p>
        </div>
      )}
    </div>
  )
}
