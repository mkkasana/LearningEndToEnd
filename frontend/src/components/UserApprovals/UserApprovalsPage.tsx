/**
 * UserApprovalsPage - Full-page view for managing attachment requests
 * Requirements: 10.2, 10.3, 10.4, 10.5, 10.6, 12.1, 12.2, 12.3, 12.4
 *
 * Displays all pending attachment requests for the current user to approve or deny.
 * Provides a responsive grid layout with request cards.
 */

import { useQuery, useQueryClient } from "@tanstack/react-query"
import { Loader2, UserCheck, Users } from "lucide-react"
import { useState } from "react"
import {
  type AttachmentRequestWithDetails,
  AttachmentRequestsService,
} from "@/client"
import { Card, CardContent } from "@/components/ui/card"
import ApprovalRequestCard from "./ApprovalRequestCard"
import ApprovalDetailDialog from "./ApprovalDetailDialog"

export default function UserApprovalsPage() {
  const queryClient = useQueryClient()
  const [selectedRequest, setSelectedRequest] =
    useState<AttachmentRequestWithDetails | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  // Fetch pending requests - Requirements: 10.3
  const {
    data: requests,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["pendingApprovalRequests"],
    queryFn: () => AttachmentRequestsService.getRequestsToApprove(),
  })

  const totalRequests = requests?.length ?? 0

  const handleCardClick = (request: AttachmentRequestWithDetails) => {
    setSelectedRequest(request)
    setIsDialogOpen(true)
  }

  const handleDialogClose = () => {
    setIsDialogOpen(false)
    setSelectedRequest(null)
  }

  const handleActionComplete = () => {
    // Refresh the list after an action
    queryClient.invalidateQueries({ queryKey: ["pendingApprovalRequests"] })
    queryClient.invalidateQueries({ queryKey: ["pendingApprovalCount"] })
    handleDialogClose()
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Page Header - Requirements: 10.2 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <UserCheck className="h-8 w-8" />
          User Approvals
        </h1>
        <p className="text-muted-foreground mt-2">
          Review and manage attachment requests from new users
        </p>
      </div>

      {/* Summary Stats */}
      {!isLoading && !error && requests && (
        <div className="flex gap-6 mb-8">
          <Card className="flex-1 max-w-xs">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Users className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{totalRequests}</p>
                  <p className="text-sm text-muted-foreground">
                    Pending Requests
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Loading State - Requirements: 10.5 */}
      {isLoading && (
        <div className="flex justify-center items-center py-16">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="text-center py-16">
          <p className="text-destructive text-lg">
            Failed to load approval requests
          </p>
          <p className="text-muted-foreground mt-2">Please try again later</p>
        </div>
      )}

      {/* Empty State - Requirements: 10.6 */}
      {!isLoading && !error && requests?.length === 0 && (
        <div className="text-center py-16">
          <UserCheck className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <p className="text-lg text-muted-foreground">
            No pending approval requests
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            When new users request to attach to persons you created, they will
            appear here.
          </p>
        </div>
      )}

      {/* Request Cards Grid - Requirements: 10.4, 12.1, 12.2, 12.3, 12.4 */}
      {!isLoading && !error && requests && requests.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {requests.map((request: AttachmentRequestWithDetails) => (
            <ApprovalRequestCard
              key={request.id}
              request={request}
              onClick={() => handleCardClick(request)}
            />
          ))}
        </div>
      )}

      {/* Detail Dialog - Requirements: 11.1-11.8 */}
      {selectedRequest && (
        <ApprovalDetailDialog
          request={selectedRequest}
          isOpen={isDialogOpen}
          onClose={handleDialogClose}
          onActionComplete={handleActionComplete}
        />
      )}
    </div>
  )
}
