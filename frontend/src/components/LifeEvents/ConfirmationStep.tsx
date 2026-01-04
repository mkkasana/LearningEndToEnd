// @ts-nocheck

import { CheckCircle2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { LoadingButton } from "@/components/ui/loading-button"

interface ConfirmationStepProps {
  eventData: any
  locationData: any
  onSubmit: () => void
  onBack: () => void
  isSubmitting: boolean
}

export function ConfirmationStep({
  eventData,
  locationData,
  onSubmit,
  onBack,
  isSubmitting,
}: ConfirmationStepProps) {
  // Build location string from display names
  const locationParts = [
    locationData?._displayNames?.locality,
    locationData?._displayNames?.subDistrict,
    locationData?._displayNames?.district,
    locationData?._displayNames?.state,
    locationData?._displayNames?.country,
  ].filter(Boolean)
  const locationString = locationParts.join(", ")

  // Format date display
  const formatDate = () => {
    const parts = []
    if (eventData?.event_year) parts.push(eventData.event_year)
    if (eventData?.event_month) {
      const months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
      ]
      parts.push(months[eventData.event_month - 1])
    }
    if (eventData?.event_date) parts.push(eventData.event_date)

    if (parts.length === 1) return parts[0]
    if (parts.length === 2) return `${parts[1]} ${parts[0]}`
    return `${parts[1]} ${parts[2]}, ${parts[0]}`
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center justify-center py-4 gap-4">
        <CheckCircle2 className="h-16 w-16 text-green-500" />
        <h3 className="text-xl font-semibold">Review Life Event</h3>
        <p className="text-muted-foreground text-center">
          Please review the information before saving
        </p>
      </div>

      <div className="border rounded-lg p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Event Type</p>
            <p className="font-medium capitalize">
              {eventData?.event_type_label || eventData?.event_type}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Date</p>
            <p className="font-medium">{formatDate()}</p>
          </div>
        </div>

        <div>
          <p className="text-sm text-muted-foreground">Title</p>
          <p className="font-medium">{eventData?.title}</p>
        </div>

        {eventData?.description && (
          <div>
            <p className="text-sm text-muted-foreground">Description</p>
            <p className="font-medium">{eventData.description}</p>
          </div>
        )}

        {(locationString || locationData?.address_details) && (
          <div className="pt-4 border-t">
            <p className="text-sm font-semibold mb-2">Location</p>
            <div className="text-sm text-muted-foreground space-y-1">
              {locationString && <p>{locationString}</p>}
              {locationData?.address_details && (
                <p className="text-xs italic">
                  Details: {locationData.address_details}
                </p>
              )}
            </div>
          </div>
        )}
      </div>

      <div className="flex justify-between">
        <Button variant="outline" onClick={onBack} disabled={isSubmitting}>
          Back
        </Button>
        <LoadingButton onClick={onSubmit} loading={isSubmitting} size="lg">
          Save Life Event
        </LoadingButton>
      </div>
    </div>
  )
}
