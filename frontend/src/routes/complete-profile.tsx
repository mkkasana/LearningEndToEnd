import { createFileRoute } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import { ProfileService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { CheckCircle2, Circle } from "lucide-react"

export const Route = createFileRoute("/complete-profile" as any)({
  component: CompleteProfile,
})

function CompleteProfile() {
  const { data: profileStatus, isLoading } = useQuery({
    queryKey: ["profileCompletion"],
    queryFn: () => ProfileService.getProfileCompletionStatus(),
  })

  if (isLoading) {
    return (
      <div className="container flex items-center justify-center min-h-screen">
        <p>Loading...</p>
      </div>
    )
  }

  // If profile is complete, redirect to dashboard
  if (profileStatus?.is_complete) {
    window.location.href = "/"
    return null
  }

  return (
    <div className="container flex items-center justify-center min-h-screen py-8">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-2xl">Complete Your Profile</CardTitle>
          <CardDescription>
            Please complete the following steps to access your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            {/* Person Info Step */}
            <div className="flex items-start gap-4 p-4 border rounded-lg">
              <div className="mt-1">
                {profileStatus?.has_person ? (
                  <CheckCircle2 className="h-6 w-6 text-green-500" />
                ) : (
                  <Circle className="h-6 w-6 text-muted-foreground" />
                )}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">Personal Information</h3>
                <p className="text-sm text-muted-foreground">
                  Your basic personal details are already set up from signup
                </p>
              </div>
              {profileStatus?.has_person && (
                <span className="text-sm text-green-600 font-medium">
                  Complete
                </span>
              )}
            </div>

            {/* Address Step */}
            <div className="flex items-start gap-4 p-4 border rounded-lg">
              <div className="mt-1">
                {profileStatus?.has_address ? (
                  <CheckCircle2 className="h-6 w-6 text-green-500" />
                ) : (
                  <Circle className="h-6 w-6 text-muted-foreground" />
                )}
              </div>
              <div className="flex-1">
                <h3 className="font-semibold">Address Information</h3>
                <p className="text-sm text-muted-foreground">
                  Add your current address details
                </p>
              </div>
              {!profileStatus?.has_address && (
                <Button size="sm" variant="outline">
                  Add Address
                </Button>
              )}
              {profileStatus?.has_address && (
                <span className="text-sm text-green-600 font-medium">
                  Complete
                </span>
              )}
            </div>
          </div>

          {profileStatus?.is_complete && (
            <Button
              className="w-full"
              onClick={() => window.location.href = "/"}
            >
              Continue to Dashboard
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
