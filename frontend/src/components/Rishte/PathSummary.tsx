import { Users } from "lucide-react"
import { memo } from "react"
import { Card } from "@/components/ui/card"

interface PathSummaryProps {
  personCount: number
  pathSummary: string
}

/**
 * PathSummary component displays a summary of the relationship path
 *
 * Requirements:
 * - 11.1: Display the total number of persons in the path
 * - 11.2: Display a text summary of the path (e.g., "name1 → name2 → name3...")
 */
export const PathSummary = memo(function PathSummary({
  personCount,
  pathSummary,
}: PathSummaryProps) {
  return (
    <Card className="p-4 bg-muted/50">
      <div className="flex items-start gap-3">
        <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 shrink-0">
          <Users className="h-4 w-4 text-primary" />
        </div>
        <div className="flex flex-col gap-1 min-w-0">
          <div className="text-sm font-medium">
            {personCount} {personCount === 1 ? "person" : "persons"} in path
          </div>
          <div className="text-sm text-muted-foreground break-words">
            {pathSummary}
          </div>
        </div>
      </div>
    </Card>
  )
})

export type { PathSummaryProps }
