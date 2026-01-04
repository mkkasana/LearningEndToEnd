import { useSuspenseQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { Calendar } from "lucide-react"
import { Suspense } from "react"

import { LifeEventsService } from "@/client"
import { DataTable } from "@/components/Common/DataTable"
import { AddLifeEventDialog } from "@/components/LifeEvents/AddLifeEventDialog"
import { columns } from "@/components/LifeEvents/columns"
import { Skeleton } from "@/components/ui/skeleton"

function getLifeEventsQueryOptions() {
  return {
    queryFn: () => LifeEventsService.getMyLifeEvents({ skip: 0, limit: 100 }),
    queryKey: ["life-events"],
  }
}

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

function LifeEventsContent() {
  const { data } = useSuspenseQuery(getLifeEventsQueryOptions())

  if (data.data.length === 0) {
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

function LifeEventsTable() {
  return (
    <Suspense
      fallback={
        <div className="space-y-4">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      }
    >
      <LifeEventsContent />
    </Suspense>
  )
}

function LifeEventsPage() {
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Life Events</h1>
          <p className="text-muted-foreground">
            Record and manage your life milestones
          </p>
        </div>
        <AddLifeEventDialog />
      </div>
      <LifeEventsTable />
    </div>
  )
}
