import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { z } from "zod"
import {
  type MaritalStatus,
  type PersonUpdate,
  PersonMetadataService,
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
  marital_status: z.string().min(1, "Marital status is required"),
})

type FormData = z.infer<typeof formSchema>

interface EditMaritalStatusDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function EditMaritalStatusDialog({
  open,
  onOpenChange,
  onSuccess,
}: EditMaritalStatusDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      marital_status: "",
    },
  })

  // Fetch marital status options
  const { data: maritalStatusOptions } = useQuery({
    queryKey: ["maritalStatuses"],
    queryFn: () => PersonMetadataService.getMaritalStatuses(),
  })

  // Type the options as array of {value, label}
  const options = maritalStatusOptions as
    | Array<{ value: string; label: string }>
    | undefined

  const updateMaritalStatusMutation = useMutation({
    mutationFn: (data: PersonUpdate) =>
      PersonService.updateMyPerson({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Marital status updated successfully!")
      queryClient.invalidateQueries({ queryKey: ["profileCompletion"] })
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
      onOpenChange(false)
      form.reset()
      if (onSuccess) onSuccess()
    },
    onError: (error: Error) => {
      showErrorToast(error.message || "Failed to update marital status")
    },
  })

  const onSubmit = (data: FormData) => {
    const updateData: PersonUpdate = {
      marital_status: data.marital_status as MaritalStatus,
    }
    updateMaritalStatusMutation.mutate(updateData)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Edit Marital Status</DialogTitle>
          <DialogDescription>
            Please select your marital status
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="marital_status"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Marital Status *</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select marital status" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {options?.map(
                        (option: { value: string; label: string }) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        )
                      )}
                    </SelectContent>
                  </Select>
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
                loading={updateMaritalStatusMutation.isPending}
              >
                Save
              </LoadingButton>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
