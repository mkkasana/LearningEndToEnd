// @ts-nocheck
import { useState } from "react"
import { useQueryClient, useMutation } from "@tanstack/react-query"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { PersonService } from "@/client"
import { BasicInfoStep } from "./BasicInfoStep"
import { AddressStep } from "./AddressStep"
import { ReligionStep } from "./ReligionStep"
import { ConnectExistingPersonStep } from "./ConnectExistingPersonStep"
import { ConfirmationStep } from "./ConfirmationStep"
import { ConnectConfirmationDialog } from "./ConnectConfirmationDialog"

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
  const [currentStep, setCurrentStep] = useState(STEPS.BASIC_INFO)
  const [familyMemberData, setFamilyMemberData] = useState<any>(null)
  const [addressData, setAddressData] = useState<any>(null)
  const [religionData, setReligionData] = useState<any>(null)
  const [matchingPersons, setMatchingPersons] = useState<any[]>([])
  const [showMatchingStep, setShowMatchingStep] = useState(false)
  const [showConnectDialog, setShowConnectDialog] = useState(false)
  const [selectedPersonToConnect, setSelectedPersonToConnect] = useState<any>(null)

  // Mutation for creating relationship with existing person
  const createRelationshipMutation = useMutation({
    mutationFn: (data: { relatedPersonId: string; relationshipType: string }) =>
      PersonService.createMyRelationship({
        requestBody: {
          related_person_id: data.relatedPersonId,
          relationship_type: data.relationshipType,
          is_active: true,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Successfully connected to existing person!")
      queryClient.invalidateQueries({ queryKey: ["myRelationshipsWithDetails"] })
      handleClose()
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to create relationship")
    },
  })

  const handleBasicInfoComplete = (data: any) => {
    setFamilyMemberData(data)
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
    if (addressData._displayNames?.locality) addressParts.push(addressData._displayNames.locality)
    if (addressData._displayNames?.subDistrict) addressParts.push(addressData._displayNames.subDistrict)
    if (addressData._displayNames?.district) addressParts.push(addressData._displayNames.district)
    if (addressData._displayNames?.state) addressParts.push(addressData._displayNames.state)
    if (addressData._displayNames?.country) addressParts.push(addressData._displayNames.country)
    const addressDisplay = addressParts.join(", ")
    
    // Build religion display string from religionData
    const religionParts = []
    if (data._displayNames?.religion) religionParts.push(data._displayNames.religion)
    if (data._displayNames?.category) religionParts.push(data._displayNames.category)
    if (data._displayNames?.subCategory) religionParts.push(data._displayNames.subCategory)
    const religionDisplay = religionParts.join(", ")
    
    // Build PersonSearchCriteria from collected data
    const searchCriteria = {
      firstName: familyMemberData.first_name,
      lastName: familyMemberData.last_name,
      middleName: familyMemberData.middle_name,
      genderId: familyMemberData.gender_id,
      dateOfBirth: familyMemberData.date_of_birth,
      
      countryId: addressData.country_id,
      stateId: addressData.state_id,
      districtId: addressData.district_id,
      subDistrictId: addressData.sub_district_id,
      localityId: addressData.locality_id,
      
      religionId: data.religion_id,
      religionCategoryId: data.religion_category_id,
      religionSubCategoryId: data.religion_sub_category_id,
      
      addressDisplay,
      religionDisplay,
    }
    
    try {
      // Call search API
      const matches = await PersonService.searchMatchingPersons({
        requestBody: {
          first_name: searchCriteria.firstName,
          last_name: searchCriteria.lastName,
          middle_name: searchCriteria.middleName || null,
          gender_id: searchCriteria.genderId,
          date_of_birth: searchCriteria.dateOfBirth,
          country_id: searchCriteria.countryId,
          state_id: searchCriteria.stateId,
          district_id: searchCriteria.districtId,
          sub_district_id: searchCriteria.subDistrictId || null,
          locality_id: searchCriteria.localityId || null,
          religion_id: searchCriteria.religionId,
          religion_category_id: searchCriteria.religionCategoryId || null,
          religion_sub_category_id: searchCriteria.religionSubCategoryId || null,
          address_display: addressDisplay,
          religion_display: religionDisplay,
        },
      })
      
      // If matches found, show matching step
      if (matches && matches.length > 0) {
        setMatchingPersons(matches)
        setShowMatchingStep(true)
        setCurrentStep(STEPS.MATCHING)
      } else {
        // No matches, skip to confirmation
        setShowMatchingStep(false)
        setCurrentStep(STEPS.CONFIRMATION)
      }
    } catch (error) {
      // On error, allow proceeding to confirmation
      console.error("Error searching for matches:", error)
      showErrorToast("Failed to search for matches. Proceeding to create new person.")
      setShowMatchingStep(false)
      setCurrentStep(STEPS.CONFIRMATION)
    }
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

  const handleConnectToPerson = (personId: string) => {
    // Find the person in matching results
    const person = matchingPersons.find((p) => p.person_id === personId)
    if (person) {
      setSelectedPersonToConnect(person)
      setShowConnectDialog(true)
    }
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
                  if (addressData?._displayNames?.locality) parts.push(addressData._displayNames.locality)
                  if (addressData?._displayNames?.subDistrict) parts.push(addressData._displayNames.subDistrict)
                  if (addressData?._displayNames?.district) parts.push(addressData._displayNames.district)
                  if (addressData?._displayNames?.state) parts.push(addressData._displayNames.state)
                  if (addressData?._displayNames?.country) parts.push(addressData._displayNames.country)
                  return parts.join(", ")
                })(),
                religionDisplay: (() => {
                  const parts = []
                  if (religionData?._displayNames?.religion) parts.push(religionData._displayNames.religion)
                  if (religionData?._displayNames?.category) parts.push(religionData._displayNames.category)
                  if (religionData?._displayNames?.subCategory) parts.push(religionData._displayNames.subCategory)
                  return parts.join(", ")
                })(),
              }}
              relationshipType={familyMemberData?.relationship_type || ""}
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
              onBack={showMatchingStep ? handleBackToMatching : handleBackToReligion}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Connect Confirmation Dialog */}
      {selectedPersonToConnect && (
        <ConnectConfirmationDialog
          open={showConnectDialog}
          onOpenChange={setShowConnectDialog}
          personName={`${selectedPersonToConnect.first_name} ${selectedPersonToConnect.middle_name ? selectedPersonToConnect.middle_name + ' ' : ''}${selectedPersonToConnect.last_name}`}
          relationshipType={familyMemberData?.relationshipType || ""}
          onConfirm={() => {
            createRelationshipMutation.mutate({
              relatedPersonId: selectedPersonToConnect.person_id,
              relationshipType: familyMemberData?.relationshipType || "",
            })
          }}
        />
      )}
    </>
  )
}
