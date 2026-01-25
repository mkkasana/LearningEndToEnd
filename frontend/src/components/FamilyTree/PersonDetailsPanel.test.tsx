import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

// Mock the hooks
vi.mock("@/hooks/usePersonCompleteDetails", () => ({
  usePersonCompleteDetails: vi.fn(),
}))

vi.mock("@/hooks/usePersonLifeEvents", () => ({
  usePersonLifeEvents: vi.fn(),
}))

// Mock useNavigate from @tanstack/react-router
const mockNavigate = vi.fn()
vi.mock("@tanstack/react-router", () => ({
  useNavigate: () => mockNavigate,
}))

import { usePersonCompleteDetails } from "@/hooks/usePersonCompleteDetails"
import { usePersonLifeEvents } from "@/hooks/usePersonLifeEvents"
import { PersonDetailsPanel } from "./PersonDetailsPanel"

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

// Mock person data
const mockPersonData = {
  id: "123e4567-e89b-12d3-a456-426614174000",
  first_name: "John",
  middle_name: null,
  last_name: "Doe",
  gender_id: "gender-1",
  gender_name: "Male",
  date_of_birth: "1990-01-15",
  date_of_death: null,
  user_id: null,
  created_by_user_id: "user-1",
  is_primary: true,
  created_at: "2024-01-01T00:00:00Z",
  updated_at: "2024-01-01T00:00:00Z",
  address: null,
  religion: null,
}

describe("PersonDetailsPanel - Explore Button Tests", () => {
  const mockOnOpenChange = vi.fn()
  const mockRefetch = vi.fn()
  const mockRefetchEvents = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    sessionStorage.clear()

    // Default mock for life events (empty)
    vi.mocked(usePersonLifeEvents).mockReturnValue({
      data: { data: [], count: 0 },
      isLoading: false,
      error: null,
      refetch: mockRefetchEvents,
    })
  })

  describe("Button Rendering", () => {
    it("should render Explore button when data is loaded successfully", async () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: mockPersonData,
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      await waitFor(() => {
        expect(screen.getByText("Explore in Family Tree")).toBeInTheDocument()
      })
    })

    it("should render button with Network icon", async () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: mockPersonData,
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      await waitFor(() => {
        const button = screen.getByRole("button", {
          name: /Explore.*in Family Tree/i,
        })
        expect(button).toBeInTheDocument()
        // Check that button contains an SVG (the Network icon)
        expect(button.querySelector("svg")).toBeInTheDocument()
      })
    })

    it("should have correct aria-label for accessibility", async () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: mockPersonData,
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      await waitFor(() => {
        const button = screen.getByRole("button", {
          name: "Explore John Doe in Family Tree",
        })
        expect(button).toBeInTheDocument()
      })
    })

    it("should NOT render Explore button during loading state", () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: undefined,
        isLoading: true,
        error: null,
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      expect(screen.queryByText("Explore in Family Tree")).not.toBeInTheDocument()
      expect(screen.getByText("Loading details...")).toBeInTheDocument()
    })

    it("should NOT render Explore button during error state", () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: undefined,
        isLoading: false,
        error: new Error("Failed to load"),
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      expect(screen.queryByText("Explore in Family Tree")).not.toBeInTheDocument()
      expect(screen.getByText("Failed to load person details")).toBeInTheDocument()
    })
  })

  describe("Click Behavior", () => {
    it("should store personId in sessionStorage when clicked", async () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: mockPersonData,
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      await waitFor(() => {
        expect(screen.getByText("Explore in Family Tree")).toBeInTheDocument()
      })

      const button = screen.getByText("Explore in Family Tree")
      fireEvent.click(button)

      expect(sessionStorage.getItem("familyTreeExplorePersonId")).toBe(
        "123e4567-e89b-12d3-a456-426614174000",
      )
    })

    it("should close panel when clicked", async () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: mockPersonData,
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      await waitFor(() => {
        expect(screen.getByText("Explore in Family Tree")).toBeInTheDocument()
      })

      const button = screen.getByText("Explore in Family Tree")
      fireEvent.click(button)

      expect(mockOnOpenChange).toHaveBeenCalledWith(false)
    })

    it("should trigger navigation to /family-tree when clicked", async () => {
      vi.mocked(usePersonCompleteDetails).mockReturnValue({
        data: mockPersonData,
        isLoading: false,
        error: null,
        refetch: mockRefetch,
      })

      render(
        <PersonDetailsPanel
          personId="123e4567-e89b-12d3-a456-426614174000"
          open={true}
          onOpenChange={mockOnOpenChange}
        />,
        { wrapper: createWrapper() },
      )

      await waitFor(() => {
        expect(screen.getByText("Explore in Family Tree")).toBeInTheDocument()
      })

      const button = screen.getByText("Explore in Family Tree")
      fireEvent.click(button)

      expect(mockNavigate).toHaveBeenCalledWith({ to: "/family-tree" })
    })
  })
})
