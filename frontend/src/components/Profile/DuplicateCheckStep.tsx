/**
 * DuplicateCheckStep - Component for the duplicate check step in profile completion.
 *
 * Requirements: 3.1-3.8, 10.1, 10.2, 10.6, 10.7
 * - Display "Check for Existing Records" step after basic profile completion
 * - Automatically search for matching persons using user's data
 * - Display matches in a grid layout with MatchCard components
 * - Display "No matches found" when empty
 * - Add "None of these are me" button
 * - Handle "This is me" click (create attachment request)
 * - Handle "None of these are me" click (complete without attachment)
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Loader2, Search, UserCheck } from "lucide-react"
import { useState } from "react"
import {
  AttachmentRequestsService,
  ProfileService,
  type PersonMatchResult,
} from "@/client"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import useCustomToast from "@/hooks/useCustomToast"
import { MatchCard } from "./MatchCard"

export interface DuplicateCheckStepProps {
  /** Callback when the step is completed (either by attachment request or completing without) */
  onComplete: () => void
}

/**
 * DuplicateCheckStep component handles the duplicate check flow:
 * 1. Fetches potential duplicate matches from the API
 * 2. Displays matches in a responsive grid
 * 3. Allows user to select "This is me" to create an attachment request
 * 4. Allows user to select "None of these are me" to complete profile without attachment
 */
export function DuplicateCheckStep({ onComplete }: DuplicateCheckStepProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null)

  // Fetch duplicate matches
  const {
    data: matches,
    isLoading: isLoadingMatches,
    error: matchesError,
  } = useQuery({
    queryKey: ["duplicateCheck"],
    queryFn: () => ProfileService.getDuplicateCheck(),
  })

  // Create attachment request mutation
  const createRequestMutation = useMutation({
    mutationFn: (targetPersonId: string) =>
      AttachmentRequestsService.createAttachmentRequest({
        requestBody: { target_person_id: targetPersonId },
      }),
    onSuccess: () => {
      showSuccessToast(
        "Attachment request submitted. Waiting for approval from the record owner."
      )
      // Invalidate profile completion status to trigger re-fetch
      queryClient.invalidateQueries({ queryKey: ["profileCompletion"] })
      onComplete()
    },
    onError: (error: any) => {
      setSelectedPersonId(null)
      showErrorToast(
        error?.body?.detail || "Failed to submit attachment request. Please try again."
      )
    },
  })

  // Complete without attachment mutation
  const completeWithoutAttachmentMutation = useMutation({
    mutationFn: () => ProfileService.completeWithoutAttachment(),
    onSuccess: () => {
      showSuccessToast("Profile completed successfully!")
      // Invalidate profile completion status
      queryClient.invalidateQueries({ queryKey: ["profileCompletion"] })
      // Redirect to dashboard
      window.location.href = "/"
    },
    onError: (error: any) => {
      showErrorToast(
        error?.body?.detail || "Failed to complete profile. Please try again."
      )
    },
  })

  // Handle "This is me" click
  const handleSelectMatch = (personId: string) => {
    setSelectedPersonId(personId)
    createRequestMutation.mutate(personId)
  }

  // Handle "None of these are me" click
  const handleNoneOfThese = () => {
    completeWithoutAttachmentMutation.mutate()
  }

  // Loading state
  if (isLoadingMatches) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Check for Existing Records
          </CardTitle>
          <CardDescription>
            Searching for existing records that might be you...
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">
              Searching for matching records...
            </p>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Error state
  if (matchesError) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Check for Existing Records
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert variant="destructive">
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>
              Failed to search for matching records. Please try again later.
            </AlertDescription>
          </Alert>
          <Button
            variant="outline"
            className="w-full mt-4"
            onClick={handleNoneOfThese}
            disabled={completeWithoutAttachmentMutation.isPending}
          >
            {completeWithoutAttachmentMutation.isPending && (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            )}
            Continue without checking
          </Button>
        </CardContent>
      </Card>
    )
  }

  const hasMatches = matches && matches.length > 0
  const isProcessing =
    createRequestMutation.isPending || completeWithoutAttachmentMutation.isPending

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <UserCheck className="h-5 w-5" />
          Check for Existing Records
        </CardTitle>
        <CardDescription>
          {hasMatches
            ? "We found some people that might be you. If you see yourself in the list, click \"This is me\" to link your account. Otherwise, click \"None of these are me\" to continue."
            : "No matching records found. You can continue to complete your profile."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Matches Grid - Responsive: 1 col mobile, 2 col tablet, 2-3 col desktop */}
        {hasMatches && (
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
            {matches.map((match: PersonMatchResult) => (
              <MatchCard
                key={match.person_id}
                match={match}
                onSelect={() => handleSelectMatch(match.person_id)}
                isLoading={
                  isProcessing && selectedPersonId === match.person_id
                }
              />
            ))}
          </div>
        )}

        {/* No matches message */}
        {!hasMatches && (
          <div className="flex flex-col items-center justify-center py-8 px-4">
            <div className="rounded-full bg-muted/50 p-6 mb-4">
              <Search className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No Matching Records</h3>
            <p className="text-muted-foreground text-center max-w-md text-sm">
              We didn't find any existing records that match your information.
              Click the button below to complete your profile.
            </p>
          </div>
        )}

        {/* Helpful text explaining what happens */}
        {hasMatches && (
          <Alert>
            <AlertDescription>
              <strong>What happens next?</strong>
              <ul className="list-disc list-inside mt-2 space-y-1 text-sm">
                <li>
                  <strong>"This is me"</strong>: Your account will be linked to
                  the existing record after approval from the record owner.
                </li>
                <li>
                  <strong>"None of these are me"</strong>: A new record will be
                  created for you and you can start using the app immediately.
                </li>
              </ul>
            </AlertDescription>
          </Alert>
        )}

        {/* None of these are me button */}
        <Button
          variant={hasMatches ? "outline" : "default"}
          className="w-full"
          onClick={handleNoneOfThese}
          disabled={isProcessing}
        >
          {completeWithoutAttachmentMutation.isPending && (
            <Loader2 className="h-4 w-4 animate-spin mr-2" />
          )}
          {hasMatches
            ? "None of these are me - Complete my profile"
            : "Complete my profile"}
        </Button>
      </CardContent>
    </Card>
  )
}
