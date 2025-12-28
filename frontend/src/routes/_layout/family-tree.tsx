import { createFileRoute } from "@tanstack/react-router"
import { useState, useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { Loader2, AlertCircle, Network } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { ProfileService, PersonService } from "@/client"
import type { PersonDetails } from "@/client"
import { useFamilyTreeData } from "@/hooks/useFamilyTreeData"
import { PersonCard } from "@/components/FamilyTree/PersonCard"
import { ParentsSection } from "@/components/FamilyTree/ParentsSection"
import { SpouseSection } from "@/components/FamilyTree/SpouseSection"
import { SiblingsSection } from "@/components/FamilyTree/SiblingsSection"
import { ChildrenSection } from "@/components/FamilyTree/ChildrenSection"

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
  const [personCache, setPersonCache] = useState<Map<string, PersonDetails>>(new Map())

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

  // Initialize selected person to current user's person and cache it
  useEffect(() => {
    if (myPerson && !selectedPersonId) {
      setSelectedPersonId(myPerson.id)
      setPersonCache(prev => new Map(prev).set(myPerson.id, myPerson))
    }
  }, [myPerson, selectedPersonId])

  // Fetch family tree data for selected person
  const { familyData, isLoading, error, refetch } = useFamilyTreeData(selectedPersonId)

  // Cache all persons from family data
  useEffect(() => {
    if (familyData) {
      setPersonCache(prev => {
        const newCache = new Map(prev)
        familyData.parents.forEach(p => newCache.set(p.id, p))
        familyData.spouses.forEach(p => newCache.set(p.id, p))
        familyData.siblings.forEach(p => newCache.set(p.id, p))
        familyData.children.forEach(p => newCache.set(p.id, p))
        return newCache
      })
    }
  }, [familyData])

  /**
   * Handle person card click - update selected person and fetch new data
   * Requirements: 7.1, 7.2, 7.3
   */
  const handlePersonClick = (personId: string) => {
    setSelectedPersonId(personId)
    // Data will be automatically fetched by useFamilyTreeData hook
    // when selectedPersonId changes
  }

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

  // Get the selected person from cache
  const selectedPerson = personCache.get(selectedPersonId) || null

  // Main content - Family Tree View
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Family Tree View</h1>
          <p className="text-muted-foreground">
            Explore your family relationships visually
          </p>
        </div>
      </div>

      <div className="relative flex flex-col items-center gap-8 p-8 border rounded-lg">
        {/* Loading overlay - shows while fetching new data but maintains previous data */}
        {isLoading && familyData && (
          <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-10 rounded-lg">
            <div className="flex flex-col items-center">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
              <p className="mt-4 text-muted-foreground">Loading family tree...</p>
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

        {/* Center Section: Siblings, Selected Person, Spouse */}
        <div className="flex items-center gap-8">
          {/* Siblings on the left */}
          {familyData.siblings.length > 0 && (
            <SiblingsSection
              siblings={familyData.siblings}
              onPersonClick={handlePersonClick}
            />
          )}

          {/* Selected Person in the center */}
          {selectedPerson && (
            <PersonCard
              person={selectedPerson}
              variant="selected"
              onClick={handlePersonClick}
              showPhoto={true}
            />
          )}

          {/* Spouse on the right */}
          {familyData.spouses.length > 0 && (
            <SpouseSection
              spouses={familyData.spouses}
              onPersonClick={handlePersonClick}
            />
          )}
        </div>

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
            <div className="flex flex-col items-center justify-center py-12">
              <Network className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold">No Family Relationships</h3>
              <p className="text-muted-foreground text-center max-w-md mt-2">
                No family relationships have been recorded yet. Add family members to see them in the tree.
              </p>
            </div>
          )}
      </div>
    </div>
  )
}
