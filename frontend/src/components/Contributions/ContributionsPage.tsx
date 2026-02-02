/**
 * ContributionsPage - Full-page view for user contributions
 * Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1-3.7, 6.1-6.3
 *
 * Displays all persons created by the current user with engagement statistics.
 * Provides a more spacious layout compared to the dialog version.
 */

import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"
import {
  BarChart3,
  Calendar,
  Eye,
  Loader2,
  MapPin,
  Network,
  Users,
} from "lucide-react"
import { type PersonContributionPublic, PersonService } from "@/client"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

/**
 * Format date range for display.
 * Shows "birthYear - deathYear" for deceased persons.
 * Shows "birthYear" only for living persons.
 * Requirements: 3.3, 3.4
 */
function formatDateRange(
  birthDate: string,
  deathDate: string | null | undefined,
): string {
  const birthYear = new Date(birthDate).getFullYear()
  if (deathDate) {
    const deathYear = new Date(deathDate).getFullYear()
    return `${birthYear} - ${deathYear}`
  }
  return `${birthYear}`
}


/**
 * Navigate to family tree with a specific person selected.
 * Uses custom event to notify the family tree component, plus sessionStorage as fallback.
 * Requirements: 3.7
 */
function handleExplorePerson(
  personId: string,
  navigate: ReturnType<typeof useNavigate>,
) {
  // Store in sessionStorage as fallback for fresh page loads
  sessionStorage.setItem("familyTreeExplorePersonId", personId)
  navigate({ to: "/family-tree" })
  // Dispatch custom event after a small delay to ensure navigation completes
  setTimeout(() => {
    window.dispatchEvent(
      new CustomEvent("familyTreeExplorePerson", { detail: { personId } }),
    )
  }, 100)
}

export default function ContributionsPage() {
  const navigate = useNavigate()

  // Fetch contributions - Requirements: 2.4
  const {
    data: contributions,
    isLoading,
    error,
  } = useQuery({
    queryKey: ["myContributions"],
    queryFn: () => PersonService.getMyContributions(),
  })

  // Calculate summary stats - Requirements: 2.3
  const totalContributions = contributions?.length ?? 0
  const totalViews =
    contributions?.reduce((sum, p) => sum + (p.total_views ?? 0), 0) ?? 0

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Page Header - Requirements: 2.2 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-3">
          <BarChart3 className="h-8 w-8" />
          My Contributions
        </h1>
        <p className="text-muted-foreground mt-2">
          View all persons you have created and their profile view statistics
        </p>
      </div>

      {/* Summary Stats - Requirements: 2.3 */}
      {!isLoading && !error && contributions && (
        <div className="flex gap-6 mb-8">
          <Card className="flex-1">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Users className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{totalContributions}</p>
                  <p className="text-sm text-muted-foreground">
                    Total Contributions
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="flex-1">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <Eye className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-2xl font-bold">{totalViews}</p>
                  <p className="text-sm text-muted-foreground">Total Views</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Loading State - Requirements: 2.6 */}
      {isLoading && (
        <div className="flex justify-center items-center py-16">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
        </div>
      )}

      {/* Error State - Requirements: 2.6 */}
      {error && (
        <div className="text-center py-16">
          <p className="text-destructive text-lg">Failed to load contributions</p>
          <p className="text-muted-foreground mt-2">Please try again later</p>
        </div>
      )}

      {/* Empty State - Requirements: 2.7 */}
      {!isLoading && !error && contributions?.length === 0 && (
        <div className="text-center py-16">
          <Users className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <p className="text-lg text-muted-foreground">
            You haven't created any person profiles yet.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            Start building your family tree to see your contributions here.
          </p>
          <Button
            className="mt-6"
            onClick={() => navigate({ to: "/family" })}
          >
            Add Family Members
          </Button>
        </div>
      )}


      {/* Person Cards Grid - Requirements: 2.5, 6.1, 6.2, 6.3 */}
      {!isLoading && !error && contributions && contributions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {contributions.map((person: PersonContributionPublic) => (
            <Card
              key={person.id}
              className="hover:shadow-md transition-shadow"
            >
              <CardContent className="pt-6">
                {/* Name and Status - Requirements: 3.1, 3.2 */}
                <div className="flex items-center gap-2 mb-3">
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

                {/* Date Range - Requirements: 3.3, 3.4 */}
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
                  <Calendar className="h-4 w-4" />
                  <span>
                    {formatDateRange(person.date_of_birth, person.date_of_death)}
                  </span>
                </div>

                {/* Address - Requirements: 3.5 */}
                {person.address && (
                  <div className="flex items-start gap-2 text-sm text-muted-foreground mb-3">
                    <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
                    <span className="line-clamp-2">{person.address}</span>
                  </div>
                )}

                {/* Footer: View Count and Explore - Requirements: 3.6, 3.7 */}
                <div className="flex items-center justify-between mt-4 pt-4 border-t">
                  <Badge variant="secondary" className="flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    <span>{person.total_views} views</span>
                  </Badge>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExplorePerson(person.id, navigate)}
                  >
                    <Network className="h-4 w-4 mr-1" />
                    Explore
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
