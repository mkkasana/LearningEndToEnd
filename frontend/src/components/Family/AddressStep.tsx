// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { AddressMetadataService, PersonService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { useActivePersonContext } from "@/contexts/ActivePersonContext"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"

const formSchema = z.object({
  country_id: z.string().min(1, "Country is required"),
  state_id: z.string().min(1, "State is required"),
  district_id: z.string().min(1, "District is required"),
  sub_district_id: z.string().optional(),
  locality_id: z.string().optional(),
  address_line: z.string().optional(),
  start_date: z.string().min(1, "Start date is required"),
  is_current: z.boolean().default(true),
})

type FormData = z.infer<typeof formSchema>

interface AddressStepProps {
  onComplete: (data: any) => void
  onBack: () => void
  initialData?: any
}

export function AddressStep({
  onComplete,
  onBack,
  initialData,
}: AddressStepProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const { user } = useAuth()
  const { activePersonId } = useActivePersonContext()

  const [selectedCountry, setSelectedCountry] = useState<string>("")
  const [selectedState, setSelectedState] = useState<string>("")
  const [selectedDistrict, setSelectedDistrict] = useState<string>("")
  const [selectedSubDistrict, setSelectedSubDistrict] = useState<string>("")

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      address_line: initialData?.address_line || "",
      start_date:
        initialData?.start_date || new Date().toISOString().split("T")[0],
      is_current:
        initialData?.is_current !== undefined ? initialData.is_current : true,
      country_id: initialData?.country_id || "",
      state_id: initialData?.state_id || "",
      district_id: initialData?.district_id || "",
      sub_district_id: initialData?.sub_district_id || "",
      locality_id: initialData?.locality_id || "",
    },
  })

  // Initialize selected values from initialData
  useEffect(() => {
    if (initialData) {
      if (initialData.country_id) setSelectedCountry(initialData.country_id)
      if (initialData.state_id) setSelectedState(initialData.state_id)
      if (initialData.district_id) setSelectedDistrict(initialData.district_id)
      if (initialData.sub_district_id)
        setSelectedSubDistrict(initialData.sub_district_id)
    }
  }, [initialData])

  // Fetch current user's address to prefill using person-specific endpoint
  // _Requirements: 7.2_
  const { data: myAddresses } = useQuery({
    queryKey: ["personAddresses", activePersonId],
    queryFn: () =>
      PersonService.getPersonAddresses({ personId: activePersonId! }),
    enabled: !!activePersonId,
  })

  // Prefill with user's current address only if no initialData
  useEffect(() => {
    if (!initialData && myAddresses && myAddresses.length > 0) {
      const currentAddress =
        myAddresses.find((addr: any) => addr.is_current) || myAddresses[0]
      if (currentAddress) {
        form.setValue("country_id", currentAddress.country_id)
        setSelectedCountry(currentAddress.country_id)

        if (currentAddress.state_id) {
          form.setValue("state_id", currentAddress.state_id)
          setSelectedState(currentAddress.state_id)
        }

        if (currentAddress.district_id) {
          form.setValue("district_id", currentAddress.district_id)
          setSelectedDistrict(currentAddress.district_id)
        }

        if (currentAddress.sub_district_id) {
          form.setValue("sub_district_id", currentAddress.sub_district_id)
          setSelectedSubDistrict(currentAddress.sub_district_id)
        }

        if (currentAddress.locality_id) {
          form.setValue("locality_id", currentAddress.locality_id)
        }
      }
    }
  }, [myAddresses, initialData, form.setValue])

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

  const addAddressMutation = useMutation({
    mutationFn: async (data: FormData) => {
      // Just return the data without saving for now
      return data
    },
    onSuccess: (data) => {
      showSuccessToast("Address details saved!")
      onComplete(data)
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to save address")
    },
  })

  const onSubmit = (data: FormData) => {
    // Add display names to the data
    const enrichedData = {
      ...data,
      _displayNames: {
        country: countries?.find((c: any) => c.countryId === data.country_id)
          ?.countryName,
        state: states?.find((s: any) => s.stateId === data.state_id)?.stateName,
        district: districts?.find((d: any) => d.districtId === data.district_id)
          ?.districtName,
        subDistrict: subDistricts?.find(
          (sd: any) => sd.subDistrictId === data.sub_district_id,
        )?.subDistrictName,
        locality: localities?.find(
          (l: any) => l.localityId === data.locality_id,
        )?.localityName,
      },
    }
    addAddressMutation.mutate(enrichedData)
  }

  const handleCountryChange = (value: string) => {
    setSelectedCountry(value)
    setSelectedState("")
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    form.setValue("country_id", value)
    form.setValue("state_id", "")
    form.setValue("district_id", "")
    form.setValue("sub_district_id", "")
    form.setValue("locality_id", "")
  }

  const handleStateChange = (value: string) => {
    setSelectedState(value)
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    form.setValue("state_id", value)
    form.setValue("district_id", "")
    form.setValue("sub_district_id", "")
    form.setValue("locality_id", "")
  }

  const handleDistrictChange = (value: string) => {
    setSelectedDistrict(value)
    setSelectedSubDistrict("")
    form.setValue("district_id", value)
    form.setValue("sub_district_id", "")
    form.setValue("locality_id", "")
  }

  const handleSubDistrictChange = (value: string) => {
    setSelectedSubDistrict(value)
    form.setValue("sub_district_id", value)
    form.setValue("locality_id", "")
  }

  return (
    <div className="space-y-4">
      <div className="bg-muted p-3 rounded-md text-sm">
        <p className="text-muted-foreground">
          Address details are pre-filled based on your current address. You can
          modify them if needed.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {/* Country */}
          <FormField
            control={form.control}
            name="country_id"
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

          {/* State */}
          {selectedCountry && (
            <FormField
              control={form.control}
              name="state_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>State *</FormLabel>
                  <Select onValueChange={handleStateChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select state" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
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

          {/* District */}
          {selectedState && (
            <FormField
              control={form.control}
              name="district_id"
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
                    <SelectContent>
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

          {/* Sub-District */}
          {selectedDistrict && (
            <FormField
              control={form.control}
              name="sub_district_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Sub-District</FormLabel>
                  <Select
                    onValueChange={handleSubDistrictChange}
                    value={field.value}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select sub-district" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
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

          {/* Locality */}
          {selectedSubDistrict && (
            <FormField
              control={form.control}
              name="locality_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Locality</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select locality" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
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

          {/* Address Line */}
          <FormField
            control={form.control}
            name="address_line"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Address Line (Optional)</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Street, building, apartment, etc."
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Start Date */}
          <FormField
            control={form.control}
            name="start_date"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Start Date *</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="flex justify-between">
            <Button type="button" variant="outline" onClick={onBack}>
              Back
            </Button>
            <LoadingButton type="submit" loading={addAddressMutation.isPending}>
              Next: Add Religion
            </LoadingButton>
          </div>
        </form>
      </Form>
    </div>
  )
}
