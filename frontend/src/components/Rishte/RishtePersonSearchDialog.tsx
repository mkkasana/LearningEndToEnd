// @ts-nocheck

import { useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { PersonReligionService, PersonService } from "@/client"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import { RishteAddressStep } from "./RishteAddressStep"
import { RishteBasicInfoStep } from "./RishteBasicInfoStep"
import { RishteReligionStep } from "./RishteReligionStep"
import { RishteResultsStep } from "./RishteResultsStep"
import {
  WizardStep,
  type AddressFormData,
  type BasicInfoFormData,
  type PersonSearchCriteria,
  type ReligionFormData,
  type RishtePersonSearchDialogProps,
  type SelectedPerson,
} from "./types"

/**
 * Progress indicator component for wizard steps
 */
function WizardProgress({ currentStep }: { currentStep: WizardStep }) {
  const steps = [
    { step: WizardStep.BASIC_INFO, label: "Basic Info" },
    { step: WizardStep.ADDRESS, label: "Address" },
    { step: WizardStep.RELIGION, label: "Religion" },
    { step: WizardStep.RESULTS, label: "Results" },
  ]

  return (
    <div className="flex items-center justify-center gap-2 mb-4">
      {steps.map((s, index) => (
        <div key={s.step} className="flex items-center">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
              currentStep >= s.step
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-muted-foreground"
            }`}
          >
            {index + 1}
          </div>
          {index < steps.length - 1 && (
            <div
              className={`w-8 h-0.5 mx-1 ${
                currentStep > s.step ? "bg-primary" : "bg-muted"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  )
}

/**
 * RishtePersonSearchDialog component - Main wizard dialog
 * 
 * Manages the 4-step wizard flow for searching and selecting a person:
 * - Step 1: Basic Info (name, gender, birth year)
 * - Step 2: Address (cascading dropdowns with defaults from active person)
 * - Step 3: Religion (cascading dropdowns with defaults from active person)
 * - Step 4: Results (search results with selection)
 * 
 * Requirements:
 * - 8.1: Display as modal dialog
 * - 8.2: Display progress indicator (Step X of 4)
 * - 8.3: Display title indicating which person is being selected
 * - 8.4: Preserve previously selected person when closing without selection
 * - 8.5: Reset to Step 1 when opened
 * - 9.1: Fetch active person's address on mount
 * - 9.2: Fetch active person's religion on mount
 * - 9.5: Handle missing address gracefully
 * - 9.6: Handle missing religion gracefully
 */
export function RishtePersonSearchDialog({
  open,
  onOpenChange,
  personLabel,
  onPersonSelect,
}: RishtePersonSearchDialogProps) {
  const { activePersonId } = useActivePersonContext()

  // Wizard state
  const [currentStep, setCurrentStep] = useState<WizardStep>(WizardStep.BASIC_INFO)
  const [basicInfoData, setBasicInfoData] = useState<BasicInfoFormData | null>(null)
  const [addressData, setAddressData] = useState<AddressFormData | null>(null)
  const [religionData, setReligionData] = useState<ReligionFormData | null>(null)

  // Reset wizard when dialog opens
  useEffect(() => {
    if (open) {
      setCurrentStep(WizardStep.BASIC_INFO)
      setBasicInfoData(null)
      setAddressData(null)
      setReligionData(null)
    }
  }, [open])

  // Fetch active person's addresses for defaults
  const { data: myAddresses } = useQuery({
    queryKey: ["personAddresses", activePersonId],
    queryFn: () => PersonService.getPersonAddresses({ personId: activePersonId! }),
    enabled: !!activePersonId && open,
  })

  // Get current address (is_current = true)
  const currentAddress = myAddresses?.find((addr: any) => addr.is_current)

  // Build default address from active person's current address
  const defaultAddress: AddressFormData | undefined = currentAddress
    ? {
        countryId: currentAddress.country_id || "",
        stateId: currentAddress.state_id || "",
        districtId: currentAddress.district_id || "",
        subDistrictId: currentAddress.sub_district_id || "",
        localityId: currentAddress.locality_id || "",
      }
    : undefined

  // Fetch active person's religion for defaults
  const { data: myReligion } = useQuery({
    queryKey: ["myReligion"],
    queryFn: () => PersonReligionService.getMyReligion(),
    enabled: open,
  })

  // Build default religion from active person's religion
  const defaultReligion: ReligionFormData | undefined = myReligion
    ? {
        religionId: myReligion.religion_id || "",
        religionCategoryId: myReligion.religion_category_id || "",
        religionSubCategoryId: myReligion.religion_sub_category_id || "",
      }
    : undefined

  /**
   * Handle Basic Info step completion
   */
  const handleBasicInfoNext = (data: BasicInfoFormData) => {
    setBasicInfoData(data)
    setCurrentStep(WizardStep.ADDRESS)
  }

  /**
   * Handle Address step completion
   */
  const handleAddressNext = (data: AddressFormData) => {
    setAddressData(data)
    setCurrentStep(WizardStep.RELIGION)
  }

  /**
   * Handle Address step back
   */
  const handleAddressBack = () => {
    setCurrentStep(WizardStep.BASIC_INFO)
  }

  /**
   * Handle Religion step completion (triggers search)
   */
  const handleReligionSearch = (data: ReligionFormData) => {
    setReligionData(data)
    setCurrentStep(WizardStep.RESULTS)
  }

  /**
   * Handle Religion step back
   */
  const handleReligionBack = () => {
    setCurrentStep(WizardStep.ADDRESS)
  }

  /**
   * Handle Results step back
   */
  const handleResultsBack = () => {
    setCurrentStep(WizardStep.RELIGION)
  }

  /**
   * Handle person selection from results
   */
  const handlePersonSelect = (person: SelectedPerson) => {
    onPersonSelect(person)
    onOpenChange(false)
  }

  /**
   * Build search criteria from collected data
   */
  const searchCriteria: PersonSearchCriteria | null =
    basicInfoData && addressData && religionData
      ? {
          basicInfo: basicInfoData,
          address: addressData,
          religion: religionData,
        }
      : null

  /**
   * Get step title
   */
  const getStepTitle = () => {
    switch (currentStep) {
      case WizardStep.BASIC_INFO:
        return "Enter Name & Details"
      case WizardStep.ADDRESS:
        return "Select Address"
      case WizardStep.RELIGION:
        return "Select Religion"
      case WizardStep.RESULTS:
        return "Select Person"
      default:
        return ""
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Select Person {personLabel}</DialogTitle>
          <p className="text-sm text-muted-foreground">
            Step {currentStep + 1} of 4: {getStepTitle()}
          </p>
        </DialogHeader>

        {/* Progress indicator */}
        <WizardProgress currentStep={currentStep} />

        {/* Step content */}
        {currentStep === WizardStep.BASIC_INFO && (
          <RishteBasicInfoStep
            initialData={basicInfoData || undefined}
            onNext={handleBasicInfoNext}
          />
        )}

        {currentStep === WizardStep.ADDRESS && (
          <RishteAddressStep
            initialData={addressData || undefined}
            defaultAddress={defaultAddress}
            onNext={handleAddressNext}
            onBack={handleAddressBack}
          />
        )}

        {currentStep === WizardStep.RELIGION && (
          <RishteReligionStep
            initialData={religionData || undefined}
            defaultReligion={defaultReligion}
            onSearch={handleReligionSearch}
            onBack={handleReligionBack}
          />
        )}

        {currentStep === WizardStep.RESULTS && searchCriteria && (
          <RishteResultsStep
            searchCriteria={searchCriteria}
            onSelect={handlePersonSelect}
            onBack={handleResultsBack}
          />
        )}
      </DialogContent>
    </Dialog>
  )
}
