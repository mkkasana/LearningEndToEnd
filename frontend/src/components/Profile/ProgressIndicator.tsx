import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

/**
 * Profile step types for the complete-profile flow.
 */
export type ProfileStep =
  | "personal-info"
  | "address"
  | "religion"
  | "marital-status"
  | "duplicate-check"
  | "pending-approval"

/**
 * Profile completion status from the API.
 */
interface ProfileCompletionStatus {
  is_complete: boolean
  has_person: boolean
  has_address: boolean
  has_religion: boolean
  has_marital_status: boolean
  has_duplicate_check: boolean
  has_pending_attachment_request: boolean
  pending_request_id: string | null
  missing_fields: string[]
}

interface ProgressIndicatorProps {
  currentStep: ProfileStep
  profileStatus: ProfileCompletionStatus | undefined
}

/**
 * ProgressIndicator component displays a 5-step progress indicator
 * for the profile completion flow.
 *
 * Steps:
 * 1. Personal Info
 * 2. Address
 * 3. Religion
 * 4. Marital Status
 * 5. Verification (Duplicate Check)
 *
 * Features:
 * - Shows checkmarks for completed steps
 * - Highlights the current step
 * - Responsive: hides labels on mobile, shows on md+
 * - Connecting lines between steps
 */
export function ProgressIndicator({
  currentStep,
  profileStatus,
}: ProgressIndicatorProps) {
  const steps = [
    {
      id: "personal-info" as ProfileStep,
      label: "Personal Info",
      complete: profileStatus?.has_person ?? false,
    },
    {
      id: "address" as ProfileStep,
      label: "Address",
      complete: profileStatus?.has_address ?? false,
    },
    {
      id: "religion" as ProfileStep,
      label: "Religion",
      complete: profileStatus?.has_religion ?? false,
    },
    {
      id: "marital-status" as ProfileStep,
      label: "Marital Status",
      complete: profileStatus?.has_marital_status ?? false,
    },
    {
      id: "duplicate-check" as ProfileStep,
      label: "Verification",
      complete: profileStatus?.has_duplicate_check ?? false,
    },
  ]

  return (
    <div className="flex items-center justify-between mb-8 px-2">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center flex-1 last:flex-none">
          {/* Step circle and label */}
          <div className="flex flex-col items-center">
            <div
              className={cn(
                "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors",
                step.complete
                  ? "bg-green-500 text-white"
                  : currentStep === step.id
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground"
              )}
            >
              {step.complete ? (
                <Check className="h-4 w-4" />
              ) : (
                index + 1
              )}
            </div>
            <span
              className={cn(
                "mt-2 text-xs text-center hidden md:block",
                step.complete
                  ? "text-green-600 font-medium"
                  : currentStep === step.id
                    ? "text-primary font-medium"
                    : "text-muted-foreground"
              )}
            >
              {step.label}
            </span>
          </div>

          {/* Connecting line (not after last step) */}
          {index < steps.length - 1 && (
            <div
              className={cn(
                "flex-1 h-0.5 mx-2",
                step.complete ? "bg-green-500" : "bg-muted"
              )}
            />
          )}
        </div>
      ))}
    </div>
  )
}
