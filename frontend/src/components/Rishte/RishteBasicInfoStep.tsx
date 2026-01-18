// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useQuery } from "@tanstack/react-query"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { PersonMetadataService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import type { RishteBasicInfoStepProps, BasicInfoFormData } from "./types"

/**
 * Zod schema for basic info form validation
 * Requirements:
 * - 3.2: First name required with min 1 char
 * - 3.3: Last name required with min 1 char
 * - 3.4: Gender optional
 * - 3.5: Birth year range optional
 * - 3.7: Validation error when first name is empty
 */
const basicInfoSchema = z.object({
  firstName: z
    .string()
    .min(1, "First name is required")
    .refine((val) => val.trim().length > 0, "First name cannot be only whitespace"),
  lastName: z
    .string()
    .min(1, "Last name is required")
    .refine((val) => val.trim().length > 0, "Last name cannot be only whitespace"),
  genderId: z.string().optional(),
  birthYearFrom: z.union([
    z.literal(""),
    z.coerce.number().min(1800).max(new Date().getFullYear()),
  ]).optional().transform(val => val === "" ? undefined : val),
  birthYearTo: z.union([
    z.literal(""),
    z.coerce.number().min(1800).max(new Date().getFullYear()),
  ]).optional().transform(val => val === "" ? undefined : val),
}).refine(
  (data) => {
    // If both years are provided, birthYearTo must be >= birthYearFrom
    if (data.birthYearFrom && data.birthYearTo) {
      return data.birthYearTo >= data.birthYearFrom
    }
    return true
  },
  {
    message: "End year must be greater than or equal to start year",
    path: ["birthYearTo"],
  }
)

type FormData = z.infer<typeof basicInfoSchema>

/**
 * RishteBasicInfoStep component - Step 1 of the Person Search Wizard
 * 
 * Collects basic search criteria:
 * - First name (required)
 * - Last name (required)  
 * - Gender (optional dropdown from API)
 * - Birth year range (optional)
 * 
 * Requirements:
 * - 3.1: Display form with first name, last name, gender, birth year range
 * - 3.2: First name required with min 1 char
 * - 3.3: Last name required with min 1 char
 * - 3.4: Gender optional dropdown from genders API
 * - 3.5: Birth year range optional number inputs
 * - 3.6: Display "Next" button to proceed
 * - 3.7: Show validation error when first name is empty
 */
export function RishteBasicInfoStep({
  initialData,
  onNext,
}: RishteBasicInfoStepProps) {
  const form = useForm<FormData>({
    resolver: zodResolver(basicInfoSchema),
    defaultValues: {
      firstName: initialData?.firstName || "",
      lastName: initialData?.lastName || "",
      genderId: initialData?.genderId || undefined,
      birthYearFrom: initialData?.birthYearFrom || "",
      birthYearTo: initialData?.birthYearTo || "",
    },
  })

  // Fetch genders from API
  const { data: genders } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
  })

  const onSubmit = (data: FormData) => {
    // Transform form data to BasicInfoFormData
    const basicInfoData: BasicInfoFormData = {
      firstName: data.firstName.trim(),
      lastName: data.lastName.trim(),
      genderId: data.genderId || undefined,
      birthYearFrom: typeof data.birthYearFrom === "number" ? data.birthYearFrom : undefined,
      birthYearTo: typeof data.birthYearTo === "number" ? data.birthYearTo : undefined,
    }
    onNext(basicInfoData)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
        {/* First Name - Required */}
        <FormField
          control={form.control}
          name="firstName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>First Name *</FormLabel>
              <FormControl>
                <Input placeholder="Enter first name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Last Name - Required */}
        <FormField
          control={form.control}
          name="lastName"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Last Name *</FormLabel>
              <FormControl>
                <Input placeholder="Enter last name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Gender - Optional */}
        <FormField
          control={form.control}
          name="genderId"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Gender (Optional)</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent className="max-h-[300px]">
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

        {/* Birth Year Range - Optional */}
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="birthYearFrom"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Birth Year From (Optional)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="e.g., 1950"
                    min={1800}
                    max={new Date().getFullYear()}
                    {...field}
                    value={field.value || ""}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="birthYearTo"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Birth Year To (Optional)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="e.g., 2000"
                    min={1800}
                    max={new Date().getFullYear()}
                    {...field}
                    value={field.value || ""}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Next Button */}
        <div className="flex justify-end pt-4">
          <Button type="submit">Next</Button>
        </div>
      </form>
    </Form>
  )
}
