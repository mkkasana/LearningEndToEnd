/**
 * Property-Based Tests for MatchPersonNode Component
 * Feature: partner-match-visualizer
 *
 * Property 5: Node Label Correctness
 * Property 6: Birth-Death Year Formatting
 * Validates: Requirements 6.3, 6.4, 6.5
 */

import { cleanup, render, screen } from "@testing-library/react"
import { ReactFlowProvider } from "@xyflow/react"
import * as fc from "fast-check"
import { afterEach, describe, expect, it } from "vitest"
import { formatBirthDeathYears, MatchPersonNode } from "./MatchPersonNode"
import type { MatchPersonNodeData } from "./types"

// Cleanup after each test to prevent multiple elements
afterEach(() => {
  cleanup()
})

// Helper to wrap component with ReactFlowProvider (required for Handle components)
function renderWithProvider(data: MatchPersonNodeData) {
  return render(
    <ReactFlowProvider>
      <MatchPersonNode data={data} />
    </ReactFlowProvider>,
  )
}

// ============================================
// Property-Based Tests
// ============================================

describe("MatchPersonNode - Property-Based Tests", () => {
  /**
   * Feature: partner-match-visualizer, Property 5: Node Label Correctness
   * Validates: Requirements 6.4, 6.5
   *
   * For any MatchPersonNodeData:
   * - If `isSeeker` is true, the node SHALL display "Seeker" label with green styling
   * - If `isMatch` is true, the node SHALL display "Match" label with blue styling
   */
  describe("Property 5: Node Label Correctness", () => {
    it("should display 'Seeker' label when isSeeker is true", () => {
      fc.assert(
        fc.property(
          fc.record({
            personId: fc.uuid(),
            firstName: fc.string({ minLength: 1, maxLength: 15 }),
            lastName: fc.string({ minLength: 1, maxLength: 15 }),
            birthYear: fc.option(fc.integer({ min: 1900, max: 2024 }), {
              nil: null,
            }),
            deathYear: fc.option(fc.integer({ min: 1900, max: 2024 }), {
              nil: null,
            }),
            isSeeker: fc.constant(true),
            isMatch: fc.constant(false),
          }),
          (data) => {
            const { unmount } = renderWithProvider(data)

            // Should display "Seeker" label
            expect(screen.getByText("Seeker")).toBeInTheDocument()

            // Should NOT display "Match" label
            expect(screen.queryByText("Match")).not.toBeInTheDocument()

            // Should have green styling (check for green class)
            const label = screen.getByText("Seeker")
            expect(label.className).toContain("green")

            // Cleanup for next iteration
            unmount()
          },
        ),
        { numRuns: 100 },
      )
    })

    it("should display 'Match' label when isMatch is true", () => {
      fc.assert(
        fc.property(
          fc.record({
            personId: fc.uuid(),
            firstName: fc.string({ minLength: 1, maxLength: 15 }),
            lastName: fc.string({ minLength: 1, maxLength: 15 }),
            birthYear: fc.option(fc.integer({ min: 1900, max: 2024 }), {
              nil: null,
            }),
            deathYear: fc.option(fc.integer({ min: 1900, max: 2024 }), {
              nil: null,
            }),
            isSeeker: fc.constant(false),
            isMatch: fc.constant(true),
          }),
          (data) => {
            const { unmount } = renderWithProvider(data)

            // Should display "Match" label
            expect(screen.getByText("Match")).toBeInTheDocument()

            // Should NOT display "Seeker" label
            expect(screen.queryByText("Seeker")).not.toBeInTheDocument()

            // Should have blue styling (check for blue class)
            const label = screen.getByText("Match")
            expect(label.className).toContain("blue")

            // Cleanup for next iteration
            unmount()
          },
        ),
        { numRuns: 100 },
      )
    })

    it("should not display any label when neither isSeeker nor isMatch is true", () => {
      fc.assert(
        fc.property(
          fc.record({
            personId: fc.uuid(),
            firstName: fc.string({ minLength: 1, maxLength: 15 }),
            lastName: fc.string({ minLength: 1, maxLength: 15 }),
            birthYear: fc.option(fc.integer({ min: 1900, max: 2024 }), {
              nil: null,
            }),
            deathYear: fc.option(fc.integer({ min: 1900, max: 2024 }), {
              nil: null,
            }),
            isSeeker: fc.constant(false),
            isMatch: fc.constant(false),
          }),
          (data) => {
            const { unmount } = renderWithProvider(data)

            // Should NOT display "Seeker" or "Match" labels
            expect(screen.queryByText("Seeker")).not.toBeInTheDocument()
            expect(screen.queryByText("Match")).not.toBeInTheDocument()

            // Cleanup for next iteration
            unmount()
          },
        ),
        { numRuns: 100 },
      )
    })
  })

  /**
   * Feature: partner-match-visualizer, Property 6: Birth-Death Year Formatting
   * Validates: Requirements 6.3
   *
   * For any MatchPersonNodeData with birth_year and optional death_year:
   * - If death_year is null, the display SHALL be "{birth_year} -"
   * - If death_year is not null, the display SHALL be "{birth_year} - {death_year}"
   */
  describe("Property 6: Birth-Death Year Formatting", () => {
    it("should format as 'birthYear -' when deathYear is null", () => {
      fc.assert(
        fc.property(fc.integer({ min: 1900, max: 2024 }), (birthYear) => {
          const result = formatBirthDeathYears(birthYear, null)
          expect(result).toBe(`${birthYear} -`)
        }),
        { numRuns: 100 },
      )
    })

    it("should format as 'birthYear - deathYear' when both are present", () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1900, max: 2024 }),
          fc.integer({ min: 1900, max: 2024 }),
          (birthYear, deathYear) => {
            const result = formatBirthDeathYears(birthYear, deathYear)
            expect(result).toBe(`${birthYear} - ${deathYear}`)
          },
        ),
        { numRuns: 100 },
      )
    })

    it("should return empty string when birthYear is null", () => {
      fc.assert(
        fc.property(
          fc.option(fc.integer({ min: 1900, max: 2024 }), { nil: null }),
          (deathYear) => {
            const result = formatBirthDeathYears(null, deathYear)
            expect(result).toBe("")
          },
        ),
        { numRuns: 100 },
      )
    })

    it("should display formatted years in the component", () => {
      fc.assert(
        fc.property(
          fc.record({
            personId: fc.uuid(),
            firstName: fc.string({ minLength: 1, maxLength: 15 }),
            lastName: fc.string({ minLength: 1, maxLength: 15 }),
            birthYear: fc.integer({ min: 1900, max: 2024 }),
            deathYear: fc.option(fc.integer({ min: 1900, max: 2024 }), {
              nil: null,
            }),
            isSeeker: fc.constant(false),
            isMatch: fc.constant(false),
          }),
          (data) => {
            const { container, unmount } = renderWithProvider(data)
            const expectedFormat = formatBirthDeathYears(
              data.birthYear,
              data.deathYear,
            )

            // The formatted years should appear in the component
            expect(container.textContent).toContain(expectedFormat)

            // Cleanup for next iteration
            unmount()
          },
        ),
        { numRuns: 100 },
      )
    })
  })
})

// ============================================
// Unit Tests for Edge Cases
// ============================================

describe("MatchPersonNode - Unit Tests", () => {
  it("should display first name and last name", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isSeeker: false,
      isMatch: false,
    })

    expect(screen.getByText("John Doe")).toBeInTheDocument()
  })

  it("should display birth year only when death year is null", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isSeeker: false,
      isMatch: false,
    })

    expect(screen.getByText("1990 -")).toBeInTheDocument()
  })

  it("should display both birth and death years", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1950,
      deathYear: 2020,
      isSeeker: false,
      isMatch: false,
    })

    expect(screen.getByText("1950 - 2020")).toBeInTheDocument()
  })

  it("should not display years when birthYear is null", () => {
    const { container } = renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: null,
      deathYear: null,
      isSeeker: false,
      isMatch: false,
    })

    // Should not contain any year format
    expect(container.textContent).not.toMatch(/\d{4}\s*-/)
  })

  it("should have green border for seeker", () => {
    const { container } = renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isSeeker: true,
      isMatch: false,
    })

    // Check for green border class on the Card
    const card = container.querySelector(".border-green-500")
    expect(card).toBeInTheDocument()
  })

  it("should have blue border for match", () => {
    const { container } = renderWithProvider({
      personId: "123",
      firstName: "Jane",
      lastName: "Smith",
      birthYear: 1992,
      deathYear: null,
      isSeeker: false,
      isMatch: true,
    })

    // Check for blue border class on the Card
    const card = container.querySelector(".border-blue-500")
    expect(card).toBeInTheDocument()
  })
})
