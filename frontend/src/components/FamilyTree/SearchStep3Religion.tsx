// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useQuery } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import type { PersonDetails } from "@/client"
import { PersonReligionService, ReligionMetadataService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const formSchema = z.object({
  religionId: z.string().min(1, "Religion is required"),
  religionCategoryId: z.string().optional(),
  religionSubCategoryId: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

interface SearchStep3ReligionProps {
  initialData: {
    religionId: string
    religionCategoryId?: string
    religionSubCategoryId?: string
  }
  myPerson?: PersonDetails
  onComplete: (data: FormData) => void
  onBack: () => void
}

export function SearchStep3Religion({
  initialData,
  myPerson,
  onComplete,
  onBack,
}: SearchStep3ReligionProps) {
  const [selectedReligion, setSelectedReligion] = useState<string>(
    initialData.religionId || "",
  )
  const [selectedCategory, setSelectedCategory] = useState<string>(
    initialData.religionCategoryId || "",
  )
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: initialData,
  })

  // Fetch user's religion for default values
  const { data: myReligion } = useQuery({
    queryKey: ["myReligion"],
    queryFn: () => PersonReligionService.getMyReligion(),
    enabled: !!myPerson && !initialData.religionId,
  })

  // Set default values from user's religion
  useEffect(() => {
    if (myReligion && !initialData.religionId) {
      if (myReligion.religion_id) {
        setSelectedReligion(myReligion.religion_id)
        form.setValue("religionId", myReligion.religion_id)
      }
      if (myReligion.religion_category_id) {
        setSelectedCategory(myReligion.religion_category_id)
        form.setValue("religionCategoryId", myReligion.religion_category_id)
      }
      if (myReligion.religion_sub_category_id) {
        form.setValue(
          "religionSubCategoryId",
          myReligion.religion_sub_category_id,
        )
      }
    }
  }, [myReligion, initialData.religionId, form])

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

  const handleReligionChange = (value: string) => {
    setSelectedReligion(value)
    setSelectedCategory("")
    form.setValue("religionId", value)
    form.setValue("religionCategoryId", "")
    form.setValue("religionSubCategoryId", "")
  }

  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value)
    form.setValue("religionCategoryId", value)
    form.setValue("religionSubCategoryId", "")
  }

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true)
    try {
      await onComplete(data)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
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
                <SelectContent>
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

        {selectedReligion && categories && categories.length > 0 && (
          <FormField
            control={form.control}
            name="religionCategoryId"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Category (Optional)</FormLabel>
                <Select
                  onValueChange={handleCategoryChange}
                  value={field.value}
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
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
                  <SelectContent>
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

        <div className="flex justify-between pt-4">
          <Button type="button" variant="outline" onClick={onBack}>
            Back
          </Button>
          <LoadingButton type="submit" loading={isSubmitting}>
            Search
          </LoadingButton>
        </div>
      </form>
    </Form>
  )
}
