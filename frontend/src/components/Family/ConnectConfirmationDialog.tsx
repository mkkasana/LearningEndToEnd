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

interface ConnectConfirmationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  personName: string
  relationshipType: string
  onConfirm: () => void
  isLoading?: boolean
}

export function ConnectConfirmationDialog({
  open,
  onOpenChange,
  personName,
  relationshipType,
  onConfirm,
  isLoading = false,
}: ConnectConfirmationDialogProps) {
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
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Connect to Existing Person</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to connect to <strong>{personName}</strong> as
            your <strong>{relationshipType}</strong>?
          </AlertDialogDescription>
        </AlertDialogHeader>
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
