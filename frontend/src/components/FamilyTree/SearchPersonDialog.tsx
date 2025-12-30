// @ts-nocheck

import { useQuery } from "@tanstack/react-query"
import { ArrowLeft, Loader2 } from "lucide-react"
import { useState } from "react"
import type { PersonMatchResult } from "@/client"
import { PersonService, ProfileService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import { SearchStep1NameGender } from "./SearchStep1NameGender"
import { SearchStep2Address } from "./SearchStep2Address"
import { SearchStep3Religion } from "./SearchStep3Religion"
import { SearchStep4Results } from "./SearchStep4Results"

interface SearchPersonDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onPersonSelected: (personId: string) => void
}

export interface SearchCriteria {
  // Step 1
  firstName: string
  lastName: string
  genderId?: string

  // Step 2
  countryId: string
  stateId: string
  districtId: string
  subDistrictId?: string
  localityId?: string

  // Step 3
  religionId: string
  religionCategoryId?: string
  religionSubCategoryId?: string
}

export function SearchPersonDialog({
  open,
  onOpenChange,
  onPersonSelected,
}: SearchPersonDialogProps) {
  const [currentStep, setCurrentStep] = useState<1 | 2 | 3 | 4>(1)
  const [searchCriteria, setSearchCriteria] = useState<Partial<SearchCriteria>>(
    {},
  )
  const [searchResults, setSearchResults] = useState<PersonMatchResult[]>([])
  const [isSearching, setIsSearching] = useState(false)

  // Get current user's profile for default values
  const { data: profileStatus } = useQuery({
    queryKey: ["profileCompletion"],
    queryFn: () => ProfileService.getProfileCompletionStatus(),
    enabled: open,
  })

  const { data: myPerson } = useQuery({
    queryKey: ["myPerson"],
    queryFn: () => PersonService.getMyPerson(),
    enabled: open && profileStatus?.has_person === true,
  })

  const handleStep1Complete = (data: {
    firstName: string
    lastName: string
    genderId?: string
  }) => {
    setSearchCriteria((prev) => ({
      ...prev,
      firstName: data.firstName,
      lastName: data.lastName,
      genderId: data.genderId,
    }))
    setCurrentStep(2)
  }

  const handleStep2Complete = (data: {
    countryId: string
    stateId: string
    districtId: string
    subDistrictId?: string
    localityId?: string
  }) => {
    setSearchCriteria((prev) => ({
      ...prev,
      countryId: data.countryId,
      stateId: data.stateId,
      districtId: data.districtId,
      subDistrictId: data.subDistrictId,
      localityId: data.localityId,
    }))
    setCurrentStep(3)
  }

  const handleStep3Complete = async (data: {
    religionId: string
    religionCategoryId?: string
    religionSubCategoryId?: string
  }) => {
    const finalCriteria = {
      ...searchCriteria,
      religionId: data.religionId,
      religionCategoryId: data.religionCategoryId,
      religionSubCategoryId: data.religionSubCategoryId,
    }
    setSearchCriteria(finalCriteria)

    // Execute search
    setIsSearching(true)
    try {
      const results = await PersonService.searchMatchingPersons({
        requestBody: {
          first_name: finalCriteria.firstName!,
          last_name: finalCriteria.lastName!,
          middle_name: null,
          gender_id: finalCriteria.genderId || "",
          date_of_birth: "1900-01-01", // Placeholder - we don't collect this in the search
          country_id: finalCriteria.countryId!,
          state_id: finalCriteria.stateId!,
          district_id: finalCriteria.districtId!,
          sub_district_id: finalCriteria.subDistrictId || null,
          locality_id: finalCriteria.localityId || null,
          religion_id: finalCriteria.religionId!,
          religion_category_id: finalCriteria.religionCategoryId || null,
          religion_sub_category_id: finalCriteria.religionSubCategoryId || null,
          address_display: "",
          religion_display: "",
        },
      })
      setSearchResults(results)
      setCurrentStep(4)
    } catch (error) {
      console.error("Search failed:", error)
      // TODO: Show error toast
    } finally {
      setIsSearching(false)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => (prev - 1) as 1 | 2 | 3 | 4)
    }
  }

  const handleExplore = (personId: string) => {
    onPersonSelected(personId)
    onOpenChange(false)
    // Reset state for next time
    setCurrentStep(1)
    setSearchCriteria({})
    setSearchResults([])
  }

  const handleClose = () => {
    onOpenChange(false)
    // Reset state
    setCurrentStep(1)
    setSearchCriteria({})
    setSearchResults([])
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            {currentStep > 1 && currentStep < 4 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBack}
                className="h-8 w-8 p-0"
              >
                <ArrowLeft className="h-4 w-4" />
              </Button>
            )}
            <span>Search Person</span>
            <span className="text-sm text-muted-foreground font-normal">
              (Step {currentStep} of 4)
            </span>
          </DialogTitle>
          <DialogDescription>
            {currentStep === 1 && "Enter the person's name and gender"}
            {currentStep === 2 && "Enter address details"}
            {currentStep === 3 && "Enter religion details"}
            {currentStep === 4 &&
              "Select a person to explore their family tree"}
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="flex-1 pr-4">
          {isSearching ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
              <p className="mt-4 text-muted-foreground">Searching...</p>
            </div>
          ) : (
            <>
              {currentStep === 1 && (
                <SearchStep1NameGender
                  initialData={{
                    firstName: searchCriteria.firstName || "",
                    lastName: searchCriteria.lastName || "",
                    genderId: searchCriteria.genderId,
                  }}
                  onComplete={handleStep1Complete}
                />
              )}

              {currentStep === 2 && (
                <SearchStep2Address
                  initialData={{
                    countryId: searchCriteria.countryId || "",
                    stateId: searchCriteria.stateId || "",
                    districtId: searchCriteria.districtId || "",
                    subDistrictId: searchCriteria.subDistrictId,
                    localityId: searchCriteria.localityId,
                  }}
                  myPerson={myPerson}
                  onComplete={handleStep2Complete}
                  onBack={handleBack}
                />
              )}

              {currentStep === 3 && (
                <SearchStep3Religion
                  initialData={{
                    religionId: searchCriteria.religionId || "",
                    religionCategoryId: searchCriteria.religionCategoryId,
                    religionSubCategoryId: searchCriteria.religionSubCategoryId,
                  }}
                  myPerson={myPerson}
                  onComplete={handleStep3Complete}
                  onBack={handleBack}
                />
              )}

              {currentStep === 4 && (
                <SearchStep4Results
                  results={searchResults}
                  onExplore={handleExplore}
                  onBack={handleBack}
                />
              )}
            </>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}
