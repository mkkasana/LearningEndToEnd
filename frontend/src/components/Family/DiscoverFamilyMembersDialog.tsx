// @ts-nocheck

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { type PersonDiscoveryResult, PersonService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { ConnectConfirmationDialog } from "./ConnectConfirmationDialog"

interface DiscoverFamilyMembersDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSkip: () => void
  onClose?: () => void // Called when dialog closes without connecting
}

export function DiscoverFamilyMembersDialog({
  open,
  onOpenChange,
  onSkip,
  onClose,
}: DiscoverFamilyMembersDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [showConnectDialog, setShowConnectDialog] = useState(false)
  const [selectedPerson, setSelectedPerson] =
    useState<PersonDiscoveryResult | null>(null)
  const [closedAfterConnection, setClosedAfterConnection] = useState(false)

  // Fetch discovered family members
  const {
    data: discoveries,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["discoverFamilyMembers"],
    queryFn: () => PersonService.discoverFamilyMembers(),
    enabled: open, // Only fetch when dialog is open
    retry: false, // Don't auto-retry on error
  })

  // Auto-skip to manual wizard if no discoveries found
  // This handles Requirement 1.4: When API returns no suggestions, proceed directly to wizard
  useEffect(() => {
    if (
      !isLoading &&
      !isError &&
      open &&
      discoveries &&
      discoveries.length === 0
    ) {
      // Close discovery dialog and open manual wizard
      onOpenChange(false)
      onSkip()
    }
  }, [isLoading, isError, open, discoveries, onOpenChange, onSkip])

  // Handle dialog close - call onClose callback if provided
  // This handles Requirement 1.5: When user closes dialog without connecting, proceed to wizard
  const handleOpenChange = (newOpen: boolean) => {
    onOpenChange(newOpen)
    if (!newOpen && !closedAfterConnection && onClose) {
      onClose()
    }
    // Reset the flag when dialog opens again
    if (newOpen) {
      setClosedAfterConnection(false)
    }
  }

  // Handle "Connect as <Relationship>" button click
  const handleConnect = (person: PersonDiscoveryResult) => {
    setSelectedPerson(person)
    setShowConnectDialog(true)
  }

  // Mutation for creating relationship
  const createRelationshipMutation = useMutation({
    mutationFn: (data: { relatedPersonId: string; relationshipType: string }) =>
      PersonService.createMyRelationship({
        requestBody: {
          related_person_id: data.relatedPersonId,
          relationship_type: data.relationshipType,
          is_active: true,
        },
      }),
    onSuccess: async () => {
      showSuccessToast("Successfully connected to family member!")
      setShowConnectDialog(false)

      // Invalidate queries to refresh the discoveries list
      await queryClient.invalidateQueries({
        queryKey: ["myRelationshipsWithDetails"],
      })
      await queryClient.invalidateQueries({
        queryKey: ["discoverFamilyMembers"],
      })

      // Auto-close dialog if no more suggestions after this connection
      // We check if the current list has only 1 item (the one we just connected to)
      if (discoveries && discoveries.length <= 1) {
        setClosedAfterConnection(true)
        onOpenChange(false)
      }
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to create relationship")
    },
  })

  const handleConfirmConnect = () => {
    if (selectedPerson) {
      createRelationshipMutation.mutate({
        relatedPersonId: selectedPerson.person_id,
        relationshipType: selectedPerson.inferred_relationship_type,
      })
    }
  }

  return (
    <>
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Discover Family Members</DialogTitle>
            <DialogDescription>
              We found some family members you might want to connect with
            </DialogDescription>
          </DialogHeader>

          {/* Content will be added in next sub-tasks */}
          <div className="py-4">
            {/* Loading state */}
            {isLoading && (
              <div className="flex items-center justify-center py-8 space-x-2">
                <Loader2 className="h-8 w-8 animate-spin" />
                <p className="text-sm text-muted-foreground">
                  Searching for family members...
                </p>
              </div>
            )}

            {/* Error state */}
            {isError && (
              <div className="space-y-4">
                <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
                  <p className="text-sm text-destructive font-medium mb-2">
                    Failed to discover family members
                  </p>
                  <p className="text-sm text-muted-foreground mb-3">
                    {error?.message ||
                      "An error occurred while searching. Please try again or skip to create a new person."}
                  </p>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => refetch()}
                      disabled={isLoading}
                    >
                      Try Again
                    </Button>
                    <Button size="sm" onClick={onSkip}>
                      Skip to Manual Entry
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Results will be implemented in sub-task 5.3 */}
            {!isLoading &&
              !isError &&
              discoveries &&
              discoveries.length > 0 && (
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Found {discoveries.length} potential family member(s)
                  </p>

                  {/* Scrollable container for results */}
                  <div className="max-h-96 overflow-y-auto space-y-3">
                    {discoveries.map((person) => (
                      <div
                        key={person.person_id}
                        className="border rounded-lg p-4 space-y-2 hover:bg-muted/50 transition-colors"
                      >
                        {/* Name and relationship */}
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className="font-medium">
                              {person.first_name}{" "}
                              {person.middle_name && `${person.middle_name} `}
                              {person.last_name}
                            </h4>
                            <p className="text-sm text-muted-foreground">
                              Suggested as: {person.inferred_relationship_label}
                            </p>
                          </div>
                        </div>

                        {/* Connection path */}
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">Connection:</span>{" "}
                          {person.connection_path}
                        </div>

                        {/* Date of birth */}
                        <div className="text-sm text-muted-foreground">
                          <span className="font-medium">DOB:</span>{" "}
                          {new Date(person.date_of_birth).toLocaleDateString()}
                          {person.date_of_death && (
                            <>
                              {" - "}
                              <span className="font-medium">DOD:</span>{" "}
                              {new Date(
                                person.date_of_death,
                              ).toLocaleDateString()}
                            </>
                          )}
                        </div>

                        {/* Address */}
                        {person.address_display && (
                          <div className="text-sm text-muted-foreground">
                            <span className="font-medium">Address:</span>{" "}
                            {person.address_display}
                          </div>
                        )}

                        {/* Religion */}
                        {person.religion_display && (
                          <div className="text-sm text-muted-foreground">
                            <span className="font-medium">Religion:</span>{" "}
                            {person.religion_display}
                          </div>
                        )}

                        {/* Connect button - will be implemented in sub-task 5.4 */}
                        <div className="pt-2">
                          <Button
                            size="sm"
                            onClick={() => handleConnect(person)}
                          >
                            Connect as {person.inferred_relationship_label}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            {/* No results */}
            {!isLoading &&
              !isError &&
              discoveries &&
              discoveries.length === 0 && (
                <div className="bg-muted p-4 rounded-md">
                  <p className="text-sm font-medium mb-2">
                    No family members discovered
                  </p>
                  <p className="text-sm text-muted-foreground">
                    We couldn't find any potential family connections. You can
                    proceed to create a new family member.
                  </p>
                </div>
              )}
          </div>

          {/* Footer buttons */}
          <DialogFooter className="flex justify-between sm:justify-between">
            <Button variant="outline" onClick={() => handleOpenChange(false)}>
              Close
            </Button>
            {!isError && (
              <Button onClick={onSkip}>Skip: Move to create new</Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Connect Confirmation Dialog - will be implemented in sub-task 5.4 */}
      {selectedPerson && (
        <ConnectConfirmationDialog
          open={showConnectDialog}
          onOpenChange={setShowConnectDialog}
          personId={selectedPerson.person_id}
          personName={`${selectedPerson.first_name} ${selectedPerson.middle_name ? `${selectedPerson.middle_name} ` : ""}${selectedPerson.last_name}`}
          relationshipType={selectedPerson.inferred_relationship_label}
          onConfirm={handleConfirmConnect}
          isLoading={createRelationshipMutation.isPending}
        />
      )}
    </>
  )
}
