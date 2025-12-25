// @ts-nocheck
import { useState } from "react"
import { useQueryClient } from "@tanstack/react-query"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { BasicInfoStep } from "./BasicInfoStep"
import { AddressStep } from "./AddressStep"
import { ReligionStep } from "./ReligionStep"
import { ConfirmationStep } from "./ConfirmationStep"

const STEPS = {
  BASIC_INFO: 0,
  ADDRESS: 1,
  RELIGION: 2,
  CONFIRMATION: 3,
}

interface AddFamilyMemberDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function AddFamilyMemberDialog({
  open,
  onOpenChange,
}: AddFamilyMemberDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [currentStep, setCurrentStep] = useState(STEPS.BASIC_INFO)
  const [familyMemberData, setFamilyMemberData] = useState<any>(null)
  const [addressData, setAddressData] = useState<any>(null)
  const [religionData, setReligionData] = useState<any>(null)

  const handleBasicInfoComplete = (data: any) => {
    setFamilyMemberData(data)
    setCurrentStep(STEPS.ADDRESS)
  }

  const handleAddressComplete = (data: any) => {
    setAddressData(data)
    setCurrentStep(STEPS.RELIGION)
  }

  const handleReligionComplete = (data: any) => {
    setReligionData(data)
    setCurrentStep(STEPS.CONFIRMATION)
  }

  const handleClose = () => {
    setCurrentStep(STEPS.BASIC_INFO)
    setFamilyMemberData(null)
    setAddressData(null)
    setReligionData(null)
    onOpenChange(false)
  }

  const handleFinish = () => {
    // This will be called from ConfirmationStep after successful API calls
    showSuccessToast("Family member added successfully!")
    queryClient.invalidateQueries({ queryKey: ["familyMembers"] })
    handleClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Family Member</DialogTitle>
          <DialogDescription>
            {currentStep === STEPS.BASIC_INFO &&
              "Step 1 of 4: Enter basic information"}
            {currentStep === STEPS.ADDRESS &&
              "Step 2 of 4: Add address details"}
            {currentStep === STEPS.RELIGION &&
              "Step 3 of 4: Add religion details"}
            {currentStep === STEPS.CONFIRMATION &&
              "Step 4 of 4: Review and confirm"}
          </DialogDescription>
        </DialogHeader>

        {/* Progress Indicator */}
        <div className="flex items-center justify-center gap-2 mb-4">
          <div
            className={`h-2 w-16 rounded ${currentStep >= STEPS.BASIC_INFO ? "bg-primary" : "bg-muted"}`}
          />
          <div
            className={`h-2 w-16 rounded ${currentStep >= STEPS.ADDRESS ? "bg-primary" : "bg-muted"}`}
          />
          <div
            className={`h-2 w-16 rounded ${currentStep >= STEPS.RELIGION ? "bg-primary" : "bg-muted"}`}
          />
          <div
            className={`h-2 w-16 rounded ${currentStep >= STEPS.CONFIRMATION ? "bg-primary" : "bg-muted"}`}
          />
        </div>

        {currentStep === STEPS.BASIC_INFO && (
          <BasicInfoStep onComplete={handleBasicInfoComplete} />
        )}

        {currentStep === STEPS.ADDRESS && (
          <AddressStep onComplete={handleAddressComplete} />
        )}

        {currentStep === STEPS.RELIGION && (
          <ReligionStep onComplete={handleReligionComplete} />
        )}

        {currentStep === STEPS.CONFIRMATION && (
          <ConfirmationStep
            familyMemberData={familyMemberData}
            addressData={addressData}
            religionData={religionData}
            onFinish={handleFinish}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}
