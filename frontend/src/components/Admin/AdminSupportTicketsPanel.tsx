import {
  useMutation,
  useQueryClient,
  useSuspenseQuery,
} from "@tanstack/react-query"
import { Bug, CheckCircle, Lightbulb, RotateCcw, Trash2 } from "lucide-react"
import { useState } from "react"

import { type IssueStatus, IssuesService, type IssueType } from "@/client"
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
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

function getAdminSupportTicketsQueryOptions(
  status?: IssueStatus | null,
  issueType?: IssueType | null,
) {
  return {
    queryFn: () =>
      IssuesService.getAllSupportTicketsAdmin({
        status: status,
        issueType: issueType,
        skip: 0,
        limit: 100,
      }),
    queryKey: ["admin-support-tickets", status, issueType],
  }
}

const AdminSupportTicketsPanel = () => {
  const [statusFilter, setStatusFilter] = useState<IssueStatus | "all">("all")
  const [typeFilter, setTypeFilter] = useState<IssueType | "all">("all")
  const [deleteTicketId, setDeleteTicketId] = useState<string | null>(null)

  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const { data: tickets } = useSuspenseQuery(
    getAdminSupportTicketsQueryOptions(
      statusFilter === "all" ? undefined : statusFilter,
      typeFilter === "all" ? undefined : typeFilter,
    ),
  )

  const resolveMutation = useMutation({
    mutationFn: (ticketId: string) =>
      IssuesService.resolveSupportTicket({ supportTicketId: ticketId }),
    onSuccess: () => {
      showSuccessToast("Ticket marked as resolved")
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-support-tickets"] })
    },
  })

  const reopenMutation = useMutation({
    mutationFn: (ticketId: string) =>
      IssuesService.reopenSupportTicket({ supportTicketId: ticketId }),
    onSuccess: () => {
      showSuccessToast("Ticket reopened")
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-support-tickets"] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (ticketId: string) =>
      IssuesService.deleteSupportTicket({ supportTicketId: ticketId }),
    onSuccess: () => {
      showSuccessToast("Ticket deleted successfully")
      setDeleteTicketId(null)
    },
    onError: handleError.bind(showErrorToast),
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["admin-support-tickets"] })
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

  // Calculate statistics
  const openBugs = tickets.filter(
    (t) => t.status === "open" && t.issue_type === "bug",
  ).length
  const openFeatureRequests = tickets.filter(
    (t) => t.status === "open" && t.issue_type === "feature_request",
  ).length

  // Sort by creation date (oldest first)
  const sortedTickets = [...tickets].sort(
    (a, b) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime(),
  )

  return (
    <div className="space-y-6">
      {/* Statistics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Bugs</CardTitle>
            <Bug className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{openBugs}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Open Feature Requests
            </CardTitle>
            <Lightbulb className="size-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{openFeatureRequests}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="w-[180px]">
          <Select
            value={statusFilter}
            onValueChange={(value) =>
              setStatusFilter(value as IssueStatus | "all")
            }
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="w-[180px]">
          <Select
            value={typeFilter}
            onValueChange={(value) => setTypeFilter(value as IssueType | "all")}
          >
            <SelectTrigger>
              <SelectValue placeholder="Filter by type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="bug">Bug</SelectItem>
              <SelectItem value="feature_request">Feature Request</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Tickets Table */}
      {sortedTickets.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 text-center">
          <Bug className="size-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No tickets found</h3>
          <p className="text-sm text-muted-foreground">
            No support tickets match the selected filters.
          </p>
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[80px]">Ticket #</TableHead>
              <TableHead className="w-[200px]">Submitter</TableHead>
              <TableHead className="w-[120px]">Type</TableHead>
              <TableHead>Title</TableHead>
              <TableHead className="w-[100px]">Status</TableHead>
              <TableHead className="w-[120px]">Created</TableHead>
              <TableHead className="w-[180px] text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedTickets.map((ticket, index) => (
              <TableRow key={ticket.id}>
                <TableCell className="font-medium">#{index + 1}</TableCell>
                <TableCell>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">
                      {ticket.user_email}
                    </span>
                    {ticket.user_full_name && (
                      <span className="text-xs text-muted-foreground">
                        {ticket.user_full_name}
                      </span>
                    )}
                  </div>
                </TableCell>
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
                    {ticket.status === "open" ? (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => resolveMutation.mutate(ticket.id)}
                        disabled={resolveMutation.isPending}
                        title="Mark Resolved"
                      >
                        <CheckCircle className="size-4 mr-1" />
                        Resolve
                      </Button>
                    ) : (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => reopenMutation.mutate(ticket.id)}
                        disabled={reopenMutation.isPending}
                        title="Reopen Ticket"
                      >
                        <RotateCcw className="size-4 mr-1" />
                        Reopen
                      </Button>
                    )}
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
      )}

      {/* Delete Confirmation Dialog */}
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
    </div>
  )
}

export default AdminSupportTicketsPanel
