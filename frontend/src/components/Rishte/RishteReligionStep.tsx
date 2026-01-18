// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { ReligionMetadataService } from "@/client"
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
import type { RishteReligionStepProps, ReligionFormData } from "./types"

/**
 * Zod schema for religion form validation
 * Requirements:
 * - 5.3: Religion and Category required
 * - 5.4: Sub-Category optional
 */
const religionSchema = z.object({
  religionId: z.string().min(1, "Religion is required"),
  religionCategoryId: z.string().min(1, "Category is required"),
  religionSubCategoryId: z.string().optional(),
})

type FormData = z.infer<typeof religionSchema>

/**
 * RishteReligionStep component - Step 3 of the Person Search Wizard
 * 
 * Collects religion filters with cascading dropdowns:
 * - Religion (required)
 * - Category (required)
 * - Sub-Category (optional)
 * 
 * Requirements:
 * - 5.1: Display cascading dropdowns for religion hierarchy
 * - 5.2: Pre-populate with active person's religion as defaults
 * - 5.3: Religion and Category required
 * - 5.4: Sub-Category optional
 * - 5.5: Reset child dropdowns when parent changes
 * - 5.6: Display Back and Search buttons
 * - 5.7: Proceed to Results step when Search is clicked
 */
export function RishteReligionStep({
  initialData,
  defaultReligion,
  onSearch,
  onBack,
}: RishteReligionStepProps) {
  // Track selected values for cascading queries
  const [selectedReligion, setSelectedReligion] = useState<string>(
    initialData?.religionId || defaultReligion?.religionId || ""
  )
  const [selectedCategory, setSelectedCategory] = useState<string>(
    initialData?.religionCategoryId || defaultReligion?.religionCategoryId || ""
  )

  const form = useForm<FormData>({
    resolver: zodResolver(religionSchema),
    defaultValues: {
      religionId: initialData?.religionId || defaultReligion?.religionId || "",
      religionCategoryId: initialData?.religionCategoryId || defaultReligion?.religionCategoryId || "",
      religionSubCategoryId: initialData?.religionSubCategoryId || defaultReligion?.religionSubCategoryId || "",
    },
  })

  // Apply default religion when it becomes available
  useEffect(() => {
    if (defaultReligion && !initialData?.religionId) {
      if (defaultReligion.religionId) {
        setSelectedReligion(defaultReligion.religionId)
        form.setValue("religionId", defaultReligion.religionId)
      }
      if (defaultReligion.religionCategoryId) {
        setSelectedCategory(defaultReligion.religionCategoryId)
        form.setValue("religionCategoryId", defaultReligion.religionCategoryId)
      }
      if (defaultReligion.religionSubCategoryId) {
        form.setValue("religionSubCategoryId", defaultReligion.religionSubCategoryId)
      }
    }
  }, [defaultReligion, initialData?.religionId, form])

  // Fetch religions
  const { data: religions } = useQuery({
    queryKey: ["religions"],
    queryFn: () => ReligionMetadataService.getReligions(),
  })

  // Fetch categories for selected religion
  const { data: categories } = useQuery({
    queryKey: ["religionCategories", selectedReligion],
    queryFn: () =>
      ReligionMetadataService.getCategoriesByReligion({
        religionId: selectedReligion,
      }),
    enabled: !!selectedReligion,
  })

  // Fetch sub-categories for selected category
  const { data: subCategories } = useQuery({
    queryKey: ["religionSubCategories", selectedCategory],
    queryFn: () =>
      ReligionMetadataService.getSubCategoriesByCategory({
        categoryId: selectedCategory,
      }),
    enabled: !!selectedCategory,
  })

  /**
   * Handle religion change - reset category and sub-category
   * Requirement 5.5: Reset child dropdowns on parent change
   */
  const handleReligionChange = (value: string) => {
    setSelectedReligion(value)
    setSelectedCategory("")
    form.setValue("religionId", value)
    form.setValue("religionCategoryId", "")
    form.setValue("religionSubCategoryId", "")
  }

  /**
   * Handle category change - reset sub-category
   * Requirement 5.5: Reset child dropdowns on parent change
   */
  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value)
    form.setValue("religionCategoryId", value)
    form.setValue("religionSubCategoryId", "")
  }

  const onSubmit = (data: FormData) => {
    const religionData: ReligionFormData = {
      religionId: data.religionId,
      religionCategoryId: data.religionCategoryId,
      religionSubCategoryId: data.religionSubCategoryId || undefined,
    }
    onSearch(religionData)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
        {/* Religion - Required */}
        <FormField
          control={form.control}
          name="religionId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Religion *</FormLabel>
              <Select onValueChange={handleReligionChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select religion" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent className="max-h-[300px]">
                  {religions?.map((religion: any) => (
                    <SelectItem
                      key={religion.religionId}
                      value={religion.religionId}
                    >
                      {religion.religionName}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Category - Required (shown when religion selected) */}
        {selectedReligion && (
          <FormField
            control={form.control}
            name="religionCategoryId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Category *</FormLabel>
                <Select onValueChange={handleCategoryChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="max-h-[300px]">
                    {categories?.map((category: any) => (
                      <SelectItem
                        key={category.categoryId}
                        value={category.categoryId}
                      >
                        {category.categoryName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Sub-Category - Optional (shown when category selected and data available) */}
        {selectedCategory && subCategories && subCategories.length > 0 && (
          <FormField
            control={form.control}
            name="religionSubCategoryId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Sub-Category (Optional)</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select sub-category" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent className="max-h-[300px]">
                    {subCategories?.map((subCategory: any) => (
                      <SelectItem
                        key={subCategory.subCategoryId}
                        value={subCategory.subCategoryId}
                      >
                        {subCategory.subCategoryName}
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
          <Button type="submit">Search</Button>
        </div>
      </form>
    </Form>
  )
}
