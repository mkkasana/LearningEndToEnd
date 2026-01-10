import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react"

import { PersonService, type PersonPublic } from "@/client"

/**
 * Session storage key for assumed person data
 * Using sessionStorage ensures data is cleared on tab close
 * _Requirements: 3.3_
 */
const ASSUMED_PERSON_STORAGE_KEY = "assumedPerson"

/**
 * Assumed person data stored in sessionStorage
 */
interface AssumedPersonStorage {
  assumedPersonId: string
  assumedPersonName: string
  assumedAt: number
}

/**
 * Active Person Context State
 * 
 * Provides the currently active person for API operations.
 * Supports both primary person (user's own) and assumed person (acting on behalf of).
 * 
 * _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.2, 2.3, 3.5, 7.2_
 */
type ActivePersonContextState = {
  /** The user's primary person (their own identity) */
  primaryPerson: PersonPublic | null
  /** The currently assumed person (if any) */
  assumedPerson: PersonPublic | null
  /** The currently active person (assumed if assuming, otherwise primary) */
  activePerson: PersonPublic | null
  /** The ID of the currently active person (convenience accessor) */
  activePersonId: string | null
  /** Whether the user is currently assuming another person's role */
  isAssuming: boolean
  /** Whether the person data is currently loading */
  isLoading: boolean
  /** Error that occurred while fetching person data */
  error: Error | null
  /** Whether the context has been initialized with data */
  isInitialized: boolean
  /** Function to assume a person's role */
  assumePerson: (personId: string, personName: string) => Promise<boolean>
  /** Function to return to primary person */
  returnToPrimary: () => void
  /** Function to clear assumed person (called on logout) */
  clearAssumedPerson: () => void
  /** Whether an assume operation is in progress */
  isAssumeLoading: boolean
}

const initialState: ActivePersonContextState = {
  primaryPerson: null,
  assumedPerson: null,
  activePerson: null,
  activePersonId: null,
  isAssuming: false,
  isLoading: true,
  error: null,
  isInitialized: false,
  assumePerson: async () => false,
  returnToPrimary: () => {},
  clearAssumedPerson: () => {},
  isAssumeLoading: false,
}

const ActivePersonContext = createContext<ActivePersonContextState>(initialState)

type ActivePersonProviderProps = {
  children: ReactNode
}


/**
 * Helper to read assumed person from sessionStorage
 */
function getStoredAssumedPerson(): AssumedPersonStorage | null {
  try {
    const stored = sessionStorage.getItem(ASSUMED_PERSON_STORAGE_KEY)
    if (stored) {
      return JSON.parse(stored) as AssumedPersonStorage
    }
  } catch {
    // Invalid JSON, clear it
    sessionStorage.removeItem(ASSUMED_PERSON_STORAGE_KEY)
  }
  return null
}

/**
 * Helper to store assumed person in sessionStorage
 */
function storeAssumedPerson(personId: string, personName: string): void {
  const data: AssumedPersonStorage = {
    assumedPersonId: personId,
    assumedPersonName: personName,
    assumedAt: Date.now(),
  }
  sessionStorage.setItem(ASSUMED_PERSON_STORAGE_KEY, JSON.stringify(data))
}

/**
 * Helper to clear assumed person from sessionStorage
 */
function clearStoredAssumedPerson(): void {
  sessionStorage.removeItem(ASSUMED_PERSON_STORAGE_KEY)
}

/**
 * ActivePersonProvider
 * 
 * Provides the active person context to the application.
 * Fetches the user's primary person on mount and supports assuming other persons.
 * 
 * Usage:
 * ```tsx
 * // In main.tsx or layout
 * <ActivePersonProvider>
 *   <App />
 * </ActivePersonProvider>
 * 
 * // In components
 * const { activePerson, activePersonId, isAssuming, assumePerson, returnToPrimary } = useActivePersonContext()
 * ```
 * 
 * _Requirements: 2.2, 2.3, 3.5, 7.2_
 */
export function ActivePersonProvider({ children }: ActivePersonProviderProps) {
  const queryClient = useQueryClient()
  
  // State for assumed person ID (from sessionStorage)
  const [assumedPersonId, setAssumedPersonId] = useState<string | null>(() => {
    const stored = getStoredAssumedPerson()
    return stored?.assumedPersonId ?? null
  })

  // Fetch primary person (user's own person)
  const {
    data: primaryPerson,
    isLoading: isPrimaryLoading,
    error: primaryError,
    isFetched: isPrimaryFetched,
  } = useQuery<PersonPublic | null, Error>({
    queryKey: ["primaryPerson"],
    queryFn: async () => {
      try {
        const person = await PersonService.getMyPerson()
        return person
      } catch (err) {
        // If 404, user doesn't have a person profile yet
        if (err && typeof err === "object" && "status" in err && err.status === 404) {
          return null
        }
        throw err
      }
    },
    enabled: !!localStorage.getItem("access_token"),
    staleTime: 5 * 60 * 1000,
    retry: (failureCount, error) => {
      if (error && typeof error === "object" && "status" in error && error.status === 404) {
        return false
      }
      return failureCount < 3
    },
  })

  // Fetch assumed person details (if assuming)
  const {
    data: assumedPerson,
    isLoading: isAssumedLoading,
    error: assumedError,
  } = useQuery<PersonPublic | null, Error>({
    queryKey: ["assumedPerson", assumedPersonId],
    queryFn: async () => {
      if (!assumedPersonId) return null
      
      // First validate we can still assume this person
      try {
        const canAssumeResponse = await PersonService.canAssumePerson({ personId: assumedPersonId })
        if (!canAssumeResponse.can_assume) {
          // Can't assume anymore, clear storage and return null
          clearStoredAssumedPerson()
          setAssumedPersonId(null)
          return null
        }
      } catch {
        // Error checking, clear and fall back to primary
        clearStoredAssumedPerson()
        setAssumedPersonId(null)
        return null
      }
      
      // Fetch the person details
      try {
        const response = await PersonService.getPersonRelationshipsWithDetails({ personId: assumedPersonId })
        return response.selected_person as PersonPublic
      } catch {
        // Person not found or error, clear and fall back
        clearStoredAssumedPerson()
        setAssumedPersonId(null)
        return null
      }
    },
    enabled: !!assumedPersonId && !!localStorage.getItem("access_token"),
    staleTime: 5 * 60 * 1000,
  })


  // Mutation for assuming a person
  const assumeMutation = useMutation({
    mutationFn: async ({ personId }: { personId: string }) => {
      const response = await PersonService.canAssumePerson({ personId })
      return response
    },
  })

  /**
   * Assume a person's role
   * _Requirements: 2.2, 2.3_
   */
  const assumePerson = useCallback(async (personId: string, personName: string): Promise<boolean> => {
    try {
      const response = await assumeMutation.mutateAsync({ personId })
      
      if (!response.can_assume) {
        console.warn(`Cannot assume person ${personId}: ${response.reason}`)
        return false
      }
      
      // Store in sessionStorage
      storeAssumedPerson(personId, personName)
      
      // Update state
      setAssumedPersonId(personId)
      
      // Invalidate assumed person query to refetch
      queryClient.invalidateQueries({ queryKey: ["assumedPerson", personId] })
      
      return true
    } catch (error) {
      console.error("Failed to assume person:", error)
      return false
    }
  }, [assumeMutation, queryClient])

  /**
   * Return to primary person
   * _Requirements: 4.2, 4.3_
   */
  const returnToPrimary = useCallback(() => {
    clearStoredAssumedPerson()
    setAssumedPersonId(null)
    // Clear the assumed person query cache
    queryClient.removeQueries({ queryKey: ["assumedPerson"] })
  }, [queryClient])

  /**
   * Clear assumed person (called on logout)
   * _Requirements: 3.1_
   */
  const clearAssumedPerson = useCallback(() => {
    clearStoredAssumedPerson()
    setAssumedPersonId(null)
  }, [])

  // Validate stored assumed person on mount
  // _Requirements: 7.2, 7.3_
  useEffect(() => {
    const stored = getStoredAssumedPerson()
    if (stored && !assumedPersonId) {
      // Restore from storage
      setAssumedPersonId(stored.assumedPersonId)
    }
  }, [])

  // Determine active person
  const isAssuming = !!assumedPersonId && !!assumedPerson
  const activePerson = isAssuming ? (assumedPerson ?? null) : (primaryPerson ?? null)
  const activePersonId = activePerson?.id ?? null

  const value: ActivePersonContextState = {
    primaryPerson: primaryPerson ?? null,
    assumedPerson: assumedPerson ?? null,
    activePerson,
    activePersonId,
    isAssuming,
    isLoading: isPrimaryLoading || (!!assumedPersonId && isAssumedLoading),
    error: primaryError ?? assumedError ?? null,
    isInitialized: isPrimaryFetched,
    assumePerson,
    returnToPrimary,
    clearAssumedPerson,
    isAssumeLoading: assumeMutation.isPending,
  }

  return (
    <ActivePersonContext.Provider value={value}>
      {children}
    </ActivePersonContext.Provider>
  )
}

/**
 * Hook to access the active person context
 * 
 * @throws Error if used outside of ActivePersonProvider
 * 
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { 
 *     activePerson, 
 *     activePersonId, 
 *     isAssuming,
 *     primaryPerson,
 *     assumePerson,
 *     returnToPrimary 
 *   } = useActivePersonContext()
 *   
 *   if (isLoading) return <Spinner />
 *   if (error) return <Error message={error.message} />
 *   if (!activePerson) return <CreateProfilePrompt />
 *   
 *   return (
 *     <div>
 *       {isAssuming && <Banner>Acting as {activePerson.first_name}</Banner>}
 *       <div>Hello, {activePerson.first_name}!</div>
 *     </div>
 *   )
 * }
 * ```
 */
export function useActivePersonContext() {
  const context = useContext(ActivePersonContext)

  if (context === undefined) {
    throw new Error(
      "useActivePersonContext must be used within an ActivePersonProvider"
    )
  }

  return context
}

export { ActivePersonContext }
