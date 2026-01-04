import type { ColumnDef } from "@tanstack/react-table"

import type { LifeEventPublic } from "@/client"
import { cn } from "@/lib/utils"
import { LifeEventActionsMenu } from "./LifeEventActionsMenu"

// Format date display from year, month, date
function formatEventDate(
  year: number,
  month?: number | null,
  date?: number | null,
): string {
  if (!month) return String(year)

  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ]

  if (!date) return `${months[month - 1]} ${year}`
  return `${months[month - 1]} ${date}, ${year}`
}

// Get event type badge color
function getEventTypeColor(eventType: string): string {
  const colors: Record<string, string> = {
    birth: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
    marriage: "bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300",
    death: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300",
    purchase: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
    sale: "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
    achievement:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
    education:
      "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300",
    career:
      "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
    health: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
    travel: "bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300",
    other: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300",
  }
  return colors[eventType] || colors.other
}

export const columns: ColumnDef<LifeEventPublic>[] = [
  {
    accessorKey: "event_type",
    header: "Type",
    cell: ({ row }) => {
      const eventType = row.original.event_type
      return (
        <span
          className={cn(
            "text-xs px-2 py-1 rounded-full font-medium capitalize",
            getEventTypeColor(eventType),
          )}
        >
          {eventType}
        </span>
      )
    },
  },
  {
    accessorKey: "title",
    header: "Title",
    cell: ({ row }) => (
      <span className="font-medium">{row.original.title}</span>
    ),
  },
  {
    accessorKey: "event_year",
    header: "Date",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {formatEventDate(
          row.original.event_year,
          row.original.event_month,
          row.original.event_date,
        )}
      </span>
    ),
  },
  {
    accessorKey: "description",
    header: "Description",
    cell: ({ row }) => {
      const description = row.original.description
      return (
        <span
          className={cn(
            "max-w-xs truncate block text-muted-foreground",
            !description && "italic",
          )}
        >
          {description || "No description"}
        </span>
      )
    },
  },
  {
    id: "actions",
    header: () => <span className="sr-only">Actions</span>,
    cell: ({ row }) => (
      <div className="flex justify-end">
        <LifeEventActionsMenu event={row.original} />
      </div>
    ),
  },
]
