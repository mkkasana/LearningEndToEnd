// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { AddressMetadataService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { AddressFormData, RishteAddressStepProps } from "./types"

/**
 * Zod schema for address form validation
 * Requirements:
 * - 4.3: Country and State required
 * - 4.4: District required
 * - 4.5: Sub-District and Locality optional
 */
const addressSchema = z.object({
  countryId: z.string().min(1, "Country is required"),
  stateId: z.string().min(1, "State is required"),
  districtId: z.string().min(1, "District is required"),
  subDistrictId: z.string().optional(),
  localityId: z.string().optional(),
})

type FormData = z.infer<typeof addressSchema>

/**
 * RishteAddressStep component - Step 2 of the Person Search Wizard
 *
 * Collects address filters with cascading dropdowns:
 * - Country (required)
 * - State (required)
 * - District (required)
 * - Sub-District (optional)
 * - Locality (optional)
 *
 * Requirements:
 * - 4.1: Display cascading dropdowns for address hierarchy
 * - 4.2: Pre-populate with active person's address as defaults
 * - 4.3: Country and State required
 * - 4.4: District required
 * - 4.5: Sub-District and Locality optional
 * - 4.6: Reset child dropdowns when parent changes
 * - 4.7: Display Back and Next buttons
 */
export function RishteAddressStep({
  initialData,
  defaultAddress,
  onNext,
  onBack,
}: RishteAddressStepProps) {
  // Track selected values for cascading queries
  const [selectedCountry, setSelectedCountry] = useState<string>(
    initialData?.countryId || defaultAddress?.countryId || "",
  )
  const [selectedState, setSelectedState] = useState<string>(
    initialData?.stateId || defaultAddress?.stateId || "",
  )
  const [selectedDistrict, setSelectedDistrict] = useState<string>(
    initialData?.districtId || defaultAddress?.districtId || "",
  )
  const [selectedSubDistrict, setSelectedSubDistrict] = useState<string>(
    initialData?.subDistrictId || defaultAddress?.subDistrictId || "",
  )

  const form = useForm<FormData>({
    resolver: zodResolver(addressSchema),
    defaultValues: {
      countryId: initialData?.countryId || defaultAddress?.countryId || "",
      stateId: initialData?.stateId || defaultAddress?.stateId || "",
      districtId: initialData?.districtId || defaultAddress?.districtId || "",
      subDistrictId:
        initialData?.subDistrictId || defaultAddress?.subDistrictId || "",
      localityId: initialData?.localityId || defaultAddress?.localityId || "",
    },
  })

  // Apply default address when it becomes available
  useEffect(() => {
    if (defaultAddress && !initialData?.countryId) {
      if (defaultAddress.countryId) {
        setSelectedCountry(defaultAddress.countryId)
        form.setValue("countryId", defaultAddress.countryId)
      }
      if (defaultAddress.stateId) {
        setSelectedState(defaultAddress.stateId)
        form.setValue("stateId", defaultAddress.stateId)
      }
      if (defaultAddress.districtId) {
        setSelectedDistrict(defaultAddress.districtId)
        form.setValue("districtId", defaultAddress.districtId)
      }
      if (defaultAddress.subDistrictId) {
        setSelectedSubDistrict(defaultAddress.subDistrictId)
        form.setValue("subDistrictId", defaultAddress.subDistrictId)
      }
      if (defaultAddress.localityId) {
        form.setValue("localityId", defaultAddress.localityId)
      }
    }
  }, [defaultAddress, initialData?.countryId, form])

  // Fetch countries
  const { data: countries } = useQuery({
    queryKey: ["countries"],
    queryFn: () => AddressMetadataService.getCountries(),
  })

  // Fetch states for selected country
  const { data: states } = useQuery({
    queryKey: ["states", selectedCountry],
    queryFn: () =>
      AddressMetadataService.getStatesByCountry({ countryId: selectedCountry }),
    enabled: !!selectedCountry,
  })

  // Fetch districts for selected state
  const { data: districts } = useQuery({
    queryKey: ["districts", selectedState],
    queryFn: () =>
      AddressMetadataService.getDistrictsByState({ stateId: selectedState }),
    enabled: !!selectedState,
  })

  // Fetch sub-districts for selected district
  const { data: subDistricts } = useQuery({
    queryKey: ["subDistricts", selectedDistrict],
    queryFn: () =>
      AddressMetadataService.getSubDistrictsByDistrict({
        districtId: selectedDistrict,
      }),
    enabled: !!selectedDistrict,
  })

  // Fetch localities for selected sub-district
  const { data: localities } = useQuery({
    queryKey: ["localities", selectedSubDistrict],
    queryFn: () =>
      AddressMetadataService.getLocalitiesBySubDistrict({
        subDistrictId: selectedSubDistrict,
      }),
    enabled: !!selectedSubDistrict,
  })

  /**
   * Handle country change - reset all child dropdowns
   * Requirement 4.6: Reset child dropdowns on parent change
   */
  const handleCountryChange = (value: string) => {
    setSelectedCountry(value)
    setSelectedState("")
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    form.setValue("countryId", value)
    form.setValue("stateId", "")
    form.setValue("districtId", "")
    form.setValue("subDistrictId", "")
    form.setValue("localityId", "")
  }

  /**
   * Handle state change - reset district and below
   * Requirement 4.6: Reset child dropdowns on parent change
   */
  const handleStateChange = (value: string) => {
    setSelectedState(value)
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    form.setValue("stateId", value)
    form.setValue("districtId", "")
    form.setValue("subDistrictId", "")
    form.setValue("localityId", "")
  }

  /**
   * Handle district change - reset sub-district and locality
   * Requirement 4.6: Reset child dropdowns on parent change
   */
  const handleDistrictChange = (value: string) => {
    setSelectedDistrict(value)
    setSelectedSubDistrict("")
    form.setValue("districtId", value)
    form.setValue("subDistrictId", "")
    form.setValue("localityId", "")
  }

  /**
   * Handle sub-district change - reset locality
   * Requirement 4.6: Reset child dropdowns on parent change
   */
  const handleSubDistrictChange = (value: string) => {
    setSelectedSubDistrict(value)
    form.setValue("subDistrictId", value)
    form.setValue("localityId", "")
  }

  const onSubmit = (data: FormData) => {
    const addressData: AddressFormData = {
      countryId: data.countryId,
      stateId: data.stateId,
      districtId: data.districtId,
      subDistrictId: data.subDistrictId || undefined,
      localityId: data.localityId || undefined,
    }
    onNext(addressData)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
        {/* Country - Required */}
        <FormField
          control={form.control}
          name="countryId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Country *</FormLabel>
              <Select onValueChange={handleCountryChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select country" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent className="max-h-[300px]">
                  {countries?.map((country: any) => (
                    <SelectItem
                      key={country.countryId}
                      value={country.countryId}
                    >
                      {country.countryName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* State - Required (shown when country selected) */}
        {selectedCountry && (
          <FormField
            control={form.control}
            name="stateId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>State *</FormLabel>
                <Select onValueChange={handleStateChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select state" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="max-h-[300px]">
                    {states?.map((state: any) => (
                      <SelectItem key={state.stateId} value={state.stateId}>
                        {state.stateName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* District - Required (shown when state selected) */}
        {selectedState && (
          <FormField
            control={form.control}
            name="districtId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>District *</FormLabel>
                <Select
                  onValueChange={handleDistrictChange}
                  value={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select district" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="max-h-[300px]">
                    {districts?.map((district: any) => (
                      <SelectItem
                        key={district.districtId}
                        value={district.districtId}
                      >
                        {district.districtName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Sub-District - Optional (shown when district selected and data available) */}
        {selectedDistrict && subDistricts && subDistricts.length > 0 && (
          <FormField
            control={form.control}
            name="subDistrictId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Sub-District (Optional)</FormLabel>
                <Select
                  onValueChange={handleSubDistrictChange}
                  value={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select sub-district" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="max-h-[300px]">
                    {subDistricts?.map((subDistrict: any) => (
                      <SelectItem
                        key={subDistrict.tehsilId}
                        value={subDistrict.tehsilId}
                      >
                        {subDistrict.tehsilName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Locality - Optional (shown when sub-district selected and data available) */}
        {selectedSubDistrict && localities && localities.length > 0 && (
          <FormField
            control={form.control}
            name="localityId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Locality (Optional)</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select locality" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="max-h-[300px]">
                    {localities?.map((locality: any) => (
                      <SelectItem
                        key={locality.localityId}
                        value={locality.localityId}
                      >
                        {locality.localityName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Navigation Buttons */}
        <div className="flex justify-between pt-4">
          <Button type="button" variant="outline" onClick={onBack}>
            Back
          </Button>
          <Button type="submit">Next</Button>
        </div>
      </form>
    </Form>
  )
}
