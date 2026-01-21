// @ts-nocheck
import { useQuery } from "@tanstack/react-query"

import {
  AddressMetadataService,
  PersonMetadataService,
  PersonReligionService,
  PersonService,
  ReligionMetadataService,
} from "@/client"
import { Separator } from "@/components/ui/separator"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

const UserInformation = () => {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { user: currentUser } = useAuth()
  const { activePersonId } = useActivePersonContext()

  // Fetch person details
  const { data: personData } = useQuery({
    queryKey: ["person", "me"],
    queryFn: () => PersonService.getMyPerson(),
  })

  // Fetch gender metadata
  const { data: genders } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
    enabled: !!personData,
  })

  // Fetch addresses using person-specific endpoint
  // _Requirements: 7.2_
  const { data: addresses } = useQuery({
    queryKey: ["personAddresses", activePersonId],
    queryFn: () =>
      PersonService.getPersonAddresses({ personId: activePersonId! }),
    enabled: !!activePersonId,
  })

  // Fetch religion
  const { data: religionData } = useQuery({
    queryKey: ["religion", "me"],
    queryFn: () => PersonReligionService.getMyReligion(),
    retry: false, // Don't retry if religion not found
  })

  // Fetch religion metadata for display names
  const { data: religions } = useQuery({
    queryKey: ["religions"],
    queryFn: () => ReligionMetadataService.getReligions(),
    enabled: !!religionData,
  })

  const { data: categories } = useQuery({
    queryKey: ["religionCategories", religionData?.religion_id],
    queryFn: () =>
      ReligionMetadataService.getCategoriesByReligion({
        religionId: religionData?.religion_id,
      }),
    enabled: !!religionData?.religion_id,
  })

  const { data: subCategories } = useQuery({
    queryKey: ["religionSubCategories", religionData?.religion_category_id],
    queryFn: () =>
      ReligionMetadataService.getSubCategoriesByCategory({
        categoryId: religionData?.religion_category_id,
      }),
    enabled: !!religionData?.religion_category_id,
  })

  // Fetch address metadata for display names
  const currentAddress = addresses?.[0]

  const { data: countries } = useQuery({
    queryKey: ["countries"],
    queryFn: () => AddressMetadataService.getCountries(),
    enabled: !!currentAddress,
  })

  const { data: states } = useQuery({
    queryKey: ["states", currentAddress?.country_id],
    queryFn: () =>
      AddressMetadataService.getStatesByCountry({
        countryId: currentAddress?.country_id,
      }),
    enabled: !!currentAddress?.country_id,
  })

  const { data: districts } = useQuery({
    queryKey: ["districts", currentAddress?.state_id],
    queryFn: () =>
      AddressMetadataService.getDistrictsByState({
        stateId: currentAddress?.state_id,
      }),
    enabled: !!currentAddress?.state_id,
  })

  const { data: subDistricts } = useQuery({
    queryKey: ["subDistricts", currentAddress?.district_id],
    queryFn: () =>
      AddressMetadataService.getSubDistrictsByDistrict({
        districtId: currentAddress?.district_id,
      }),
    enabled: !!currentAddress?.district_id,
  })

  const { data: localities } = useQuery({
    queryKey: ["localities", currentAddress?.sub_district_id],
    queryFn: () =>
      AddressMetadataService.getLocalitiesBySubDistrict({
        subDistrictId: currentAddress?.sub_district_id,
      }),
    enabled: !!currentAddress?.sub_district_id,
  })

  // Helper functions to get display names
  const getGenderName = () => {
    if (!personData || !genders) return "N/A"
    const gender = genders.find((g: any) => g.genderId === personData.gender_id)
    return gender?.genderName || "N/A"
  }

  const getReligionName = () => {
    if (!religionData || !religions) return "N/A"
    const religion = religions.find(
      (r: any) => r.religionId === religionData.religion_id,
    )
    return religion?.religionName || "N/A"
  }

  const getCategoryName = () => {
    if (!religionData?.religion_category_id || !categories) return null
    const category = categories.find(
      (c: any) => c.categoryId === religionData.religion_category_id,
    )
    return category?.categoryName
  }

  const getSubCategoryName = () => {
    if (!religionData?.religion_sub_category_id || !subCategories) return null
    const subCategory = subCategories.find(
      (sc: any) => sc.subCategoryId === religionData.religion_sub_category_id,
    )
    return subCategory?.subCategoryName
  }

  const getAddressDisplay = () => {
    if (!currentAddress) return "N/A"

    const parts = []

    if (currentAddress.address_line) {
      parts.push(currentAddress.address_line)
    }

    if (currentAddress.locality_id && localities) {
      const locality = localities.find(
        (l: any) => l.localityId === currentAddress.locality_id,
      )
      if (locality) parts.push(locality.localityName)
    }

    if (currentAddress.sub_district_id && subDistricts) {
      const subDistrict = subDistricts.find(
        (sd: any) => sd.tehsilId === currentAddress.sub_district_id,
      )
      if (subDistrict) parts.push(subDistrict.tehsilName)
    }

    if (currentAddress.district_id && districts) {
      const district = districts.find(
        (d: any) => d.districtId === currentAddress.district_id,
      )
      if (district) parts.push(district.districtName)
    }

    if (currentAddress.state_id && states) {
      const state = states.find(
        (s: any) => s.stateId === currentAddress.state_id,
      )
      if (state) parts.push(state.stateName)
    }

    if (currentAddress.country_id && countries) {
      const country = countries.find(
        (c: any) => c.countryId === currentAddress.country_id,
      )
      if (country) parts.push(country.countryName)
    }

    return parts.length > 0 ? parts.join(", ") : "N/A"
  }

  const getReligionDisplay = () => {
    const religionName = getReligionName()
    const categoryName = getCategoryName()
    const subCategoryName = getSubCategoryName()

    const parts = [religionName]
    if (categoryName) parts.push(categoryName)
    if (subCategoryName) parts.push(subCategoryName)

    return parts.join(", ")
  }

  return (
    <div className="max-w-2xl">
      <h3 className="text-lg font-semibold py-4">User Information</h3>

      <div className="space-y-4">
        {/* Full Name */}
        <div>
          <p className="text-sm font-medium text-muted-foreground">Full Name</p>
          <p className="py-2">{currentUser?.full_name || "N/A"}</p>
        </div>

        {/* Email */}
        <div>
          <p className="text-sm font-medium text-muted-foreground">Email</p>
          <p className="py-2">{currentUser?.email}</p>
        </div>
      </div>

      <Separator className="my-6" />

      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Personal Details</h3>

        {/* Date of Birth */}
        <div>
          <p className="text-sm font-medium text-muted-foreground">
            Date of Birth
          </p>
          <p className="py-2">
            {personData?.date_of_birth
              ? new Date(personData.date_of_birth).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })
              : "N/A"}
          </p>
        </div>

        {/* Gender */}
        <div>
          <p className="text-sm font-medium text-muted-foreground">Gender</p>
          <p className="py-2">{getGenderName()}</p>
        </div>

        {/* Address */}
        <div>
          <p className="text-sm font-medium text-muted-foreground">Address</p>
          <p className="py-2">{getAddressDisplay()}</p>
        </div>

        {/* Religion */}
        <div>
          <p className="text-sm font-medium text-muted-foreground">Religion</p>
          <p className="py-2">{getReligionDisplay()}</p>
        </div>
      </div>
    </div>
  )
}

export default UserInformation
