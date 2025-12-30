import { useEffect } from "react"
import { useQuery } from "@tanstack/react-query"
import { Loader2, Eye, MapPin, Calendar } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Badge } from "@/components/ui/badge"
import { PersonContributionService, type PersonContributionPublic } from "@/client"

interface ContributionStatsDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * Format date range for display.
 * Shows "birthYear - deathYear" for deceased persons.
 * Shows "birthYear" only for living persons.
 */
function formatDateRange(birthDate: string, deathDate: string | null): string {
  const birthYear = new Date(birthDate).getFullYear()
  if (deathDate) {
    const deathYear = new Date(deathDate).getFullYear()
    return `${birthYear} - ${deathYear}`
  }
  return `${birthYear}`
}

export function ContributionStatsDialog({
  open,
  onOpenChange,
}: ContributionStatsDialogProps) {
  // Fetch contributions when dialog opens
  const {
    data: contributions,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["myContributions"],
    queryFn: () => PersonContributionService.getMyContributions(),
    enabled: open, // Only fetch when dialog is open
  })

  // Refetch when dialog opens
  useEffect(() => {
    if (open) {
      refetch()
    }
  }, [open, refetch])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>My Contribution Stats</DialogTitle>
          <DialogDescription>
            View all persons you have created and their profile view statistics
          </DialogDescription>
        </DialogHeader>

        {/* Loading State */}
        {isLoading && (
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="text-center py-8 text-destructive">
            <p>Failed to load contributions</p>
            <p className="text-sm mt-2 text-muted-foreground">
              Please try again later
            </p>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && !error && contributions?.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>You haven't created any person profiles yet.</p>
            <p className="text-sm mt-2">
              Start building your family tree to see your contributions here.
            </p>
          </div>
        )}

        {/* Contributions List */}
        {!isLoading && !error && contributions && contributions.length > 0 && (
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground mb-4">
              Total contributions: {contributions.length}
            </div>

            {contributions.map((person: PersonContributionPublic) => (
              <div
                key={person.id}
                className="border rounded-lg p-4 hover:bg-accent/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Name and Status */}
                    <div className="flex items-center gap-2 mb-2">
                      <h3 className="font-semibold text-lg">
                        {person.first_name} {person.last_name}
                      </h3>
                      <div
                        className={`w-3 h-3 rounded-full ${
                          person.is_active
                            ? "bg-green-500"
                            : "bg-gray-300 border border-gray-400"
                        }`}
                        title={person.is_active ? "Active" : "Deactivated"}
                      />
                    </div>

                    {/* Date Range */}
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                      <Calendar className="h-4 w-4" />
                      <span>
                        {formatDateRange(person.date_of_birth, person.date_of_death)}
                      </span>
                    </div>

                    {/* Address */}
                    {person.address && (
                      <div className="flex items-start gap-2 text-sm text-muted-foreground mb-2">
                        <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <span>{person.address}</span>
                      </div>
                    )}
                  </div>

                  {/* View Count */}
                  <div className="flex items-center gap-2 ml-4">
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Eye className="h-4 w-4" />
                      <span>{person.total_views}</span>
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
