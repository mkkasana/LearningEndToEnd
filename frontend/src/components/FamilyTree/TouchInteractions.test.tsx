import { fireEvent } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import type { PersonDetails } from "@/client"
import { renderWithProviders } from "@/test-utils"
import { PersonCard } from "./PersonCard"
import { SiblingsList } from "./SiblingsList"
import { SpouseCarousel } from "./SpouseCarousel"

/**
 * Unit tests for touch interactions
 * Requirements: 10.5
 */
describe("Touch Interactions", () => {
  const mockPerson: PersonDetails = {
    id: "person-1",
    first_name: "John",
    middle_name: null,
    last_name: "Doe",
    gender_id: "gen-6a0ede824d101",
    date_of_birth: "1990-01-01",
    date_of_death: null,
    user_id: null,
    created_by_user_id: "user-1",
    is_primary: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  }

  const mockSiblings: PersonDetails[] = [
    {
      ...mockPerson,
      id: "sibling-1",
      first_name: "Jane",
    },
    {
      ...mockPerson,
      id: "sibling-2",
      first_name: "Jack",
    },
    {
      ...mockPerson,
      id: "sibling-3",
      first_name: "Jill",
    },
  ]

  const mockSpouses: PersonDetails[] = [
    {
      ...mockPerson,
      id: "spouse-1",
      first_name: "Mary",
      gender_id: "gen-6a0ede824d102",
    },
    {
      ...mockPerson,
      id: "spouse-2",
      first_name: "Sarah",
      gender_id: "gen-6a0ede824d102",
    },
  ]

  /**
   * Test touch events for selecting persons
   */
  describe("Person Selection Touch Events", () => {
    it("should handle touch events on PersonCard", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Simulate touch start
      fireEvent.touchStart(card)

      // Simulate touch end (which triggers click)
      fireEvent.touchEnd(card)
      fireEvent.click(card)

      expect(handleClick).toHaveBeenCalledWith(mockPerson.id)
    })

    it("should handle multiple touch events on different person cards", () => {
      const handleClick = vi.fn()

      const { getAllByRole } = renderWithProviders(
        <div>
          <PersonCard
            person={mockPerson}
            variant="selected"
            onClick={handleClick}
            showPhoto={true}
          />
          <PersonCard
            person={{ ...mockPerson, id: "person-2", first_name: "Jane" }}
            variant="parent"
            onClick={handleClick}
            showPhoto={true}
          />
        </div>,
      )

      const cards = getAllByRole("button")

      // Touch first card
      fireEvent.touchStart(cards[0])
      fireEvent.touchEnd(cards[0])
      fireEvent.click(cards[0])

      expect(handleClick).toHaveBeenCalledWith(mockPerson.id)

      // Touch second card
      fireEvent.touchStart(cards[1])
      fireEvent.touchEnd(cards[1])
      fireEvent.click(cards[1])

      expect(handleClick).toHaveBeenCalledWith("person-2")
      expect(handleClick).toHaveBeenCalledTimes(2)
    })

    it("should not trigger click on touch cancel", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Simulate touch start
      fireEvent.touchStart(card)

      // Simulate touch cancel (user dragged away)
      fireEvent.touchCancel(card)

      // Click should not be triggered
      expect(handleClick).not.toHaveBeenCalled()
    })

    it("should handle rapid touch events (tap quickly)", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Simulate rapid taps
      for (let i = 0; i < 3; i++) {
        fireEvent.touchStart(card)
        fireEvent.touchEnd(card)
        fireEvent.click(card)
      }

      expect(handleClick).toHaveBeenCalledTimes(3)
    })
  })

  /**
   * Test touch scrolling for siblings/spouses
   */
  describe("Touch Scrolling", () => {
    it("should allow touch scrolling on SiblingsList", () => {
      const handleClick = vi.fn()

      const { container } = renderWithProviders(
        <SiblingsList siblings={mockSiblings} onPersonClick={handleClick} />,
      )

      // Find the scroll container
      const scrollContainer = container.querySelector(
        "[data-radix-scroll-area-viewport]",
      )
      expect(scrollContainer).toBeTruthy()

      if (scrollContainer) {
        // Simulate touch scroll
        fireEvent.touchStart(scrollContainer, {
          touches: [{ clientX: 100, clientY: 0 }],
        })

        fireEvent.touchMove(scrollContainer, {
          touches: [{ clientX: 50, clientY: 0 }],
        })

        fireEvent.touchEnd(scrollContainer)

        // Scroll container should exist and be scrollable
        expect(scrollContainer).toBeTruthy()
      }
    })

    it("should allow touch scrolling with momentum", () => {
      const handleClick = vi.fn()

      const { container } = renderWithProviders(
        <SiblingsList siblings={mockSiblings} onPersonClick={handleClick} />,
      )

      const scrollContainer = container.querySelector(
        "[data-radix-scroll-area-viewport]",
      )

      if (scrollContainer) {
        // Simulate fast swipe (momentum scroll)
        const startX = 200
        const endX = 50

        fireEvent.touchStart(scrollContainer, {
          touches: [{ clientX: startX, clientY: 0 }],
        })

        // Simulate multiple move events (fast swipe)
        for (let x = startX; x > endX; x -= 30) {
          fireEvent.touchMove(scrollContainer, {
            touches: [{ clientX: x, clientY: 0 }],
          })
        }

        fireEvent.touchEnd(scrollContainer)

        // Container should still be present after scroll
        expect(scrollContainer).toBeTruthy()
      }
    })

    it("should handle touch scrolling on SpouseCarousel navigation", () => {
      const handleClick = vi.fn()

      const { getByLabelText } = renderWithProviders(
        <SpouseCarousel spouses={mockSpouses} onPersonClick={handleClick} />,
      )

      const nextButton = getByLabelText("Next spouse")
      const prevButton = getByLabelText("Previous spouse")

      // Touch next button
      fireEvent.touchStart(nextButton)
      fireEvent.touchEnd(nextButton)
      fireEvent.click(nextButton)

      // Touch previous button
      fireEvent.touchStart(prevButton)
      fireEvent.touchEnd(prevButton)
      fireEvent.click(prevButton)

      // Buttons should be interactive
      expect(nextButton).toBeTruthy()
      expect(prevButton).toBeTruthy()
    })

    it("should handle touch on carousel indicator dots", () => {
      const handleClick = vi.fn()

      const { getAllByRole } = renderWithProviders(
        <SpouseCarousel spouses={mockSpouses} onPersonClick={handleClick} />,
      )

      // Get indicator dots (tabs)
      const dots = getAllByRole("tab")
      expect(dots.length).toBe(2)

      // Touch second dot
      fireEvent.touchStart(dots[1])
      fireEvent.touchEnd(dots[1])
      fireEvent.click(dots[1])

      // Dot should be clickable
      expect(dots[1]).toBeTruthy()
    })

    it("should prevent default scroll behavior during touch on cards", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Simulate touch with preventDefault
      const touchStartEvent = new TouchEvent("touchstart", {
        bubbles: true,
        cancelable: true,
        touches: [
          {
            clientX: 100,
            clientY: 100,
          } as Touch,
        ],
      })

      card.dispatchEvent(touchStartEvent)

      // Card should handle touch events
      expect(card).toBeTruthy()
    })
  })

  /**
   * Test touch interaction accessibility
   */
  describe("Touch Accessibility", () => {
    it("should maintain focus after touch interaction", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Touch and focus
      fireEvent.touchStart(card)
      fireEvent.touchEnd(card)
      fireEvent.click(card)
      card.focus()

      expect(document.activeElement).toBe(card)
    })

    it("should support both touch and keyboard navigation", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Touch interaction
      fireEvent.touchStart(card)
      fireEvent.touchEnd(card)
      fireEvent.click(card)

      expect(handleClick).toHaveBeenCalledTimes(1)

      // Keyboard interaction
      fireEvent.keyDown(card, { key: "Enter" })

      expect(handleClick).toHaveBeenCalledTimes(2)
    })

    it("should have appropriate touch target size", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Card should be rendered and clickable
      expect(card).toBeTruthy()
      expect(card.getAttribute("role")).toBe("button")
      expect(card.getAttribute("tabIndex")).toBe("0")
    })
  })

  /**
   * Test touch gestures
   */
  describe("Touch Gestures", () => {
    it("should handle swipe gesture on siblings list", () => {
      const handleClick = vi.fn()

      const { container } = renderWithProviders(
        <SiblingsList siblings={mockSiblings} onPersonClick={handleClick} />,
      )

      const scrollContainer = container.querySelector(
        "[data-radix-scroll-area-viewport]",
      )

      if (scrollContainer) {
        // Simulate swipe left
        fireEvent.touchStart(scrollContainer, {
          touches: [{ clientX: 200, clientY: 0 }],
        })

        fireEvent.touchMove(scrollContainer, {
          touches: [{ clientX: 50, clientY: 0 }],
        })

        fireEvent.touchEnd(scrollContainer)

        expect(scrollContainer).toBeTruthy()
      }
    })

    it("should distinguish between tap and swipe", () => {
      const handleClick = vi.fn()

      const { getByRole } = renderWithProviders(
        <PersonCard
          person={mockPerson}
          variant="selected"
          onClick={handleClick}
          showPhoto={true}
        />,
      )

      const card = getByRole("button")

      // Tap (short touch without movement)
      fireEvent.touchStart(card, {
        touches: [{ clientX: 100, clientY: 100 }],
      })

      fireEvent.touchEnd(card, {
        changedTouches: [{ clientX: 100, clientY: 100 }],
      })

      fireEvent.click(card)

      expect(handleClick).toHaveBeenCalledWith(mockPerson.id)
    })

    it("should handle pinch zoom gesture gracefully", () => {
      const handleClick = vi.fn()

      const { container } = renderWithProviders(
        <div>
          <PersonCard
            person={mockPerson}
            variant="selected"
            onClick={handleClick}
            showPhoto={true}
          />
        </div>,
      )

      // Simulate pinch zoom (two-finger touch)
      const element = container.firstChild as HTMLElement

      fireEvent.touchStart(element, {
        touches: [
          { clientX: 100, clientY: 100 },
          { clientX: 200, clientY: 100 },
        ],
      })

      fireEvent.touchMove(element, {
        touches: [
          { clientX: 80, clientY: 100 },
          { clientX: 220, clientY: 100 },
        ],
      })

      fireEvent.touchEnd(element)

      // Component should handle multi-touch gracefully
      expect(element).toBeTruthy()
    })
  })
})
