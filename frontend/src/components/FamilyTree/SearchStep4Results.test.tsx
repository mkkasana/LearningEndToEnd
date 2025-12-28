// @ts-nocheck
import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { SearchStep4Results } from "./SearchStep4Results"
import type { PersonMatchResult } from "@/client"

describe("SearchStep4Results", () => {
  const mockOnExplore = vi.fn()
  const mockOnBack = vi.fn()

  const mockResults: PersonMatchResult[] = [
    {
      person_id: "person-1",
      first_name: "John",
      middle_name: "Michael",
      last_name: "Doe",
      date_of_birth: "1990-05-15",
      date_of_death: null,
      address_display: "Mumbai, Maharashtra, India",
      religion_display: "Hindu, Brahmin",
      match_score: 85.5,
      name_match_score: 90.0,
    },
    {
      person_id: "person-2",
      first_name: "Jane",
      middle_name: null,
      last_name: "Smith",
      date_of_birth: "1985-03-20",
      date_of_death: "2020-12-10",
      address_display: "Delhi, India",
      religion_display: "Christian, Catholic",
      match_score: 75.2,
      name_match_score: 80.0,
    },
  ]

  it("should display search results correctly", () => {
    render(
      <SearchStep4Results
        results={mockResults}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    // Check that both results are displayed
    expect(screen.getByText("John Michael Doe")).toBeInTheDocument()
    expect(screen.getByText("Jane Smith")).toBeInTheDocument()

    // Check birth/death years
    expect(screen.getByText("1990 -")).toBeInTheDocument()
    expect(screen.getByText("1985 - 2020")).toBeInTheDocument()

    // Check address display
    expect(screen.getByText("Mumbai, Maharashtra, India")).toBeInTheDocument()
    expect(screen.getByText("Delhi, India")).toBeInTheDocument()

    // Check religion display
    expect(screen.getByText("Hindu, Brahmin")).toBeInTheDocument()
    expect(screen.getByText("Christian, Catholic")).toBeInTheDocument()
  })

  it("should display match scores", () => {
    render(
      <SearchStep4Results
        results={mockResults}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    // Match scores should be rounded
    expect(screen.getByText("Match Score: 86%")).toBeInTheDocument()
    expect(screen.getByText("Match Score: 75%")).toBeInTheDocument()
  })

  it("should show correct result count", () => {
    render(
      <SearchStep4Results
        results={mockResults}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    expect(screen.getByText("Found 2 matches")).toBeInTheDocument()
  })

  it("should show singular 'match' for single result", () => {
    const singleResult = [mockResults[0]]
    
    render(
      <SearchStep4Results
        results={singleResult}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    expect(screen.getByText("Found 1 match")).toBeInTheDocument()
  })

  it("should display empty state when no results", () => {
    render(
      <SearchStep4Results
        results={[]}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    expect(screen.getByText("No Results Found")).toBeInTheDocument()
    expect(
      screen.getByText(/No persons match your search criteria/i)
    ).toBeInTheDocument()
  })

  it("should call onExplore when Explore button is clicked", () => {
    render(
      <SearchStep4Results
        results={mockResults}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    const exploreButtons = screen.getAllByText("Explore")
    fireEvent.click(exploreButtons[0])

    expect(mockOnExplore).toHaveBeenCalledWith("person-1")
  })

  it("should call onBack when Back button is clicked", () => {
    render(
      <SearchStep4Results
        results={mockResults}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    const backButton = screen.getByText("Back to Search")
    fireEvent.click(backButton)

    expect(mockOnBack).toHaveBeenCalled()
  })

  it("should handle missing middle name", () => {
    render(
      <SearchStep4Results
        results={mockResults}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    // Jane Smith has no middle name
    expect(screen.getByText("Jane Smith")).toBeInTheDocument()
    expect(screen.queryByText("Jane null Smith")).not.toBeInTheDocument()
  })

  it("should format address and religion display", () => {
    render(
      <SearchStep4Results
        results={mockResults}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    // Check that comma-separated displays are shown correctly
    expect(screen.getByText("Mumbai, Maharashtra, India")).toBeInTheDocument()
    expect(screen.getByText("Hindu, Brahmin")).toBeInTheDocument()
  })

  it("should handle empty address and religion display", () => {
    const resultWithEmptyFields: PersonMatchResult[] = [
      {
        person_id: "person-3",
        first_name: "Test",
        middle_name: null,
        last_name: "User",
        date_of_birth: "2000-01-01",
        date_of_death: null,
        address_display: "",
        religion_display: "",
        match_score: 50.0,
        name_match_score: 60.0,
      },
    ]

    render(
      <SearchStep4Results
        results={resultWithEmptyFields}
        onExplore={mockOnExplore}
        onBack={mockOnBack}
      />
    )

    // Should show "Not specified" for empty fields
    const notSpecifiedElements = screen.getAllByText("Not specified")
    expect(notSpecifiedElements).toHaveLength(2) // One for address, one for religion
  })
})
