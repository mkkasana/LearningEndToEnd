import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { RowConnector } from "./RowConnector"

/**
 * Unit tests for RowConnector component
 * Tests simple downward arrow visual indicator between rows
 * Validates: Requirements 3.3, 6.2
 */

describe("RowConnector - Unit Tests", () => {
  it("should render connector with downward arrow", () => {
    const { container } = render(<RowConnector />)

    // Should have the main container
    const connector = container.querySelector("div")
    expect(connector).toBeTruthy()

    // Should contain the downward arrow character
    expect(connector?.textContent).toContain("↓")
  })

  it("should apply custom className", () => {
    const { container } = render(<RowConnector className="custom-class" />)

    const connector = container.querySelector("div")
    expect(connector?.className).toContain("custom-class")
  })

  it("should have aria-hidden attribute", () => {
    const { container } = render(<RowConnector />)

    const connector = container.querySelector("div")
    expect(connector?.getAttribute("aria-hidden")).toBe("true")
  })

  it("should have max height of 30px", () => {
    const { container } = render(<RowConnector />)

    const connector = container.querySelector("div")
    const className = connector?.className || ""

    // Should have h-[30px] class
    expect(className).toContain("h-[30px]")
  })

  it("should have muted styling", () => {
    const { container } = render(<RowConnector />)

    const connector = container.querySelector("div")
    const className = connector?.className || ""

    // Should have muted foreground color
    expect(className).toMatch(/text-muted-foreground/)
  })
})
