import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { type Position, RelationshipLines } from "./RelationshipLines"

/**
 * Unit tests for RelationshipLines component
 * Tests parent-child vertical lines, spouse horizontal lines, and line positioning calculations
 * Validates: Requirements 3.3, 4.2, 6.2
 */

describe("RelationshipLines - Unit Tests", () => {
  describe("Parent-Child Vertical Lines", () => {
    it("should render parent-child line with correct path", () => {
      const fromPosition: Position = { x: 100, y: 50 }
      const toPosition: Position = { x: 100, y: 200 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg).toBeTruthy()

      const path = container.querySelector("path")
      expect(path).toBeTruthy()
      expect(path?.getAttribute("d")).toBeTruthy()
    })

    it("should render parent-child line with solid stroke", () => {
      const fromPosition: Position = { x: 100, y: 50 }
      const toPosition: Position = { x: 100, y: 200 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const path = container.querySelector("path")
      expect(path?.getAttribute("stroke-width")).toBe("2")
      // Parent-child should not have stroke-dasharray (solid line)
      expect(path?.getAttribute("stroke-dasharray")).toBeNull()
    })

    it("should handle parent-child line with horizontal offset", () => {
      const fromPosition: Position = { x: 100, y: 50 }
      const toPosition: Position = { x: 200, y: 200 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const path = container.querySelector("path")
      expect(path).toBeTruthy()

      // Path should contain both x coordinates
      const pathData = path?.getAttribute("d") || ""
      expect(pathData).toContain("100")
      expect(pathData).toContain("200")
    })
  })

  describe("Spouse Horizontal Lines", () => {
    it("should render spouse line with correct path", () => {
      const fromPosition: Position = { x: 50, y: 100 }
      const toPosition: Position = { x: 200, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="spouse"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg).toBeTruthy()

      const path = container.querySelector("path")
      expect(path).toBeTruthy()
      expect(path?.getAttribute("d")).toBeTruthy()
    })

    it("should render spouse line with dashed stroke", () => {
      const fromPosition: Position = { x: 50, y: 100 }
      const toPosition: Position = { x: 200, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="spouse"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const path = container.querySelector("path")
      expect(path?.getAttribute("stroke-width")).toBe("2")
      // Spouse should have dashed line
      expect(path?.getAttribute("stroke-dasharray")).toBe("5,5")
    })

    it("should create horizontal line for spouse relationship", () => {
      const fromPosition: Position = { x: 50, y: 100 }
      const toPosition: Position = { x: 200, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="spouse"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const path = container.querySelector("path")
      const pathData = path?.getAttribute("d") || ""

      // Should be a simple horizontal line (M x1 y1 L x2 y2)
      expect(pathData).toContain("M 50 100")
      expect(pathData).toContain("L 200 100")
    })
  })

  describe("Sibling Lines", () => {
    it("should render sibling line with correct path", () => {
      const fromPosition: Position = { x: 50, y: 100 }
      const toPosition: Position = { x: 150, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="sibling"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg).toBeTruthy()

      const path = container.querySelector("path")
      expect(path).toBeTruthy()
      expect(path?.getAttribute("d")).toBeTruthy()
    })

    it("should render sibling line with dotted stroke", () => {
      const fromPosition: Position = { x: 50, y: 100 }
      const toPosition: Position = { x: 150, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="sibling"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const path = container.querySelector("path")
      expect(path?.getAttribute("stroke-width")).toBe("1")
      // Sibling should have dotted line
      expect(path?.getAttribute("stroke-dasharray")).toBe("3,3")
    })

    it("should create inverted U shape for sibling relationship", () => {
      const fromPosition: Position = { x: 50, y: 100 }
      const toPosition: Position = { x: 150, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="sibling"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const path = container.querySelector("path")
      const pathData = path?.getAttribute("d") || ""

      // Should go up, across, then down (inverted U)
      // Path should contain both x coordinates and a y coordinate above the siblings
      expect(pathData).toContain("50")
      expect(pathData).toContain("150")
      expect(pathData).toContain("70") // 100 - 30 = 70 (goes up 30px)
    })
  })

  describe("Line Positioning Calculations", () => {
    it("should calculate correct viewBox for vertical line", () => {
      const fromPosition: Position = { x: 100, y: 50 }
      const toPosition: Position = { x: 100, y: 200 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      const viewBox = svg?.getAttribute("viewBox")
      expect(viewBox).toBeTruthy()

      // ViewBox should encompass both positions with padding
      const [x, y, width, height] = viewBox!.split(" ").map(Number)
      expect(x).toBeLessThanOrEqual(100)
      expect(y).toBeLessThanOrEqual(50)
      expect(x + width).toBeGreaterThanOrEqual(100)
      expect(y + height).toBeGreaterThanOrEqual(200)
    })

    it("should calculate correct viewBox for horizontal line", () => {
      const fromPosition: Position = { x: 50, y: 100 }
      const toPosition: Position = { x: 200, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="spouse"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      const viewBox = svg?.getAttribute("viewBox")
      expect(viewBox).toBeTruthy()

      // ViewBox should encompass both positions with padding
      const [x, y, width, height] = viewBox!.split(" ").map(Number)
      expect(x).toBeLessThanOrEqual(50)
      expect(y).toBeLessThanOrEqual(100)
      expect(x + width).toBeGreaterThanOrEqual(200)
      expect(y + height).toBeGreaterThanOrEqual(100)
    })

    it("should calculate correct viewBox for diagonal line", () => {
      const fromPosition: Position = { x: 50, y: 50 }
      const toPosition: Position = { x: 200, y: 200 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      const viewBox = svg?.getAttribute("viewBox")
      expect(viewBox).toBeTruthy()

      // ViewBox should encompass both positions with padding
      const [x, y, width, height] = viewBox!.split(" ").map(Number)
      expect(x).toBeLessThanOrEqual(50)
      expect(y).toBeLessThanOrEqual(50)
      expect(x + width).toBeGreaterThanOrEqual(200)
      expect(y + height).toBeGreaterThanOrEqual(200)
    })

    it("should handle reversed positions (to before from)", () => {
      const fromPosition: Position = { x: 200, y: 200 }
      const toPosition: Position = { x: 50, y: 50 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      const viewBox = svg?.getAttribute("viewBox")
      expect(viewBox).toBeTruthy()

      // ViewBox should still encompass both positions correctly
      const [x, y, width, height] = viewBox!.split(" ").map(Number)
      expect(x).toBeLessThanOrEqual(50)
      expect(y).toBeLessThanOrEqual(50)
      expect(x + width).toBeGreaterThanOrEqual(200)
      expect(y + height).toBeGreaterThanOrEqual(200)
    })

    it("should apply custom className", () => {
      const fromPosition: Position = { x: 100, y: 50 }
      const toPosition: Position = { x: 100, y: 200 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
          className="custom-class"
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg?.getAttribute("class")).toContain("custom-class")
    })

    it("should position SVG absolutely", () => {
      const fromPosition: Position = { x: 100, y: 50 }
      const toPosition: Position = { x: 100, y: 200 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg?.getAttribute("class")).toContain("absolute")
      expect(svg?.getAttribute("class")).toContain("pointer-events-none")
    })
  })

  describe("Edge Cases", () => {
    it("should handle zero-length line (same from and to position)", () => {
      const position: Position = { x: 100, y: 100 }

      const { container } = render(
        <RelationshipLines
          type="spouse"
          fromPosition={position}
          toPosition={position}
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg).toBeTruthy()

      const path = container.querySelector("path")
      expect(path).toBeTruthy()
    })

    it("should handle negative coordinates", () => {
      const fromPosition: Position = { x: -50, y: -50 }
      const toPosition: Position = { x: 50, y: 50 }

      const { container } = render(
        <RelationshipLines
          type="parent-child"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg).toBeTruthy()

      const path = container.querySelector("path")
      expect(path).toBeTruthy()
    })

    it("should handle very large coordinates", () => {
      const fromPosition: Position = { x: 10000, y: 10000 }
      const toPosition: Position = { x: 20000, y: 20000 }

      const { container } = render(
        <RelationshipLines
          type="sibling"
          fromPosition={fromPosition}
          toPosition={toPosition}
        />,
      )

      const svg = container.querySelector("svg")
      expect(svg).toBeTruthy()

      const path = container.querySelector("path")
      expect(path).toBeTruthy()
    })
  })
})
