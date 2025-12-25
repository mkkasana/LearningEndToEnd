// @ts-nocheck
import { useState, useEffect } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import {
  ReligionMetadataService,
  PersonReligionService,
  type PersonReligionCreate,
} from "@/client"
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
import { LoadingButton } from "@/components/ui/loading-button"
import useCustomToast from "@/hooks/useCustomToast"

const formSchema = z.object({
  religion_id: z.string().min(1, "Religion is required"),
  religion_category_id: z.string().optional(),
  religion_sub_category_id: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

interface ReligionStepProps {
  onComplete: (data: any) => void
  onBack: () => void
  initialData?: any
}

export function ReligionStep({ onComplete, onBack, initialData }: ReligionStepProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()

  const [selectedReligion, setSelectedReligion] = useState<string>("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      religion_id: initialData?.religion_id || "",
      religion_category_id: initialData?.religion_category_id || "",
      religion_sub_category_id: initialData?.religion_sub_category_id || "",
    },
  })

  // Initialize selected values from initialData
  useEffect(() => {
    if (initialData) {
      if (initialData.religion_id) setSelectedReligion(initialData.religion_id)
      if (initialData.religion_category_id) setSelectedCategory(initialData.religion_category_id)
    }
  }, [initialData])

  // Fetch current user's religion to prefill
  const { data: myReligion } = useQuery({
    queryKey: ["myReligion"],
    queryFn: () => PersonReligionService.getMyReligion(),
  })

  // Prefill with user's religion only if no initialData
  useEffect(() => {
    if (!initialData && myReligion) {
      form.setValue("religion_id", myReligion.religion_id)
      setSelectedReligion(myReligion.religion_id)
      
      if (myReligion.religion_category_id) {
        form.setValue("religion_category_id", myReligion.religion_category_id)
        setSelectedCategory(myReligion.religion_category_id)
      }
      
      if (myReligion.religion_sub_category_id) {
        form.setValue("religion_sub_category_id", myReligion.religion_sub_category_id)
      }
    }
  }, [myReligion, initialData])

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

  const addReligionMutation = useMutation({
    mutationFn: async (data: FormData) => {
      // Just return the data without saving for now
      return data
    },
    onSuccess: (data) => {
      showSuccessToast("Religion details saved!")
      onComplete(data)
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to save religion details")
    },
  })

  const onSubmit = (data: FormData) => {
    // Add display names to the data
    const enrichedData = {
      ...data,
      _displayNames: {
        religion: religions?.find((r: any) => r.religionId === data.religion_id)?.religionName,
        category: categories?.find((c: any) => c.categoryId === data.religion_category_id)?.categoryName,
        subCategory: subCategories?.find((sc: any) => sc.subCategoryId === data.religion_sub_category_id)?.subCategoryName,
      },
    }
    addReligionMutation.mutate(enrichedData)
  }

  const handleReligionChange = (value: string) => {
    setSelectedReligion(value)
    setSelectedCategory("")
    form.setValue("religion_id", value)
    form.setValue("religion_category_id", "")
    form.setValue("religion_sub_category_id", "")
  }

  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value)
    form.setValue("religion_category_id", value)
    form.setValue("religion_sub_category_id", "")
  }

  return (
    <div className="space-y-4">
      <div className="bg-muted p-3 rounded-md text-sm">
        <p className="text-muted-foreground">
          Religion details are pre-filled based on your religion. You can modify them if needed.
        </p>
      </div>

      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {/* Religion */}
          <FormField
            control={form.control}
            name="religion_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Religion *</FormLabel>
                <Select
                  onValueChange={handleReligionChange}
                  value={field.value}
                >
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

          {/* Category */}
          {selectedReligion && categories && categories.length > 0 && (
            <FormField
              control={form.control}
              name="religion_category_id"
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

          {/* Sub-Category */}
          {selectedCategory && subCategories && subCategories.length > 0 && (
            <FormField
              control={form.control}
              name="religion_sub_category_id"
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

          <div className="flex justify-between">
            <Button type="button" variant="outline" onClick={onBack}>
              Back
            </Button>
            <LoadingButton type="submit" loading={addReligionMutation.isPending}>
              Next: Review
            </LoadingButton>
          </div>
        </form>
      </Form>
    </div>
  )
}
