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
  onConnect: (personId: string, personData: any) => void
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
    data: matchingPersonsRaw,
    isLoading,
    isError,
    error,
    refetch,
    isFetching,
  } = useQuery({
    queryKey: ["searchMatchingPersons", searchRequest],
    queryFn: () =>
      PersonService.searchMatchingPersons({
        requestBody: searchRequest,
      }),
    retry: false,
  })

  // Filter out only the current user (but keep already-connected persons to show them)
  const matchingPersons = matchingPersonsRaw?.filter(
    (person) => !person.is_current_user
  ) || []

  return (
    <div className="space-y-4">
      {/* Loading state */}
      {(isLoading || isFetching) && (
        <div className="flex items-center justify-center py-8 space-x-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <p className="text-sm text-muted-foreground">Searching for matches...</p>
        </div>
      )}

      {/* Error state */}
      {isError && !isLoading && !isFetching && (
        <div className="space-y-4 py-4">
          <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
            <p className="text-sm text-destructive font-medium mb-2">
              Failed to search for matching persons
            </p>
            <p className="text-sm text-muted-foreground">
              {error?.message || "An error occurred while searching. Please try again or proceed to create a new person."}
            </p>
          </div>
          <div className="flex gap-2">
            <LoadingButton 
              variant="outline" 
              onClick={() => refetch()}
              loading={isFetching}
            >
              Retry Search
            </LoadingButton>
            <Button variant="default" onClick={onNext}>
              Proceed to Create New
            </Button>
          </div>
        </div>
      )}

      {/* No matches found */}
      {!isLoading && !isFetching && !isError && matchingPersons && matchingPersons.length === 0 && (
        <div className="space-y-4 py-4">
          <div className="bg-muted p-4 rounded-md">
            <p className="text-sm font-medium mb-2">
              No matching persons found
            </p>
            <p className="text-sm text-muted-foreground">
              We could not find any existing person with similar details. This does not appear to be a duplicate. You can proceed to create this new person.
            </p>
          </div>
        </div>
      )}

      {/* Results with matches */}
      {!isLoading && !isFetching && !isError && matchingPersons && matchingPersons.length > 0 && (
        <div className="space-y-4">
          <div className="bg-muted p-3 rounded-md text-sm">
            <p className="text-muted-foreground">
              We found some existing persons that match the details you entered. 
              You can connect to an existing person or create a new one.
            </p>
          </div>
          
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

                {/* Connect button or status */}
                <div className="pt-2">
                  {person.is_already_connected ? (
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="text-green-600 border-green-600">
                        Already Connected
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        This person is already in your family
                      </span>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      onClick={() => onConnect(person.person_id, person)}
                    >
                      Connect as {relationshipType}
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Navigation buttons */}
      <div className="flex justify-between">
        <Button type="button" variant="outline" onClick={onBack} disabled={isLoading || isFetching}>
          Back
        </Button>
        <Button type="button" onClick={onNext} disabled={isLoading || isFetching}>
          Next: Create New
        </Button>
      </div>
    </div>
  )
}
