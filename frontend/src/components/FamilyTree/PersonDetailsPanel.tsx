import { Calendar, Heart, Loader2, MapPin, RefreshCw, User } from "lucide-react"
import type { PersonAddressDetails, PersonReligionDetails } from "@/client"
import { LifeEventsList } from "@/components/LifeEvents/LifeEventsList"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { usePersonCompleteDetails } from "@/hooks/usePersonCompleteDetails"
import { usePersonLifeEvents } from "@/hooks/usePersonLifeEvents"

export interface PersonDetailsPanelProps {
  personId: string | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

/**
 * Format birth and death years for display
 * @param dateOfBirth - ISO date string for birth date
 * @param dateOfDeath - ISO date string for death date (optional)
 * @returns Formatted string like "1990 -" or "1990 - 2020"
 */
function formatYearsDisplay(
  dateOfBirth: string,
  dateOfDeath?: string | null,
): string {
  const birthYear = parseInt(dateOfBirth.split("-")[0], 10)

  if (dateOfDeath) {
    const deathYear = parseInt(dateOfDeath.split("-")[0], 10)
    return `${birthYear} - ${deathYear}`
  }

  return `${birthYear} -`
}

/**
 * Format full name from first, middle, and last name
 * @param firstName - First name
 * @param middleName - Middle name (optional)
 * @param lastName - Last name
 * @returns Full name with middle name if present
 */
function formatFullName(
  firstName: string,
  middleName?: string | null,
  lastName?: string,
): string {
  const parts = [firstName]
  if (middleName) {
    parts.push(middleName)
  }
  if (lastName) {
    parts.push(lastName)
  }
  return parts.join(" ")
}

/**
 * Format address as comma-separated values
 * Order: locality, sub-district, district, state, country
 * @param address - Address details object
 * @returns Formatted address string or null if no address
 */
function formatAddress(
  address: PersonAddressDetails | null | undefined,
): string | null {
  if (!address) return null

  const parts: string[] = []

  if (address.locality_name) parts.push(address.locality_name)
  if (address.sub_district_name) parts.push(address.sub_district_name)
  if (address.district_name) parts.push(address.district_name)
  if (address.state_name) parts.push(address.state_name)
  if (address.country_name) parts.push(address.country_name)

  return parts.length > 0 ? parts.join(", ") : null
}

/**
 * Format religion as comma-separated values
 * Order: religion, category, sub-category
 * @param religion - Religion details object
 * @returns Formatted religion string or null if no religion
 */
function formatReligion(
  religion: PersonReligionDetails | null | undefined,
): string | null {
  if (!religion) return null

  const parts: string[] = [religion.religion_name]

  if (religion.category_name) parts.push(religion.category_name)
  if (religion.sub_category_name) parts.push(religion.sub_category_name)

  return parts.join(", ")
}

/**
 * PersonDetailsPanel component displays comprehensive person information in a sliding panel.
 *
 * Requirements covered:
 * - 2.1: Panel slides in from the right side
 * - 2.2: Close button to dismiss the panel
 * - 2.3: Closes on outside click or Escape (handled by Sheet component)
 * - 2.4: Semi-transparent overlay (handled by Sheet component)
 * - 3.1: Person photo in circular format
 * - 3.2: Full name (first, middle, last)
 * - 3.3: Birth/death years in correct format
 * - 3.4: Gender name
 * - 3.5: Address as comma-separated values
 * - 3.6: Religion as comma-separated values
 * - 3.7: Graceful handling of null values
 * - 5.1: Loading indicator while fetching
 * - 5.2: Error message with retry option
 * - 5.3: Loading state doesn't block closing
 */
export function PersonDetailsPanel({
  personId,
  open,
  onOpenChange,
}: PersonDetailsPanelProps) {
  const { data, isLoading, error, refetch } = usePersonCompleteDetails(personId)

  // Fetch life events for the person
  const {
    data: lifeEventsData,
    isLoading: isLoadingEvents,
    error: eventsError,
    refetch: refetchEvents,
  } = usePersonLifeEvents(personId)

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader className="text-center">
          <SheetTitle>Person Details</SheetTitle>
          <SheetDescription className="sr-only">
            Detailed information about the selected person
          </SheetDescription>
        </SheetHeader>

        {/* Loading State - Requirement 5.1 */}
        {isLoading && (
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="mt-4 text-sm text-muted-foreground">
              Loading details...
            </p>
          </div>
        )}

        {/* Error State - Requirement 5.2 */}
        {error && !isLoading && (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <p className="text-destructive font-medium">
              Failed to load person details
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              {error.message || "An unexpected error occurred"}
            </p>
            <Button
              variant="outline"
              size="sm"
              className="mt-4"
              onClick={() => refetch()}
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        )}

        {/* Person Details Content */}
        {data && !isLoading && !error && (
          <div className="flex flex-col items-center gap-6 py-6">
            {/* Photo - Requirement 3.1 */}
            <Avatar className="h-24 w-24">
              <AvatarImage
                src={undefined}
                alt={formatFullName(
                  data.first_name,
                  data.middle_name,
                  data.last_name,
                )}
              />
              <AvatarFallback className="text-2xl">
                <User className="h-12 w-12" />
              </AvatarFallback>
            </Avatar>

            {/* Name and Years - Requirements 3.2, 3.3 */}
            <div className="text-center">
              <h2 className="text-xl font-semibold">
                {formatFullName(
                  data.first_name,
                  data.middle_name,
                  data.last_name,
                )}
              </h2>
              <p className="text-muted-foreground mt-1 flex items-center justify-center gap-2">
                <Calendar className="h-4 w-4" />
                {formatYearsDisplay(data.date_of_birth, data.date_of_death)}
              </p>
            </div>

            {/* Details Section */}
            <div className="w-full space-y-4 px-2">
              {/* Gender - Requirement 3.4 */}
              <div className="flex items-start gap-3">
                <User className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    Gender
                  </p>
                  <p className="text-sm">{data.gender_name}</p>
                </div>
              </div>

              {/* Address - Requirements 3.5, 3.7 */}
              {formatAddress(data.address) && (
                <div className="flex items-start gap-3">
                  <MapPin className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Address
                    </p>
                    <p className="text-sm">{formatAddress(data.address)}</p>
                  </div>
                </div>
              )}

              {/* Religion - Requirements 3.6, 3.7 */}
              {formatReligion(data.religion) && (
                <div className="flex items-start gap-3">
                  <Heart className="h-5 w-5 text-muted-foreground mt-0.5 flex-shrink-0" />
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      Religion
                    </p>
                    <p className="text-sm">{formatReligion(data.religion)}</p>
                  </div>
                </div>
              )}
            </div>

            {/* Life Events Section */}
            <div className="w-full border-t pt-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 px-2">
                <Calendar className="h-5 w-5" />
                Life Events
              </h3>

              {/* Loading State */}
              {isLoadingEvents && (
                <div className="flex justify-center py-4">
                  <Loader2 className="h-6 w-6 animate-spin text-primary" />
                </div>
              )}

              {/* Error State */}
              {eventsError && !isLoadingEvents && (
                <div className="text-center py-4 px-2">
                  <p className="text-sm text-destructive">
                    Failed to load life events
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-2"
                    onClick={() => refetchEvents()}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retry
                  </Button>
                </div>
              )}

              {/* Success State */}
              {lifeEventsData &&
                !isLoadingEvents &&
                !eventsError &&
                (lifeEventsData.data.length === 0 ? (
                  <p className="text-sm text-muted-foreground text-center py-4 px-2">
                    No life events recorded
                  </p>
                ) : (
                  <div className="px-2">
                    <LifeEventsList events={lifeEventsData.data} compact />
                  </div>
                ))}
            </div>
          </div>
        )}
      </SheetContent>
    </Sheet>
  )
}
