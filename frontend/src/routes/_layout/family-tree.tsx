import { createFileRoute } from "@tanstack/react-router"
import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { Loader2, AlertCircle, Network } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { ProfileService } from "@/client"

export const Route = createFileRoute("/_layout/family-tree")({
  component: FamilyTreeView,
  head: () => ({
    meta: [
      {
        title: "Family Tree View - FastAPI Cloud",
      },
    ],
  }),
})

function FamilyTreeView() {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<Error | null>(null)

  // Check if user has a person profile
  const { data: profileStatus } = useQuery({
    queryKey: ["profileCompletion"],
    queryFn: () => ProfileService.getProfileCompletionStatus(),
  })

  if (!profileStatus?.has_person) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Profile Not Complete</AlertTitle>
          <AlertDescription>
            <p>You need to complete your profile before viewing the family tree.</p>
            <Button
              className="mt-4"
              onClick={() => {
                window.location.href = "/complete-profile"
              }}
            >
              Complete Profile
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        <p className="mt-4 text-muted-foreground">Loading family tree...</p>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <Alert variant="destructive" className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Error Loading Family Tree</AlertTitle>
          <AlertDescription>
            <p>{error.message || "An unexpected error occurred while loading the family tree."}</p>
            <Button
              className="mt-4"
              variant="outline"
              onClick={() => {
                setError(null)
                setIsLoading(true)
                // Retry logic will be implemented in future tasks
                setTimeout(() => setIsLoading(false), 1000)
              }}
            >
              Retry
            </Button>
          </AlertDescription>
        </Alert>
      </div>
    )
  }

  // Main content (placeholder for now)
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Family Tree View</h1>
          <p className="text-muted-foreground">
            Explore your family relationships visually
          </p>
        </div>
      </div>

      <div className="flex flex-col items-center justify-center min-h-[50vh] border-2 border-dashed rounded-lg">
        <Network className="h-12 w-12 text-muted-foreground mb-4" />
        <h3 className="text-lg font-semibold">Family Tree View</h3>
        <p className="text-muted-foreground text-center max-w-md mt-2">
          The family tree visualization will be displayed here. This feature is currently under development.
        </p>
      </div>
    </div>
  )
}
