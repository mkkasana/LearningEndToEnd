/**
 * Property-Based Tests for MatchRelationshipEdge Component
 * Feature: partner-match-visualizer
 * 
 * Property 7: Edge Styling Correctness
 * Validates: Requirements 7.1, 7.2, 7.3, 7.5
 * 
 * Note: EdgeLabelRenderer uses a portal that requires a full React Flow setup.
 * These tests focus on the path styling which can be tested in isolation.
 */

import * as fc from "fast-check"
import { describe, expect, it, afterEach } from "vitest"
import { render, cleanup } from "@testing-library/react"
import { ReactFlowProvider, Position } from "@xyflow/react"
import { MatchRelationshipEdge } from "./MatchRelationshipEdge"
import type { MatchRelationshipEdgeData } from "./types"

// Cleanup after each test to prevent multiple elements
afterEach(() => {
  cleanup()
})

// Helper to wrap component with ReactFlowProvider
function renderEdge(data: MatchRelationshipEdgeData) {
  const edgeProps = {
    id: "test-edge",
    source: "source-node",
    target: "target-node",
    sourceX: 0,
    sourceY: 0,
    targetX: 100,
    targetY: 100,
    sourcePosition: Position.Bottom,
    targetPosition: Position.Top,
    data,
    markerEnd: "url(#arrow)",
  }

  return render(
    <ReactFlowProvider>
      <svg>
        <MatchRelationshipEdge {...edgeProps} />
      </svg>
    </ReactFlowProvider>
  )
}

// Helper to get SVG path className (handles SVGAnimatedString)
function getPathClassName(path: Element | null): string {
  if (!path) return ""
  const svgPath = path as SVGPathElement
  return svgPath.className?.baseVal ?? ""
}

// ============================================
// Property-Based Tests
// ============================================

describe("MatchRelationshipEdge - Property-Based Tests", () => {
  describe("Property 7: Edge Styling Correctness", () => {
    const spouseRelationshipArb = fc.oneof(
      fc.constant("Spouse"),
      fc.constant("Husband"),
      fc.constant("Wife")
    )
    
    const parentChildRelationshipArb = fc.oneof(
      fc.constant("Son"),
      fc.constant("Daughter"),
      fc.constant("Father"),
      fc.constant("Mother")
    )

    it("should apply purple stroke class for spouse edges", () => {
      fc.assert(
        fc.property(
          fc.record({
            relationship: spouseRelationshipArb,
            isSpouseEdge: fc.constant(true),
          }),
          (data) => {
            const { container, unmount } = renderEdge(data)
            const path = container.querySelector("path.react-flow__edge-path")
            expect(getPathClassName(path)).toContain("purple")
            unmount()
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should apply dashed stroke for spouse edges", () => {
      fc.assert(
        fc.property(
          fc.record({
            relationship: spouseRelationshipArb,
            isSpouseEdge: fc.constant(true),
          }),
          (data) => {
            const { container, unmount } = renderEdge(data)
            const path = container.querySelector("path.react-flow__edge-path") as HTMLElement
            expect(path?.style.strokeDasharray).toBe("5,5")
            unmount()
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should apply thicker stroke width for spouse edges", () => {
      fc.assert(
        fc.property(
          fc.record({
            relationship: spouseRelationshipArb,
            isSpouseEdge: fc.constant(true),
          }),
          (data) => {
            const { container, unmount } = renderEdge(data)
            const path = container.querySelector("path.react-flow__edge-path") as HTMLElement
            expect(path?.style.strokeWidth).toBe("3")
            unmount()
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should NOT apply purple stroke class for non-spouse edges", () => {
      fc.assert(
        fc.property(
          fc.record({
            relationship: parentChildRelationshipArb,
            isSpouseEdge: fc.constant(false),
          }),
          (data) => {
            const { container, unmount } = renderEdge(data)
            const path = container.querySelector("path.react-flow__edge-path")
            expect(getPathClassName(path)).not.toContain("purple")
            unmount()
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should NOT apply dashed stroke for non-spouse edges", () => {
      fc.assert(
        fc.property(
          fc.record({
            relationship: parentChildRelationshipArb,
            isSpouseEdge: fc.constant(false),
          }),
          (data) => {
            const { container, unmount } = renderEdge(data)
            const path = container.querySelector("path.react-flow__edge-path") as HTMLElement
            expect(path?.style.strokeDasharray).toBeFalsy()
            unmount()
          }
        ),
        { numRuns: 100 }
      )
    })

    it("should apply normal stroke width for non-spouse edges", () => {
      fc.assert(
        fc.property(
          fc.record({
            relationship: parentChildRelationshipArb,
            isSpouseEdge: fc.constant(false),
          }),
          (data) => {
            const { container, unmount } = renderEdge(data)
            const path = container.querySelector("path.react-flow__edge-path") as HTMLElement
            expect(path?.style.strokeWidth).toBe("2")
            unmount()
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

describe("MatchRelationshipEdge - Unit Tests", () => {
  it("should render spouse edge with purple stroke and dashed line", () => {
    const { container } = renderEdge({
      relationship: "Spouse",
      isSpouseEdge: true,
    })
    
    const path = container.querySelector("path.react-flow__edge-path") as SVGPathElement
    expect(getPathClassName(path)).toContain("purple")
    expect(path?.style.strokeDasharray).toBe("5,5")
    expect(path?.style.strokeWidth).toBe("3")
  })

  it("should render parent-child edge without purple stroke or dashed line", () => {
    const { container } = renderEdge({
      relationship: "Father",
      isSpouseEdge: false,
    })
    
    const path = container.querySelector("path.react-flow__edge-path") as SVGPathElement
    expect(getPathClassName(path)).not.toContain("purple")
    expect(path?.style.strokeDasharray).toBeFalsy()
    expect(path?.style.strokeWidth).toBe("2")
  })

  it("should render Husband edge with spouse styling", () => {
    const { container } = renderEdge({
      relationship: "Husband",
      isSpouseEdge: true,
    })
    
    const path = container.querySelector("path.react-flow__edge-path") as SVGPathElement
    expect(getPathClassName(path)).toContain("purple")
    expect(path?.style.strokeDasharray).toBe("5,5")
  })

  it("should render Wife edge with spouse styling", () => {
    const { container } = renderEdge({
      relationship: "Wife",
      isSpouseEdge: true,
    })
    
    const path = container.querySelector("path.react-flow__edge-path") as SVGPathElement
    expect(getPathClassName(path)).toContain("purple")
    expect(path?.style.strokeDasharray).toBe("5,5")
  })

  it("should render Son edge without spouse styling", () => {
    const { container } = renderEdge({
      relationship: "Son",
      isSpouseEdge: false,
    })
    
    const path = container.querySelector("path.react-flow__edge-path") as SVGPathElement
    expect(getPathClassName(path)).not.toContain("purple")
    expect(path?.style.strokeDasharray).toBeFalsy()
  })

  it("should render Daughter edge without spouse styling", () => {
    const { container } = renderEdge({
      relationship: "Daughter",
      isSpouseEdge: false,
    })
    
    const path = container.querySelector("path.react-flow__edge-path") as SVGPathElement
    expect(getPathClassName(path)).not.toContain("purple")
    expect(path?.style.strokeDasharray).toBeFalsy()
  })

  it("should render Mother edge without spouse styling", () => {
    const { container } = renderEdge({
      relationship: "Mother",
      isSpouseEdge: false,
    })
    
    const path = container.querySelector("path.react-flow__edge-path") as SVGPathElement
    expect(getPathClassName(path)).not.toContain("purple")
    expect(path?.style.strokeDasharray).toBeFalsy()
  })

  it("should include marker end for arrow", () => {
    const { container } = renderEdge({
      relationship: "Father",
      isSpouseEdge: false,
    })
    
    const path = container.querySelector("path.react-flow__edge-path")
    expect(path?.getAttribute("marker-end")).toBe("url(#arrow)")
  })
})
