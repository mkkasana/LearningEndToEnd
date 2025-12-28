import { createFileRoute } from "@tanstack/react-router"
import { useState, useEffect, useRef } from "react"
import { useQuery } from "@tanstack/react-query"
import { Loader2, AlertCircle, Network, Search } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { ProfileService, PersonService } from "@/client"
import type { PersonDetails } from "@/client"
import { useFamilyTreeData } from "@/hooks/useFamilyTreeData"
import { ParentsSection } from "@/components/FamilyTree/ParentsSection"
import { HorizontalScrollRow } from "@/components/FamilyTree/HorizontalScrollRow"
import { ChildrenSection } from "@/components/FamilyTree/ChildrenSection"
import { RowConnector } from "@/components/FamilyTree/RowConnector"
import { SearchPersonDialog } from "@/components/FamilyTree/SearchPersonDialog"

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
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null)
  const [isSearchDialogOpen, setIsSearchDialogOpen] = useState(false)
  const treeContainerRef = useRef<HTMLDivElement>(null)
  const selectedPersonRef = useRef<HTMLDivElement>(null)

  // Check if user has a person profile
  const { data: profileStatus } = useQuery({
    queryKey: ["profileCompletion"],
    queryFn: () => ProfileService.getProfileCompletionStatus(),
  })

  // Get the current user's person ID
  const { data: myPerson } = useQuery({
    queryKey: ["myPerson"],
    queryFn: () => PersonService.getMyPerson(),
    enabled: profileStatus?.has_person === true,
  })

  // Initialize selected person to current user's person
  useEffect(() => {
    if (myPerson && !selectedPersonId) {
      setSelectedPersonId(myPerson.id)
    }
  }, [myPerson, selectedPersonId])

  // Fetch family tree data for selected person
  const { familyData, isLoading, error, refetch } = useFamilyTreeData(selectedPersonId)

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
      treeContainerRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' })
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
  }, [selectedPersonId, isLoading])

  // Error handling: No person profile (Requirement 1.4)
  if (profileStatus && !profileStatus.has_person) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Profile Not Complete</AlertTitle>
          <AlertDescription>
            <p className="mb-4">
              You need to complete your profile and add your personal information before viewing the family tree.
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

  // Loading state
  if (isLoading) {
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
              {error.message || "An unexpected error occurred while loading the family tree."}
            </p>
            <div className="flex flex-col gap-2">
              <Button
                className="w-full"
                variant="outline"
                onClick={() => refetch()}
              >
                Retry
              </Button>
              {selectedPersonId && myPerson && selectedPersonId !== myPerson.id && (
                <Button
                  className="w-full"
                  variant="secondary"
                  onClick={() => {
                    setSelectedPersonId(myPerson.id)
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

  // No data yet (waiting for initial load)
  if (!familyData || !selectedPersonId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading family tree...</p>
      </div>
    )
  }

  // Get the selected person from the API response (not from cache)
  const selectedPerson = familyData?.selectedPerson || null

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
              <p className="mt-4 text-muted-foreground font-medium">Loading family tree...</p>
            </div>
          </div>
        )}
        {/* Parents Section */}
        {familyData.parents.length > 0 && (
          <ParentsSection
            parents={familyData.parents}
            onPersonClick={handlePersonClick}
          />
        )}

        {/* Connector from parents to center row */}
        {familyData.parents.length > 0 && (
          <RowConnector />
        )}

        {/* Center Section: Siblings, Selected Person, Spouses - All in one horizontal row */}
        {/* Requirements: 9.3 - Single horizontally scrollable row with color-coding */}
        {(() => {
          // Combine siblings, selected person, and spouses into one array
          const centerRowPeople: PersonDetails[] = []
          const colorCoding = new Map<string, 'sibling' | 'spouse'>()
          
          // Add siblings on the left
          familyData.siblings.forEach(sibling => {
            centerRowPeople.push(sibling)
            colorCoding.set(sibling.id, 'sibling')
          })
          
          // Add selected person in the center
          if (selectedPerson) {
            centerRowPeople.push(selectedPerson)
          }
          
          // Add spouses on the right
          familyData.spouses.forEach(spouse => {
            centerRowPeople.push(spouse)
            colorCoding.set(spouse.id, 'spouse')
          })
          
          return centerRowPeople.length > 0 ? (
            <HorizontalScrollRow
              people={centerRowPeople}
              selectedPersonId={selectedPersonId || undefined}
              onPersonClick={handlePersonClick}
              variant="center"
              colorCoding={colorCoding}
            />
          ) : null
        })()}

        {/* Connector from center row to children */}
        {familyData.children.length > 0 && (
          <RowConnector />
        )}

        {/* Children Section */}
        {familyData.children.length > 0 && (
          <ChildrenSection
            children={familyData.children}
            onPersonClick={handlePersonClick}
          />
        )}

        {/* Empty state if no relationships */}
        {familyData.parents.length === 0 &&
          familyData.spouses.length === 0 &&
          familyData.siblings.length === 0 &&
          familyData.children.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 px-4">
              <div className="rounded-full bg-muted/50 p-6 mb-4">
                <Network className="h-12 w-12 text-muted-foreground" />
              </div>
              <h3 className="text-lg md:text-xl font-semibold mb-2">No Family Relationships</h3>
              <p className="text-muted-foreground text-center max-w-md text-sm md:text-base">
                No family relationships have been recorded yet. Add family members to see them in the tree.
              </p>
            </div>
          )}
      </main>
    </div>
  )
}
