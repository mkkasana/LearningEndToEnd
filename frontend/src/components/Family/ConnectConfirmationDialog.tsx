// @ts-nocheck
import { useQuery } from "@tanstack/react-query"
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { LoadingButton } from "@/components/ui/loading-button"
import { PersonService } from "@/client"

interface ConnectConfirmationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  personId: string
  personName: string
  relationshipType: string
  onConfirm: () => void
  isLoading?: boolean
}

export function ConnectConfirmationDialog({
  open,
  onOpenChange,
  personId,
  personName,
  relationshipType,
  onConfirm,
  isLoading = false,
}: ConnectConfirmationDialogProps) {
  // Fetch relatives of the person user is trying to connect to
  const { data: relationshipsData, isLoading: isLoadingRelatives } = useQuery({
    queryKey: ["personRelationships", personId],
    queryFn: () => PersonService.getPersonRelationshipsWithDetails({ personId }),
    enabled: open && !!personId, // Only fetch when dialog is open and personId exists
  })

  // Extract relationships array from the response
  const relatives = relationshipsData?.relationships || []

  const handleConfirm = () => {
    onConfirm()
    // Don't close dialog here - let parent handle it on success
  }

  const handleCancel = () => {
    if (!isLoading) {
      onOpenChange(false)
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={isLoading ? undefined : onOpenChange}>
      <AlertDialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <AlertDialogHeader>
          <AlertDialogTitle>Connect to Existing Person</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to connect to <strong>{personName}</strong> as
            your <strong>{relationshipType}</strong>?
          </AlertDialogDescription>
        </AlertDialogHeader>

        {/* Show relatives to help identify the correct person */}
        {isLoadingRelatives && (
          <div className="flex items-center justify-center py-4 space-x-2">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
            <p className="text-sm text-muted-foreground">Loading relatives...</p>
          </div>
        )}

        {!isLoadingRelatives && relatives && relatives.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium">
              Known relatives of {personName}:
            </p>
            <div className="max-h-48 overflow-y-auto border rounded-md p-3 space-y-2 bg-muted/30">
              {relatives.map((rel: any) => (
                <div
                  key={rel.relationship.id}
                  className="text-sm flex items-center gap-2"
                >
                  <span className="text-muted-foreground">•</span>
                  <span>
                    <strong>
                      {rel.person.first_name}{" "}
                      {rel.person.middle_name && `${rel.person.middle_name} `}
                      {rel.person.last_name}
                    </strong>
                    <span className="text-muted-foreground">
                      {" "}({rel.relationship.relationship_type_label || rel.relationship.relationship_type})
                    </span>
                  </span>
                </div>
              ))}
            </div>
            <p className="text-xs text-muted-foreground italic">
              This information helps you verify you're connecting to the correct person.
            </p>
          </div>
        )}

        {!isLoadingRelatives && relatives && relatives.length === 0 && (
          <div className="py-2">
            <p className="text-sm text-muted-foreground">
              No known relatives found for this person.
            </p>
          </div>
        )}

        <AlertDialogFooter>
          <AlertDialogCancel onClick={handleCancel} disabled={isLoading}>
            Cancel
          </AlertDialogCancel>
          <LoadingButton onClick={handleConfirm} loading={isLoading}>
            Confirm
          </LoadingButton>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
