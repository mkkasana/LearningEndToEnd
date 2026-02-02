/**
 * ApprovalRequestCard - Card component for displaying attachment request summary
 * Requirements: 10.4
 *
 * Displays requester information, target person details, and request date.
 * Clickable to open the detail dialog.
 */

import { Calendar, Church, MapPin, User } from "lucide-react"
import type { AttachmentRequestWithDetails } from "@/client"
import { Card, CardContent } from "@/components/ui/card"

interface ApprovalRequestCardProps {
  request: AttachmentRequestWithDetails
  onClick: () => void
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
    month: "short",
    day: "numeric",
  })
}

export default function ApprovalRequestCard({
  request,
  onClick,
}: ApprovalRequestCardProps) {
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

  return (
    <Card
      className="hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onClick()
        }
      }}
      aria-label={`Approval request from ${requesterName} for ${targetName}`}
    >
      <CardContent className="pt-6">
        {/* Requester Section */}
        <div className="mb-4">
          <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
            Requester
          </p>
          <div className="flex items-center gap-2 mb-2">
            <User className="h-4 w-4 text-primary" />
            <h3 className="font-semibold text-lg">{requesterName}</h3>
          </div>

          {/* Requester DOB and Gender */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
            <Calendar className="h-4 w-4" />
            <span>
              {formatDate(request.requester_date_of_birth)} •{" "}
              {request.requester_gender}
            </span>
          </div>

          {/* Requester Address */}
          {request.requester_address_display && (
            <div className="flex items-start gap-2 text-sm text-muted-foreground mb-1">
              <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span className="line-clamp-1">
                {request.requester_address_display}
              </span>
            </div>
          )}

          {/* Requester Religion */}
          {request.requester_religion_display && (
            <div className="flex items-start gap-2 text-sm text-muted-foreground">
              <Church className="h-4 w-4 mt-0.5 flex-shrink-0" />
              <span className="line-clamp-1">
                {request.requester_religion_display}
              </span>
            </div>
          )}
        </div>

        {/* Target Person Section */}
        <div className="pt-4 border-t">
          <p className="text-xs text-muted-foreground uppercase tracking-wide mb-1">
            Wants to attach to
          </p>
          <div className="flex items-center gap-2">
            <User className="h-4 w-4 text-orange-500" />
            <span className="font-medium">{targetName}</span>
          </div>
          <div className="flex items-center gap-2 text-sm text-muted-foreground mt-1">
            <Calendar className="h-4 w-4" />
            <span>{formatDate(request.target_date_of_birth)}</span>
          </div>
        </div>

        {/* Request Date */}
        <div className="mt-4 pt-4 border-t">
          <p className="text-xs text-muted-foreground">
            Requested on {formatDate(request.created_at)}
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
