// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { PersonMetadataService } from "@/client"
import { Checkbox } from "@/components/ui/checkbox"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { LoadingButton } from "@/components/ui/loading-button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import useCustomToast from "@/hooks/useCustomToast"

const RELATIONSHIP_TYPES = [
  { value: "rel-6a0ede824d101", label: "Father" },
  { value: "rel-6a0ede824d102", label: "Mother" },
  { value: "rel-6a0ede824d103", label: "Daughter" },
  { value: "rel-6a0ede824d104", label: "Son" },
  { value: "rel-6a0ede824d105", label: "Wife" },
  { value: "rel-6a0ede824d106", label: "Husband" },
  { value: "rel-6a0ede824d107", label: "Spouse" },
]

const MARITAL_STATUS_OPTIONS = [
  { value: "single", label: "Single" },
  { value: "married", label: "Married" },
  { value: "divorced", label: "Divorced" },
  { value: "widowed", label: "Widowed" },
  { value: "separated", label: "Separated" },
]

const formSchema = z.object({
  relationship_type: z.string().min(1, "Relationship is required"),
  first_name: z.string().min(1, "First name is required").max(100),
  middle_name: z.string().max(100).optional(),
  last_name: z.string().min(1, "Last name is required").max(100),
  gender_id: z.string().min(1, "Gender is required"),
  date_of_birth: z.string().min(1, "Date of birth is required"),
  marital_status: z.string().min(1, "Marital status is required"),
  is_dead: z.boolean().default(false),
  date_of_death: z.string().optional(),
  about: z.string().max(500).optional(),
})

type FormData = z.infer<typeof formSchema>

interface BasicInfoStepProps {
  onComplete: (data: any) => void
  initialData?: any
}

export function BasicInfoStep({ onComplete, initialData }: BasicInfoStepProps) {
  const { showErrorToast } = useCustomToast()

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      relationship_type: initialData?.relationship_type || "",
      first_name: initialData?.first_name || "",
      middle_name: initialData?.middle_name || "",
      last_name: initialData?.last_name || "",
      gender_id: initialData?.gender_id || "",
      date_of_birth: initialData?.date_of_birth || "",
      marital_status: initialData?.marital_status || "",
      is_dead: initialData?.is_dead || false,
      date_of_death: initialData?.date_of_death || "",
      about: initialData?.about || "",
    },
  })

  const isDead = form.watch("is_dead")

  // Fetch genders
  const { data: genders } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
  })

  const createPersonMutation = useMutation({
    mutationFn: async (data: FormData) => {
      // Just return the data without creating the person yet
      return data
    },
    onSuccess: (data) => {
      onComplete(data)
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to validate data")
    },
  })

  const onSubmit = (data: FormData) => {
    // Validate date of death if person is marked as dead
    if (data.is_dead && !data.date_of_death) {
      form.setError("date_of_death", {
        message: "Date of death is required when marked as deceased",
      })
      return
    }

    createPersonMutation.mutate(data)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        {/* Relationship Type */}
        <FormField
          control={form.control}
          name="relationship_type"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Relationship with You *</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select relationship" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {RELATIONSHIP_TYPES.map((type) => (
                    <SelectItem key={type.value} value={type.value}>
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* First Name */}
          <FormField
            control={form.control}
            name="first_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>First Name *</FormLabel>
                <FormControl>
                  <Input placeholder="First name" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Middle Name */}
          <FormField
            control={form.control}
            name="middle_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Middle Name</FormLabel>
                <FormControl>
                  <Input placeholder="Middle name" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Last Name */}
          <FormField
            control={form.control}
            name="last_name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Last Name *</FormLabel>
                <FormControl>
                  <Input placeholder="Last name" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Gender */}
          <FormField
            control={form.control}
            name="gender_id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Gender *</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {genders?.map((gender: any) => (
                      <SelectItem key={gender.genderId} value={gender.genderId}>
                        {gender.genderName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Date of Birth */}
          <FormField
            control={form.control}
            name="date_of_birth"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Date of Birth *</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Marital Status */}
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
                  {MARITAL_STATUS_OPTIONS.map((status) => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Is Dead Checkbox */}
        <FormField
          control={form.control}
          name="is_dead"
          render={({ field }) => (
            <FormItem className="flex flex-row items-start space-x-3 space-y-0">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel>Deceased</FormLabel>
              </div>
            </FormItem>
          )}
        />

        {/* Date of Death (conditional) */}
        {isDead && (
          <FormField
            control={form.control}
            name="date_of_death"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Date of Death *</FormLabel>
                <FormControl>
                  <Input type="date" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* About */}
        <FormField
          control={form.control}
          name="about"
          render={({ field }) => (
            <FormItem>
              <FormLabel>About (Optional)</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Additional information about this person..."
                  className="resize-none"
                  rows={3}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end">
          <LoadingButton type="submit" loading={createPersonMutation.isPending}>
            Next: Add Address
          </LoadingButton>
        </div>
      </form>
    </Form>
  )
}
