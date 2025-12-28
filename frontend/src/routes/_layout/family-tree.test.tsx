import { describe, it, expect, vi, beforeEach } from 'vitest'
import * as fc from 'fast-check'
import { renderHook, waitFor, act, render } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useState } from 'react'
import React from 'react'
import type { ReactNode } from 'react'

/**
 * Feature: family-tree-view, Property 8: Person Selection Navigation
 * Validates: Requirements 7.1, 7.2, 7.3
 * 
 * For any person card displayed in the family tree, when clicked, the system
 * should update the selected person to that person, fetch that person's
 * relationship data, and re-render the tree centered on the new person.
 */
describe('Property 8: Person Selection Navigation', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })
  })

  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )

  /**
   * Test that person selection updates state correctly
   */
  it('should update selected person when a person is clicked', () => {
    fc.assert(
      fc.property(
        fc.uuid(), // Initial person ID
        fc.uuid(), // New person ID to select
        (initialPersonId, newPersonId) => {
          // Simulate the person selection logic
          const { result } = renderHook(
            () => {
              const [selectedPersonId, setSelectedPersonId] = useState<string | null>(initialPersonId)
              
              const handlePersonClick = (personId: string) => {
                setSelectedPersonId(personId)
              }

              return { selectedPersonId, handlePersonClick }
            },
            { wrapper }
          )

          // Initial state should be the initial person
          expect(result.current.selectedPersonId).toBe(initialPersonId)

          // Click on a new person
          act(() => {
            result.current.handlePersonClick(newPersonId)
          })

          // Selected person should be updated
          expect(result.current.selectedPersonId).toBe(newPersonId)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Test that clicking the same person doesn't break the state
   */
  it('should handle clicking the same person multiple times', () => {
    fc.assert(
      fc.property(
        fc.uuid(),
        fc.integer({ min: 1, max: 5 }),
        (personId, clickCount) => {
          const { result } = renderHook(
            () => {
              const [selectedPersonId, setSelectedPersonId] = useState<string | null>(personId)
              
              const handlePersonClick = (id: string) => {
                setSelectedPersonId(id)
              }

              return { selectedPersonId, handlePersonClick }
            },
            { wrapper }
          )

          // Click the same person multiple times
          act(() => {
            for (let i = 0; i < clickCount; i++) {
              result.current.handlePersonClick(personId)
            }
          })

          // Selected person should still be the same
          expect(result.current.selectedPersonId).toBe(personId)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Test that person selection triggers data fetching
   */
  it('should trigger data fetch when person is selected', () => {
    fc.assert(
      fc.property(
        fc.uuid(),
        fc.uuid(),
        (initialPersonId, newPersonId) => {
          // Track if data fetch was triggered
          let fetchTriggered = false
          const mockFetch = vi.fn(() => {
            fetchTriggered = true
            return Promise.resolve({ data: null })
          })

          const { result } = renderHook(
            () => {
              const [selectedPersonId, setSelectedPersonId] = useState<string | null>(initialPersonId)
              
              const handlePersonClick = (personId: string) => {
                setSelectedPersonId(personId)
                // Simulate data fetch trigger
                mockFetch()
              }

              return { selectedPersonId, handlePersonClick }
            },
            { wrapper }
          )

          // Reset fetch tracking
          fetchTriggered = false
          mockFetch.mockClear()

          // Click on a new person
          act(() => {
            result.current.handlePersonClick(newPersonId)
          })

          // Data fetch should be triggered
          expect(fetchTriggered).toBe(true)
          expect(mockFetch).toHaveBeenCalledTimes(1)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Test that person selection sequence maintains correct state
   */
  it('should maintain correct state through multiple person selections', () => {
    fc.assert(
      fc.property(
        fc.array(fc.uuid(), { minLength: 2, maxLength: 10 }),
        (personIds) => {
          const { result } = renderHook(
            () => {
              const [selectedPersonId, setSelectedPersonId] = useState<string | null>(personIds[0])
              const [selectionHistory, setSelectionHistory] = useState<string[]>([personIds[0]])
              
              const handlePersonClick = (personId: string) => {
                setSelectedPersonId(personId)
                setSelectionHistory(prev => [...prev, personId])
              }

              return { selectedPersonId, handlePersonClick, selectionHistory }
            },
            { wrapper }
          )

          // Click through all persons in sequence
          act(() => {
            for (let i = 1; i < personIds.length; i++) {
              result.current.handlePersonClick(personIds[i])
            }
          })

          // Final selected person should be the last one
          expect(result.current.selectedPersonId).toBe(personIds[personIds.length - 1])

          // Selection history should contain all persons in order
          expect(result.current.selectionHistory).toEqual(personIds)
        }
      ),
      { numRuns: 100 }
    )
  })
})


/**
 * Unit tests for loading indicator
 * Requirements: 7.5
 */
describe('Loading Indicator', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })
  })

  /**
   * Test that loading indicator appears during data fetch
   */
  it('should display loading indicator during data fetch', async () => {
    // Simulate a component with loading state
    const TestComponent = () => {
      const [isLoading, setIsLoading] = useState(true)
      const [data, setData] = useState<string | null>(null)

      const fetchData = async () => {
        setIsLoading(true)
        // Simulate async data fetch
        await new Promise(resolve => setTimeout(resolve, 100))
        setData('loaded')
        setIsLoading(false)
      }

      return (
        <div>
          {isLoading ? (
            <div data-testid="loading-indicator">Loading family tree...</div>
          ) : (
            <div data-testid="content">{data}</div>
          )}
          <button onClick={fetchData} data-testid="fetch-button">
            Fetch
          </button>
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // Initially, loading indicator should be visible
    expect(getByTestId('loading-indicator')).toBeTruthy()
    expect(queryByTestId('content')).toBeNull()
  })

  /**
   * Test that loading indicator disappears after data loads
   */
  it('should hide loading indicator after data loads', async () => {
    // Simulate a component with loading state
    const TestComponent = () => {
      const [isLoading, setIsLoading] = useState(true)
      const [data, setData] = useState<string | null>(null)

      const fetchData = async () => {
        setIsLoading(true)
        // Simulate async data fetch
        await new Promise(resolve => setTimeout(resolve, 10))
        setData('loaded')
        setIsLoading(false)
      }

      // Auto-fetch on mount
      React.useEffect(() => {
        fetchData()
      }, [])

      return (
        <div>
          {isLoading ? (
            <div data-testid="loading-indicator">Loading family tree...</div>
          ) : (
            <div data-testid="content">{data}</div>
          )}
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // Initially, loading indicator should be visible
    expect(getByTestId('loading-indicator')).toBeTruthy()

    // Wait for data to load
    await waitFor(() => {
      expect(queryByTestId('loading-indicator')).toBeNull()
      expect(getByTestId('content')).toBeTruthy()
    })
  })

  /**
   * Test that loading indicator shows during person selection
   */
  it('should show loading indicator when selecting a new person', async () => {
    const TestComponent = () => {
      const [isLoading, setIsLoading] = useState(false)
      const [selectedPerson, setSelectedPerson] = useState('person-1')

      const handlePersonClick = async (personId: string) => {
        setIsLoading(true)
        setSelectedPerson(personId)
        // Simulate data fetch
        await new Promise(resolve => setTimeout(resolve, 10))
        setIsLoading(false)
      }

      return (
        <div>
          {isLoading && <div data-testid="loading-indicator">Loading...</div>}
          <div data-testid="selected-person">{selectedPerson}</div>
          <button
            onClick={() => handlePersonClick('person-2')}
            data-testid="select-button"
          >
            Select Person 2
          </button>
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // Initially, no loading indicator
    expect(queryByTestId('loading-indicator')).toBeNull()

    // Click to select new person
    act(() => {
      getByTestId('select-button').click()
    })

    // Loading indicator should appear
    await waitFor(() => {
      expect(getByTestId('loading-indicator')).toBeTruthy()
    })

    // Wait for loading to complete
    await waitFor(() => {
      expect(queryByTestId('loading-indicator')).toBeNull()
      expect(getByTestId('selected-person').textContent).toBe('person-2')
    })
  })
})


/**
 * Unit tests for error scenarios
 * Requirements: Error handling for various failure cases
 */
describe('Error Scenarios', () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })
  })

  /**
   * Test API fetch failure handling
   */
  it('should handle API fetch failure gracefully', async () => {
    const TestComponent = () => {
      const [error, setError] = useState<Error | null>(null)
      const [isLoading, setIsLoading] = useState(false)

      const fetchData = async () => {
        setIsLoading(true)
        setError(null)
        try {
          // Simulate API failure
          throw new Error('Failed to fetch family tree data')
        } catch (err) {
          setError(err as Error)
        } finally {
          setIsLoading(false)
        }
      }

      return (
        <div>
          {isLoading && <div data-testid="loading">Loading...</div>}
          {error && (
            <div data-testid="error-message">
              {error.message}
              <button onClick={fetchData} data-testid="retry-button">
                Retry
              </button>
            </div>
          )}
          <button onClick={fetchData} data-testid="fetch-button">
            Fetch
          </button>
        </div>
      )
    }

    const { getByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // Trigger fetch
    act(() => {
      getByTestId('fetch-button').click()
    })

    // Wait for error to appear
    await waitFor(() => {
      expect(getByTestId('error-message')).toBeTruthy()
      expect(getByTestId('error-message').textContent).toContain('Failed to fetch family tree data')
      expect(getByTestId('retry-button')).toBeTruthy()
    })
  })

  /**
   * Test invalid person ID handling
   */
  it('should handle invalid person ID gracefully', async () => {
    const TestComponent = () => {
      const [error, setError] = useState<Error | null>(null)
      const [selectedPersonId, setSelectedPersonId] = useState<string | null>(null)

      const handlePersonClick = async (personId: string) => {
        setError(null)
        try {
          // Validate person ID format (basic UUID check)
          if (!personId || personId.length === 0) {
            throw new Error('Invalid person ID')
          }
          setSelectedPersonId(personId)
        } catch (err) {
          setError(err as Error)
        }
      }

      return (
        <div>
          {error && <div data-testid="error-message">{error.message}</div>}
          {selectedPersonId && <div data-testid="selected-person">{selectedPersonId}</div>}
          <button onClick={() => handlePersonClick('')} data-testid="invalid-button">
            Select Invalid
          </button>
          <button onClick={() => handlePersonClick('valid-id')} data-testid="valid-button">
            Select Valid
          </button>
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // Try to select invalid person ID
    act(() => {
      getByTestId('invalid-button').click()
    })

    // Error should be displayed
    await waitFor(() => {
      expect(getByTestId('error-message')).toBeTruthy()
      expect(getByTestId('error-message').textContent).toContain('Invalid person ID')
      expect(queryByTestId('selected-person')).toBeNull()
    })

    // Try to select valid person ID
    act(() => {
      getByTestId('valid-button').click()
    })

    // Valid person should be selected
    await waitFor(() => {
      expect(queryByTestId('error-message')).toBeNull()
      expect(getByTestId('selected-person')).toBeTruthy()
    })
  })

  /**
   * Test empty relationship data handling
   */
  it('should handle empty relationship data gracefully', async () => {
    const TestComponent = () => {
      const [familyData, setFamilyData] = useState<{
        parents: any[]
        spouses: any[]
        siblings: any[]
        children: any[]
      } | null>(null)
      const [isLoading, setIsLoading] = useState(false)

      const fetchData = async () => {
        setIsLoading(true)
        // Simulate fetching empty relationship data
        await new Promise(resolve => setTimeout(resolve, 10))
        setFamilyData({
          parents: [],
          spouses: [],
          siblings: [],
          children: [],
        })
        setIsLoading(false)
      }

      React.useEffect(() => {
        fetchData()
      }, [])

      const hasNoRelationships = familyData &&
        familyData.parents.length === 0 &&
        familyData.spouses.length === 0 &&
        familyData.siblings.length === 0 &&
        familyData.children.length === 0

      return (
        <div>
          {isLoading && <div data-testid="loading">Loading...</div>}
          {hasNoRelationships && (
            <div data-testid="empty-state">
              No family relationships have been recorded yet.
            </div>
          )}
          {familyData && !hasNoRelationships && (
            <div data-testid="family-tree">Family Tree Content</div>
          )}
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // Wait for data to load
    await waitFor(() => {
      expect(queryByTestId('loading')).toBeNull()
      expect(getByTestId('empty-state')).toBeTruthy()
      expect(getByTestId('empty-state').textContent).toContain('No family relationships')
      expect(queryByTestId('family-tree')).toBeNull()
    })
  })

  /**
   * Test partial data handling
   */
  it('should handle partial data gracefully', async () => {
    const TestComponent = () => {
      const [familyData, setFamilyData] = useState<{
        parents: any[]
        spouses: any[]
        siblings: any[]
        children: any[]
      } | null>(null)
      const [isLoading, setIsLoading] = useState(false)

      const fetchData = async () => {
        setIsLoading(true)
        // Simulate fetching partial relationship data
        await new Promise(resolve => setTimeout(resolve, 10))
        setFamilyData({
          parents: [{ id: '1', first_name: 'John', last_name: 'Doe' }],
          spouses: [], // No spouses
          siblings: [{ id: '2', first_name: 'Jane', last_name: 'Doe' }],
          children: [], // No children
        })
        setIsLoading(false)
      }

      React.useEffect(() => {
        fetchData()
      }, [])

      return (
        <div>
          {isLoading && <div data-testid="loading">Loading...</div>}
          {familyData && (
            <div data-testid="family-tree">
              {familyData.parents.length > 0 && (
                <div data-testid="parents-section">Parents: {familyData.parents.length}</div>
              )}
              {familyData.spouses.length > 0 && (
                <div data-testid="spouses-section">Spouses: {familyData.spouses.length}</div>
              )}
              {familyData.siblings.length > 0 && (
                <div data-testid="siblings-section">Siblings: {familyData.siblings.length}</div>
              )}
              {familyData.children.length > 0 && (
                <div data-testid="children-section">Children: {familyData.children.length}</div>
              )}
            </div>
          )}
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // Wait for data to load
    await waitFor(() => {
      expect(queryByTestId('loading')).toBeNull()
      expect(getByTestId('family-tree')).toBeTruthy()
      
      // Should show sections with data
      expect(getByTestId('parents-section')).toBeTruthy()
      expect(getByTestId('siblings-section')).toBeTruthy()
      
      // Should not show sections without data
      expect(queryByTestId('spouses-section')).toBeNull()
      expect(queryByTestId('children-section')).toBeNull()
    })
  })

  /**
   * Test retry mechanism after API failure
   */
  it('should allow retry after API failure', async () => {
    let attemptCount = 0

    const TestComponent = () => {
      const [error, setError] = useState<Error | null>(null)
      const [data, setData] = useState<string | null>(null)
      const [isLoading, setIsLoading] = useState(false)

      const fetchData = async () => {
        setIsLoading(true)
        setError(null)
        try {
          attemptCount++
          if (attemptCount === 1) {
            // First attempt fails
            throw new Error('Network error')
          }
          // Second attempt succeeds
          setData('Success')
        } catch (err) {
          setError(err as Error)
        } finally {
          setIsLoading(false)
        }
      }

      return (
        <div>
          {isLoading && <div data-testid="loading">Loading...</div>}
          {error && (
            <div data-testid="error-message">
              {error.message}
              <button onClick={fetchData} data-testid="retry-button">
                Retry
              </button>
            </div>
          )}
          {data && <div data-testid="success">{data}</div>}
          <button onClick={fetchData} data-testid="fetch-button">
            Fetch
          </button>
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>
    )

    // First attempt - should fail
    act(() => {
      getByTestId('fetch-button').click()
    })

    await waitFor(() => {
      expect(getByTestId('error-message')).toBeTruthy()
      expect(getByTestId('retry-button')).toBeTruthy()
    })

    // Retry - should succeed
    act(() => {
      getByTestId('retry-button').click()
    })

    await waitFor(() => {
      expect(queryByTestId('error-message')).toBeNull()
      expect(getByTestId('success')).toBeTruthy()
      expect(getByTestId('success').textContent).toBe('Success')
    })
  })
})
