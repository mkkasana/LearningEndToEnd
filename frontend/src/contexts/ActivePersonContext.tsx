import { useQuery } from "@tanstack/react-query"
import {
  createContext,
  useContext,
  type ReactNode,
} from "react"

import { PersonService, type PersonPublic } from "@/client"

/**
 * Active Person Context State
 * 
 * Provides the currently active person for API operations.
 * Initially set to the user's primary person (from /me endpoint).
 * Will be extended later to support "Assume Person Role" feature.
 * 
 * _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
 */
type ActivePersonContextState = {
  /** The currently active person object */
  activePerson: PersonPublic | null
  /** The ID of the currently active person (convenience accessor) */
  activePersonId: string | null
  /** Whether the person data is currently loading */
  isLoading: boolean
  /** Error that occurred while fetching person data */
  error: Error | null
  /** Whether the context has been initialized with data */
  isInitialized: boolean
}

const initialState: ActivePersonContextState = {
  activePerson: null,
  activePersonId: null,
  isLoading: true,
  error: null,
  isInitialized: false,
}

const ActivePersonContext = createContext<ActivePersonContextState>(initialState)

type ActivePersonProviderProps = {
  children: ReactNode
}

/**
 * ActivePersonProvider
 * 
 * Provides the active person context to the application.
 * Fetches the user's primary person on mount using the existing getMyPerson() API.
 * 
 * Usage:
 * ```tsx
 * // In main.tsx or layout
 * <ActivePersonProvider>
 *   <App />
 * </ActivePersonProvider>
 * 
 * // In components
 * const { activePerson, activePersonId, isLoading } = useActivePersonContext()
 * ```
 */
export function ActivePersonProvider({ children }: ActivePersonProviderProps) {
  const {
    data: activePerson,
    isLoading,
    error,
    isFetched,
  } = useQuery<PersonPublic | null, Error>({
    queryKey: ["activePerson"],
    queryFn: async () => {
      try {
        const person = await PersonService.getMyPerson()
        return person
      } catch (err) {
        // If 404, user doesn't have a person profile yet
        // This is expected for new users
        if (err && typeof err === "object" && "status" in err && err.status === 404) {
          return null
        }
        throw err
      }
    },
    // Only fetch when user is logged in
    enabled: !!localStorage.getItem("access_token"),
    // Keep data fresh but don't refetch too aggressively
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: (failureCount, error) => {
      // Don't retry on 404 (no person profile)
      if (error && typeof error === "object" && "status" in error && error.status === 404) {
        return false
      }
      return failureCount < 3
    },
  })

  const value: ActivePersonContextState = {
    activePerson: activePerson ?? null,
    activePersonId: activePerson?.id ?? null,
    isLoading,
    error: error ?? null,
    isInitialized: isFetched,
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
 *   const { activePerson, activePersonId, isLoading, error } = useActivePersonContext()
 *   
 *   if (isLoading) return <Spinner />
 *   if (error) return <Error message={error.message} />
 *   if (!activePerson) return <CreateProfilePrompt />
 *   
 *   return <div>Hello, {activePerson.first_name}!</div>
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
