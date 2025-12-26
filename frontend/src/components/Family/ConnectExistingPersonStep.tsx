// @ts-nocheck
import { useQuery } from "@tanstack/react-query"
import { PersonService, type PersonSearchRequest, type PersonMatchResult } from "@/client"
import { Button } from "@/components/ui/button"
import { LoadingButton } from "@/components/ui/loading-button"
import { Badge } from "@/components/ui/badge"
import useCustomToast from "@/hooks/useCustomToast"

interface ConnectExistingPersonStepProps {
  searchCriteria: PersonSearchCriteria
  relationshipType: string
  onConnect: (personId: string) => void
  onNext: () => void
  onBack: () => void
}

interface PersonSearchCriteria {
  firstName: string
  lastName: string
  middleName?: string
  genderId: string
  dateOfBirth: string
  
  countryId: string
  stateId: string
  districtId: string
  subDistrictId?: string
  localityId?: string
  
  religionId: string
  religionCategoryId?: string
  religionSubCategoryId?: string
  
  addressDisplay: string
  religionDisplay: string
}

export function ConnectExistingPersonStep({
  searchCriteria,
  relationshipType,
  onConnect,
  onNext,
  onBack,
}: ConnectExistingPersonStepProps) {
  const { showErrorToast } = useCustomToast()

  // Build the search request from criteria
  const searchRequest: PersonSearchRequest = {
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
    address_display: searchCriteria.addressDisplay,
    religion_display: searchCriteria.religionDisplay,
  }

  // Fetch matching persons
  const {
    data: matchingPersons,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["searchMatchingPersons", searchRequest],
    queryFn: () =>
      PersonService.searchMatchingPersons({
        requestBody: searchRequest,
      }),
    retry: false,
  })

  // Show error toast if query fails
  if (isError && error) {
    showErrorToast(
      error.message || "Failed to search for matching persons"
    )
  }

  return (
    <div className="space-y-4">
      <div className="bg-muted p-3 rounded-md text-sm">
        <p className="text-muted-foreground">
          We found some existing persons that match the details you entered. 
          You can connect to an existing person or create a new one.
        </p>
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">Loading matches...</p>
        </div>
      )}

      {/* Error state */}
      {isError && (
        <div className="space-y-2">
          <p className="text-sm text-destructive">
            Failed to load matching persons. Please try again.
          </p>
          <Button variant="outline" onClick={() => refetch()}>
            Retry
          </Button>
        </div>
      )}

      {/* Results will be displayed here */}
      {!isLoading && !isError && matchingPersons && (
        <div className="space-y-4">
          <p className="text-sm font-medium">
            Found {matchingPersons.length} matching person(s)
          </p>
          
          {/* Scrollable container for results */}
          <div className="max-h-96 overflow-y-auto space-y-3">
            {matchingPersons.map((person: PersonMatchResult) => (
              <div
                key={person.person_id}
                className="border rounded-lg p-4 space-y-2 hover:bg-muted/50 transition-colors"
              >
                {/* Name and match score */}
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium">
                      {person.first_name}{" "}
                      {person.middle_name && `${person.middle_name} `}
                      {person.last_name}
                    </h4>
                  </div>
                  <Badge variant="secondary" className="ml-2">
                    {Math.round(person.match_score)}% match
                  </Badge>
                </div>

                {/* Date of birth */}
                <div className="text-sm text-muted-foreground">
                  <span className="font-medium">DOB:</span>{" "}
                  {new Date(person.date_of_birth).toLocaleDateString()}
                  {person.date_of_death && (
                    <>
                      {" - "}
                      <span className="font-medium">DOD:</span>{" "}
                      {new Date(person.date_of_death).toLocaleDateString()}
                    </>
                  )}
                </div>

                {/* Address */}
                {person.address_display && (
                  <div className="text-sm text-muted-foreground">
                    <span className="font-medium">Address:</span>{" "}
                    {person.address_display}
                  </div>
                )}

                {/* Religion */}
                {person.religion_display && (
                  <div className="text-sm text-muted-foreground">
                    <span className="font-medium">Religion:</span>{" "}
                    {person.religion_display}
                  </div>
                )}

                {/* Connect button */}
                <div className="pt-2">
                  <Button
                    size="sm"
                    onClick={() => onConnect(person.person_id)}
                  >
                    Connect as {relationshipType}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation buttons */}
      <div className="flex justify-between">
        <Button type="button" variant="outline" onClick={onBack}>
          Back
        </Button>
        <Button type="button" onClick={onNext}>
          Next: Create New
        </Button>
      </div>
    </div>
  )
}
