// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import {
  AddressMetadataService,
  type PersonAddressCreate,
  PersonService,
} from "@/client"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
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
import useCustomToast from "@/hooks/useCustomToast"

const formSchema = z.object({
  country_id: z.string().min(1, "Country is required"),
  state_id: z.string().optional(),
  district_id: z.string().optional(),
  sub_district_id: z.string().optional(),
  locality_id: z.string().optional(),
  address_line: z.string().optional(),
  start_date: z.string().min(1, "Start date is required"),
  is_current: z.boolean().default(true),
})

type FormData = z.infer<typeof formSchema>

interface AddAddressDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function AddAddressDialog({
  open,
  onOpenChange,
  onSuccess,
}: AddAddressDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const { activePersonId } = useActivePersonContext()

  const [selectedCountry, setSelectedCountry] = useState<string>("")
  const [selectedState, setSelectedState] = useState<string>("")
  const [selectedDistrict, setSelectedDistrict] = useState<string>("")
  const [selectedSubDistrict, setSelectedSubDistrict] = useState<string>("")

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      address_line: "",
      start_date: new Date().toISOString().split("T")[0],
      is_current: true,
    },
  })

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

  // Create address using person-specific endpoint
  // _Requirements: 7.2_
  const addAddressMutation = useMutation({
    mutationFn: (data: PersonAddressCreate) =>
      PersonService.createPersonAddress({
        personId: activePersonId!,
        requestBody: data,
      }),
    onSuccess: () => {
      showSuccessToast("Address added successfully!")
      queryClient.invalidateQueries({ queryKey: ["profileCompletion"] })
      queryClient.invalidateQueries({
        queryKey: ["personAddresses", activePersonId],
      })
      onOpenChange(false)
      form.reset()
      if (onSuccess) onSuccess()
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to add address")
    },
  })

  const onSubmit = (data: FormData) => {
    const addressData: PersonAddressCreate = {
      country_id: data.country_id,
      state_id: data.state_id || undefined,
      district_id: data.district_id || undefined,
      sub_district_id: data.sub_district_id || undefined,
      locality_id: data.locality_id || undefined,
      address_line: data.address_line || undefined,
      start_date: data.start_date,
      is_current: data.is_current,
    }
    addAddressMutation.mutate(addressData)
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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Address</DialogTitle>
          <DialogDescription>
            Please provide your address details
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            {/* Country */}
            <FormField
              control={form.control}
              name="country_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Country *</FormLabel>
                  <Select
                    onValueChange={handleCountryChange}
                    value={field.value}
                  >
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
                    <FormLabel>State</FormLabel>
                    <Select
                      onValueChange={handleStateChange}
                      value={field.value}
                    >
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
                    <FormLabel>District</FormLabel>
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

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
              >
                Cancel
              </Button>
              <LoadingButton
                type="submit"
                loading={addAddressMutation.isPending}
              >
                Add Address
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
