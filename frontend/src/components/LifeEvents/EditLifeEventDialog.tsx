// @ts-nocheck

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { type LifeEventPublic, LifeEventsService } from "@/client"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { ConfirmationStep } from "./ConfirmationStep"
import { EventDetailsStep } from "./EventDetailsStep"
import { LocationStep } from "./LocationStep"

const STEPS = {
  EVENT_DETAILS: 0,
  LOCATION: 1,
  CONFIRMATION: 2,
}

interface EditLifeEventDialogProps {
  event: LifeEventPublic
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export function EditLifeEventDialog({
  event,
  open,
  onOpenChange,
  onSuccess,
}: EditLifeEventDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const [currentStep, setCurrentStep] = useState(STEPS.EVENT_DETAILS)
  const [eventData, setEventData] = useState<any>(null)
  const [locationData, setLocationData] = useState<any>(null)

  // Initialize form data from the event when dialog opens
  useEffect(() => {
    if (open && event) {
      setEventData({
        event_type: event.event_type,
        title: event.title,
        description: event.description || "",
        event_year: event.event_year,
        event_month: event.event_month,
        event_date: event.event_date,
        event_type_label:
          event.event_type.charAt(0).toUpperCase() + event.event_type.slice(1),
      })
      setLocationData({
        country_id: event.country_id || "",
        state_id: event.state_id || "",
        district_id: event.district_id || "",
        sub_district_id: event.sub_district_id || "",
        locality_id: event.locality_id || "",
        address_details: event.address_details || "",
        _displayNames: {}, // Will be populated when user navigates to location step
      })
    }
  }, [open, event])

  const updateLifeEventMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        event_type: eventData.event_type,
        title: eventData.title,
        description: eventData.description || undefined,
        event_year: eventData.event_year,
        event_month: eventData.event_month || undefined,
        event_date: eventData.event_date || undefined,
        country_id: locationData?.country_id || undefined,
        state_id: locationData?.state_id || undefined,
        district_id: locationData?.district_id || undefined,
        sub_district_id: locationData?.sub_district_id || undefined,
        locality_id: locationData?.locality_id || undefined,
        address_details: locationData?.address_details || undefined,
      }
      return LifeEventsService.updateLifeEvent({
        lifeEventId: event.id,
        requestBody: payload,
      })
    },
    onSuccess: () => {
      showSuccessToast("Life event updated successfully!")
      queryClient.invalidateQueries({ queryKey: ["life-events"] })
      handleClose()
      onSuccess()
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to update life event")
    },
  })

  const handleEventDetailsComplete = (data: any) => {
    setEventData(data)
    setCurrentStep(STEPS.LOCATION)
  }

  const handleLocationComplete = (data: any) => {
    setLocationData(data)
    setCurrentStep(STEPS.CONFIRMATION)
  }

  const handleBackToEventDetails = () => {
    setCurrentStep(STEPS.EVENT_DETAILS)
  }

  const handleBackToLocation = () => {
    setCurrentStep(STEPS.LOCATION)
  }

  const handleSubmit = () => {
    updateLifeEventMutation.mutate()
  }

  const handleClose = () => {
    setCurrentStep(STEPS.EVENT_DETAILS)
    onOpenChange(false)
  }

  const getStepDescription = () => {
    switch (currentStep) {
      case STEPS.EVENT_DETAILS:
        return "Step 1 of 3: Edit event details"
      case STEPS.LOCATION:
        return "Step 2 of 3: Edit location (optional)"
      case STEPS.CONFIRMATION:
        return "Step 3 of 3: Review and save"
      default:
        return ""
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Life Event</DialogTitle>
          <DialogDescription>{getStepDescription()}</DialogDescription>
        </DialogHeader>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center gap-2 mb-4">
          <div
            className={`h-2 w-16 rounded ${currentStep >= STEPS.EVENT_DETAILS ? "bg-primary" : "bg-muted"}`}
          />
          <div
            className={`h-2 w-16 rounded ${currentStep >= STEPS.LOCATION ? "bg-primary" : "bg-muted"}`}
          />
          <div
            className={`h-2 w-16 rounded ${currentStep >= STEPS.CONFIRMATION ? "bg-primary" : "bg-muted"}`}
          />
        </div>

        {currentStep === STEPS.EVENT_DETAILS && (
          <EventDetailsStep
            onComplete={handleEventDetailsComplete}
            initialData={eventData}
          />
        )}

        {currentStep === STEPS.LOCATION && (
          <LocationStep
            onComplete={handleLocationComplete}
            onBack={handleBackToEventDetails}
            initialData={locationData}
          />
        )}

        {currentStep === STEPS.CONFIRMATION && (
          <ConfirmationStep
            eventData={eventData}
            locationData={locationData}
            onSubmit={handleSubmit}
            onBack={handleBackToLocation}
            isSubmitting={updateLifeEventMutation.isPending}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}
