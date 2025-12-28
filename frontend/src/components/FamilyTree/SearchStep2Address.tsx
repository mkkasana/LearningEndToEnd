// @ts-nocheck
import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useQuery } from "@tanstack/react-query"
import { AddressMetadataService, PersonService } from "@/client"
import type { PersonDetails } from "@/client"
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
import { Button } from "@/components/ui/button"

const formSchema = z.object({
  countryId: z.string().min(1, "Country is required"),
  stateId: z.string().min(1, "State is required"),
  districtId: z.string().min(1, "District is required"),
  subDistrictId: z.string().optional(),
  localityId: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

interface SearchStep2AddressProps {
  initialData: {
    countryId: string
    stateId: string
    districtId: string
    subDistrictId?: string
    localityId?: string
  }
  myPerson?: PersonDetails
  onComplete: (data: FormData) => void
  onBack: () => void
}

export function SearchStep2Address({
  initialData,
  myPerson,
  onComplete,
  onBack,
}: SearchStep2AddressProps) {
  const [selectedCountry, setSelectedCountry] = useState<string>(initialData.countryId || "")
  const [selectedState, setSelectedState] = useState<string>(initialData.stateId || "")
  const [selectedDistrict, setSelectedDistrict] = useState<string>(initialData.districtId || "")
  const [selectedSubDistrict, setSelectedSubDistrict] = useState<string>(initialData.subDistrictId || "")

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: initialData,
  })

  // Fetch user's address for default values
  const { data: myAddresses } = useQuery({
    queryKey: ["myAddresses"],
    queryFn: () => PersonService.getMyAddresses(),
    enabled: !!myPerson && !initialData.countryId,
  })

  // Get current address (is_current = true)
  const myAddress = myAddresses?.find((addr: any) => addr.is_current)

  // Set default values from user's address
  useEffect(() => {
    if (myAddress && !initialData.countryId) {
      if (myAddress.country_id) {
        setSelectedCountry(myAddress.country_id)
        form.setValue("countryId", myAddress.country_id)
      }
      if (myAddress.state_id) {
        setSelectedState(myAddress.state_id)
        form.setValue("stateId", myAddress.state_id)
      }
      if (myAddress.district_id) {
        setSelectedDistrict(myAddress.district_id)
        form.setValue("districtId", myAddress.district_id)
      }
      if (myAddress.sub_district_id) {
        setSelectedSubDistrict(myAddress.sub_district_id)
        form.setValue("subDistrictId", myAddress.sub_district_id)
      }
      if (myAddress.locality_id) {
        form.setValue("localityId", myAddress.locality_id)
      }
    }
  }, [myAddress, initialData.countryId, form])

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

  const handleStateChange = (value: string) => {
    setSelectedState(value)
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    form.setValue("stateId", value)
    form.setValue("districtId", "")
    form.setValue("subDistrictId", "")
    form.setValue("localityId", "")
  }

  const handleDistrictChange = (value: string) => {
    setSelectedDistrict(value)
    setSelectedSubDistrict("")
    form.setValue("districtId", value)
    form.setValue("subDistrictId", "")
    form.setValue("localityId", "")
  }

  const handleSubDistrictChange = (value: string) => {
    setSelectedSubDistrict(value)
    form.setValue("subDistrictId", value)
    form.setValue("localityId", "")
  }

  const onSubmit = (data: FormData) => {
    onComplete(data)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
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
                    <SelectItem key={country.countryId} value={country.countryId}>
                      {country.countryName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

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

        {selectedState && (
          <FormField
            control={form.control}
            name="districtId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>District *</FormLabel>
                <Select onValueChange={handleDistrictChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select district" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {districts?.map((district: any) => (
                      <SelectItem key={district.districtId} value={district.districtId}>
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

        {selectedDistrict && subDistricts && subDistricts.length > 0 && (
          <FormField
            control={form.control}
            name="subDistrictId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Sub-District (Optional)</FormLabel>
                <Select onValueChange={handleSubDistrictChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select sub-district" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {subDistricts?.map((subDistrict: any) => (
                      <SelectItem key={subDistrict.tehsilId} value={subDistrict.tehsilId}>
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
                  <SelectContent>
                    {localities?.map((locality: any) => (
                      <SelectItem key={locality.localityId} value={locality.localityId}>
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
