// @ts-nocheck
import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
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

interface AddReligionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function AddReligionDialog({
  open,
  onOpenChange,
  onSuccess,
}: AddReligionDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const [selectedReligion, setSelectedReligion] = useState<string>("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      religion_id: "",
      religion_category_id: "",
      religion_sub_category_id: "",
    },
  })

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
    mutationFn: (data: PersonReligionCreate) =>
      PersonReligionService.createMyReligion({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Religion details added successfully!")
      queryClient.invalidateQueries({ queryKey: ["profileCompletion"] })
      onOpenChange(false)
      form.reset()
      setSelectedReligion("")
      setSelectedCategory("")
      if (onSuccess) onSuccess()
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to add religion details")
    },
  })

  const onSubmit = (data: FormData) => {
    const religionData: PersonReligionCreate = {
      religion_id: data.religion_id,
      religion_category_id: data.religion_category_id || undefined,
      religion_sub_category_id: data.religion_sub_category_id || undefined,
    }
    addReligionMutation.mutate(religionData)
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
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add Religion Details</DialogTitle>
          <DialogDescription>
            Please provide your religion information
          </DialogDescription>
        </DialogHeader>

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
                loading={addReligionMutation.isPending}
              >
                Add Religion
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
