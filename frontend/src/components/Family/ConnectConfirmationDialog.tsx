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

interface ConnectConfirmationDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  personName: string
  relationshipType: string
  onConfirm: () => void
}

export function ConnectConfirmationDialog({
  open,
  onOpenChange,
  personName,
  relationshipType,
  onConfirm,
}: ConnectConfirmationDialogProps) {
  const handleConfirm = () => {
    onConfirm()
    onOpenChange(false)
  }

  const handleCancel = () => {
    onOpenChange(false)
  }

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Connect to Existing Person</AlertDialogTitle>
          <AlertDialogDescription>
            Are you sure you want to connect to <strong>{personName}</strong> as
            your <strong>{relationshipType}</strong>?
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={handleCancel}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={handleConfirm}>Confirm</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
