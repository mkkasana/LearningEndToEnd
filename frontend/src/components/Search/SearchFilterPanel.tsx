// @ts-nocheck

import { useQuery } from "@tanstack/react-query"
import { RotateCcw, Search } from "lucide-react"
import { useEffect, useState } from "react"
import {
  AddressMetadataService,
  PersonMetadataService,
  ReligionMetadataService,
} from "@/client"
import { Button } from "@/components/ui/button"
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

export interface SearchFilters {
  firstName?: string
  lastName?: string
  countryId: string
  stateId: string
  districtId: string
  subDistrictId: string
  localityId?: string
  religionId: string
  religionCategoryId: string
  religionSubCategoryId?: string
  genderId?: string
  birthYearFrom?: number
  birthYearTo?: number
}

export interface SearchFilterPanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  filters: SearchFilters
  onApply: (filters: SearchFilters) => void
  onReset: () => void
  defaultFilters: SearchFilters
}

/**
 * SearchFilterPanel component - slide-out panel for advanced search filters
 * Requirements: 3.1-3.7, 4.1-4.2, 5.1-5.7, 6.1-6.5, 7.1-7.2, 8.1-8.2
 */
export function SearchFilterPanel({
  open,
  onOpenChange,
  filters,
  onApply,
  onReset,
  defaultFilters,
}: SearchFilterPanelProps) {
  // Local state for form fields
  const [localFilters, setLocalFilters] = useState<SearchFilters>(filters)
  const [birthYearError, setBirthYearError] = useState<string | null>(null)

  // Cascading dropdown state
  const [selectedCountry, setSelectedCountry] = useState<string>(filters.countryId)
  const [selectedState, setSelectedState] = useState<string>(filters.stateId)
  const [selectedDistrict, setSelectedDistrict] = useState<string>(filters.districtId)
  const [selectedSubDistrict, setSelectedSubDistrict] = useState<string>(filters.subDistrictId)
  const [selectedReligion, setSelectedReligion] = useState<string>(filters.religionId)
  const [selectedCategory, setSelectedCategory] = useState<string>(filters.religionCategoryId)

  // Sync local state when filters prop changes
  useEffect(() => {
    setLocalFilters(filters)
    setSelectedCountry(filters.countryId)
    setSelectedState(filters.stateId)
    setSelectedDistrict(filters.districtId)
    setSelectedSubDistrict(filters.subDistrictId)
    setSelectedReligion(filters.religionId)
    setSelectedCategory(filters.religionCategoryId)
  }, [filters])

  // Address metadata queries
  const { data: countries } = useQuery({
    queryKey: ["countries"],
    queryFn: () => AddressMetadataService.getCountries(),
  })

  const { data: states } = useQuery({
    queryKey: ["states", selectedCountry],
    queryFn: () => AddressMetadataService.getStatesByCountry({ countryId: selectedCountry }),
    enabled: !!selectedCountry,
  })

  const { data: districts } = useQuery({
    queryKey: ["districts", selectedState],
    queryFn: () => AddressMetadataService.getDistrictsByState({ stateId: selectedState }),
    enabled: !!selectedState,
  })

  const { data: subDistricts } = useQuery({
    queryKey: ["subDistricts", selectedDistrict],
    queryFn: () => AddressMetadataService.getSubDistrictsByDistrict({ districtId: selectedDistrict }),
    enabled: !!selectedDistrict,
  })

  const { data: localities } = useQuery({
    queryKey: ["localities", selectedSubDistrict],
    queryFn: () => AddressMetadataService.getLocalitiesBySubDistrict({ subDistrictId: selectedSubDistrict }),
    enabled: !!selectedSubDistrict,
  })

  // Religion metadata queries
  const { data: religions } = useQuery({
    queryKey: ["religions"],
    queryFn: () => ReligionMetadataService.getReligions(),
  })

  const { data: categories } = useQuery({
    queryKey: ["religionCategories", selectedReligion],
    queryFn: () => ReligionMetadataService.getCategoriesByReligion({ religionId: selectedReligion }),
    enabled: !!selectedReligion,
  })

  const { data: subCategories } = useQuery({
    queryKey: ["religionSubCategories", selectedCategory],
    queryFn: () => ReligionMetadataService.getSubCategoriesByCategory({ categoryId: selectedCategory }),
    enabled: !!selectedCategory,
  })

  // Gender metadata query
  const { data: genders } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
  })


  // Address cascading handlers
  const handleCountryChange = (value: string) => {
    setSelectedCountry(value)
    setSelectedState("")
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    setLocalFilters((prev) => ({
      ...prev,
      countryId: value,
      stateId: "",
      districtId: "",
      subDistrictId: "",
      localityId: undefined,
    }))
  }

  const handleStateChange = (value: string) => {
    setSelectedState(value)
    setSelectedDistrict("")
    setSelectedSubDistrict("")
    setLocalFilters((prev) => ({
      ...prev,
      stateId: value,
      districtId: "",
      subDistrictId: "",
      localityId: undefined,
    }))
  }

  const handleDistrictChange = (value: string) => {
    setSelectedDistrict(value)
    setSelectedSubDistrict("")
    setLocalFilters((prev) => ({
      ...prev,
      districtId: value,
      subDistrictId: "",
      localityId: undefined,
    }))
  }

  const handleSubDistrictChange = (value: string) => {
    setSelectedSubDistrict(value)
    setLocalFilters((prev) => ({
      ...prev,
      subDistrictId: value,
      localityId: undefined,
    }))
  }

  // Religion cascading handlers
  const handleReligionChange = (value: string) => {
    setSelectedReligion(value)
    setSelectedCategory("")
    setLocalFilters((prev) => ({
      ...prev,
      religionId: value,
      religionCategoryId: "",
      religionSubCategoryId: undefined,
    }))
  }

  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value)
    setLocalFilters((prev) => ({
      ...prev,
      religionCategoryId: value,
      religionSubCategoryId: undefined,
    }))
  }

  // Validate birth year range
  const validateBirthYearRange = (from?: number, to?: number): boolean => {
    if (from !== undefined && to !== undefined && from > to) {
      setBirthYearError("Birth Year From must be less than or equal to Birth Year To")
      return false
    }
    setBirthYearError(null)
    return true
  }

  // Handle apply filters
  const handleApply = () => {
    if (!validateBirthYearRange(localFilters.birthYearFrom, localFilters.birthYearTo)) {
      return
    }
    onApply(localFilters)
    onOpenChange(false)
  }

  // Handle reset filters
  const handleReset = () => {
    setLocalFilters(defaultFilters)
    setSelectedCountry(defaultFilters.countryId)
    setSelectedState(defaultFilters.stateId)
    setSelectedDistrict(defaultFilters.districtId)
    setSelectedSubDistrict(defaultFilters.subDistrictId)
    setSelectedReligion(defaultFilters.religionId)
    setSelectedCategory(defaultFilters.religionCategoryId)
    setBirthYearError(null)
    onReset()
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-[350px] sm:w-[400px] p-0">
        <SheetHeader className="px-6 pt-6 pb-4">
          <SheetTitle>Search Filters</SheetTitle>
          <SheetDescription>
            Refine your search with advanced filters
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-200px)] px-6">
          <div className="space-y-6 pb-6">
            {/* Name Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Name
              </h3>
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label htmlFor="firstName">First Name</Label>
                  <Input
                    id="firstName"
                    placeholder="Enter first name"
                    value={localFilters.firstName || ""}
                    onChange={(e) =>
                      setLocalFilters((prev) => ({
                        ...prev,
                        firstName: e.target.value || undefined,
                      }))
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="lastName">Last Name</Label>
                  <Input
                    id="lastName"
                    placeholder="Enter last name"
                    value={localFilters.lastName || ""}
                    onChange={(e) =>
                      setLocalFilters((prev) => ({
                        ...prev,
                        lastName: e.target.value || undefined,
                      }))
                    }
                  />
                </div>
              </div>
            </div>

            <Separator />

            {/* Address Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Address
              </h3>
              <div className="space-y-3">
                {/* Country */}
                <div className="space-y-2">
                  <Label>Country *</Label>
                  <Select value={selectedCountry} onValueChange={handleCountryChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select country" />
                    </SelectTrigger>
                    <SelectContent>
                      {countries?.map((country: any) => (
                        <SelectItem key={country.countryId} value={country.countryId}>
                          {country.countryName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* State */}
                {selectedCountry && (
                  <div className="space-y-2">
                    <Label>State *</Label>
                    <Select value={selectedState} onValueChange={handleStateChange}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select state" />
                      </SelectTrigger>
                      <SelectContent>
                        {states?.map((state: any) => (
                          <SelectItem key={state.stateId} value={state.stateId}>
                            {state.stateName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* District */}
                {selectedState && (
                  <div className="space-y-2">
                    <Label>District *</Label>
                    <Select value={selectedDistrict} onValueChange={handleDistrictChange}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select district" />
                      </SelectTrigger>
                      <SelectContent>
                        {districts?.map((district: any) => (
                          <SelectItem key={district.districtId} value={district.districtId}>
                            {district.districtName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Sub-District */}
                {selectedDistrict && (
                  <div className="space-y-2">
                    <Label>Sub-District *</Label>
                    <Select value={selectedSubDistrict} onValueChange={handleSubDistrictChange}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select sub-district" />
                      </SelectTrigger>
                      <SelectContent>
                        {subDistricts?.map((subDistrict: any) => (
                          <SelectItem key={subDistrict.tehsilId} value={subDistrict.tehsilId}>
                            {subDistrict.tehsilName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Locality */}
                {selectedSubDistrict && localities && localities.length > 0 && (
                  <div className="space-y-2">
                    <Label>Locality</Label>
                    <Select
                      value={localFilters.localityId || ""}
                      onValueChange={(value) =>
                        setLocalFilters((prev) => ({
                          ...prev,
                          localityId: value || undefined,
                        }))
                      }
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select locality (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        {localities?.map((locality: any) => (
                          <SelectItem key={locality.localityId} value={locality.localityId}>
                            {locality.localityName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>

            <Separator />

            {/* Religion Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Religion
              </h3>
              <div className="space-y-3">
                {/* Religion */}
                <div className="space-y-2">
                  <Label>Religion *</Label>
                  <Select value={selectedReligion} onValueChange={handleReligionChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select religion" />
                    </SelectTrigger>
                    <SelectContent>
                      {religions?.map((religion: any) => (
                        <SelectItem key={religion.religionId} value={religion.religionId}>
                          {religion.religionName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Category */}
                {selectedReligion && categories && categories.length > 0 && (
                  <div className="space-y-2">
                    <Label>Category *</Label>
                    <Select value={selectedCategory} onValueChange={handleCategoryChange}>
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories?.map((category: any) => (
                          <SelectItem key={category.categoryId} value={category.categoryId}>
                            {category.categoryName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                {/* Sub-Category */}
                {selectedCategory && subCategories && subCategories.length > 0 && (
                  <div className="space-y-2">
                    <Label>Sub-Category</Label>
                    <Select
                      value={localFilters.religionSubCategoryId || ""}
                      onValueChange={(value) =>
                        setLocalFilters((prev) => ({
                          ...prev,
                          religionSubCategoryId: value || undefined,
                        }))
                      }
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue placeholder="Select sub-category (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        {subCategories?.map((subCategory: any) => (
                          <SelectItem key={subCategory.subCategoryId} value={subCategory.subCategoryId}>
                            {subCategory.subCategoryName}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}
              </div>
            </div>

            <Separator />

            {/* Demographics Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Demographics
              </h3>
              <div className="space-y-3">
                {/* Gender */}
                <div className="space-y-2">
                  <Label>Gender</Label>
                  <Select
                    value={localFilters.genderId || ""}
                    onValueChange={(value) =>
                      setLocalFilters((prev) => ({
                        ...prev,
                        genderId: value || undefined,
                      }))
                    }
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Any gender" />
                    </SelectTrigger>
                    <SelectContent>
                      {genders?.map((gender: any) => (
                        <SelectItem key={gender.genderId} value={gender.genderId}>
                          {gender.genderName}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Birth Year Range */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="space-y-2">
                    <Label htmlFor="birthYearFrom">Birth Year From</Label>
                    <Input
                      id="birthYearFrom"
                      type="number"
                      placeholder="e.g. 1980"
                      min={1900}
                      max={2100}
                      value={localFilters.birthYearFrom || ""}
                      onChange={(e) => {
                        const value = e.target.value ? parseInt(e.target.value, 10) : undefined
                        setLocalFilters((prev) => ({
                          ...prev,
                          birthYearFrom: value,
                        }))
                        validateBirthYearRange(value, localFilters.birthYearTo)
                      }}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="birthYearTo">Birth Year To</Label>
                    <Input
                      id="birthYearTo"
                      type="number"
                      placeholder="e.g. 2000"
                      min={1900}
                      max={2100}
                      value={localFilters.birthYearTo || ""}
                      onChange={(e) => {
                        const value = e.target.value ? parseInt(e.target.value, 10) : undefined
                        setLocalFilters((prev) => ({
                          ...prev,
                          birthYearTo: value,
                        }))
                        validateBirthYearRange(localFilters.birthYearFrom, value)
                      }}
                    />
                  </div>
                </div>
                {birthYearError && (
                  <p className="text-sm text-destructive">{birthYearError}</p>
                )}
              </div>
            </div>
          </div>
        </ScrollArea>

        <SheetFooter className="px-6 py-4 border-t">
          <div className="flex w-full gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={handleReset}
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button
              className="flex-1"
              onClick={handleApply}
              disabled={!selectedCountry || !selectedState || !selectedDistrict || !selectedSubDistrict || !selectedReligion || !selectedCategory}
            >
              <Search className="h-4 w-4 mr-2" />
              Apply Filters
            </Button>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
