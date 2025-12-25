// @ts-nocheck
import { useState } from "react"
import { useMutation } from "@tanstack/react-query"
import { CheckCircle2, Loader2 } from "lucide-react"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  PersonService,
  type PersonCreate,
  type PersonAddressCreate,
  type PersonReligionCreate,
  type PersonRelationshipCreate,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"

interface ConfirmationStepProps {
  familyMemberData: any
  addressData: any
  religionData: any
  onFinish: () => void
}

const RELATIONSHIP_LABELS: Record<string, string> = {
  "rel-6a0ede824d101": "Father",
  "rel-6a0ede824d102": "Mother",
  "rel-6a0ede824d103": "Daughter",
  "rel-6a0ede824d104": "Son",
  "rel-6a0ede824d105": "Wife",
  "rel-6a0ede824d106": "Husband",
  "rel-6a0ede824d107": "Spouse",
}

export function ConfirmationStep({
  familyMemberData,
  addressData,
  religionData,
  onFinish,
}: ConfirmationStepProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const [creationStatus, setCreationStatus] = useState<string>("")

  const createFamilyMemberMutation = useMutation({
    mutationFn: async () => {
      // Step 1: Create the person
      setCreationStatus("Creating person...")
      const personData: PersonCreate = {
        first_name: familyMemberData.first_name,
        middle_name: familyMemberData.middle_name || undefined,
        last_name: familyMemberData.last_name,
        gender_id: familyMemberData.gender_id,
        date_of_birth: familyMemberData.date_of_birth,
        date_of_death:
          familyMemberData.is_dead && familyMemberData.date_of_death
            ? familyMemberData.date_of_death
            : undefined,
        user_id: undefined,
        is_primary: false,
      }

      const person = await PersonService.createFamilyMember({
        requestBody: personData,
      })

      // Step 2: Create address for the person
      setCreationStatus("Adding address...")
      const addressPayload: PersonAddressCreate = {
        country_id: addressData.country_id,
        state_id: addressData.state_id || undefined,
        district_id: addressData.district_id || undefined,
        sub_district_id: addressData.sub_district_id || undefined,
        locality_id: addressData.locality_id || undefined,
        address_line: addressData.address_line || undefined,
        start_date: addressData.start_date,
        is_current: addressData.is_current || false,
      }

      await PersonService.createPersonAddress({
        personId: person.id,
        requestBody: addressPayload,
      })

      // Step 3: Create religion for the person
      setCreationStatus("Adding religion...")
      const religionPayload: PersonReligionCreate = {
        religion_id: religionData.religion_id,
        religion_category_id: religionData.religion_category_id || undefined,
        religion_sub_category_id:
          religionData.religion_sub_category_id || undefined,
      }

      await PersonService.createPersonReligion({
        personId: person.id,
        requestBody: religionPayload,
      })

      // Step 4: Create relationship
      setCreationStatus("Creating relationship...")
      const relationshipData: PersonRelationshipCreate = {
        related_person_id: person.id,
        relationship_type: familyMemberData.relationship_type,
        is_active: true,
      }

      await PersonService.createMyRelationship({
        requestBody: relationshipData,
      })

      return person
    },
    onSuccess: () => {
      setCreationStatus("Complete!")
      showSuccessToast("Family member added successfully!")
      onFinish()
    },
    onError: (error: any) => {
      setCreationStatus("")
      showErrorToast(
        error.message || "Failed to create family member. Please try again."
      )
    },
  })

  if (!familyMemberData) return null

  const relationshipLabel =
    RELATIONSHIP_LABELS[familyMemberData.relationship_type] || "Family Member"

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center justify-center py-4 gap-4">
        <CheckCircle2 className="h-16 w-16 text-green-500" />
        <h3 className="text-xl font-semibold">Review Family Member Details</h3>
        <p className="text-muted-foreground text-center">
          Please review the information before adding to your family
        </p>
      </div>

      <div className="border rounded-lg p-6 space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Relationship</p>
            <p className="font-medium">{relationshipLabel}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Full Name</p>
            <p className="font-medium">
              {familyMemberData.first_name}{" "}
              {familyMemberData.middle_name && `${familyMemberData.middle_name} `}
              {familyMemberData.last_name}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Date of Birth</p>
            <p className="font-medium">
              {new Date(familyMemberData.date_of_birth).toLocaleDateString()}
            </p>
          </div>
          {familyMemberData.is_dead && familyMemberData.date_of_death && (
            <div>
              <p className="text-sm text-muted-foreground">Date of Death</p>
              <p className="font-medium">
                {new Date(familyMemberData.date_of_death).toLocaleDateString()}
              </p>
            </div>
          )}
        </div>

        {familyMemberData.about && (
          <div>
            <p className="text-sm text-muted-foreground">About</p>
            <p className="font-medium">{familyMemberData.about}</p>
          </div>
        )}

        <div className="pt-4 border-t space-y-4">
          <div>
            <p className="text-sm font-semibold mb-2">Address Details</p>
            <div className="text-sm text-muted-foreground space-y-1">
              {addressData.address_line && (
                <p>Address: {addressData.address_line}</p>
              )}
              <p>Start Date: {new Date(addressData.start_date).toLocaleDateString()}</p>
              {addressData.is_current && (
                <p className="text-green-600">Current Address</p>
              )}
            </div>
          </div>
          
          <div>
            <p className="text-sm font-semibold mb-2">Religion Details</p>
            <div className="text-sm text-muted-foreground">
              <p>Religion information will be saved</p>
            </div>
          </div>
        </div>
      </div>

      {creationStatus && (
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>{creationStatus}</span>
        </div>
      )}

      <div className="flex justify-end">
        <LoadingButton
          onClick={() => createFamilyMemberMutation.mutate()}
          loading={createFamilyMemberMutation.isPending}
          size="lg"
        >
          Add Family Member
        </LoadingButton>
      </div>
    </div>
  )
}
