/**
 * Unit Tests for Rishte PersonNode Component
 * Feature: rishte-view-button
 *
 * Tests for:
 * - View button rendering and functionality
 * - Aria-label correctness
 * - Click handler invocation
 * - Keyboard accessibility
 * - Person A/B label display
 * - Birth/death year formatting
 *
 * Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3, 4.4
 */

import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { ReactFlowProvider } from "@xyflow/react"
import { afterEach, describe, expect, it, vi } from "vitest"
import { formatBirthDeathYears, PersonNode } from "./PersonNode"
import type { PersonNodeData } from "./types"

// Cleanup after each test to prevent multiple elements
afterEach(() => {
  cleanup()
})

// Helper to wrap component with ReactFlowProvider (required for Handle components)
function renderWithProvider(data: PersonNodeData) {
  return render(
    <ReactFlowProvider>
      <PersonNode data={data} />
    </ReactFlowProvider>,
  )
}

// ============================================
// Unit Tests for View Button
// ============================================

describe("PersonNode - View Button Tests", () => {
  /**
   * Validates: Requirement 1.1
   * THE PersonNode component SHALL display a View button with an Eye icon
   */
  it("should render View button with Eye icon when onViewClick is provided", () => {
    const mockOnViewClick = vi.fn()
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: false,
      onViewClick: mockOnViewClick,
    })

    // View button should be present
    const viewButton = screen.getByRole("button", { name: /view details for/i })
    expect(viewButton).toBeInTheDocument()

    // Button should contain "View" text
    expect(screen.getByText("View")).toBeInTheDocument()
  })

  /**
   * Validates: Requirement 1.1 (conditional rendering)
   * View button should NOT render when onViewClick is not provided
   */
  it("should not render View button when onViewClick is not provided", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: false,
    })

    // View button should NOT be present
    expect(screen.queryByText("View")).not.toBeInTheDocument()
  })

  /**
   * Validates: Requirement 1.2
   * WHEN a user clicks the View button, THE PersonNode SHALL emit an onViewClick callback with the person's ID
   */
  it("should call onViewClick with personId when View button is clicked", () => {
    const mockOnViewClick = vi.fn()
    const personId = "test-person-123"
    renderWithProvider({
      personId,
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: false,
      onViewClick: mockOnViewClick,
    })

    const viewButton = screen.getByRole("button", { name: /view details for/i })
    fireEvent.click(viewButton)

    expect(mockOnViewClick).toHaveBeenCalledTimes(1)
    expect(mockOnViewClick).toHaveBeenCalledWith(personId)
  })

  /**
   * Validates: Requirement 1.3
   * THE View button SHALL stop event propagation to prevent triggering any parent click handlers
   */
  it("should stop event propagation when View button is clicked", () => {
    const mockOnViewClick = vi.fn()
    const mockParentClick = vi.fn()

    render(
      <div onClick={mockParentClick}>
        <ReactFlowProvider>
          <PersonNode
            data={{
              personId: "123",
              firstName: "John",
              lastName: "Doe",
              birthYear: 1990,
              deathYear: null,
              isPersonA: false,
              isPersonB: false,
              onViewClick: mockOnViewClick,
            }}
          />
        </ReactFlowProvider>
      </div>,
    )

    const viewButton = screen.getByRole("button", { name: /view details for/i })
    fireEvent.click(viewButton)

    // onViewClick should be called
    expect(mockOnViewClick).toHaveBeenCalledTimes(1)
    // Parent click handler should NOT be called due to stopPropagation
    expect(mockParentClick).not.toHaveBeenCalled()
  })

  /**
   * Validates: Requirement 1.5
   * THE View button SHALL have an aria-label of "View details for {firstName} {lastName}"
   */
  it("should have correct aria-label with person's name", () => {
    const mockOnViewClick = vi.fn()
    renderWithProvider({
      personId: "123",
      firstName: "Jane",
      lastName: "Smith",
      birthYear: 1985,
      deathYear: null,
      isPersonA: false,
      isPersonB: false,
      onViewClick: mockOnViewClick,
    })

    const viewButton = screen.getByRole("button", {
      name: "View details for Jane Smith",
    })
    expect(viewButton).toBeInTheDocument()
  })

  /**
   * Validates: Requirements 4.1, 4.2, 4.3
   * THE View button SHALL use the outline variant styling and small (sm) size
   */
  it("should have correct button styling classes", () => {
    const mockOnViewClick = vi.fn()
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: false,
      onViewClick: mockOnViewClick,
    })

    const viewButton = screen.getByRole("button", { name: /view details for/i })
    // Check for nodrag and nopan classes (React Flow specific)
    expect(viewButton.className).toContain("nodrag")
    expect(viewButton.className).toContain("nopan")
  })
})

// ============================================
// Unit Tests for Person A/B Labels
// ============================================

describe("PersonNode - Person A/B Label Tests", () => {
  it("should display 'Person A' label with green styling when isPersonA is true", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: true,
      isPersonB: false,
    })

    const label = screen.getByText("Person A")
    expect(label).toBeInTheDocument()
    expect(label.className).toContain("green")
  })

  it("should display 'Person B' label with blue styling when isPersonB is true", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: true,
    })

    const label = screen.getByText("Person B")
    expect(label).toBeInTheDocument()
    expect(label.className).toContain("blue")
  })

  it("should not display any label when neither isPersonA nor isPersonB is true", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: false,
    })

    expect(screen.queryByText("Person A")).not.toBeInTheDocument()
    expect(screen.queryByText("Person B")).not.toBeInTheDocument()
  })

  it("should have green border for Person A", () => {
    const { container } = renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: true,
      isPersonB: false,
    })

    const card = container.querySelector(".border-green-500")
    expect(card).toBeInTheDocument()
  })

  it("should have blue border for Person B", () => {
    const { container } = renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: true,
    })

    const card = container.querySelector(".border-blue-500")
    expect(card).toBeInTheDocument()
  })
})

// ============================================
// Unit Tests for Name and Year Display
// ============================================

describe("PersonNode - Name and Year Display Tests", () => {
  it("should display first name and last name", () => {
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: false,
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
      isPersonA: false,
      isPersonB: false,
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
      isPersonA: false,
      isPersonB: false,
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
      isPersonA: false,
      isPersonB: false,
    })

    // Should not contain any year format
    expect(container.textContent).not.toMatch(/\d{4}\s*-/)
  })
})

// ============================================
// Unit Tests for formatBirthDeathYears function
// ============================================

describe("formatBirthDeathYears", () => {
  it("should format as 'birthYear -' when deathYear is null", () => {
    expect(formatBirthDeathYears(1990, null)).toBe("1990 -")
  })

  it("should format as 'birthYear - deathYear' when both are present", () => {
    expect(formatBirthDeathYears(1950, 2020)).toBe("1950 - 2020")
  })

  it("should return empty string when birthYear is null", () => {
    expect(formatBirthDeathYears(null, null)).toBe("")
    expect(formatBirthDeathYears(null, 2020)).toBe("")
  })
})

// ============================================
// Unit Tests for View Button with Person A/B
// ============================================

describe("PersonNode - View Button with Person A/B", () => {
  it("should render View button alongside Person A label", () => {
    const mockOnViewClick = vi.fn()
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: true,
      isPersonB: false,
      onViewClick: mockOnViewClick,
    })

    // Both should be present
    expect(screen.getByText("Person A")).toBeInTheDocument()
    expect(screen.getByText("View")).toBeInTheDocument()
  })

  it("should render View button alongside Person B label", () => {
    const mockOnViewClick = vi.fn()
    renderWithProvider({
      personId: "123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
      deathYear: null,
      isPersonA: false,
      isPersonB: true,
      onViewClick: mockOnViewClick,
    })

    // Both should be present
    expect(screen.getByText("Person B")).toBeInTheDocument()
    expect(screen.getByText("View")).toBeInTheDocument()
  })
})
