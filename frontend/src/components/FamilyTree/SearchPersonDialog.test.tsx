// @ts-nocheck

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"
import { PersonMetadataService, PersonService, ProfileService } from "@/client"
import { SearchPersonDialog } from "./SearchPersonDialog"

// Mock the API services
vi.mock("@/client", () => ({
  PersonService: {
    searchMatchingPersons: vi.fn(),
    getMyPerson: vi.fn(),
    getMyAddresses: vi.fn(),
  },
  ProfileService: {
    getProfileCompletionStatus: vi.fn(),
  },
  PersonMetadataService: {
    getGenders: vi.fn(),
  },
  AddressMetadataService: {
    getCountries: vi.fn(),
    getStatesByCountry: vi.fn(),
    getDistrictsByState: vi.fn(),
    getSubDistrictsByDistrict: vi.fn(),
    getLocalitiesBySubDistrict: vi.fn(),
  },
  ReligionMetadataService: {
    getReligions: vi.fn(),
    getCategoriesByReligion: vi.fn(),
    getSubCategoriesByCategory: vi.fn(),
  },
  PersonReligionService: {
    getMyReligion: vi.fn(),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe("SearchPersonDialog", () => {
  const mockOnOpenChange = vi.fn()
  const mockOnPersonSelected = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()

    // Setup default mocks
    ProfileService.getProfileCompletionStatus.mockResolvedValue({
      has_person: true,
    })

    PersonService.getMyPerson.mockResolvedValue({
      id: "user-123",
      first_name: "John",
      last_name: "Doe",
    })

    PersonMetadataService.getGenders.mockResolvedValue([
      { genderId: "gender-1", genderName: "Male" },
      { genderId: "gender-2", genderName: "Female" },
    ])
  })

  it("should render dialog when open", () => {
    render(
      <SearchPersonDialog
        open={true}
        onOpenChange={mockOnOpenChange}
        onPersonSelected={mockOnPersonSelected}
      />,
      { wrapper: createWrapper() },
    )

    expect(screen.getByText("Search Person")).toBeInTheDocument()
    expect(screen.getByText("(Step 1 of 4)")).toBeInTheDocument()
  })

  it("should not render dialog when closed", () => {
    render(
      <SearchPersonDialog
        open={false}
        onOpenChange={mockOnOpenChange}
        onPersonSelected={mockOnPersonSelected}
      />,
      { wrapper: createWrapper() },
    )

    expect(screen.queryByText("Search Person")).not.toBeInTheDocument()
  })

  it("should show Step 1 form initially", async () => {
    render(
      <SearchPersonDialog
        open={true}
        onOpenChange={mockOnOpenChange}
        onPersonSelected={mockOnPersonSelected}
      />,
      { wrapper: createWrapper() },
    )

    await waitFor(() => {
      expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/Last Name/i)).toBeInTheDocument()
    })
  })

  it("should validate required fields in Step 1", async () => {
    render(
      <SearchPersonDialog
        open={true}
        onOpenChange={mockOnOpenChange}
        onPersonSelected={mockOnPersonSelected}
      />,
      { wrapper: createWrapper() },
    )

    await waitFor(() => {
      expect(screen.getByText("Next")).toBeInTheDocument()
    })

    // Try to submit without filling required fields
    const nextButton = screen.getByText("Next")
    fireEvent.click(nextButton)

    await waitFor(() => {
      expect(screen.getByText(/First name is required/i)).toBeInTheDocument()
      expect(screen.getByText(/Last name is required/i)).toBeInTheDocument()
    })
  })

  it("should close dialog and reset state when closed", async () => {
    const { rerender } = render(
      <SearchPersonDialog
        open={true}
        onOpenChange={mockOnOpenChange}
        onPersonSelected={mockOnPersonSelected}
      />,
      { wrapper: createWrapper() },
    )

    // Fill some data
    await waitFor(() => {
      expect(screen.getByLabelText(/First Name/i)).toBeInTheDocument()
    })

    const firstNameInput = screen.getByLabelText(/First Name/i)
    fireEvent.change(firstNameInput, { target: { value: "Test" } })

    // Close dialog
    rerender(
      <SearchPersonDialog
        open={false}
        onOpenChange={mockOnOpenChange}
        onPersonSelected={mockOnPersonSelected}
      />,
    )

    // Reopen dialog
    rerender(
      <SearchPersonDialog
        open={true}
        onOpenChange={mockOnOpenChange}
        onPersonSelected={mockOnPersonSelected}
      />,
    )

    // Check that state is reset
    await waitFor(() => {
      expect(screen.getByLabelText(/First Name/i)).toHaveValue("")
    })
  })
})
