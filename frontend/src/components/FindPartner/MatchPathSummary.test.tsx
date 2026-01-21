/**
 * Property-Based Tests for MatchPathSummary Component
 * Feature: partner-match-visualizer
 * 
 * Property 3: Path Summary Correctness
 * Validates: Requirements 4.1, 4.2, 4.3
 */

import * as fc from "fast-check"
import { describe, expect, it } from "vitest"
import { render, screen } from "@testing-library/react"
import { MatchPathSummary } from "./MatchPathSummary"

// ============================================
// Property-Based Tests
// ============================================

describe("MatchPathSummary - Property-Based Tests", () => {
  /**
   * Feature: partner-match-visualizer, Property 3: Path Summary Correctness
   * Validates: Requirements 4.1, 4.2, 4.3
   *
   * For any extracted path with N persons:
   * - The path summary SHALL contain exactly N names
   * - The first name SHALL be the seeker's first name
   * - The last name SHALL be the match's first name
   * - When joined with " → ", the result SHALL have exactly N-1 arrow separators
   */
  describe("Property 3: Path Summary Correctness", () => {
    it("should display all names joined with arrow separators", () => {
      fc.assert(
        fc.property(
          fc.array(fc.string({ minLength: 1, maxLength: 15 }), {
            minLength: 2,
            maxLength: 6,
          }),
          (pathNames) => {
            const { container } = render(
              <MatchPathSummary pathNames={pathNames} />
            )

            const text = container.textContent || ""

            // Should contain all names
            for (const name of pathNames) {
              expect(text).toContain(name)
            }

            // Should have exactly N-1 arrow separators
            const arrowCount = (text.match(/→/g) || []).length
            expect(arrowCount).toBe(pathNames.length - 1)
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should display names in correct order from seeker to match", () => {
      fc.assert(
        fc.property(
          fc.array(fc.string({ minLength: 1, maxLength: 15 }), {
            minLength: 2,
            maxLength: 6,
          }),
          (pathNames) => {
            const { container } = render(
              <MatchPathSummary pathNames={pathNames} />
            )

            const text = container.textContent || ""

            // Names should appear in order
            let lastIndex = -1
            for (const name of pathNames) {
              const currentIndex = text.indexOf(name, lastIndex + 1)
              expect(currentIndex).toBeGreaterThan(lastIndex)
              lastIndex = currentIndex
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should display first name as seeker and last name as match", () => {
      fc.assert(
        fc.property(
          fc.string({ minLength: 1, maxLength: 15 }),
          fc.string({ minLength: 1, maxLength: 15 }),
          fc.array(fc.string({ minLength: 1, maxLength: 15 }), {
            minLength: 0,
            maxLength: 4,
          }),
          (seekerName, matchName, middleNames) => {
            // Ensure seeker and match names are different from middle names
            const pathNames = [seekerName, ...middleNames, matchName]

            const { container } = render(
              <MatchPathSummary pathNames={pathNames} />
            )

            const text = container.textContent || ""

            // First name in path should be seeker
            const pathPart = text.replace("Path: ", "")
            expect(pathPart.startsWith(seekerName)).toBe(true)

            // Last name in path should be match
            expect(pathPart.endsWith(matchName)).toBe(true)
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})

// ============================================
// Unit Tests for Edge Cases
// ============================================

describe("MatchPathSummary - Unit Tests", () => {
  it("should render nothing for empty path", () => {
    const { container } = render(<MatchPathSummary pathNames={[]} />)
    expect(container.textContent).toBe("")
  })

  it("should render single name without arrow", () => {
    render(<MatchPathSummary pathNames={["John"]} />)
    expect(screen.getByText(/Path:/)).toBeInTheDocument()
    expect(screen.getByText(/John/)).toBeInTheDocument()
    // No arrow for single name
    expect(screen.queryByText(/→/)).not.toBeInTheDocument()
  })

  it("should render two names with one arrow", () => {
    render(<MatchPathSummary pathNames={["John", "Jane"]} />)
    const text = screen.getByText(/Path:/).parentElement?.textContent || ""
    expect(text).toContain("John → Jane")
  })

  it("should render multiple names with correct arrows", () => {
    render(<MatchPathSummary pathNames={["John", "Ram", "Shyam", "Priya"]} />)
    const text = screen.getByText(/Path:/).parentElement?.textContent || ""
    expect(text).toContain("John → Ram → Shyam → Priya")
  })
})
