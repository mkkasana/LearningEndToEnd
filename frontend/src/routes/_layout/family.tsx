import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Trash2, UserPlus, Users } from "lucide-react"
import { useState } from "react"
import { PersonService } from "@/client"
import { ActivePersonIndicator } from "@/components/Family/ActivePersonIndicator"
import { AddFamilyMemberDialog } from "@/components/Family/AddFamilyMemberDialog"
import { DiscoverFamilyMembersDialog } from "@/components/Family/DiscoverFamilyMembersDialog"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import useCustomToast from "@/hooks/useCustomToast"

export const Route = createFileRoute("/_layout/family" as any)({
  component: Family,
})

const RELATIONSHIP_LABELS: Record<string, string> = {
  "rel-6a0ede824d101": "Father",
  "rel-6a0ede824d102": "Mother",
  "rel-6a0ede824d103": "Daughter",
  "rel-6a0ede824d104": "Son",
  "rel-6a0ede824d105": "Wife",
  "rel-6a0ede824d106": "Husband",
  "rel-6a0ede824d107": "Spouse",
}

function Family() {
  const [showAddDialog, setShowAddDialog] = useState(false)
  const [showDiscoveryDialog, setShowDiscoveryDialog] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [selectedRelationship, setSelectedRelationship] = useState<any>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  
  // Get active person from context
  // _Requirements: 7.1_
  const { activePersonId, isLoading: isPersonLoading } = useActivePersonContext()

  // Fetch family members with full details using person-specific endpoint
  // _Requirements: 7.1_
  const { data: familyMembersResponse, isLoading: isDataLoading } = useQuery({
    queryKey: ["personRelationshipsWithDetails", activePersonId],
    queryFn: () => PersonService.getPersonRelationshipsWithDetails({ 
      personId: activePersonId! 
    }),
    enabled: !!activePersonId,
  })

  const isLoading = isPersonLoading || isDataLoading
  const familyMembersData = familyMembersResponse?.relationships || []

  // Delete relationship mutation using person-specific endpoint
  // _Requirements: 5.1, 5.2 (assume-person-role)_
  const deleteMutation = useMutation({
    mutationFn: (relationshipId: string) => {
      if (activePersonId) {
        // Use person-specific endpoint for assumed person context
        return PersonService.deletePersonRelationship({ 
          personId: activePersonId, 
          relationshipId 
        })
      }
      // Fallback to /me endpoint for primary person
      return PersonService.deleteMyRelationship({ relationshipId })
    },
    onSuccess: () => {
      showSuccessToast("Family member removed successfully")
      // Invalidate person-specific relationships query
      queryClient.invalidateQueries({
        queryKey: ["personRelationshipsWithDetails", activePersonId],
      })
      setDeleteDialogOpen(false)
      setSelectedRelationship(null)
    },
    onError: (error: any) => {
      showErrorToast(error.body?.detail || "Failed to remove family member")
    },
  })

  const handleDeleteClick = (item: any) => {
    setSelectedRelationship(item)
    setDeleteDialogOpen(true)
  }

  const handleAddFamilyMember = () => {
    // First show discovery dialog
    setShowDiscoveryDialog(true)
  }

  const handleSkipDiscovery = () => {
    // Close discovery dialog and open manual wizard
    setShowDiscoveryDialog(false)
    setShowAddDialog(true)
  }

  const handleDiscoveryDialogClose = () => {
    // When user closes discovery dialog without connecting, open manual wizard
    // This handles Requirement 1.5: When user closes dialog without connecting, proceed to wizard
    setShowAddDialog(true)
  }

  const handleConfirmDelete = () => {
    if (selectedRelationship?.relationship?.id) {
      deleteMutation.mutate(selectedRelationship.relationship.id)
    }
  }

  const hasFamilyMembers = familyMembersData && familyMembersData.length > 0

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Update Family</h1>
          <p className="text-muted-foreground">
            Add and manage your family members
          </p>
        </div>
        <Button onClick={handleAddFamilyMember} className="sm:shrink-0">
          <UserPlus className="mr-2 h-4 w-4" />
          Add Family Member
        </Button>
      </div>

      {/* Active Person Indicator - Shows when assuming another person's role */}
      {/* _Requirements: 2.5, 4.1 (assume-person-role) */}
      <ActivePersonIndicator />

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <p className="text-muted-foreground">Loading family members...</p>
        </div>
      ) : hasFamilyMembers ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {familyMembersData?.map((item: any) => {
            const { relationship, person } = item
            const relationshipLabel =
              RELATIONSHIP_LABELS[relationship.relationship_type] ||
              "Family Member"

            return (
              <Card key={relationship.id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span>
                      {person.first_name}{" "}
                      {person.middle_name && `${person.middle_name} `}
                      {person.last_name}
                    </span>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleDeleteClick(item)}
                      className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">
                        Relationship:{" "}
                      </span>
                      <span className="font-medium">{relationshipLabel}</span>
                    </div>
                    {person.date_of_birth && (
                      <div>
                        <span className="text-muted-foreground">
                          Date of Birth:{" "}
                        </span>
                        <span>
                          {new Date(person.date_of_birth).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                    {person.date_of_death && (
                      <div>
                        <span className="text-muted-foreground">
                          Date of Death:{" "}
                        </span>
                        <span>
                          {new Date(person.date_of_death).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center text-center py-12 border rounded-lg">
          <div className="rounded-full bg-muted p-4 mb-4">
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold">No family members yet</h3>
          <p className="text-muted-foreground mb-4">
            Add your first family member to get started
          </p>
          <Button onClick={handleAddFamilyMember}>
            <UserPlus className="mr-2 h-4 w-4" />
            Add Family Member
          </Button>
        </div>
      )}

      {/* Pass activePersonId for assumed person context - Requirements: 5.1, 5.2 (assume-person-role) */}
      <DiscoverFamilyMembersDialog
        open={showDiscoveryDialog}
        onOpenChange={setShowDiscoveryDialog}
        onSkip={handleSkipDiscovery}
        onClose={handleDiscoveryDialogClose}
        activePersonId={activePersonId ?? undefined}
      />

      <AddFamilyMemberDialog
        open={showAddDialog}
        onOpenChange={setShowAddDialog}
      />

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Family Member</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to remove your{" "}
              <span className="font-semibold">
                {selectedRelationship?.relationship?.relationship_type &&
                  RELATIONSHIP_LABELS[
                    selectedRelationship.relationship.relationship_type
                  ]}{" "}
                {selectedRelationship?.person?.first_name}{" "}
                {selectedRelationship?.person?.middle_name &&
                  `${selectedRelationship.person.middle_name} `}
                {selectedRelationship?.person?.last_name}
              </span>{" "}
              from your family?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirmDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Remove
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
