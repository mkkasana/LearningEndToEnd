import { Bug, Lightbulb, Calendar, Clock } from "lucide-react"

import { type SupportTicketPublic } from "@/client"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"

interface SupportTicketDetailDialogProps {
  ticket: SupportTicketPublic | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

const SupportTicketDetailDialog = ({
  ticket,
  open,
  onOpenChange,
}: SupportTicketDetailDialogProps) => {
  if (!ticket) return null

  const getTypeBadge = (type: string) => {
    if (type === "bug") {
      return (
        <Badge variant="destructive" className="gap-1">
          <Bug className="size-3" />
          Bug Report
        </Badge>
      )
    }
    return (
      <Badge variant="secondary" className="gap-1">
        <Lightbulb className="size-3" />
        Feature Request
      </Badge>
    )
  }

  const getStatusBadge = (status: string) => {
    if (status === "open") {
      return (
        <Badge variant="default" className="bg-green-600 hover:bg-green-700">
          Open
        </Badge>
      )
    }
    return <Badge variant="outline">Closed</Badge>
  }

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl">{ticket.title}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Type and Status Badges */}
          <div className="flex gap-2">
            {getTypeBadge(ticket.issue_type)}
            {getStatusBadge(ticket.status)}
          </div>

          <Separator />

          {/* Description */}
          <div>
            <h4 className="text-sm font-semibold mb-2">Description</h4>
            <ScrollArea className="max-h-[300px] rounded-md border p-4">
              <p className="text-sm whitespace-pre-wrap">
                {ticket.description}
              </p>
            </ScrollArea>
          </div>

          <Separator />

          {/* Timestamps */}
          <div className="space-y-3">
            <h4 className="text-sm font-semibold">Timeline</h4>
            
            <div className="flex items-start gap-2 text-sm">
              <Calendar className="size-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="font-medium">Created</p>
                <p className="text-muted-foreground">
                  {formatDateTime(ticket.created_at)}
                </p>
              </div>
            </div>

            {ticket.updated_at !== ticket.created_at && (
              <div className="flex items-start gap-2 text-sm">
                <Clock className="size-4 text-muted-foreground mt-0.5" />
                <div>
                  <p className="font-medium">Last Updated</p>
                  <p className="text-muted-foreground">
                    {formatDateTime(ticket.updated_at)}
                  </p>
                </div>
              </div>
            )}

            {ticket.status === "closed" && ticket.resolved_at && (
              <div className="flex items-start gap-2 text-sm">
                <Clock className="size-4 text-green-600 mt-0.5" />
                <div>
                  <p className="font-medium text-green-600">Resolved</p>
                  <p className="text-muted-foreground">
                    {formatDateTime(ticket.resolved_at)}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default SupportTicketDetailDialog
