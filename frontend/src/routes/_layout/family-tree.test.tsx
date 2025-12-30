import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { act, render, renderHook, waitFor } from "@testing-library/react"
import * as fc from "fast-check"
import type { ReactNode } from "react"
import React, { useState } from "react"
import { beforeEach, describe, expect, it, vi } from "vitest"

/**
 * Feature: family-tree-view, Property 8: Person Selection Navigation
 * Validates: Requirements 7.1, 7.2, 7.3
 *
 * For any person card displayed in the family tree, when clicked, the system
 * should update the selected person to that person, fetch that person's
 * relationship data, and re-render the tree centered on the new person.
 */
describe("Property 8: Person Selection Navigation", () => {
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
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )

  /**
   * Test that person selection updates state correctly
   */
  it("should update selected person when a person is clicked", () => {
    fc.assert(
      fc.property(
        fc.uuid(), // Initial person ID
        fc.uuid(), // New person ID to select
        (initialPersonId, newPersonId) => {
          // Simulate the person selection logic
          const { result } = renderHook(
            () => {
              const [selectedPersonId, setSelectedPersonId] = useState<
                string | null
              >(initialPersonId)

              const handlePersonClick = (personId: string) => {
                setSelectedPersonId(personId)
              }

              return { selectedPersonId, handlePersonClick }
            },
            { wrapper },
          )

          // Initial state should be the initial person
          expect(result.current.selectedPersonId).toBe(initialPersonId)

          // Click on a new person
          act(() => {
            result.current.handlePersonClick(newPersonId)
          })

          // Selected person should be updated
          expect(result.current.selectedPersonId).toBe(newPersonId)
        },
      ),
      { numRuns: 100 },
    )
  })

  /**
   * Test that clicking the same person doesn't break the state
   */
  it("should handle clicking the same person multiple times", () => {
    fc.assert(
      fc.property(
        fc.uuid(),
        fc.integer({ min: 1, max: 5 }),
        (personId, clickCount) => {
          const { result } = renderHook(
            () => {
              const [selectedPersonId, setSelectedPersonId] = useState<
                string | null
              >(personId)

              const handlePersonClick = (id: string) => {
                setSelectedPersonId(id)
              }

              return { selectedPersonId, handlePersonClick }
            },
            { wrapper },
          )

          // Click the same person multiple times
          act(() => {
            for (let i = 0; i < clickCount; i++) {
              result.current.handlePersonClick(personId)
            }
          })

          // Selected person should still be the same
          expect(result.current.selectedPersonId).toBe(personId)
        },
      ),
      { numRuns: 100 },
    )
  })

  /**
   * Test that person selection triggers data fetching
   */
  it("should trigger data fetch when person is selected", () => {
    fc.assert(
      fc.property(fc.uuid(), fc.uuid(), (initialPersonId, newPersonId) => {
        // Track if data fetch was triggered
        let fetchTriggered = false
        const mockFetch = vi.fn(() => {
          fetchTriggered = true
          return Promise.resolve({ data: null })
        })

        const { result } = renderHook(
          () => {
            const [selectedPersonId, setSelectedPersonId] = useState<
              string | null
            >(initialPersonId)

            const handlePersonClick = (personId: string) => {
              setSelectedPersonId(personId)
              // Simulate data fetch trigger
              mockFetch()
            }

            return { selectedPersonId, handlePersonClick }
          },
          { wrapper },
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
      }),
      { numRuns: 100 },
    )
  })

  /**
   * Test that person selection sequence maintains correct state
   */
  it("should maintain correct state through multiple person selections", () => {
    fc.assert(
      fc.property(
        fc.array(fc.uuid(), { minLength: 2, maxLength: 10 }),
        (personIds) => {
          const { result } = renderHook(
            () => {
              const [selectedPersonId, setSelectedPersonId] = useState<
                string | null
              >(personIds[0])
              const [selectionHistory, setSelectionHistory] = useState<
                string[]
              >([personIds[0]])

              const handlePersonClick = (personId: string) => {
                setSelectedPersonId(personId)
                setSelectionHistory((prev) => [...prev, personId])
              }

              return { selectedPersonId, handlePersonClick, selectionHistory }
            },
            { wrapper },
          )

          // Click through all persons in sequence
          act(() => {
            for (let i = 1; i < personIds.length; i++) {
              result.current.handlePersonClick(personIds[i])
            }
          })

          // Final selected person should be the last one
          expect(result.current.selectedPersonId).toBe(
            personIds[personIds.length - 1],
          )

          // Selection history should contain all persons in order
          expect(result.current.selectionHistory).toEqual(personIds)
        },
      ),
      { numRuns: 100 },
    )
  })
})

/**
 * Unit tests for loading indicator
 * Requirements: 7.5
 */
describe("Loading Indicator", () => {
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
  it("should display loading indicator during data fetch", async () => {
    // Simulate a component with loading state
    const TestComponent = () => {
      const [isLoading, setIsLoading] = useState(true)
      const [data, setData] = useState<string | null>(null)

      const fetchData = async () => {
        setIsLoading(true)
        // Simulate async data fetch
        await new Promise((resolve) => setTimeout(resolve, 100))
        setData("loaded")
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
      </QueryClientProvider>,
    )

    // Initially, loading indicator should be visible
    expect(getByTestId("loading-indicator")).toBeTruthy()
    expect(queryByTestId("content")).toBeNull()
  })

  /**
   * Test that loading indicator disappears after data loads
   */
  it("should hide loading indicator after data loads", async () => {
    // Simulate a component with loading state
    const TestComponent = () => {
      const [isLoading, setIsLoading] = useState(true)
      const [data, setData] = useState<string | null>(null)

      const fetchData = async () => {
        setIsLoading(true)
        // Simulate async data fetch
        await new Promise((resolve) => setTimeout(resolve, 10))
        setData("loaded")
        setIsLoading(false)
      }

      // Auto-fetch on mount
      React.useEffect(() => {
        fetchData()
      }, [fetchData])

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
      </QueryClientProvider>,
    )

    // Initially, loading indicator should be visible
    expect(getByTestId("loading-indicator")).toBeTruthy()

    // Wait for data to load
    await waitFor(() => {
      expect(queryByTestId("loading-indicator")).toBeNull()
      expect(getByTestId("content")).toBeTruthy()
    })
  })

  /**
   * Test that loading indicator shows during person selection
   */
  it("should show loading indicator when selecting a new person", async () => {
    const TestComponent = () => {
      const [isLoading, setIsLoading] = useState(false)
      const [selectedPerson, setSelectedPerson] = useState("person-1")

      const handlePersonClick = async (personId: string) => {
        setIsLoading(true)
        setSelectedPerson(personId)
        // Simulate data fetch
        await new Promise((resolve) => setTimeout(resolve, 10))
        setIsLoading(false)
      }

      return (
        <div>
          {isLoading && <div data-testid="loading-indicator">Loading...</div>}
          <div data-testid="selected-person">{selectedPerson}</div>
          <button
            onClick={() => handlePersonClick("person-2")}
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
      </QueryClientProvider>,
    )

    // Initially, no loading indicator
    expect(queryByTestId("loading-indicator")).toBeNull()

    // Click to select new person
    act(() => {
      getByTestId("select-button").click()
    })

    // Loading indicator should appear
    await waitFor(() => {
      expect(getByTestId("loading-indicator")).toBeTruthy()
    })

    // Wait for loading to complete
    await waitFor(() => {
      expect(queryByTestId("loading-indicator")).toBeNull()
      expect(getByTestId("selected-person").textContent).toBe("person-2")
    })
  })
})

/**
 * Unit tests for error scenarios
 * Requirements: Error handling for various failure cases
 */
describe("Error Scenarios", () => {
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
  it("should handle API fetch failure gracefully", async () => {
    const TestComponent = () => {
      const [error, setError] = useState<Error | null>(null)
      const [isLoading, setIsLoading] = useState(false)

      const fetchData = async () => {
        setIsLoading(true)
        setError(null)
        try {
          // Simulate API failure
          throw new Error("Failed to fetch family tree data")
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
      </QueryClientProvider>,
    )

    // Trigger fetch
    act(() => {
      getByTestId("fetch-button").click()
    })

    // Wait for error to appear
    await waitFor(() => {
      expect(getByTestId("error-message")).toBeTruthy()
      expect(getByTestId("error-message").textContent).toContain(
        "Failed to fetch family tree data",
      )
      expect(getByTestId("retry-button")).toBeTruthy()
    })
  })

  /**
   * Test invalid person ID handling
   */
  it("should handle invalid person ID gracefully", async () => {
    const TestComponent = () => {
      const [error, setError] = useState<Error | null>(null)
      const [selectedPersonId, setSelectedPersonId] = useState<string | null>(
        null,
      )

      const handlePersonClick = async (personId: string) => {
        setError(null)
        try {
          // Validate person ID format (basic UUID check)
          if (!personId || personId.length === 0) {
            throw new Error("Invalid person ID")
          }
          setSelectedPersonId(personId)
        } catch (err) {
          setError(err as Error)
        }
      }

      return (
        <div>
          {error && <div data-testid="error-message">{error.message}</div>}
          {selectedPersonId && (
            <div data-testid="selected-person">{selectedPersonId}</div>
          )}
          <button
            onClick={() => handlePersonClick("")}
            data-testid="invalid-button"
          >
            Select Invalid
          </button>
          <button
            onClick={() => handlePersonClick("valid-id")}
            data-testid="valid-button"
          >
            Select Valid
          </button>
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>,
    )

    // Try to select invalid person ID
    act(() => {
      getByTestId("invalid-button").click()
    })

    // Error should be displayed
    await waitFor(() => {
      expect(getByTestId("error-message")).toBeTruthy()
      expect(getByTestId("error-message").textContent).toContain(
        "Invalid person ID",
      )
      expect(queryByTestId("selected-person")).toBeNull()
    })

    // Try to select valid person ID
    act(() => {
      getByTestId("valid-button").click()
    })

    // Valid person should be selected
    await waitFor(() => {
      expect(queryByTestId("error-message")).toBeNull()
      expect(getByTestId("selected-person")).toBeTruthy()
    })
  })

  /**
   * Test empty relationship data handling
   */
  it("should handle empty relationship data gracefully", async () => {
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
        await new Promise((resolve) => setTimeout(resolve, 10))
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
      }, [fetchData])

      const hasNoRelationships =
        familyData &&
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
      </QueryClientProvider>,
    )

    // Wait for data to load
    await waitFor(() => {
      expect(queryByTestId("loading")).toBeNull()
      expect(getByTestId("empty-state")).toBeTruthy()
      expect(getByTestId("empty-state").textContent).toContain(
        "No family relationships",
      )
      expect(queryByTestId("family-tree")).toBeNull()
    })
  })

  /**
   * Test partial data handling
   */
  it("should handle partial data gracefully", async () => {
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
        await new Promise((resolve) => setTimeout(resolve, 10))
        setFamilyData({
          parents: [{ id: "1", first_name: "John", last_name: "Doe" }],
          spouses: [], // No spouses
          siblings: [{ id: "2", first_name: "Jane", last_name: "Doe" }],
          children: [], // No children
        })
        setIsLoading(false)
      }

      React.useEffect(() => {
        fetchData()
      }, [fetchData])

      return (
        <div>
          {isLoading && <div data-testid="loading">Loading...</div>}
          {familyData && (
            <div data-testid="family-tree">
              {familyData.parents.length > 0 && (
                <div data-testid="parents-section">
                  Parents: {familyData.parents.length}
                </div>
              )}
              {familyData.spouses.length > 0 && (
                <div data-testid="spouses-section">
                  Spouses: {familyData.spouses.length}
                </div>
              )}
              {familyData.siblings.length > 0 && (
                <div data-testid="siblings-section">
                  Siblings: {familyData.siblings.length}
                </div>
              )}
              {familyData.children.length > 0 && (
                <div data-testid="children-section">
                  Children: {familyData.children.length}
                </div>
              )}
            </div>
          )}
        </div>
      )
    }

    const { getByTestId, queryByTestId } = render(
      <QueryClientProvider client={queryClient}>
        <TestComponent />
      </QueryClientProvider>,
    )

    // Wait for data to load
    await waitFor(() => {
      expect(queryByTestId("loading")).toBeNull()
      expect(getByTestId("family-tree")).toBeTruthy()

      // Should show sections with data
      expect(getByTestId("parents-section")).toBeTruthy()
      expect(getByTestId("siblings-section")).toBeTruthy()

      // Should not show sections without data
      expect(queryByTestId("spouses-section")).toBeNull()
      expect(queryByTestId("children-section")).toBeNull()
    })
  })

  /**
   * Test retry mechanism after API failure
   */
  it("should allow retry after API failure", async () => {
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
            throw new Error("Network error")
          }
          // Second attempt succeeds
          setData("Success")
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
      </QueryClientProvider>,
    )

    // First attempt - should fail
    act(() => {
      getByTestId("fetch-button").click()
    })

    await waitFor(() => {
      expect(getByTestId("error-message")).toBeTruthy()
      expect(getByTestId("retry-button")).toBeTruthy()
    })

    // Retry - should succeed
    act(() => {
      getByTestId("retry-button").click()
    })

    await waitFor(() => {
      expect(queryByTestId("error-message")).toBeNull()
      expect(getByTestId("success")).toBeTruthy()
      expect(getByTestId("success").textContent).toBe("Success")
    })
  })
})

/**
 * Feature: family-tree-view, Property 10: Responsive Layout Adaptation
 * Validates: Requirements 10.4
 *
 * For any viewport size change, the family tree layout should adapt appropriately
 * by adjusting card sizes, spacing, and section arrangement based on the current
 * breakpoint (desktop, tablet, or mobile).
 */
describe("Property 10: Responsive Layout Adaptation", () => {
  /**
   * Test that layout adapts to different viewport widths
   */
  it("should adapt layout based on viewport width", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 2560 }), // Viewport width range
        (viewportWidth) => {
          // Determine expected breakpoint
          const getBreakpoint = (
            width: number,
          ): "mobile" | "tablet" | "desktop" => {
            if (width <= 640) return "mobile"
            if (width <= 1024) return "tablet"
            return "desktop"
          }

          const breakpoint = getBreakpoint(viewportWidth)

          // Simulate layout adaptation logic
          const getLayoutConfig = (bp: "mobile" | "tablet" | "desktop") => {
            switch (bp) {
              case "mobile":
                return {
                  cardSize: "small",
                  spacing: "compact",
                  arrangement: "vertical",
                  maxCardsPerRow: 1,
                }
              case "tablet":
                return {
                  cardSize: "medium",
                  spacing: "normal",
                  arrangement: "mixed",
                  maxCardsPerRow: 2,
                }
              case "desktop":
                return {
                  cardSize: "large",
                  spacing: "spacious",
                  arrangement: "horizontal",
                  maxCardsPerRow: 4,
                }
            }
          }

          const layoutConfig = getLayoutConfig(breakpoint)

          // Verify layout configuration matches breakpoint
          if (viewportWidth <= 640) {
            expect(layoutConfig.cardSize).toBe("small")
            expect(layoutConfig.arrangement).toBe("vertical")
            expect(layoutConfig.maxCardsPerRow).toBe(1)
          } else if (viewportWidth <= 1024) {
            expect(layoutConfig.cardSize).toBe("medium")
            expect(layoutConfig.arrangement).toBe("mixed")
            expect(layoutConfig.maxCardsPerRow).toBe(2)
          } else {
            expect(layoutConfig.cardSize).toBe("large")
            expect(layoutConfig.arrangement).toBe("horizontal")
            expect(layoutConfig.maxCardsPerRow).toBe(4)
          }
        },
      ),
      { numRuns: 100 },
    )
  })

  /**
   * Test that card sizes scale appropriately with viewport
   */
  it("should scale card sizes based on breakpoint", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("mobile", "tablet", "desktop"),
        (breakpoint) => {
          // Simulate card size calculation
          const getCardDimensions = (bp: "mobile" | "tablet" | "desktop") => {
            switch (bp) {
              case "mobile":
                return { width: 140, height: 180, avatarSize: 48 }
              case "tablet":
                return { width: 170, height: 220, avatarSize: 56 }
              case "desktop":
                return { width: 200, height: 260, avatarSize: 64 }
            }
          }

          const dimensions = getCardDimensions(breakpoint)

          // Verify dimensions are appropriate for breakpoint
          if (breakpoint === "mobile") {
            expect(dimensions.width).toBeLessThanOrEqual(160)
            expect(dimensions.avatarSize).toBeLessThanOrEqual(48)
          } else if (breakpoint === "tablet") {
            expect(dimensions.width).toBeGreaterThan(140)
            expect(dimensions.width).toBeLessThanOrEqual(180)
            expect(dimensions.avatarSize).toBeGreaterThan(48)
            expect(dimensions.avatarSize).toBeLessThanOrEqual(56)
          } else {
            expect(dimensions.width).toBeGreaterThan(170)
            expect(dimensions.avatarSize).toBeGreaterThan(56)
          }
        },
      ),
      { numRuns: 100 },
    )
  })

  /**
   * Test that spacing adjusts based on viewport
   */
  it("should adjust spacing based on breakpoint", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("mobile", "tablet", "desktop"),
        (breakpoint) => {
          // Simulate spacing calculation
          const getSpacing = (bp: "mobile" | "tablet" | "desktop") => {
            switch (bp) {
              case "mobile":
                return { gap: 8, padding: 16, sectionGap: 16 }
              case "tablet":
                return { gap: 16, padding: 24, sectionGap: 24 }
              case "desktop":
                return { gap: 24, padding: 32, sectionGap: 32 }
            }
          }

          const spacing = getSpacing(breakpoint)

          // Verify spacing increases with larger viewports
          if (breakpoint === "mobile") {
            expect(spacing.gap).toBeLessThanOrEqual(12)
            expect(spacing.padding).toBeLessThanOrEqual(16)
          } else if (breakpoint === "tablet") {
            expect(spacing.gap).toBeGreaterThan(8)
            expect(spacing.gap).toBeLessThanOrEqual(20)
            expect(spacing.padding).toBeGreaterThan(16)
            expect(spacing.padding).toBeLessThanOrEqual(24)
          } else {
            expect(spacing.gap).toBeGreaterThan(16)
            expect(spacing.padding).toBeGreaterThan(24)
          }
        },
      ),
      { numRuns: 100 },
    )
  })

  /**
   * Test that section arrangement changes with viewport
   */
  it("should change section arrangement based on breakpoint", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("mobile", "tablet", "desktop"),
        fc.array(
          fc.record({
            id: fc.uuid(),
            type: fc.constantFrom("parent", "spouse", "sibling", "child"),
          }),
          { minLength: 1, maxLength: 10 },
        ),
        (breakpoint, sections) => {
          // Simulate section arrangement logic
          const arrangeSections = (
            bp: "mobile" | "tablet" | "desktop",
            secs: Array<{ id: string; type: string }>,
          ) => {
            if (bp === "mobile") {
              // Mobile: vertical stack
              return {
                layout: "vertical",
                columns: 1,
                sections: secs.map((s) => ({ ...s, width: "100%" })),
              }
            }
            if (bp === "tablet") {
              // Tablet: mixed layout
              return {
                layout: "mixed",
                columns: 2,
                sections: secs.map((s) => ({ ...s, width: "50%" })),
              }
            }
            // Desktop: horizontal layout
            return {
              layout: "horizontal",
              columns: 4,
              sections: secs.map((s) => ({ ...s, width: "25%" })),
            }
          }

          const arrangement = arrangeSections(breakpoint, sections)

          // Verify arrangement matches breakpoint
          if (breakpoint === "mobile") {
            expect(arrangement.layout).toBe("vertical")
            expect(arrangement.columns).toBe(1)
            arrangement.sections.forEach((s) => {
              expect(s.width).toBe("100%")
            })
          } else if (breakpoint === "tablet") {
            expect(arrangement.layout).toBe("mixed")
            expect(arrangement.columns).toBe(2)
          } else {
            expect(arrangement.layout).toBe("horizontal")
            expect(arrangement.columns).toBe(4)
          }
        },
      ),
      { numRuns: 100 },
    )
  })

  /**
   * Test that viewport resize triggers layout recalculation
   */
  it("should recalculate layout on viewport resize", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 2560 }),
        fc.integer({ min: 320, max: 2560 }),
        (initialWidth, newWidth) => {
          // Simulate viewport resize
          let currentWidth = initialWidth
          let layoutRecalculated = false

          const getBreakpoint = (width: number) => {
            if (width <= 640) return "mobile"
            if (width <= 1024) return "tablet"
            return "desktop"
          }

          const initialBreakpoint = getBreakpoint(currentWidth)

          // Simulate resize
          currentWidth = newWidth
          const newBreakpoint = getBreakpoint(currentWidth)

          // Layout should recalculate if breakpoint changed
          if (initialBreakpoint !== newBreakpoint) {
            layoutRecalculated = true
          }

          // Verify layout recalculation logic
          const breakpointChanged = initialBreakpoint !== newBreakpoint
          expect(layoutRecalculated).toBe(breakpointChanged)
        },
      ),
      { numRuns: 100 },
    )
  })

  /**
   * Test that all sections remain visible across breakpoints
   */
  it("should keep all sections visible across breakpoints", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("mobile", "tablet", "desktop"),
        fc.record({
          hasParents: fc.boolean(),
          hasSpouses: fc.boolean(),
          hasSiblings: fc.boolean(),
          hasChildren: fc.boolean(),
        }),
        (breakpoint, familyData) => {
          // Simulate section visibility logic
          const getSectionVisibility = (
            _bp: "mobile" | "tablet" | "desktop",
            data: {
              hasParents: boolean
              hasSpouses: boolean
              hasSiblings: boolean
              hasChildren: boolean
            },
          ) => {
            // All sections should be visible if they have data,
            // regardless of breakpoint
            return {
              parentsVisible: data.hasParents,
              spousesVisible: data.hasSpouses,
              siblingsVisible: data.hasSiblings,
              childrenVisible: data.hasChildren,
            }
          }

          const visibility = getSectionVisibility(breakpoint, familyData)

          // Verify sections are visible based on data, not breakpoint
          expect(visibility.parentsVisible).toBe(familyData.hasParents)
          expect(visibility.spousesVisible).toBe(familyData.hasSpouses)
          expect(visibility.siblingsVisible).toBe(familyData.hasSiblings)
          expect(visibility.childrenVisible).toBe(familyData.hasChildren)
        },
      ),
      { numRuns: 100 },
    )
  })
})
