import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { AlertCircle, Loader2, Search } from "lucide-react"
import { useEffect, useRef, useState } from "react"
import type { PersonDetails } from "@/client"
import { ProfileService } from "@/client"
import { ActivePersonIndicator } from "@/components/Family/ActivePersonIndicator"
import { AddFamilyMemberDialog } from "@/components/Family/AddFamilyMemberDialog"
import { DiscoverFamilyMembersDialog } from "@/components/Family/DiscoverFamilyMembersDialog"
import { ChildrenSection } from "@/components/FamilyTree/ChildrenSection"
import { HorizontalScrollRow } from "@/components/FamilyTree/HorizontalScrollRow"
import { ParentsSection } from "@/components/FamilyTree/ParentsSection"
import { PersonDetailsPanel } from "@/components/FamilyTree/PersonDetailsPanel"
import { RowConnector } from "@/components/FamilyTree/RowConnector"
import { SearchPersonDialog } from "@/components/FamilyTree/SearchPersonDialog"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import { useFamilyTreeData } from "@/hooks/useFamilyTreeData"

export const Route = createFileRoute("/_layout/family-tree")({
  component: FamilyTreeView,
  head: () => ({
    meta: [
      {
        title: "Family Tree View - FastAPI Cloud",
      },
    ],
  }),
})

function FamilyTreeView() {
  const queryClient = useQueryClient()
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null)
  const [isSearchDialogOpen, setIsSearchDialogOpen] = useState(false)
  // State for PersonDetailsPanel - Requirements: 1.1, 2.1
  const [detailsPanelPersonId, setDetailsPanelPersonId] = useState<
    string | null
  >(null)
  const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(false)
  // State for Add Family Member flow - Requirements: 2.1, 3.1
  const [showDiscoveryDialog, setShowDiscoveryDialog] = useState(false)
  const [showAddDialog, setShowAddDialog] = useState(false)
  const treeContainerRef = useRef<HTMLDivElement>(null)
  const selectedPersonRef = useRef<HTMLDivElement>(null)

  // Check if user has a person profile
  const { data: profileStatus } = useQuery({
    queryKey: ["profileCompletion"],
    queryFn: () => ProfileService.getProfileCompletionStatus(),
  })

  // Get the current user's person from ActivePersonContext
  // _Requirements: 7.1_
  const { activePerson, activePersonId, isLoading: isPersonLoading, isAssuming } = useActivePersonContext()

  // Initialize selected person - check sessionStorage first, then fall back to active person from context
  useEffect(() => {
    if (!selectedPersonId && activePersonId) {
      // Check if there's a person ID passed via sessionStorage (from Explore button)
      const explorePersonId = sessionStorage.getItem(
        "familyTreeExplorePersonId",
      )
      if (explorePersonId) {
        setSelectedPersonId(explorePersonId)
        // Clear it so subsequent visits start with current user
        sessionStorage.removeItem("familyTreeExplorePersonId")
      } else {
        setSelectedPersonId(activePersonId)
      }
    }
  }, [activePersonId, selectedPersonId])

  // Listen for custom event to explore a specific person (from Contribution Stats dialog)
  useEffect(() => {
    const handleExplorePerson = (event: CustomEvent<{ personId: string }>) => {
      setSelectedPersonId(event.detail.personId)
    }

    window.addEventListener(
      "familyTreeExplorePerson",
      handleExplorePerson as EventListener,
    )
    return () => {
      window.removeEventListener(
        "familyTreeExplorePerson",
        handleExplorePerson as EventListener,
      )
    }
  }, [])

  // Re-center on active person when it changes (e.g., when assuming/returning)
  // _Requirements: 5.4, 6.3 (assume-person-role)
  useEffect(() => {
    if (activePersonId && isAssuming !== undefined) {
      setSelectedPersonId(activePersonId)
    }
  }, [activePersonId, isAssuming])

  // Fetch family tree data for selected person
  const { familyData, isLoading, error, refetch } =
    useFamilyTreeData(selectedPersonId)

  /**
   * Handle person card click - update selected person and fetch new data
   * Requirements: 7.1, 7.2, 7.3
   * Accessibility: Manages focus when navigating between persons
   */
  const handlePersonClick = (personId: string) => {
    setSelectedPersonId(personId)
    // Data will be automatically fetched by useFamilyTreeData hook
    // when selectedPersonId changes

    // Scroll to top of tree container for better UX
    if (treeContainerRef.current) {
      treeContainerRef.current.scrollIntoView({
        behavior: "smooth",
        block: "start",
      })
    }
  }

  /**
   * Handle View button click - open details panel for the person
   * Requirements: 1.1, 2.1
   */
  const handleViewClick = (personId: string) => {
    setDetailsPanelPersonId(personId)
    setIsDetailsPanelOpen(true)
  }

  /**
   * Handle Add Family Member card click - open discovery dialog
   * Requirements: 2.1, 3.1
   */
  const handleAddFamilyMember = () => {
    setShowDiscoveryDialog(true)
  }

  /**
   * Handle skip discovery - close discovery dialog and open add dialog
   * Requirements: 2.1
   */
  const handleSkipDiscovery = () => {
    setShowDiscoveryDialog(false)
    setShowAddDialog(true)
  }

  /**
   * Handle discovery dialog close - open add dialog for manual entry
   * Requirements: 2.1
   */
  const handleDiscoveryDialogClose = () => {
    setShowAddDialog(true)
  }

  /**
   * Handle successful family member addition - refresh tree data
   * Requirements: 3.1, 3.2, 3.3
   */
  const handleAddDialogClose = (open: boolean) => {
    setShowAddDialog(open)
    if (!open) {
      // Invalidate family tree data to refresh after addition
      queryClient.invalidateQueries({
        queryKey: ["familyTreeData", selectedPersonId],
      })
      // Also invalidate relationships query used by other components
      queryClient.invalidateQueries({
        queryKey: ["personRelationshipsWithDetails"],
      })
    }
  }

  // Focus management: Focus the selected person card after navigation
  useEffect(() => {
    if (!isLoading && selectedPersonRef.current) {
      // Small delay to ensure DOM is updated
      setTimeout(() => {
        selectedPersonRef.current?.focus()
      }, 100)
    }
  }, [isLoading])

  // Error handling: No person profile (Requirement 1.4)
  if (profileStatus && !profileStatus.has_person) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Profile Not Complete</AlertTitle>
          <AlertDescription>
            <p className="mb-4">
              You need to complete your profile and add your personal
              information before viewing the family tree.
            </p>
            <Button
              className="w-full"
              onClick={() => {
                window.location.href = "/complete-profile"
              }}
            >
              Complete Profile
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  // Loading state - include person context loading
  if (isLoading || isPersonLoading || !activePersonId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading family tree...</p>
      </div>
    )
  }

  // Error state with recovery options
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Alert variant="destructive" className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error Loading Family Tree</AlertTitle>
          <AlertDescription>
            <p className="mb-4">
              {error.message ||
                "An unexpected error occurred while loading the family tree."}
            </p>
            <div className="flex flex-col gap-2">
              <Button
                className="w-full"
                variant="outline"
                onClick={() => refetch()}
              >
                Retry
              </Button>
              {selectedPersonId &&
                activePerson &&
                selectedPersonId !== activePerson.id && (
                  <Button
                    className="w-full"
                    variant="secondary"
                    onClick={() => {
                      setSelectedPersonId(activePerson.id)
                    }}
                  >
                    Return to My Profile
                  </Button>
                )}
            </div>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  // No data yet (waiting for initial load) or data structure is invalid
  if (!familyData || !selectedPersonId || !familyData.parents || !familyData.siblings || !familyData.spouses || !familyData.children) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading family tree...</p>
      </div>
    )
  }

  // Get the selected person from the API response (not from cache)
  const selectedPerson = familyData.selectedPerson || null

  // Safely access arrays with fallbacks
  const parents = familyData.parents || []
  const siblings = familyData.siblings || []
  const spouses = familyData.spouses || []
  const children = familyData.children || []

  // Check if user is viewing their own family tree (Add Cards only visible for own tree)
  const isViewingOwnTree = !!(activePerson && selectedPersonId === activePerson.id)

  // Main content - Family Tree View
  return (
    <div className="flex flex-col gap-6 animate-in fade-in duration-500">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text">
            Family Tree View
          </h1>
          <p className="text-muted-foreground mt-1">
            Explore your family relationships visually
          </p>
        </div>
        <Button
          onClick={() => setIsSearchDialogOpen(true)}
          className="flex items-center gap-2"
          variant="outline"
          aria-label="Search for a person"
        >
          <Search className="h-4 w-4" />
          <span className="hidden sm:inline">Search Person</span>
        </Button>
      </header>

      {/* Active Person Indicator - Shows when assuming another person's role */}
      {/* _Requirements: 2.5, 4.1 (assume-person-role) */}
      <ActivePersonIndicator />

      <SearchPersonDialog
        open={isSearchDialogOpen}
        onOpenChange={setIsSearchDialogOpen}
        onPersonSelected={handlePersonClick}
      />

      <main
        ref={treeContainerRef}
        className="relative flex flex-col items-center gap-2 md:gap-3 p-4 md:p-6 lg:p-8 border-2 rounded-xl shadow-sm bg-gradient-to-br from-background to-muted/20 transition-all duration-300"
        role="region"
        aria-label="Family tree visualization"
      >
        {/* Loading overlay - shows while fetching new data but maintains previous data */}
        {isLoading && familyData && (
          <div className="absolute inset-0 bg-background/90 backdrop-blur-sm flex items-center justify-center z-10 rounded-xl transition-all duration-300">
            <div className="flex flex-col items-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="mt-4 text-muted-foreground font-medium">
                Loading family tree...
              </p>
            </div>
          </div>
        )}
        {/* Parents Section - Requirements: 1.1, 5.1, 5.2 */}
        {/* Add Card only visible when viewing own family tree */}
        {(parents.length > 0 || isViewingOwnTree) && (
          <ParentsSection
            parents={parents}
            onPersonClick={handlePersonClick}
            onViewClick={handleViewClick}
            showAddCard={isViewingOwnTree}
            onAddClick={handleAddFamilyMember}
          />
        )}

        {/* Connector from parents to center row */}
        {(parents.length > 0 || isViewingOwnTree) && (
          <RowConnector />
        )}

        {/* Center Section: Siblings, Selected Person, Spouses - All in one horizontal row */}
        {/* Requirements: 5.1, 5.2, 9.3 - Single horizontally scrollable row with color-coding */}
        {(() => {
          // Combine siblings, selected person, and spouses into one array
          const centerRowPeople: PersonDetails[] = []
          const colorCoding = new Map<string, "sibling" | "spouse">()

          // Add siblings on the left
          siblings.forEach((sibling) => {
            centerRowPeople.push(sibling)
            colorCoding.set(sibling.id, "sibling")
          })

          // Add selected person in the center
          if (selectedPerson) {
            centerRowPeople.push(selectedPerson)
          }

          // Add spouses on the right
          spouses.forEach((spouse) => {
            centerRowPeople.push(spouse)
            colorCoding.set(spouse.id, "spouse")
          })

          // Always render the center row - it will have at least the selected person
          // Add Card only visible when viewing own family tree
          return (
            <HorizontalScrollRow
              people={centerRowPeople}
              selectedPersonId={selectedPersonId || undefined}
              onPersonClick={handlePersonClick}
              onViewClick={handleViewClick}
              variant="center"
              colorCoding={colorCoding}
              showAddCard={isViewingOwnTree}
              onAddClick={handleAddFamilyMember}
            />
          )
        })()}

        {/* Connector from center row to children */}
        {(children.length > 0 || isViewingOwnTree) && (
          <RowConnector />
        )}

        {/* Children Section - Requirements: 1.3, 5.1, 5.2 */}
        {/* Add Card only visible when viewing own family tree */}
        {(children.length > 0 || isViewingOwnTree) && (
          <ChildrenSection
            children={children}
            onPersonClick={handlePersonClick}
            onViewClick={handleViewClick}
            showAddCard={isViewingOwnTree}
            onAddClick={handleAddFamilyMember}
          />
        )}
      </main>

      {/* Person Details Panel - Requirements: 1.1, 2.1 */}
      <PersonDetailsPanel
        personId={detailsPanelPersonId}
        open={isDetailsPanelOpen}
        onOpenChange={setIsDetailsPanelOpen}
      />

      {/* Discover Family Members Dialog - Requirements: 2.1, 3.1 */}
      {/* Pass activePersonId for assumed person context - Requirements: 5.1, 5.2 (assume-person-role) */}
      <DiscoverFamilyMembersDialog
        open={showDiscoveryDialog}
        onOpenChange={setShowDiscoveryDialog}
        onSkip={handleSkipDiscovery}
        onClose={handleDiscoveryDialogClose}
        activePersonId={activePersonId ?? undefined}
      />

      {/* Add Family Member Dialog - Requirements: 2.1, 3.1 */}
      <AddFamilyMemberDialog
        open={showAddDialog}
        onOpenChange={handleAddDialogClose}
      />
    </div>
  )
}
