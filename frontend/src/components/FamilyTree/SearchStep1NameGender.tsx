// @ts-nocheck
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { useQuery } from "@tanstack/react-query"
import { PersonMetadataService } from "@/client"
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
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const formSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  genderId: z.string().optional(),
})

type FormData = z.infer<typeof formSchema>

interface SearchStep1NameGenderProps {
  initialData: {
    firstName: string
    lastName: string
    genderId?: string
  }
  onComplete: (data: FormData) => void
}

export function SearchStep1NameGender({
  initialData,
  onComplete,
}: SearchStep1NameGenderProps) {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: initialData,
  })

  // Fetch genders
  const { data: genders } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
  })

  const onSubmit = (data: FormData) => {
    onComplete(data)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
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

        <div className="flex justify-end pt-4">
          <Button type="submit">Next</Button>
        </div>
      </form>
    </Form>
  )
}
