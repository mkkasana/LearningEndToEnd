import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Suspense, useState } from "react"

import {
  type IssueStatus,
  IssuesService,
  type SupportTicketPublic,
} from "@/client"
import CreateSupportTicketDialog from "@/components/SupportTickets/CreateSupportTicketDialog"
import SupportTicketDetailDialog from "@/components/SupportTickets/SupportTicketDetailDialog"
import SupportTicketListTable from "@/components/SupportTickets/SupportTicketListTable"
import { Skeleton } from "@/components/ui/skeleton"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

function getSupportTicketsQueryOptions(status?: IssueStatus | null) {
  return {
    queryFn: () =>
      IssuesService.getMySupportTickets({
        status: status,
        skip: 0,
        limit: 100,
      }),
    queryKey: ["support-tickets", status],
  }
}

export const Route = createFileRoute("/_layout/support-tickets" as any)({
  component: SupportTicketsPage,
  head: () => ({
    meta: [
      {
        title: "Support Tickets - FastAPI Cloud",
      },
    ],
  }),
})

function SupportTicketsContent({ status }: { status?: IssueStatus | null }) {
  const { data } = useSuspenseQuery(getSupportTicketsQueryOptions(status))
  const [selectedTicket, setSelectedTicket] =
    useState<SupportTicketPublic | null>(null)
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false)

  const handleViewDetails = (ticket: SupportTicketPublic) => {
    setSelectedTicket(ticket)
    setIsDetailDialogOpen(true)
  }

  return (
    <>
      <SupportTicketListTable
        tickets={data.data}
        onViewDetails={handleViewDetails}
      />
      <SupportTicketDetailDialog
        ticket={selectedTicket}
        open={isDetailDialogOpen}
        onOpenChange={setIsDetailDialogOpen}
      />
    </>
  )
}

function SupportTicketsTable({ status }: { status?: IssueStatus | null }) {
  return (
    <Suspense
      fallback={
        <div className="space-y-4">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      }
    >
      <SupportTicketsContent status={status} />
    </Suspense>
  )
}

function SupportTicketsPage() {
  const [activeTab, setActiveTab] = useState<string>("all")

  const getStatusFilter = (tab: string): IssueStatus | null | undefined => {
    switch (tab) {
      case "open":
        return "open"
      case "closed":
        return "closed"
      default:
        return undefined
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Support Tickets</h1>
          <p className="text-muted-foreground">
            Report bugs and request features
          </p>
        </div>
        <CreateSupportTicketDialog />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="open">Open</TabsTrigger>
          <TabsTrigger value="closed">Closed</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <SupportTicketsTable status={getStatusFilter("all")} />
        </TabsContent>

        <TabsContent value="open">
          <SupportTicketsTable status={getStatusFilter("open")} />
        </TabsContent>

        <TabsContent value="closed">
          <SupportTicketsTable status={getStatusFilter("closed")} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
