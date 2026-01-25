import { useMutation } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { AlertCircle, GitBranch, Loader2, Search } from "lucide-react"
import { useCallback, useMemo, useState } from "react"
import { type LineagePathResponse, LineagePathService } from "@/client"
import { ActivePersonIndicator } from "@/components/Family/ActivePersonIndicator"
import { PersonDetailsPanel } from "@/components/FamilyTree/PersonDetailsPanel"
import {
  buildPathArray,
  generatePathSummary,
  getPersonCount,
  PathSummary,
  RishteGraph,
  transformApiResponse,
} from "@/components/Rishte"
import { RishtePersonButton } from "@/components/Rishte/RishtePersonButton"
import { RishtePersonSearchDialog } from "@/components/Rishte/RishtePersonSearchDialog"
import type { SelectedPerson } from "@/components/Rishte/types"
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
 * - 2.1: Display two Person_Buttons labeled "Select Person A" and "Select Person B"
 * - 7.1: Find button disabled when Person A not selected
 * - 7.2: Find button disabled when Person B not selected
 * - 7.3: Find button enabled when both selected
 * - 7.4: Call lineage-path API with selected person IDs
 */
function RishtePage() {
  // Person selection state (using SelectedPerson objects)
  const [selectedPersonA, setSelectedPersonA] = useState<SelectedPerson | null>(
    null,
  )
  const [selectedPersonB, setSelectedPersonB] = useState<SelectedPerson | null>(
    null,
  )

  // Wizard dialog state
  const [wizardOpen, setWizardOpen] = useState(false)
  const [wizardTarget, setWizardTarget] = useState<"A" | "B">("A")

  // PersonDetailsPanel state
  const [detailsPanelPersonId, setDetailsPanelPersonId] = useState<string | null>(null)
  const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(false)

  // API response state
  const [apiResponse, setApiResponse] = useState<LineagePathResponse | null>(
    null,
  )

  // Find relationship mutation
  const findRelationshipMutation = useMutation({
    mutationFn: async () => {
      if (!selectedPersonA || !selectedPersonB) {
        throw new Error("Both persons must be selected")
      }
      const response = await LineagePathService.findLineagePath({
        requestBody: {
          person_a_id: selectedPersonA.personId,
          person_b_id: selectedPersonB.personId,
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
    if (selectedPersonA && selectedPersonB) {
      findRelationshipMutation.mutate()
    }
  }, [selectedPersonA, selectedPersonB, findRelationshipMutation])

  // Handle opening wizard for Person A
  const handleSelectPersonA = useCallback(() => {
    setWizardTarget("A")
    setWizardOpen(true)
  }, [])

  // Handle opening wizard for Person B
  const handleSelectPersonB = useCallback(() => {
    setWizardTarget("B")
    setWizardOpen(true)
  }, [])

  // Handle clearing Person A selection
  const handleClearPersonA = useCallback(() => {
    setSelectedPersonA(null)
    setApiResponse(null)
  }, [])

  // Handle clearing Person B selection
  const handleClearPersonB = useCallback(() => {
    setSelectedPersonB(null)
    setApiResponse(null)
  }, [])

  // Handle person selection from wizard
  const handlePersonSelect = useCallback(
    (person: SelectedPerson) => {
      if (wizardTarget === "A") {
        setSelectedPersonA(person)
      } else {
        setSelectedPersonB(person)
      }
      setApiResponse(null)
    },
    [wizardTarget],
  )

  // Handle View button click on PersonNode - opens PersonDetailsPanel
  const handleViewClick = useCallback((personId: string) => {
    setDetailsPanelPersonId(personId)
    setIsDetailsPanelOpen(true)
  }, [])

  // Check if Find button should be enabled
  // Requirements: 7.1, 7.2, 7.3 - Button enabled only when both persons are selected
  const isFindButtonEnabled =
    selectedPersonA !== null && selectedPersonB !== null

  // Get person IDs for graph transformation
  const personAId = selectedPersonA?.personId ?? null
  const personBId = selectedPersonB?.personId ?? null

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
      {/* Active Person Indicator - Shows when assuming another person's role */}
      <ActivePersonIndicator />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-3">
        <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-primary/10 shrink-0">
          <GitBranch className="h-5 w-5 text-primary" />
        </div>
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight">
            Rishte
          </h1>
          <p className="text-sm sm:text-base text-muted-foreground">
            Discover how two people are connected through their family lineage
          </p>
        </div>
      </div>

      {/* Person Selection */}
      {/* Requirements: 2.1, 10.2 - Stack Person buttons vertically on smaller screens */}
      <Card className="p-3 sm:p-4">
        <div className="flex flex-col gap-3 sm:gap-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 sm:gap-4">
            <RishtePersonButton
              label="A"
              selectedPerson={selectedPersonA}
              onSelect={handleSelectPersonA}
              onClear={handleClearPersonA}
            />
            <RishtePersonButton
              label="B"
              selectedPerson={selectedPersonB}
              onSelect={handleSelectPersonB}
              onClear={handleClearPersonB}
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

      {/* Person Search Wizard Dialog */}
      <RishtePersonSearchDialog
        open={wizardOpen}
        onOpenChange={setWizardOpen}
        personLabel={wizardTarget}
        onPersonSelect={handlePersonSelect}
      />

      {/* Loading State */}
      {isLoading && (
        <div className="flex flex-col items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="mt-4 text-muted-foreground">
            Searching for connection...
          </p>
        </div>
      )}

      {/* Error State */}
      {error && !isLoading && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>
            {error instanceof Error
              ? error.message
              : "Failed to find relationship. Please try again."}
          </AlertDescription>
        </Alert>
      )}

      {/* No Connection State */}
      {showNoConnection && !isLoading && (
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>No Connection Found</AlertTitle>
          <AlertDescription>
            {apiResponse.message ||
              "These two persons do not appear to be connected through family relationships."}
          </AlertDescription>
        </Alert>
      )}

      {/* Path Summary */}
      {pathSummaryData && showGraph && !isLoading && (
        <PathSummary
          personCount={pathSummaryData.personCount}
          pathSummary={pathSummaryData.pathSummary}
        />
      )}

      {/* Graph */}
      {showGraph && !isLoading && (
        <div className="flex-1 min-h-[400px] border rounded-lg overflow-hidden">
          <RishteGraph
            nodes={transformedPath.nodes}
            edges={transformedPath.edges}
            onNodeViewClick={handleViewClick}
          />
        </div>
      )}

      {/* Empty State - No search performed yet */}
      {!isLoading && !error && !apiResponse && (
        <div className="flex flex-col items-center justify-center py-8 sm:py-12 text-center px-4">
          <div className="rounded-full bg-muted p-3 sm:p-4 mb-3 sm:mb-4">
            <GitBranch className="h-6 w-6 sm:h-8 sm:w-8 text-muted-foreground" />
          </div>
          <h3 className="text-base sm:text-lg font-semibold">
            Find Family Connections
          </h3>
          <p className="text-sm sm:text-base text-muted-foreground max-w-md">
            Select two persons above and click "Find Relationship" to discover
            how they are connected through their family lineage.
          </p>
        </div>
      )}

      {/* Person Details Panel - Slides in from right when View button is clicked */}
      <PersonDetailsPanel
        personId={detailsPanelPersonId}
        open={isDetailsPanelOpen}
        onOpenChange={setIsDetailsPanelOpen}
      />
    </div>
  )
}
