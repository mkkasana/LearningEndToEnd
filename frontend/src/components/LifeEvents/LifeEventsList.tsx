import { Calendar } from "lucide-react"
import type { LifeEventPublic } from "@/client"
import { getEventTypeIcon } from "@/components/LifeEvents/eventTypeIcons"
import { cn } from "@/lib/utils"

interface LifeEventsListProps {
  events: LifeEventPublic[]
  compact?: boolean // Compact mode for side panel
}

/**
 * LifeEventsList component displays a list of life events
 * @param events - Array of life events to display
 * @param compact - Whether to use compact styling (for side panels)
 */
export function LifeEventsList({
  events,
  compact = false,
}: LifeEventsListProps) {
  return (
    <div className={compact ? "space-y-3" : "space-y-4"}>
      {events.map((event) => (
        <LifeEventCard key={event.id} event={event} compact={compact} />
      ))}
    </div>
  )
}

interface LifeEventCardProps {
  event: LifeEventPublic
  compact?: boolean
}

/**
 * LifeEventCard component displays a single life event
 * @param event - The life event to display
 * @param compact - Whether to use compact styling
 */
function LifeEventCard({ event, compact }: LifeEventCardProps) {
  const EventIcon = getEventTypeIcon(event.event_type)
  const formattedDate = formatEventDate(
    event.event_year,
    event.event_month ?? null,
    event.event_date ?? null,
  )

  return (
    <div
      className={cn(
        "flex gap-3 p-3 rounded-lg border bg-card",
        compact && "text-sm",
      )}
    >
      <div className="flex-shrink-0">
        <EventIcon
          className={cn(
            "text-muted-foreground",
            compact ? "h-4 w-4" : "h-5 w-5",
          )}
        />
      </div>

      <div className="flex-1 min-w-0">
        <h4 className={cn("font-medium", compact ? "text-sm" : "text-base")}>
          {event.title}
        </h4>

        <p
          className={cn(
            "text-muted-foreground flex items-center gap-1 mt-1",
            compact ? "text-xs" : "text-sm",
          )}
        >
          <Calendar className="h-3 w-3" />
          {formattedDate}
        </p>

        {event.description && !compact && (
          <p className="text-sm text-muted-foreground mt-2">
            {event.description}
          </p>
        )}
      </div>
    </div>
  )
}

/**
 * Format event date based on available components
 * @param year - Event year (required)
 * @param month - Event month (1-12, optional)
 * @param date - Event date (1-31, optional)
 * @returns Formatted date string
 */
function formatEventDate(
  year: number,
  month: number | null,
  date: number | null,
): string {
  if (month && date) {
    const monthName = new Date(year, month - 1).toLocaleString("default", {
      month: "long",
    })
    return `${monthName} ${date}, ${year}`
  }
  if (month) {
    const monthName = new Date(year, month - 1).toLocaleString("default", {
      month: "long",
    })
    return `${monthName} ${year}`
  }
  return `${year}`
}
