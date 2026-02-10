/**
 * Complete Profile Page - Multi-step profile completion flow
 *
 * Requirements: 2.1, 2.2
 * - Restructure the complete-profile flow into 5 steps + pending approval
 * - Add step state management
 * - Determine current step from profile status
 * - Add ProgressIndicator component
 * - Render appropriate step component based on state
 * - Handle step transitions
 */

import { useQuery } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { CheckCircle2, Circle, Loader2 } from "lucide-react"
import { useEffect, useState } from "react"
import { ProfileService } from "@/client"
import { AddAddressDialog } from "@/components/Profile/AddAddressDialog"
import { AddReligionDialog } from "@/components/Profile/AddReligionDialog"
import { DuplicateCheckStep } from "@/components/Profile/DuplicateCheckStep"
import { EditMaritalStatusDialog } from "@/components/Profile/EditMaritalStatusDialog"
import { PendingApprovalStep } from "@/components/Profile/PendingApprovalStep"
import {
  ProgressIndicator,
  type ProfileStep,
} from "@/components/Profile/ProgressIndicator"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export const Route = createFileRoute("/complete-profile" as any)({
  component: CompleteProfile,
})

/**
 * Determine the current step based on profile completion status
 */
function determineCurrentStep(profileStatus: {
  has_person: boolean
  has_address: boolean
  has_religion: boolean
  has_marital_status: boolean
  has_duplicate_check: boolean
  has_pending_attachment_request: boolean
}): ProfileStep {
  // If user has a pending attachment request, show pending approval step
  if (profileStatus.has_pending_attachment_request) {
    return "pending-approval"
  }

  // Otherwise, determine step based on what's incomplete
  if (!profileStatus.has_person) {
    return "personal-info"
  }
  if (!profileStatus.has_address) {
    return "address"
  }
  if (!profileStatus.has_religion) {
    return "religion"
  }
  if (!profileStatus.has_marital_status) {
    return "marital-status"
  }
  if (!profileStatus.has_duplicate_check) {
    return "duplicate-check"
  }

  // All steps complete
  return "duplicate-check"
}

function CompleteProfile() {
  const [showAddressDialog, setShowAddressDialog] = useState(false)
  const [showReligionDialog, setShowReligionDialog] = useState(false)
  const [showMaritalStatusDialog, setShowMaritalStatusDialog] = useState(false)
  const [currentStep, setCurrentStep] = useState<ProfileStep>("personal-info")

  const {
    data: profileStatus,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["profileCompletion"],
    queryFn: () => ProfileService.getProfileCompletionStatus(),
  })

  // Update current step when profile status changes
  useEffect(() => {
    if (profileStatus) {
      const step = determineCurrentStep(profileStatus)
      setCurrentStep(step)
    }
  }, [profileStatus])

  if (isLoading) {
    return (
      <div className="container flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Loading your profile...</p>
        </div>
      </div>
    )
  }

  // If profile is complete, redirect to dashboard
  if (profileStatus?.is_complete) {
    window.location.href = "/"
    return null
  }

  const handleStepComplete = () => {
    refetch()
  }

  // Check if basic profile steps (1-4) are complete
  const basicStepsComplete =
    profileStatus?.has_person &&
    profileStatus?.has_address &&
    profileStatus?.has_religion &&
    profileStatus?.has_marital_status

  // Render pending approval step
  if (currentStep === "pending-approval") {
    return (
      <div className="container flex flex-col items-center justify-center min-h-screen py-8">
        <div className="w-full max-w-2xl">
          <ProgressIndicator
            currentStep={currentStep}
            profileStatus={profileStatus}
          />
          <PendingApprovalStep onCancel={handleStepComplete} />
        </div>
      </div>
    )
  }

  // Render duplicate check step
  if (currentStep === "duplicate-check" && basicStepsComplete) {
    return (
      <div className="container flex flex-col items-center justify-center min-h-screen py-8">
        <div className="w-full max-w-2xl">
          <ProgressIndicator
            currentStep={currentStep}
            profileStatus={profileStatus}
          />
          <DuplicateCheckStep onComplete={handleStepComplete} />
        </div>
      </div>
    )
  }

  // Render basic profile steps (1-4)
  return (
    <>
      <div className="container flex flex-col items-center justify-center min-h-screen py-8">
        <div className="w-full max-w-2xl">
          <ProgressIndicator
            currentStep={currentStep}
            profileStatus={profileStatus}
          />
          <Card>
            <CardHeader>
              <CardTitle className="text-2xl">Complete Your Profile</CardTitle>
              <CardDescription>
                Please complete the following steps to access your account
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                {/* Step 1: Person Info */}
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

                {/* Step 2: Address */}
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
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowAddressDialog(true)}
                    >
                      Add Address
                    </Button>
                  )}
                  {profileStatus?.has_address && (
                    <span className="text-sm text-green-600 font-medium">
                      Complete
                    </span>
                  )}
                </div>

                {/* Step 3: Religion */}
                <div className="flex items-start gap-4 p-4 border rounded-lg">
                  <div className="mt-1">
                    {profileStatus?.has_religion ? (
                      <CheckCircle2 className="h-6 w-6 text-green-500" />
                    ) : (
                      <Circle className="h-6 w-6 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">Religion Information</h3>
                    <p className="text-sm text-muted-foreground">
                      Add your religion details
                    </p>
                  </div>
                  {!profileStatus?.has_religion && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowReligionDialog(true)}
                    >
                      Add Religion
                    </Button>
                  )}
                  {profileStatus?.has_religion && (
                    <span className="text-sm text-green-600 font-medium">
                      Complete
                    </span>
                  )}
                </div>

                {/* Step 4: Marital Status */}
                <div className="flex items-start gap-4 p-4 border rounded-lg">
                  <div className="mt-1">
                    {profileStatus?.has_marital_status ? (
                      <CheckCircle2 className="h-6 w-6 text-green-500" />
                    ) : (
                      <Circle className="h-6 w-6 text-muted-foreground" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold">Marital Status</h3>
                    <p className="text-sm text-muted-foreground">
                      Select your marital status
                    </p>
                  </div>
                  {!profileStatus?.has_marital_status && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => setShowMaritalStatusDialog(true)}
                    >
                      Edit Marital Status
                    </Button>
                  )}
                  {profileStatus?.has_marital_status && (
                    <span className="text-sm text-green-600 font-medium">
                      Complete
                    </span>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      <AddAddressDialog
        open={showAddressDialog}
        onOpenChange={setShowAddressDialog}
        onSuccess={handleStepComplete}
      />

      <AddReligionDialog
        open={showReligionDialog}
        onOpenChange={setShowReligionDialog}
        onSuccess={handleStepComplete}
      />

      <EditMaritalStatusDialog
        open={showMaritalStatusDialog}
        onOpenChange={setShowMaritalStatusDialog}
        onSuccess={handleStepComplete}
      />
    </>
  )
}
