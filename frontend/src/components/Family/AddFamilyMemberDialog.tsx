// @ts-nocheck

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { PersonService } from "@/client"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import useCustomToast from "@/hooks/useCustomToast"
import { AddressStep } from "./AddressStep"
import { BasicInfoStep } from "./BasicInfoStep"
import { ConfirmationStep } from "./ConfirmationStep"
import { ConnectConfirmationDialog } from "./ConnectConfirmationDialog"
import { ConnectExistingPersonStep } from "./ConnectExistingPersonStep"
import { ReligionStep } from "./ReligionStep"

const STEPS = {
  BASIC_INFO: 0,
  ADDRESS: 1,
  RELIGION: 2,
  MATCHING: 3,
  CONFIRMATION: 4,
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
  const { activePersonId } = useActivePersonContext()
  const [currentStep, setCurrentStep] = useState(STEPS.BASIC_INFO)
  const [familyMemberData, setFamilyMemberData] = useState<any>(null)
  const [addressData, setAddressData] = useState<any>(null)
  const [religionData, setReligionData] = useState<any>(null)
  const [_matchingPersons, setMatchingPersons] = useState<any[]>([])
  const [showMatchingStep, setShowMatchingStep] = useState(false)
  const [showConnectDialog, setShowConnectDialog] = useState(false)
  const [selectedPersonToConnect, setSelectedPersonToConnect] =
    useState<any>(null)

  // Mutation for creating relationship with existing person
  // Uses person-specific endpoint with activePersonId from context
  // _Requirements: 7.1_
  const createRelationshipMutation = useMutation({
    mutationFn: (data: { relatedPersonId: string; relationshipType: string }) =>
      PersonService.createPersonRelationship({
        personId: activePersonId!,
        requestBody: {
          related_person_id: data.relatedPersonId,
          relationship_type: data.relationshipType,
          is_active: true,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Successfully connected to existing person!")
      queryClient.invalidateQueries({
        queryKey: ["myRelationshipsWithDetails"],
      })
      // Also invalidate person-specific relationships query
      queryClient.invalidateQueries({
        queryKey: ["personRelationshipsWithDetails", activePersonId],
      })
      setShowConnectDialog(false)
      handleClose()
    },
    onError: (error: any) => {
      showErrorToast(
        error.message || "Failed to create relationship. Please try again.",
      )
      // Keep dialog open to allow retry
    },
  })

  const handleBasicInfoComplete = (data: any) => {
    // Add relationship type label for display
    const RELATIONSHIP_TYPES = [
      { value: "rel-6a0ede824d101", label: "Father" },
      { value: "rel-6a0ede824d102", label: "Mother" },
      { value: "rel-6a0ede824d103", label: "Daughter" },
      { value: "rel-6a0ede824d104", label: "Son" },
      { value: "rel-6a0ede824d105", label: "Wife" },
      { value: "rel-6a0ede824d106", label: "Husband" },
      { value: "rel-6a0ede824d107", label: "Spouse" },
    ]
    const relationshipLabel =
      RELATIONSHIP_TYPES.find((r) => r.value === data.relationship_type)
        ?.label || data.relationship_type

    setFamilyMemberData({
      ...data,
      relationshipTypeLabel: relationshipLabel,
    })
    setCurrentStep(STEPS.ADDRESS)
  }

  const handleAddressComplete = (data: any) => {
    setAddressData(data)
    setCurrentStep(STEPS.RELIGION)
  }

  const handleReligionComplete = async (data: any) => {
    setReligionData(data)

    // Build address display string from addressData
    const addressParts = []
    if (addressData._displayNames?.locality)
      addressParts.push(addressData._displayNames.locality)
    if (addressData._displayNames?.subDistrict)
      addressParts.push(addressData._displayNames.subDistrict)
    if (addressData._displayNames?.district)
      addressParts.push(addressData._displayNames.district)
    if (addressData._displayNames?.state)
      addressParts.push(addressData._displayNames.state)
    if (addressData._displayNames?.country)
      addressParts.push(addressData._displayNames.country)
    const _addressDisplay = addressParts.join(", ")

    // Build religion display string from religionData
    const religionParts = []
    if (data._displayNames?.religion)
      religionParts.push(data._displayNames.religion)
    if (data._displayNames?.category)
      religionParts.push(data._displayNames.category)
    if (data._displayNames?.subCategory)
      religionParts.push(data._displayNames.subCategory)
    const _religionDisplay = religionParts.join(", ")

    // Always show matching step - it will handle search internally
    setShowMatchingStep(true)
    setCurrentStep(STEPS.MATCHING)
  }

  const handleBackToBasicInfo = () => {
    setCurrentStep(STEPS.BASIC_INFO)
  }

  const handleBackToAddress = () => {
    setCurrentStep(STEPS.ADDRESS)
  }

  const handleBackToReligion = () => {
    // Clear matching state so search will be re-run if user proceeds again
    setMatchingPersons([])
    setShowMatchingStep(false)
    setCurrentStep(STEPS.RELIGION)
  }

  const handleConnectToPerson = (_personId: string, personData: any) => {
    // personData is passed from ConnectExistingPersonStep
    setSelectedPersonToConnect(personData)
    setShowConnectDialog(true)
  }

  const handleMatchingStepNext = () => {
    // User chose to create new person instead of connecting
    setCurrentStep(STEPS.CONFIRMATION)
  }

  const handleBackToMatching = () => {
    setCurrentStep(STEPS.MATCHING)
  }

  const handleClose = () => {
    setCurrentStep(STEPS.BASIC_INFO)
    setFamilyMemberData(null)
    setAddressData(null)
    setReligionData(null)
    setMatchingPersons([])
    setShowMatchingStep(false)
    setShowConnectDialog(false)
    setSelectedPersonToConnect(null)
    onOpenChange(false)
  }

  const handleFinish = () => {
    // This will be called from ConfirmationStep after successful API calls
    showSuccessToast("Family member added successfully!")
    queryClient.invalidateQueries({ queryKey: ["myRelationshipsWithDetails"] })
    handleClose()
  }

  return (
    <>
      <Dialog open={open} onOpenChange={handleClose}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add Family Member</DialogTitle>
            <DialogDescription>
              {currentStep === STEPS.BASIC_INFO &&
                "Step 1 of 5: Enter basic information"}
              {currentStep === STEPS.ADDRESS &&
                "Step 2 of 5: Add address details"}
              {currentStep === STEPS.RELIGION &&
                "Step 3 of 5: Add religion details"}
              {currentStep === STEPS.MATCHING &&
                "Step 4 of 5: Connect to existing person"}
              {currentStep === STEPS.CONFIRMATION &&
                `Step 5 of 5: Review and confirm`}
            </DialogDescription>
          </DialogHeader>

          {/* Progress Indicator */}
          <div className="flex items-center justify-center gap-2 mb-4">
            <div
              className={`h-2 w-12 rounded ${currentStep >= STEPS.BASIC_INFO ? "bg-primary" : "bg-muted"}`}
            />
            <div
              className={`h-2 w-12 rounded ${currentStep >= STEPS.ADDRESS ? "bg-primary" : "bg-muted"}`}
            />
            <div
              className={`h-2 w-12 rounded ${currentStep >= STEPS.RELIGION ? "bg-primary" : "bg-muted"}`}
            />
            <div
              className={`h-2 w-12 rounded ${currentStep >= STEPS.MATCHING ? "bg-primary" : "bg-muted"}`}
            />
            <div
              className={`h-2 w-12 rounded ${currentStep >= STEPS.CONFIRMATION ? "bg-primary" : "bg-muted"}`}
            />
          </div>

          {currentStep === STEPS.BASIC_INFO && (
            <BasicInfoStep
              onComplete={handleBasicInfoComplete}
              initialData={familyMemberData}
            />
          )}

          {currentStep === STEPS.ADDRESS && (
            <AddressStep
              onComplete={handleAddressComplete}
              onBack={handleBackToBasicInfo}
              initialData={addressData}
            />
          )}

          {currentStep === STEPS.RELIGION && (
            <ReligionStep
              onComplete={handleReligionComplete}
              onBack={handleBackToAddress}
              initialData={religionData}
            />
          )}

          {currentStep === STEPS.MATCHING && showMatchingStep && (
            <ConnectExistingPersonStep
              searchCriteria={{
                firstName: familyMemberData?.first_name || "",
                lastName: familyMemberData?.last_name || "",
                middleName: familyMemberData?.middle_name,
                genderId: familyMemberData?.gender_id || "",
                dateOfBirth: familyMemberData?.date_of_birth || "",
                countryId: addressData?.country_id || "",
                stateId: addressData?.state_id || "",
                districtId: addressData?.district_id || "",
                subDistrictId: addressData?.sub_district_id,
                localityId: addressData?.locality_id,
                religionId: religionData?.religion_id || "",
                religionCategoryId: religionData?.religion_category_id,
                religionSubCategoryId: religionData?.religion_sub_category_id,
                addressDisplay: (() => {
                  const parts = []
                  if (addressData?._displayNames?.locality)
                    parts.push(addressData._displayNames.locality)
                  if (addressData?._displayNames?.subDistrict)
                    parts.push(addressData._displayNames.subDistrict)
                  if (addressData?._displayNames?.district)
                    parts.push(addressData._displayNames.district)
                  if (addressData?._displayNames?.state)
                    parts.push(addressData._displayNames.state)
                  if (addressData?._displayNames?.country)
                    parts.push(addressData._displayNames.country)
                  return parts.join(", ")
                })(),
                religionDisplay: (() => {
                  const parts = []
                  if (religionData?._displayNames?.religion)
                    parts.push(religionData._displayNames.religion)
                  if (religionData?._displayNames?.category)
                    parts.push(religionData._displayNames.category)
                  if (religionData?._displayNames?.subCategory)
                    parts.push(religionData._displayNames.subCategory)
                  return parts.join(", ")
                })(),
              }}
              relationshipType={familyMemberData?.relationshipTypeLabel || ""}
              onConnect={handleConnectToPerson}
              onNext={handleMatchingStepNext}
              onBack={handleBackToReligion}
            />
          )}

          {currentStep === STEPS.CONFIRMATION && (
            <ConfirmationStep
              familyMemberData={familyMemberData}
              addressData={addressData}
              religionData={religionData}
              onFinish={handleFinish}
              onBack={
                showMatchingStep ? handleBackToMatching : handleBackToReligion
              }
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Connect Confirmation Dialog */}
      {selectedPersonToConnect && (
        <ConnectConfirmationDialog
          open={showConnectDialog}
          onOpenChange={setShowConnectDialog}
          personId={selectedPersonToConnect.person_id}
          personName={`${selectedPersonToConnect.first_name} ${selectedPersonToConnect.middle_name ? `${selectedPersonToConnect.middle_name} ` : ""}${selectedPersonToConnect.last_name}`}
          relationshipType={familyMemberData?.relationshipTypeLabel || ""}
          onConfirm={() => {
            createRelationshipMutation.mutate({
              relatedPersonId: selectedPersonToConnect.person_id,
              relationshipType: familyMemberData?.relationship_type || "",
            })
          }}
          isLoading={createRelationshipMutation.isPending}
        />
      )}
    </>
  )
}
