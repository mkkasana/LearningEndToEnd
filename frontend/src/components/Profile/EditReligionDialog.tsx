// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { z } from "zod"
import {
  type PersonReligionPublic,
  type PersonReligionUpdate,
  PersonReligionService,
  ReligionMetadataService,
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
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import useCustomToast from "@/hooks/useCustomToast"

const formSchema = z.object({
  religion_id: z.string().min(1, "Religion is required"),
  religion_category_id: z.string().optional(),
  religion_sub_category_id: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

interface EditReligionDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  currentReligion: PersonReligionPublic | null
  onSuccess?: () => void
}

export function EditReligionDialog({
  open,
  onOpenChange,
  currentReligion,
  onSuccess,
}: EditReligionDialogProps) {
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

  // Initialize form with current religion when dialog opens
  useEffect(() => {
    if (open && currentReligion) {
      setSelectedReligion(currentReligion.religion_id || "")
      setSelectedCategory(currentReligion.religion_category_id || "")
      
      form.reset({
        religion_id: currentReligion.religion_id || "",
        religion_category_id: currentReligion.religion_category_id || "",
        religion_sub_category_id: currentReligion.religion_sub_category_id || "",
      })
    }
  }, [open, currentReligion, form])

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


  // Update religion mutation
  const updateReligionMutation = useMutation({
    mutationFn: (data: PersonReligionUpdate) =>
      PersonReligionService.updateMyReligion({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Religion updated successfully!")
      queryClient.invalidateQueries({ queryKey: ["religion", "me"] })
      queryClient.invalidateQueries({ queryKey: ["religionCategories"] })
      queryClient.invalidateQueries({ queryKey: ["religionSubCategories"] })
      onOpenChange(false)
      if (onSuccess) onSuccess()
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to update religion")
    },
  })

  const onSubmit = (data: FormData) => {
    const religionData: PersonReligionUpdate = {
      religion_id: data.religion_id,
      religion_category_id: data.religion_category_id || undefined,
      religion_sub_category_id: data.religion_sub_category_id || undefined,
    }
    updateReligionMutation.mutate(religionData)
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
          <DialogTitle>Edit Religion</DialogTitle>
          <DialogDescription>
            Update your religion information
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
                loading={updateReligionMutation.isPending}
              >
                Save Changes
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
