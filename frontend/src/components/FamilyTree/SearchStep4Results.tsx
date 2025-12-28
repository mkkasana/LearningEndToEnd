// @ts-nocheck
import { Search, User } from "lucide-react"
import type { PersonMatchResult } from "@/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

interface SearchStep4ResultsProps {
  results: PersonMatchResult[]
  onExplore: (personId: string) => void
  onBack: () => void
}

export function SearchStep4Results({
  results,
  onExplore,
  onBack,
}: SearchStep4ResultsProps) {
  const formatBirthYear = (dateOfBirth: string) => {
    try {
      return new Date(dateOfBirth).getFullYear().toString()
    } catch {
      return "Unknown"
    }
  }

  const formatDeathYear = (dateOfDeath: string | null | undefined) => {
    if (!dateOfDeath) return null
    try {
      return new Date(dateOfDeath).getFullYear().toString()
    } catch {
      return null
    }
  }

  if (results.length === 0) {
    return (
      <div className="py-8">
        <div className="flex flex-col items-center justify-center py-12 px-4">
          <div className="rounded-full bg-muted/50 p-6 mb-4">
            <Search className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-semibold mb-2">No Results Found</h3>
          <p className="text-muted-foreground text-center max-w-md text-sm mb-6">
            No persons match your search criteria. Try adjusting your search parameters.
          </p>
          <Button variant="outline" onClick={onBack}>
            Back to Search
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 py-4">
      <div className="flex items-center justify-between mb-4">
        <p className="text-sm text-muted-foreground">
          Found {results.length} {results.length === 1 ? "match" : "matches"}
        </p>
      </div>

      <div className="space-y-3">
        {results.map((result) => {
          const birthYear = formatBirthYear(result.date_of_birth)
          const deathYear = formatDeathYear(result.date_of_death)
          const yearsDisplay = deathYear ? `${birthYear} - ${deathYear}` : `${birthYear} -`

          return (
            <Card key={result.person_id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 space-y-2">
                    <div className="flex items-center gap-3">
                      <div className="rounded-full bg-muted p-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-base">
                          {result.first_name}
                          {result.middle_name && ` ${result.middle_name}`} {result.last_name}
                        </h4>
                        <p className="text-sm text-muted-foreground">{yearsDisplay}</p>
                      </div>
                    </div>

                    <Separator />

                    <div className="space-y-1 text-sm">
                      <div>
                        <span className="font-medium text-muted-foreground">Address: </span>
                        <span>{result.address_display || "Not specified"}</span>
                      </div>
                      <div>
                        <span className="font-medium text-muted-foreground">Religion: </span>
                        <span>{result.religion_display || "Not specified"}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 pt-2">
                      <Badge variant="secondary" className="text-xs">
                        Match Score: {Math.round(result.match_score)}%
                      </Badge>
                    </div>
                  </div>

                  <Button
                    size="sm"
                    onClick={() => onExplore(result.person_id)}
                    className="shrink-0"
                  >
                    Explore
                  </Button>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <div className="flex justify-start pt-4">
        <Button variant="outline" onClick={onBack}>
          Back to Search
        </Button>
      </div>
    </div>
  )
}
