/**
 * ApprovalDetailDialog - Dialog for viewing full request details and taking action
 * Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7, 11.8
 *
 * Displays complete requester and target person information.
 * Provides Approve and Deny action buttons with confirmation.
 */

import { useMutation } from "@tanstack/react-query"
import { Calendar, Check, Church, Loader2, MapPin, User, X } from "lucide-react"
import { useState } from "react"
import type { AttachmentRequestWithDetails } from "@/client"
import { AttachmentRequestsService } from "@/client"
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"

interface ApprovalDetailDialogProps {
  request: AttachmentRequestWithDetails
  isOpen: boolean
  onClose: () => void
  onActionComplete: () => void
}

/**
 * Format full name from first, middle, and last name
 */
function formatFullName(
  firstName: string,
  middleName: string | null | undefined,
  lastName: string
): string {
  if (middleName) {
    return `${firstName} ${middleName} ${lastName}`
  }
  return `${firstName} ${lastName}`
}

/**
 * Format date for display
 */
function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

export default function ApprovalDetailDialog({
  request,
  isOpen,
  onClose,
  onActionComplete,
}: ApprovalDetailDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [showDenyConfirm, setShowDenyConfirm] = useState(false)

  const requesterName = formatFullName(
    request.requester_first_name,
    request.requester_middle_name,
    request.requester_last_name
  )

  const targetName = formatFullName(
    request.target_first_name,
    request.target_middle_name,
    request.target_last_name
  )

  // Approve mutation - Requirements: 11.6
  const approveMutation = useMutation({
    mutationFn: () =>
      AttachmentRequestsService.approveAttachmentRequest({
        requestId: request.id,
      }),
    onSuccess: () => {
      showSuccessToast("Request approved successfully")
      onActionComplete()
    },
    onError: (error: any) => {
      showErrorToast(
        error?.body?.detail || "Failed to approve request. Please try again."
      )
    },
  })

  // Deny mutation - Requirements: 11.7
  const denyMutation = useMutation({
    mutationFn: () =>
      AttachmentRequestsService.denyAttachmentRequest({
        requestId: request.id,
      }),
    onSuccess: () => {
      showSuccessToast("Request denied successfully")
      setShowDenyConfirm(false)
      onActionComplete()
    },
    onError: (error: any) => {
      showErrorToast(
        error?.body?.detail || "Failed to deny request. Please try again."
      )
      setShowDenyConfirm(false)
    },
  })

  const isLoading = approveMutation.isPending || denyMutation.isPending

  const handleApprove = () => {
    approveMutation.mutate()
  }

  const handleDenyClick = () => {
    setShowDenyConfirm(true)
  }

  const handleDenyConfirm = () => {
    denyMutation.mutate()
  }

  return (
    <>
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Attachment Request Details</DialogTitle>
            <DialogDescription>
              Review the request details and approve or deny the attachment.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-6 py-4">
            {/* Requester Information - Requirements: 11.2 */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg border-b pb-2">
                Requester Information
              </h3>

              {/* Full Name */}
              <div className="flex items-center gap-3">
                <User className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm text-muted-foreground">Full Name</p>
                  <p className="font-medium">{requesterName}</p>
                </div>
              </div>

              {/* Date of Birth */}
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm text-muted-foreground">Date of Birth</p>
                  <p className="font-medium">
                    {formatDate(request.requester_date_of_birth)}
                  </p>
                </div>
              </div>

              {/* Gender */}
              <div className="flex items-center gap-3">
                <User className="h-5 w-5 text-primary" />
                <div>
                  <p className="text-sm text-muted-foreground">Gender</p>
                  <p className="font-medium">{request.requester_gender}</p>
                </div>
              </div>

              {/* Address */}
              {request.requester_address_display && (
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Address</p>
                    <p className="font-medium">
                      {request.requester_address_display}
                    </p>
                  </div>
                </div>
              )}

              {/* Religion */}
              {request.requester_religion_display && (
                <div className="flex items-start gap-3">
                  <Church className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <p className="text-sm text-muted-foreground">Religion</p>
                    <p className="font-medium">
                      {request.requester_religion_display}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Target Person Information - Requirements: 11.3 */}
            <div className="space-y-4">
              <h3 className="font-semibold text-lg border-b pb-2">
                Target Person (Your Creation)
              </h3>

              {/* Full Name */}
              <div className="flex items-center gap-3">
                <User className="h-5 w-5 text-orange-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Full Name</p>
                  <p className="font-medium">{targetName}</p>
                </div>
              </div>

              {/* Date of Birth */}
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-orange-500" />
                <div>
                  <p className="text-sm text-muted-foreground">Date of Birth</p>
                  <p className="font-medium">
                    {formatDate(request.target_date_of_birth)}
                  </p>
                </div>
              </div>

              {/* Request Date */}
              <div className="flex items-center gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground" />
                <div>
                  <p className="text-sm text-muted-foreground">Request Date</p>
                  <p className="font-medium">{formatDate(request.created_at)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Action Buttons - Requirements: 11.4, 11.5 */}
          <DialogFooter className="gap-2 sm:gap-0">
            <Button
              variant="destructive"
              onClick={handleDenyClick}
              disabled={isLoading}
            >
              {denyMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <X className="h-4 w-4 mr-2" />
              )}
              Deny
            </Button>
            <Button onClick={handleApprove} disabled={isLoading}>
              {approveMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Check className="h-4 w-4 mr-2" />
              )}
              Approve
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Deny Confirmation Dialog - Requirements: 11.7 */}
      <AlertDialog open={showDenyConfirm} onOpenChange={setShowDenyConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Deny Attachment Request?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. Denying this request will:
              <ul className="list-disc list-inside mt-2 space-y-1">
                <li>Delete the requester's temporary profile</li>
                <li>Delete the requester's user account</li>
                <li>Prevent them from accessing the system</li>
              </ul>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={denyMutation.isPending}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDenyConfirm}
              disabled={denyMutation.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {denyMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              Yes, Deny Request
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
