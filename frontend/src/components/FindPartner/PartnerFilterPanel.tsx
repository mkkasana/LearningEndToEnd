// @ts-nocheck
/**
 * PartnerFilterPanel Component - Filter panel for partner search
 * Requirements: 2.1, 2.2, 2.3, 3.1, 4.1, 9.1, 9.2, 10.1, 10.3
 *
 * A sliding sidebar panel containing all search filter controls for
 * finding potential marriage matches.
 */

import { useQuery } from "@tanstack/react-query"
import { RotateCcw, Search } from "lucide-react"
import { useEffect, useState } from "react"
import { PersonMetadataService, ReligionMetadataService } from "@/client"
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
import { TagInput } from "./TagInput"
import type { PartnerFilterPanelProps, PartnerFilters, TagItem } from "./types"
import { validateBirthYearRange } from "./utils/defaultsCalculator"

// Search depth options (1-50)
const SEARCH_DEPTH_OPTIONS = Array.from({ length: 50 }, (_, i) => i + 1)

/**
 * PartnerFilterPanel - Sliding sidebar panel for partner search filters
 */
export function PartnerFilterPanel({
  open,
  onOpenChange,
  filters,
  defaultFilters,
  onApply,
  onReset,
}: PartnerFilterPanelProps) {
  // Local state for form fields
  const [localFilters, setLocalFilters] = useState<PartnerFilters>(filters)
  const [birthYearError, setBirthYearError] = useState<string | null>(null)

  // Sync local state when filters prop changes
  useEffect(() => {
    setLocalFilters(filters)
    setBirthYearError(null)
  }, [filters])

  // Gender metadata query
  const { data: genders } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
  })

  // Religion metadata query
  const { data: religions } = useQuery({
    queryKey: ["religions"],
    queryFn: () => ReligionMetadataService.getReligions(),
  })

  // Get selected religion IDs for cascading category fetch
  const selectedReligionIds = localFilters.includeReligions.map((r) => r.id)

  // Fetch categories for all selected religions
  const categoryQueries = useQuery({
    queryKey: ["categories-for-religions", selectedReligionIds],
    queryFn: async () => {
      if (selectedReligionIds.length === 0) return []
      const results = await Promise.all(
        selectedReligionIds.map((religionId) =>
          ReligionMetadataService.getCategoriesByReligion({ religionId }),
        ),
      )
      // Flatten categories
      return results.flat()
    },
    enabled: selectedReligionIds.length > 0,
  })

  // Get selected category IDs for cascading sub-category fetch
  const selectedCategoryIds = localFilters.includeCategories.map((c) => c.id)

  // Fetch sub-categories for all selected categories
  const subCategoryQueries = useQuery({
    queryKey: ["subcategories-for-categories", selectedCategoryIds],
    queryFn: async () => {
      if (selectedCategoryIds.length === 0) return []
      const results = await Promise.all(
        selectedCategoryIds.map((categoryId) =>
          ReligionMetadataService.getSubCategoriesByCategory({ categoryId }),
        ),
      )
      // Flatten sub-categories
      return results.flat()
    },
    enabled: selectedCategoryIds.length > 0,
  })

  // Convert API data to TagItem format
  // Note: API returns religionId/religionName, categoryId/categoryName, subCategoryId/subCategoryName
  const availableReligions: TagItem[] =
    religions?.map((r: any) => ({
      id: r.religionId,
      name: r.religionName,
    })) || []

  const availableCategories: TagItem[] =
    categoryQueries.data?.map((c: any) => ({
      id: c.categoryId,
      name: c.categoryName,
    })) || []

  const availableSubCategories: TagItem[] =
    subCategoryQueries.data?.map((sc: any) => ({
      id: sc.subCategoryId,
      name: sc.subCategoryName,
    })) || []

  // Handle religion add
  const handleAddReligion = (item: TagItem) => {
    setLocalFilters((prev) => ({
      ...prev,
      includeReligions: [...prev.includeReligions, item],
    }))
  }

  // Handle religion remove with cascading cleanup
  const handleRemoveReligion = (religionId: string) => {
    // Since we don't have religion_id in category list response,
    // we need to clear categories that are no longer valid
    // The categoryQueries will re-fetch based on remaining religions
    const remainingReligionIds = localFilters.includeReligions
      .filter((r) => r.id !== religionId)
      .map((r) => r.id)

    // If no religions remain, clear all categories and sub-categories
    if (remainingReligionIds.length === 0) {
      setLocalFilters((prev) => ({
        ...prev,
        includeReligions: [],
        includeCategories: [],
        includeSubCategories: [],
        excludeSubCategories: [],
      }))
      return
    }

    // Otherwise just remove the religion - categories will be re-validated
    // when the user interacts with them (invalid ones won't appear in dropdown)
    setLocalFilters((prev) => ({
      ...prev,
      includeReligions: prev.includeReligions.filter(
        (r) => r.id !== religionId,
      ),
    }))
  }

  // Handle category add
  const handleAddCategory = (item: TagItem) => {
    setLocalFilters((prev) => ({
      ...prev,
      includeCategories: [...prev.includeCategories, item],
    }))
  }

  // Handle category remove with cascading cleanup
  const handleRemoveCategory = (categoryId: string) => {
    // Since we don't have category_id in sub-category list response,
    // we need to clear sub-categories when no categories remain
    const remainingCategoryIds = localFilters.includeCategories
      .filter((c) => c.id !== categoryId)
      .map((c) => c.id)

    // If no categories remain, clear all sub-categories
    if (remainingCategoryIds.length === 0) {
      setLocalFilters((prev) => ({
        ...prev,
        includeCategories: [],
        includeSubCategories: [],
        excludeSubCategories: [],
      }))
      return
    }

    // Otherwise just remove the category
    setLocalFilters((prev) => ({
      ...prev,
      includeCategories: prev.includeCategories.filter(
        (c) => c.id !== categoryId,
      ),
    }))
  }

  // Handle include sub-category add/remove
  const handleAddIncludeSubCategory = (item: TagItem) => {
    setLocalFilters((prev) => ({
      ...prev,
      includeSubCategories: [...prev.includeSubCategories, item],
    }))
  }

  const handleRemoveIncludeSubCategory = (subCategoryId: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      includeSubCategories: prev.includeSubCategories.filter(
        (sc) => sc.id !== subCategoryId,
      ),
    }))
  }

  // Handle exclude sub-category add/remove
  const handleAddExcludeSubCategory = (item: TagItem) => {
    setLocalFilters((prev) => ({
      ...prev,
      excludeSubCategories: [...prev.excludeSubCategories, item],
    }))
  }

  const handleRemoveExcludeSubCategory = (idOrName: string) => {
    setLocalFilters((prev) => ({
      ...prev,
      // Support removal by ID or by name (for items with empty IDs)
      excludeSubCategories: prev.excludeSubCategories.filter(
        (sc) => sc.id !== idOrName && sc.name !== idOrName,
      ),
    }))
  }

  // Handle birth year changes with validation
  const handleBirthYearFromChange = (value: string) => {
    const numValue = value ? parseInt(value, 10) : undefined
    setLocalFilters((prev) => ({
      ...prev,
      birthYearFrom: numValue,
    }))
    setBirthYearError(
      validateBirthYearRange(numValue, localFilters.birthYearTo),
    )
  }

  const handleBirthYearToChange = (value: string) => {
    const numValue = value ? parseInt(value, 10) : undefined
    setLocalFilters((prev) => ({
      ...prev,
      birthYearTo: numValue,
    }))
    setBirthYearError(
      validateBirthYearRange(localFilters.birthYearFrom, numValue),
    )
  }

  // Handle apply filters
  const handleApply = () => {
    const error = validateBirthYearRange(
      localFilters.birthYearFrom,
      localFilters.birthYearTo,
    )
    if (error) {
      setBirthYearError(error)
      return
    }
    onApply(localFilters)
    onOpenChange(false)
  }

  // Handle reset filters
  const handleReset = () => {
    setLocalFilters(defaultFilters)
    setBirthYearError(null)
    onReset()
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent
        side="left"
        className="w-[90vw] max-w-[400px] p-0 flex flex-col h-[100dvh] overflow-hidden"
      >
        <SheetHeader className="px-6 pt-6 pb-4 flex-shrink-0">
          <SheetTitle>Partner Search Filters</SheetTitle>
          <SheetDescription>
            Configure filters to find potential matches
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="flex-1 overflow-auto">
          <div className="space-y-6 px-6 pb-6">
            {/* Gender Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Gender
              </h3>
              <div className="space-y-2">
                <Label>Target Gender</Label>
                <Select
                  value={localFilters.genderId}
                  onValueChange={(value) =>
                    setLocalFilters((prev) => ({ ...prev, genderId: value }))
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
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

            {/* Birth Year Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Birth Year Range
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-2">
                  <Label htmlFor="birthYearFrom">From Year</Label>
                  <Input
                    id="birthYearFrom"
                    type="number"
                    placeholder="e.g. 1990"
                    min={1900}
                    max={2100}
                    value={localFilters.birthYearFrom ?? ""}
                    onChange={(e) => handleBirthYearFromChange(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="birthYearTo">To Year</Label>
                  <Input
                    id="birthYearTo"
                    type="number"
                    placeholder="e.g. 2000"
                    min={1900}
                    max={2100}
                    value={localFilters.birthYearTo ?? ""}
                    onChange={(e) => handleBirthYearToChange(e.target.value)}
                  />
                </div>
              </div>
              {birthYearError && (
                <p className="text-sm text-destructive">{birthYearError}</p>
              )}
            </div>

            <Separator />

            {/* Religion Filters Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Religion Filters
              </h3>

              {/* Include Religions */}
              <TagInput
                label="Include Religions"
                selectedItems={localFilters.includeReligions}
                availableItems={availableReligions}
                onAdd={handleAddReligion}
                onRemove={handleRemoveReligion}
                placeholder="Add religion"
              />

              {/* Include Categories - cascading from religions */}
              <TagInput
                label="Include Categories"
                selectedItems={localFilters.includeCategories}
                availableItems={availableCategories}
                onAdd={handleAddCategory}
                onRemove={handleRemoveCategory}
                placeholder="Add category"
                disabled={localFilters.includeReligions.length === 0}
              />

              {/* Include Sub-Categories - cascading from categories */}
              <TagInput
                label="Include Sub-Categories"
                selectedItems={localFilters.includeSubCategories}
                availableItems={availableSubCategories}
                onAdd={handleAddIncludeSubCategory}
                onRemove={handleRemoveIncludeSubCategory}
                placeholder="Add sub-category"
                disabled={localFilters.includeCategories.length === 0}
              />

              {/* Exclude Sub-Categories - cascading from categories */}
              <TagInput
                label="Exclude Sub-Categories (Gotras)"
                selectedItems={localFilters.excludeSubCategories}
                availableItems={availableSubCategories}
                onAdd={handleAddExcludeSubCategory}
                onRemove={handleRemoveExcludeSubCategory}
                placeholder="Add gotra to exclude"
                disabled={localFilters.includeCategories.length === 0}
              />
            </div>

            <Separator />

            {/* Search Depth Section */}
            <div className="space-y-4">
              <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                Search Depth
              </h3>
              <div className="space-y-2">
                <Label>Maximum Relationship Hops</Label>
                <Select
                  value={String(localFilters.searchDepth)}
                  onValueChange={(value) =>
                    setLocalFilters((prev) => ({
                      ...prev,
                      searchDepth: parseInt(value, 10),
                    }))
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select depth" />
                  </SelectTrigger>
                  <SelectContent>
                    {SEARCH_DEPTH_OPTIONS.map((depth) => (
                      <SelectItem key={depth} value={String(depth)}>
                        {depth}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        </ScrollArea>

        <SheetFooter className="px-6 py-4 border-t flex-shrink-0 bg-background sticky bottom-0">
          <div className="flex w-full gap-3">
            <Button variant="outline" className="flex-1" onClick={handleReset}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset Filters
            </Button>
            <Button
              className="flex-1"
              onClick={handleApply}
              disabled={!!birthYearError}
            >
              <Search className="h-4 w-4 mr-2" />
              Find Matches
            </Button>
          </div>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  )
}
