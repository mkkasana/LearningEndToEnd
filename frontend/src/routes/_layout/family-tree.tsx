import { createFileRoute } from "@tanstack/react-router"
import { useState, useEffect, useRef, useCallback } from "react"
import { useQuery } from "@tanstack/react-query"
import { Loader2, AlertCircle, Network } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { ProfileService, PersonService } from "@/client"
import type { PersonDetails } from "@/client"
import { useFamilyTreeData } from "@/hooks/useFamilyTreeData"
import { ParentsSection } from "@/components/FamilyTree/ParentsSection"
import { HorizontalScrollRow } from "@/components/FamilyTree/HorizontalScrollRow"
import { ChildrenSection } from "@/components/FamilyTree/ChildrenSection"
import { GenerationLines, type Position } from "@/components/FamilyTree/RelationshipLines"

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
  const treeContainerRef = useRef<HTMLDivElement>(null)
  const selectedPersonRef = useRef<HTMLDivElement>(null)
  const parentsRowRef = useRef<HTMLDivElement>(null)
  const centerRowRef = useRef<HTMLDivElement>(null)
  const childrenRowRef = useRef<HTMLDivElement>(null)
  const [cardPositions, setCardPositions] = useState<Map<string, DOMRect>>(new Map())

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

  /**
   * Calculate card positions for drawing connecting lines
   * This runs after the DOM is updated with new family data
   */
  const updateCardPositions = useCallback(() => {
    if (!treeContainerRef.current) return
    
    const positions = new Map<string, DOMRect>()
    
    // Find all person cards and get their positions
    const cards = treeContainerRef.current.querySelectorAll('[data-person-id]')
    cards.forEach((card) => {
      const personId = card.getAttribute('data-person-id')
      if (personId) {
        const rect = card.getBoundingClientRect()
        const containerRect = treeContainerRef.current!.getBoundingClientRect()
        
        // Store position relative to container
        positions.set(personId, new DOMRect(
          rect.left - containerRect.left,
          rect.top - containerRect.top,
          rect.width,
          rect.height
        ))
      }
    })
    
    setCardPositions(positions)
  }, [])

  // Update card positions when family data changes or window resizes
  useEffect(() => {
    if (familyData && !isLoading) {
      // Delay to ensure DOM is fully rendered
      setTimeout(updateCardPositions, 100)
    }
  }, [familyData, isLoading, updateCardPositions])

  useEffect(() => {
    window.addEventListener('resize', updateCardPositions)
    return () => window.removeEventListener('resize', updateCardPositions)
  }, [updateCardPositions])

  /**
   * Calculate generation connecting lines
   * Returns connections from parents to center row and from center row to children
   */
  const calculateGenerationLines = useCallback((): {
    parentToCenter: Array<{ from: Position; to: Position }>
    centerToChildren: Array<{ from: Position; to: Position }>
  } => {
    const parentToCenter: Array<{ from: Position; to: Position }> = []
    const centerToChildren: Array<{ from: Position; to: Position }> = []
    
    if (!familyData || !selectedPersonId) {
      return { parentToCenter, centerToChildren }
    }
    
    // Parent to center connections (parents to selected person and siblings)
    familyData.parents.forEach((parent) => {
      const parentPos = cardPositions.get(parent.id)
      if (!parentPos) return
      
      // Connect to selected person
      const selectedPos = cardPositions.get(selectedPersonId)
      if (selectedPos) {
        parentToCenter.push({
          from: {
            x: parentPos.left + parentPos.width / 2,
            y: parentPos.top + parentPos.height
          },
          to: {
            x: selectedPos.left + selectedPos.width / 2,
            y: selectedPos.top
          }
        })
      }
      
      // Connect to siblings (they share the same parents)
      familyData.siblings.forEach((sibling) => {
        const siblingPos = cardPositions.get(sibling.id)
        if (siblingPos) {
          parentToCenter.push({
            from: {
              x: parentPos.left + parentPos.width / 2,
              y: parentPos.top + parentPos.height
            },
            to: {
              x: siblingPos.left + siblingPos.width / 2,
              y: siblingPos.top
            }
          })
        }
      })
    })
    
    // Center to children connections (selected person and spouses to their children)
    const selectedPos = cardPositions.get(selectedPersonId)
    if (selectedPos) {
      familyData.children.forEach((child) => {
        const childPos = cardPositions.get(child.id)
        if (childPos) {
          centerToChildren.push({
            from: {
              x: selectedPos.left + selectedPos.width / 2,
              y: selectedPos.top + selectedPos.height
            },
            to: {
              x: childPos.left + childPos.width / 2,
              y: childPos.top
            }
          })
        }
      })
    }
    
    // Connect spouses to children (if applicable)
    familyData.spouses.forEach((spouse) => {
      const spousePos = cardPositions.get(spouse.id)
      if (!spousePos) return
      
      // For now, connect all spouses to all children
      // In a more sophisticated implementation, we would track which children belong to which spouse
      familyData.children.forEach((child) => {
        const childPos = cardPositions.get(child.id)
        if (childPos) {
          centerToChildren.push({
            from: {
              x: spousePos.left + spousePos.width / 2,
              y: spousePos.top + spousePos.height
            },
            to: {
              x: childPos.left + childPos.width / 2,
              y: childPos.top
            }
          })
        }
      })
    })
    
    return { parentToCenter, centerToChildren }
  }, [familyData, selectedPersonId, cardPositions])

  const generationLines = calculateGenerationLines()

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
      </header>

      <main 
        ref={treeContainerRef}
        className="relative flex flex-col items-center gap-4 md:gap-6 lg:gap-8 p-4 md:p-6 lg:p-8 border-2 rounded-xl shadow-sm bg-gradient-to-br from-background to-muted/20 transition-all duration-300"
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
        
        {/* Generation connecting lines */}
        {generationLines.parentToCenter.length > 0 && (
          <GenerationLines
            connections={generationLines.parentToCenter}
            className="z-0"
          />
        )}
        {generationLines.centerToChildren.length > 0 && (
          <GenerationLines
            connections={generationLines.centerToChildren}
            className="z-0"
          />
        )}
        
        {/* Parents Section */}
        {familyData.parents.length > 0 && (
          <div ref={parentsRowRef} className="w-full z-10">
            <ParentsSection
              parents={familyData.parents}
              onPersonClick={handlePersonClick}
            />
          </div>
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
            <div ref={centerRowRef} className="w-full z-10">
              <HorizontalScrollRow
                people={centerRowPeople}
                selectedPersonId={selectedPersonId || undefined}
                onPersonClick={handlePersonClick}
                variant="center"
                colorCoding={colorCoding}
              />
            </div>
          ) : null
        })()}

        {/* Children Section */}
        {familyData.children.length > 0 && (
          <div ref={childrenRowRef} className="w-full z-10">
            <ChildrenSection
              children={familyData.children}
              onPersonClick={handlePersonClick}
            />
          </div>
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
