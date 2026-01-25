// @ts-nocheck
/**
 * RelativesFilterPanel Component - Filter panel for relatives network search
 * Requirements: 6.1, 6.2, 6.3, 7.1, 8.1, 8.4, 9.1, 9.4, 9.6
 *
 * A sliding sidebar panel containing all search filter controls for
 * finding relatives within a family network.
 */

import { useQuery } from "@tanstack/react-query"
import { RotateCcw, Search } from "lucide-react"
import { useEffect, useState } from "react"

import { AddressMetadataService, PersonMetadataService } from "@/client"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"

import { DEFAULT_FILTERS, type RelativesFilters } from "./types"

// Maximum depth allowed (should match backend config)
const MAX_DEPTH = 20

export interface RelativesFilterPanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  filters: RelativesFilters
  onApply: (filters: RelativesFilters) => void
  onReset: () => void
}

/**
 * RelativesFilterPanel - Sliding sidebar panel for relatives network filters
 * Requirements: 9.6 - Slides out from the left side of the screen
 */
export function RelativesFilterPanel({
  open,
  onOpenChange,
  filters,
  onApply,
  onReset,
}: RelativesFilterPanelProps) {
  // Local state for form fields
  const [localFilters, setLocalFilters] = useState<RelativesFilters>(filters)

  // Separate state for depth input to allow clearing while typing
  const [depthInputValue, setDepthInputValue] = useState<string>(
    String(filters.depth),
  )

  // Address selection state for cascading dropdowns
  const [selectedCountry, setSelectedCountry] = useState<string>("")
  const [selectedState, setSelectedState] = useState<string>("")
  const [selectedDistrict, setSelectedDistrict] = useState<string>("")
  const [selectedSubDistrict, setSelectedSubDistrict] = useState<string>("")

  // Sync local state when filters prop changes
  useEffect(() => {
    setLocalFilters(filters)
    setDepthInputValue(String(filters.depth))
    setSelectedCountry(filters.countryId || "")
    setSelectedState(filters.stateId || "")
    setSelectedDistrict(filters.districtId || "")
    setSelectedSubDistrict(filters.subDistrictId || "")
  }, [filters])

  // Gender metadata query
  const { data: genders } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
  })

  // Address cascading queries - Requirements: 7.1-7.6
  const { data: countries } = useQuery({
    queryKey: ["countries"],
    queryFn: () => AddressMetadataService.getCountries(),
  })

  const { data: states } = useQuery({
    queryKey: ["states", selectedCountry],
    queryFn: () =>
      AddressMetadataService.getStatesByCountry({ countryId: selectedCountry }),
    enabled: !!selectedCountry,
  })

  const { data: districts } = useQuery({
    queryKey: ["districts", selectedState],
    queryFn: () =>
      AddressMetadataService.getDistrictsByState({ stateId: selectedState }),
    enabled: !!selectedState,
  })

  const { data: subDistricts } = useQuery({
    queryKey: ["subDistricts", selectedDistrict],
    queryFn: () =>
      AddressMetadataService.getSubDistrictsByDistrict({
        districtId: selectedDistrict,
      }),
    enabled: !!selectedDistrict,
  })

  const { data: localities } = useQuery({
    queryKey: ["localities", selectedSubDistrict],
    queryFn: () =>
      AddressMetadataService.getLocalitiesBySubDistrict({
        subDistrictId: selectedSubDistrict,
      }),
    enabled: !!selectedSubDistrict,
  })

  // Handle depth change - Requirements: 6.1, 6.2
  const handleDepthChange = (value: string) => {
    // Always update the input display value to allow clearing
    setDepthInputValue(value)

    // Only update filters when we have a valid number
    if (value === "") {
      return // Keep current filter value while user is typing
    }
    const numValue = parseInt(value, 10)
    if (!isNaN(numValue) && numValue >= 1 && numValue <= MAX_DEPTH) {
      setLocalFilters((prev) => ({ ...prev, depth: numValue }))
    }
  }

  // Handle depth input blur - restore valid value if empty
  const handleDepthBlur = () => {
    if (depthInputValue === "" || isNaN(parseInt(depthInputValue, 10))) {
      setDepthInputValue(String(localFilters.depth))
    }
  }

  // Handle depth mode change - Requirements: 6.3
  const handleDepthModeChange = (value: "up_to" | "only_at") => {
    setLocalFilters((prev) => ({ ...prev, depthMode: value }))
  }

  // Handle living only change - Requirements: 8.1
  const handleLivingOnlyChange = (checked: boolean) => {
    setLocalFilters((prev) => ({ ...prev, livingOnly: checked }))
  }

  // Handle gender change - Requirements: 8.4
  const handleGenderChange = (value: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      genderId: value === "any" ? undefined : value,
    }))
  }

  // Address cascading handlers - Requirements: 7.3-7.6
  const handleCountryChange = (value: string) => {
    const newValue = value === "any" ? "" : value
    setSelectedCountry(newValue)
    setSelectedState("")
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    setLocalFilters((prev) => ({
      ...prev,
      countryId: newValue || undefined,
      stateId: undefined,
      districtId: undefined,
      subDistrictId: undefined,
      localityId: undefined,
    }))
  }

  const handleStateChange = (value: string) => {
    const newValue = value === "any" ? "" : value
    setSelectedState(newValue)
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    setLocalFilters((prev) => ({
      ...prev,
      stateId: newValue || undefined,
      districtId: undefined,
      subDistrictId: undefined,
      localityId: undefined,
    }))
  }

  const handleDistrictChange = (value: string) => {
    const newValue = value === "any" ? "" : value
    setSelectedDistrict(newValue)
    setSelectedSubDistrict("")
    setLocalFilters((prev) => ({
      ...prev,
      districtId: newValue || undefined,
      subDistrictId: undefined,
      localityId: undefined,
    }))
  }

  const handleSubDistrictChange = (value: string) => {
    const newValue = value === "any" ? "" : value
    setSelectedSubDistrict(newValue)
    setLocalFilters((prev) => ({
      ...prev,
      subDistrictId: newValue || undefined,
      localityId: undefined,
    }))
  }

  const handleLocalityChange = (value: string) => {
    const newValue = value === "any" ? "" : value
    setLocalFilters((prev) => ({
      ...prev,
      localityId: newValue || undefined,
    }))
  }

  // Handle apply filters - Requirements: 9.1, 9.2, 9.3
  const handleApply = () => {
    onApply(localFilters)
    onOpenChange(false)
  }

  // Handle reset filters - Requirements: 9.4, 9.5
  const handleReset = () => {
    setLocalFilters(DEFAULT_FILTERS)
    setDepthInputValue(String(DEFAULT_FILTERS.depth))
    setSelectedCountry("")
    setSelectedState("")
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    onReset()
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="left"
        className="w-[90vw] max-w-[400px] p-0 flex flex-col h-[100dvh] overflow-hidden"
      >
        <SheetHeader className="px-6 pt-6 pb-4 flex-shrink-0">
          <SheetTitle>Relatives Network Filters</SheetTitle>
          <SheetDescription>
            Configure filters to find relatives
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="flex-1 overflow-auto">
          <div className="space-y-6 px-6 pb-6">
            {/* Depth Section - Requirements: 6.1, 6.2, 6.3 */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Depth
              </h3>

              {/* Depth Input */}
              <div className="space-y-2">
                <Label htmlFor="depth">Relationship Depth (1-{MAX_DEPTH})</Label>
                <Input
                  id="depth"
                  type="number"
                  min={1}
                  max={MAX_DEPTH}
                  value={depthInputValue}
                  onChange={(e) => handleDepthChange(e.target.value)}
                  onBlur={handleDepthBlur}
                  className="w-full"
                />
              </div>

              {/* Depth Mode Toggle */}
              <div className="space-y-2">
                <Label>Depth Mode</Label>
                <Select
                  value={localFilters.depthMode}
                  onValueChange={handleDepthModeChange}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="up_to">Up to (1 to N)</SelectItem>
                    <SelectItem value="only_at">Only at (exactly N)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            {/* Additional Filters Section - Requirements: 8.1, 8.4 */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Filters
              </h3>

              {/* Living Only Checkbox - Requirements: 8.1 */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="livingOnly"
                  checked={localFilters.livingOnly}
                  onCheckedChange={handleLivingOnlyChange}
                />
                <Label htmlFor="livingOnly" className="cursor-pointer">
                  Living relatives only
                </Label>
              </div>

              {/* Gender Dropdown - Requirements: 8.4 */}
              <div className="space-y-2">
                <Label>Gender</Label>
                <Select
                  value={localFilters.genderId || "any"}
                  onValueChange={handleGenderChange}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any</SelectItem>
                    {genders?.map((gender) => (
                      <SelectItem key={gender.genderId} value={gender.genderId}>
                        {gender.genderName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <Separator />

            {/* Address Section - Requirements: 7.1-7.6 */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Address Filters
              </h3>

              {/* Country */}
              <div className="space-y-2">
                <Label>Country</Label>
                <Select
                  value={selectedCountry || "any"}
                  onValueChange={handleCountryChange}
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Any" />
                  </SelectTrigger>
                  <SelectContent className="max-h-[300px]">
                    <SelectItem value="any">Any</SelectItem>
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
              </div>

              {/* State - Requirements: 7.3 */}
              {selectedCountry && (
                <div className="space-y-2">
                  <Label>State</Label>
                  <Select
                    value={selectedState || "any"}
                    onValueChange={handleStateChange}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any</SelectItem>
                      {states?.map((state: any) => (
                        <SelectItem key={state.stateId} value={state.stateId}>
                          {state.stateName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              {/* District - Requirements: 7.4 */}
              {selectedState && (
                <div className="space-y-2">
                  <Label>District</Label>
                  <Select
                    value={selectedDistrict || "any"}
                    onValueChange={handleDistrictChange}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any</SelectItem>
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
                </div>
              )}

              {/* Sub-District - Requirements: 7.5 */}
              {selectedDistrict && (
                <div className="space-y-2">
                  <Label>Sub-District</Label>
                  <Select
                    value={selectedSubDistrict || "any"}
                    onValueChange={handleSubDistrictChange}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any</SelectItem>
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
                </div>
              )}

              {/* Locality - Requirements: 7.6 */}
              {selectedSubDistrict && (
                <div className="space-y-2">
                  <Label>Locality</Label>
                  <Select
                    value={localFilters.localityId || "any"}
                    onValueChange={handleLocalityChange}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Any" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any</SelectItem>
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
                </div>
              )}
            </div>
          </div>
        </ScrollArea>

        {/* Footer with Reset and Apply buttons - Requirements: 9.1, 9.4 */}
        <SheetFooter className="px-6 py-4 border-t flex-shrink-0 bg-background sticky bottom-0">
          <div className="flex w-full gap-3">
            <Button variant="outline" className="flex-1" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button className="flex-1" onClick={handleApply}>
              <Search className="h-4 w-4 mr-2" />
              Apply Filters
            </Button>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
