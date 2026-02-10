/**
 * PendingApprovalStep - Component for the pending approval waiting step in profile completion.
 *
 * Requirements: 4.1-4.7
 * - Display "Pending Approval" screen when user has a pending attachment request
 * - Display target person details and request submission date
 * - Provide "Cancel Request" button
 * - Implement 30-second polling for status changes
 * - Handle approval (redirect to dashboard)
 * - Handle denial (show error, logout)
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Calendar, Clock, Loader2, User, XCircle } from "lucide-react"
import { useEffect } from "react"
import {
  AttachmentRequestsService,
  ProfileService,
} from "@/client"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

export interface PendingApprovalStepProps {
  /** Callback when the request is cancelled */
  onCancel: () => void
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
 * Format date for display (e.g., "January 15, 2024")
 * Uses T00:00:00 suffix to avoid timezone conversion issues for date-only strings
 */
function formatDate(dateString: string): string {
  // Add time component to prevent timezone shift for date-only strings
  const date = new Date(dateString + "T00:00:00")
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

/**
 * Format date with time for display (e.g., "January 15, 2024 at 2:30 PM")
 */
function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  })
}

/**
 * PendingApprovalStep component displays the waiting screen when user has
 * submitted an attachment request and is waiting for approval.
 *
 * Features:
 * - Polls for status changes every 30 seconds
 * - Displays target person details
 * - Allows cancellation of the request
 * - Handles approval (redirect) and denial (logout)
 */
export function PendingApprovalStep({ onCancel }: PendingApprovalStepProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { logout } = useAuth()
  const queryClient = useQueryClient()

  // Fetch pending request with polling every 30 seconds
  const {
    data: pendingRequest,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["myPendingRequest"],
    queryFn: () => AttachmentRequestsService.getMyPendingRequest(),
    refetchInterval: 30000, // Poll every 30 seconds
    retry: false, // Don't retry on 404 (no pending request)
  })

  // Cancel request mutation
  const cancelMutation = useMutation({
    mutationFn: (requestId: string) =>
      AttachmentRequestsService.cancelAttachmentRequest({
        requestId,
      }),
    onSuccess: () => {
      showSuccessToast("Request cancelled successfully")
      // Invalidate queries to refresh state
      queryClient.invalidateQueries({ queryKey: ["myPendingRequest"] })
      queryClient.invalidateQueries({ queryKey: ["profileCompletion"] })
      onCancel()
    },
    onError: (error: any) => {
      showErrorToast(
        error?.body?.detail || "Failed to cancel request. Please try again."
      )
    },
  })

  // Check for status changes when request data changes
  useEffect(() => {
    if (!pendingRequest) {
      // Request might have been approved or denied
      // Check profile status to determine what happened
      ProfileService.getProfileCompletionStatus()
        .then((status) => {
          if (status.is_complete) {
            // Request was approved - redirect to dashboard
            showSuccessToast(
              "Your request has been approved! Welcome to the family."
            )
            window.location.href = "/"
          }
        })
        .catch(() => {
          // If we can't get profile status, the user might have been deleted (denied)
          showErrorToast(
            "Your request was denied. Please contact support if you believe this is an error."
          )
          logout()
        })
      return
    }

    // Check if status changed from pending
    if (pendingRequest.status === "approved") {
      showSuccessToast(
        "Your request has been approved! Welcome to the family."
      )
      window.location.href = "/"
    } else if (pendingRequest.status === "denied") {
      showErrorToast(
        "Your request was denied. Please contact support if you believe this is an error."
      )
      logout()
    }
  }, [pendingRequest, showSuccessToast, showErrorToast, logout])

  // Handle cancel click
  const handleCancel = () => {
    if (pendingRequest) {
      cancelMutation.mutate(pendingRequest.id)
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Waiting for Approval
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Loading request details...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Error state or no pending request
  if (error || !pendingRequest) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-destructive" />
            No Pending Request
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-8">
            <p className="text-muted-foreground text-center mb-4">
              No pending attachment request found. You may need to restart the
              profile completion process.
            </p>
            <Button variant="outline" onClick={onCancel}>
              Go Back
            </Button>
          </div>
        </CardContent>
      </Card>
    )
  }

  const targetName = formatFullName(
    pendingRequest.target_first_name,
    pendingRequest.target_middle_name,
    pendingRequest.target_last_name
  )

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-amber-500" />
          Waiting for Approval
        </CardTitle>
        <CardDescription>
          Your request to link your account is pending approval from the person
          who created this record.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Target Person Details */}
        <div className="p-4 bg-muted/50 rounded-lg space-y-3">
          <h4 className="font-semibold text-sm text-muted-foreground uppercase tracking-wide">
            Requested Person
          </h4>
          <div className="flex items-center gap-2">
            <User className="h-5 w-5 text-primary" />
            <span className="font-semibold text-lg">{targetName}</span>
          </div>
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-1 sm:gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4 flex-shrink-0" />
            <span>Born {formatDate(pendingRequest.target_date_of_birth)}</span>
            <span className="hidden sm:inline mx-1">•</span>
            <span>{pendingRequest.target_gender}</span>
          </div>
        </div>

        {/* Request Submission Date */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-1 sm:gap-2 text-sm text-muted-foreground">
          <Clock className="h-4 w-4 flex-shrink-0" />
          <span className="break-words">Request submitted: {formatDateTime(pendingRequest.created_at)}</span>
        </div>

        {/* Status Indicator */}
        <div className="flex items-center justify-center py-4">
          <div className="flex items-center gap-3 px-4 py-2 bg-amber-50 dark:bg-amber-950/30 rounded-full border border-amber-200 dark:border-amber-800">
            <Loader2 className="h-4 w-4 animate-spin text-amber-600 dark:text-amber-400" />
            <span className="text-sm font-medium text-amber-700 dark:text-amber-400">
              Waiting for approval...
            </span>
          </div>
        </div>

        {/* Info Text */}
        <p className="text-sm text-muted-foreground text-center">
          The owner of this record will review your request. You'll be notified
          once they respond. This page will automatically update when there's a
          change.
        </p>

        {/* Cancel Request Button with Confirmation */}
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button
              variant="outline"
              className="w-full"
              disabled={cancelMutation.isPending}
            >
              {cancelMutation.isPending && (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              )}
              Cancel Request
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Cancel Attachment Request?</AlertDialogTitle>
              <AlertDialogDescription>
                Are you sure you want to cancel this request? You can submit a
                new request later if needed, or complete your profile without
                linking to an existing record.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Keep Waiting</AlertDialogCancel>
              <AlertDialogAction
                onClick={handleCancel}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                Yes, Cancel Request
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </CardContent>
    </Card>
  )
}
