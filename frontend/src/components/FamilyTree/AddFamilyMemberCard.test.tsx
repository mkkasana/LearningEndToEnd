import { fireEvent, render, screen } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import {
  AddFamilyMemberCard,
  type AddFamilyMemberCardVariant,
} from "./AddFamilyMemberCard"

describe("AddFamilyMemberCard - Unit Tests", () => {
  const variants: AddFamilyMemberCardVariant[] = ["parent", "center", "child"]

  describe("Plus Icon Rendering", () => {
    it("should render Plus icon", () => {
      render(<AddFamilyMemberCard variant="parent" onClick={() => {}} />)

      // The Plus icon from lucide-react renders as an SVG
      const card = screen.getByTestId("add-family-member-card")
      const svg = card.querySelector("svg")
      expect(svg).toBeTruthy()
    })

    it.each(variants)("should render Plus icon for %s variant", (variant) => {
      render(<AddFamilyMemberCard variant={variant} onClick={() => {}} />)

      const card = screen.getByTestId("add-family-member-card")
      const svg = card.querySelector("svg")
      expect(svg).toBeTruthy()
    })
  })

  describe("Click Handler", () => {
    it("should call onClick when card is clicked", () => {
      const handleClick = vi.fn()
      render(<AddFamilyMemberCard variant="parent" onClick={handleClick} />)

      const card = screen.getByRole("button")
      fireEvent.click(card)

      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it("should call onClick when Enter key is pressed", () => {
      const handleClick = vi.fn()
      render(<AddFamilyMemberCard variant="center" onClick={handleClick} />)

      const card = screen.getByRole("button")
      fireEvent.keyDown(card, { key: "Enter" })

      expect(handleClick).toHaveBeenCalledTimes(1)
    })

    it("should call onClick when Space key is pressed", () => {
      const handleClick = vi.fn()
      render(<AddFamilyMemberCard variant="child" onClick={handleClick} />)

      const card = screen.getByRole("button")
      fireEvent.keyDown(card, { key: " " })

      expect(handleClick).toHaveBeenCalledTimes(1)
    })
  })

  describe("Variant Styling", () => {
    it("should render parent variant with correct dimensions", () => {
      const { container } = render(
        <AddFamilyMemberCard variant="parent" onClick={() => {}} />,
      )

      const card = container.querySelector('[data-slot="card"]')
      expect(card?.className).toContain("min-w-[140px]")
      expect(card?.className).toContain("min-h-[160px]")
    })

    it("should render center variant with correct dimensions", () => {
      const { container } = render(
        <AddFamilyMemberCard variant="center" onClick={() => {}} />,
      )

      const card = container.querySelector('[data-slot="card"]')
      expect(card?.className).toContain("min-w-[140px]")
      expect(card?.className).toContain("min-h-[160px]")
    })

    it("should render child variant with correct dimensions", () => {
      const { container } = render(
        <AddFamilyMemberCard variant="child" onClick={() => {}} />,
      )

      const card = container.querySelector('[data-slot="card"]')
      expect(card?.className).toContain("min-w-[130px]")
      expect(card?.className).toContain("min-h-[150px]")
    })

    it.each(
      variants,
    )("should have dashed border styling for %s variant", (variant) => {
      const { container } = render(
        <AddFamilyMemberCard variant={variant} onClick={() => {}} />,
      )

      const card = container.querySelector('[data-slot="card"]')
      expect(card?.className).toContain("border-dashed")
    })

    it.each(
      variants,
    )("should have muted background for %s variant", (variant) => {
      const { container } = render(
        <AddFamilyMemberCard variant={variant} onClick={() => {}} />,
      )

      const card = container.querySelector('[data-slot="card"]')
      expect(card?.className).toContain("bg-muted/20")
    })

    it.each(
      variants,
    )("should have cursor-pointer for %s variant", (variant) => {
      const { container } = render(
        <AddFamilyMemberCard variant={variant} onClick={() => {}} />,
      )

      const card = container.querySelector('[data-slot="card"]')
      expect(card?.className).toContain("cursor-pointer")
    })

    it.each(variants)("should have hover effects for %s variant", (variant) => {
      const { container } = render(
        <AddFamilyMemberCard variant={variant} onClick={() => {}} />,
      )

      const card = container.querySelector('[data-slot="card"]')
      expect(card?.className).toContain("hover:border-primary/50")
      expect(card?.className).toContain("hover:scale-[1.02]")
    })
  })

  describe("Accessibility", () => {
    it("should have role button", () => {
      render(<AddFamilyMemberCard variant="parent" onClick={() => {}} />)

      const card = screen.getByRole("button")
      expect(card).toBeTruthy()
    })

    it("should be focusable with tabIndex 0", () => {
      render(<AddFamilyMemberCard variant="center" onClick={() => {}} />)

      const card = screen.getByRole("button")
      expect(card.getAttribute("tabindex")).toBe("0")
    })

    it("should have appropriate aria-label for parent variant", () => {
      render(<AddFamilyMemberCard variant="parent" onClick={() => {}} />)

      const card = screen.getByRole("button")
      expect(card.getAttribute("aria-label")).toContain("parents")
    })

    it("should have appropriate aria-label for center variant", () => {
      render(<AddFamilyMemberCard variant="center" onClick={() => {}} />)

      const card = screen.getByRole("button")
      expect(card.getAttribute("aria-label")).toContain("siblings and spouses")
    })

    it("should have appropriate aria-label for child variant", () => {
      render(<AddFamilyMemberCard variant="child" onClick={() => {}} />)

      const card = screen.getByRole("button")
      expect(card.getAttribute("aria-label")).toContain("children")
    })
  })

  describe("Circle Element", () => {
    it("should render a centered circle containing the Plus icon", () => {
      const { container } = render(
        <AddFamilyMemberCard variant="parent" onClick={() => {}} />,
      )

      const circle = container.querySelector(".rounded-full")
      expect(circle).toBeTruthy()
      expect(circle?.className).toContain("border-dashed")
    })
  })
})
