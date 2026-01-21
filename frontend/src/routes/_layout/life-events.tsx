import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Calendar, Loader2 } from "lucide-react"

import { LifeEventsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { ActivePersonIndicator } from "@/components/Family/ActivePersonIndicator"
import { AddLifeEventDialog } from "@/components/LifeEvents/AddLifeEventDialog"
import { columns } from "@/components/LifeEvents/columns"
import { Skeleton } from "@/components/ui/skeleton"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"

export const Route = createFileRoute("/_layout/life-events" as any)({
  component: LifeEventsPage,
  head: () => ({
    meta: [
      {
        title: "Life Events - FastAPI Cloud",
      },
    ],
  }),
})

function LifeEventsContent({ activePersonId }: { activePersonId: string }) {
  // Fetch life events for the active person (assumed or primary)
  // _Requirements: 5.1, 5.2 (assume-person-role)
  const { data, isLoading, error } = useQuery({
    queryKey: ["life-events", activePersonId],
    queryFn: () =>
      LifeEventsService.getPersonLifeEvents({
        personId: activePersonId,
        skip: 0,
        limit: 100,
      }),
    enabled: !!activePersonId,
  })

  if (isLoading) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
        <Skeleton className="h-16 w-full" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <p className="text-destructive">Failed to load life events</p>
      </div>
    )
  }

  if (!data || data.data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <Calendar className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold">No life events yet</h3>
        <p className="text-muted-foreground">
          Add your first life event to start recording your milestones
        </p>
      </div>
    )
  }

  return <DataTable columns={columns} data={data.data} />
}

function LifeEventsPage() {
  // Get active person from context (assumed or primary)
  // _Requirements: 5.1, 5.2 (assume-person-role)
  const { activePersonId, isLoading: isPersonLoading } =
    useActivePersonContext()

  if (isPersonLoading || !activePersonId) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading...</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Life Events</h1>
          <p className="text-muted-foreground">
            Record and manage your life milestones
          </p>
        </div>
        <AddLifeEventDialog activePersonId={activePersonId} />
      </div>

      {/* Active Person Indicator - Shows when assuming another person's role */}
      {/* _Requirements: 2.5, 4.1 (assume-person-role) */}
      <ActivePersonIndicator />

      <LifeEventsContent activePersonId={activePersonId} />
    </div>
  )
}
