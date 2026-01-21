// @ts-nocheck

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Plus } from "lucide-react"
import { useState } from "react"
import { LifeEventsService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
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

interface AddLifeEventDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  activePersonId?: string // Person ID to create life event for (assumed or primary)
}

export function AddLifeEventDialog({
  open: controlledOpen,
  onOpenChange,
  activePersonId,
}: AddLifeEventDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const [internalOpen, setInternalOpen] = useState(false)
  const [currentStep, setCurrentStep] = useState(STEPS.EVENT_DETAILS)
  const [eventData, setEventData] = useState<any>(null)
  const [locationData, setLocationData] = useState<any>(null)

  // Support both controlled and uncontrolled modes
  const isOpen = controlledOpen !== undefined ? controlledOpen : internalOpen
  const setIsOpen = onOpenChange || setInternalOpen

  const createLifeEventMutation = useMutation({
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
      // Use person-specific endpoint when activePersonId is provided
      // _Requirements: 5.1, 5.2 (assume-person-role)
      if (activePersonId) {
        return LifeEventsService.createPersonLifeEvent({
          personId: activePersonId,
          requestBody: payload,
        })
      }
      return LifeEventsService.createLifeEvent({ requestBody: payload })
    },
    onSuccess: () => {
      showSuccessToast("Life event created successfully!")
      // Invalidate the correct query key based on activePersonId
      if (activePersonId) {
        queryClient.invalidateQueries({
          queryKey: ["life-events", activePersonId],
        })
      } else {
        queryClient.invalidateQueries({ queryKey: ["life-events"] })
      }
      handleClose()
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to create life event")
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
    createLifeEventMutation.mutate()
  }

  const handleClose = () => {
    setCurrentStep(STEPS.EVENT_DETAILS)
    setEventData(null)
    setLocationData(null)
    setIsOpen(false)
  }

  const getStepDescription = () => {
    switch (currentStep) {
      case STEPS.EVENT_DETAILS:
        return "Step 1 of 3: Enter event details"
      case STEPS.LOCATION:
        return "Step 2 of 3: Add location (optional)"
      case STEPS.CONFIRMATION:
        return "Step 3 of 3: Review and confirm"
      default:
        return ""
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Add Life Event
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Life Event</DialogTitle>
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
            isSubmitting={createLifeEventMutation.isPending}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}
