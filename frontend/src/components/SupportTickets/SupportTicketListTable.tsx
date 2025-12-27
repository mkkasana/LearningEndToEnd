import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Eye, Trash2, Bug, Lightbulb } from "lucide-react"
import { useState } from "react"

import { type SupportTicketPublic, IssuesService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
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
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface SupportTicketListTableProps {
  tickets: SupportTicketPublic[]
  onViewDetails: (ticket: SupportTicketPublic) => void
}

const SupportTicketListTable = ({
  tickets,
  onViewDetails,
}: SupportTicketListTableProps) => {
  const [deleteTicketId, setDeleteTicketId] = useState<string | null>(null)
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const deleteMutation = useMutation({
    mutationFn: (ticketId: string) =>
      IssuesService.deleteSupportTicket({ supportTicketId: ticketId }),
    onSuccess: () => {
      showSuccessToast("Support ticket deleted successfully")
      setDeleteTicketId(null)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["support-tickets"] })
    },
  })

  const handleDelete = () => {
    if (deleteTicketId) {
      deleteMutation.mutate(deleteTicketId)
    }
  }

  const getTypeBadge = (type: string) => {
    if (type === "bug") {
      return (
        <Badge variant="destructive" className="gap-1">
          <Bug className="size-3" />
          Bug
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

  if (tickets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <Bug className="size-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold mb-2">No tickets found</h3>
        <p className="text-sm text-muted-foreground">
          You haven't submitted any support tickets yet.
        </p>
      </div>
    )
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="w-[80px]">Ticket #</TableHead>
            <TableHead className="w-[140px]">Type</TableHead>
            <TableHead>Title</TableHead>
            <TableHead className="w-[100px]">Status</TableHead>
            <TableHead className="w-[140px]">Created</TableHead>
            <TableHead className="w-[140px] text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tickets.map((ticket, index) => (
            <TableRow key={ticket.id}>
              <TableCell className="font-medium">#{index + 1}</TableCell>
              <TableCell>{getTypeBadge(ticket.issue_type)}</TableCell>
              <TableCell className="max-w-md truncate">
                {ticket.title}
              </TableCell>
              <TableCell>{getStatusBadge(ticket.status)}</TableCell>
              <TableCell>
                {new Date(ticket.created_at).toLocaleDateString()}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex justify-end gap-2">
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => onViewDetails(ticket)}
                    title="View Details"
                  >
                    <Eye className="size-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => setDeleteTicketId(ticket.id)}
                    title="Delete Ticket"
                  >
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      <AlertDialog
        open={deleteTicketId !== null}
        onOpenChange={(open) => !open && setDeleteTicketId(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Support Ticket</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this support ticket? This action
              cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMutation.isPending}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="bg-destructive text-white hover:bg-destructive/90"
            >
              {deleteMutation.isPending ? "Deleting..." : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}

export default SupportTicketListTable
