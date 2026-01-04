// @ts-nocheck

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
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
import { Textarea } from "@/components/ui/textarea"

const EVENT_TYPES = [
  { value: "birth", label: "Birth" },
  { value: "marriage", label: "Marriage" },
  { value: "death", label: "Death" },
  { value: "purchase", label: "Purchase" },
  { value: "sale", label: "Sale" },
  { value: "achievement", label: "Achievement" },
  { value: "education", label: "Education" },
  { value: "career", label: "Career" },
  { value: "health", label: "Health" },
  { value: "travel", label: "Travel" },
  { value: "other", label: "Other" },
]

const MONTHS = [
  { value: "1", label: "January" },
  { value: "2", label: "February" },
  { value: "3", label: "March" },
  { value: "4", label: "April" },
  { value: "5", label: "May" },
  { value: "6", label: "June" },
  { value: "7", label: "July" },
  { value: "8", label: "August" },
  { value: "9", label: "September" },
  { value: "10", label: "October" },
  { value: "11", label: "November" },
  { value: "12", label: "December" },
]

const formSchema = z
  .object({
    event_type: z.string().min(1, "Event type is required"),
    title: z
      .string()
      .min(1, "Title is required")
      .max(100, "Title must be 100 characters or less"),
    description: z
      .string()
      .max(500, "Description must be 500 characters or less")
      .optional(),
    event_year: z
      .string()
      .min(1, "Year is required")
      .refine((val) => {
        const year = parseInt(val, 10)
        return (
          !Number.isNaN(year) &&
          year >= 1900 &&
          year <= new Date().getFullYear()
        )
      }, "Please enter a valid year"),
    event_month: z.string().optional(),
    event_date: z.string().optional(),
  })
  .refine(
    (data) => {
      // Validate date against month/year if provided
      if (data.event_date && data.event_month && data.event_year) {
        const year = parseInt(data.event_year, 10)
        const month = parseInt(data.event_month, 10)
        const date = parseInt(data.event_date, 10)
        const daysInMonth = new Date(year, month, 0).getDate()
        return date >= 1 && date <= daysInMonth
      }
      return true
    },
    {
      message: "Invalid date for the selected month/year",
      path: ["event_date"],
    },
  )

type FormData = z.infer<typeof formSchema>

interface EventDetailsStepProps {
  onComplete: (data: any) => void
  initialData?: any
}

export function EventDetailsStep({
  onComplete,
  initialData,
}: EventDetailsStepProps) {
  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      event_type: initialData?.event_type || "",
      title: initialData?.title || "",
      description: initialData?.description || "",
      event_year: initialData?.event_year?.toString() || "",
      event_month: initialData?.event_month?.toString() || "",
      event_date: initialData?.event_date?.toString() || "",
    },
  })

  const titleValue = form.watch("title")
  const descriptionValue = form.watch("description")

  const onSubmit = (data: FormData) => {
    // Convert string values to numbers where needed
    const processedData = {
      ...data,
      event_year: parseInt(data.event_year, 10),
      event_month: data.event_month ? parseInt(data.event_month, 10) : null,
      event_date: data.event_date ? parseInt(data.event_date, 10) : null,
      // Add display label for event type
      event_type_label:
        EVENT_TYPES.find((t) => t.value === data.event_type)?.label ||
        data.event_type,
    }
    onComplete(processedData)
  }

  return (
    <div className="space-y-4">
      <Form {...form}>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
          {/* Event Type */}
          <FormField
            control={form.control}
            name="event_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Event Type <span className="text-destructive">*</span>
                </FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select event type" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {EVENT_TYPES.map((type) => (
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

          {/* Title */}
          <FormField
            control={form.control}
            name="title"
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Title <span className="text-destructive">*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder="Brief description of the event"
                    {...field}
                  />
                </FormControl>
                <FormDescription className="text-xs text-muted-foreground">
                  {titleValue?.length || 0}/100 characters
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Description */}
          <FormField
            control={form.control}
            name="description"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Description</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Additional details about the event (optional)"
                    className="min-h-[100px]"
                    {...field}
                  />
                </FormControl>
                <FormDescription className="text-xs text-muted-foreground">
                  {descriptionValue?.length || 0}/500 characters
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Date Fields */}
          <div className="grid grid-cols-3 gap-4">
            {/* Year */}
            <FormField
              control={form.control}
              name="event_year"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Year <span className="text-destructive">*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="YYYY"
                      min="1900"
                      max={new Date().getFullYear()}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Month */}
            <FormField
              control={form.control}
              name="event_month"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Month</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {MONTHS.map((month) => (
                        <SelectItem key={month.value} value={month.value}>
                          {month.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Date */}
            <FormField
              control={form.control}
              name="event_date"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Day</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="DD"
                      min="1"
                      max="31"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <div className="flex justify-end pt-4">
            <Button type="submit">Next: Location Details</Button>
          </div>
        </form>
      </Form>
    </div>
  )
}
