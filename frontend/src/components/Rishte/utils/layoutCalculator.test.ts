import { describe, expect, it } from "vitest"
import type { GenerationInfo } from "../types"
import {
  calculatePositions,
  getGenerationY,
  isSameGeneration,
  isParentOf,
  getSpouseXOffset,
  getEdgeHandles,
  NODE_WIDTH,
  NODE_HEIGHT,
  HORIZONTAL_GAP,
  VERTICAL_GAP,
  SPOUSE_GAP,
} from "./layoutCalculator"

describe("layoutCalculator - Constants", () => {
  it("should have expected layout constants", () => {
    expect(NODE_WIDTH).toBe(180)
    expect(NODE_HEIGHT).toBe(200)
    expect(HORIZONTAL_GAP).toBe(100)
    expect(VERTICAL_GAP).toBe(150)
    expect(SPOUSE_GAP).toBe(50)
  })
})

describe("layoutCalculator - calculatePositions", () => {
  it("should return empty map for empty generations", () => {
    const generations = new Map<string, GenerationInfo>()
    const result = calculatePositions(generations)
    expect(result.size).toBe(0)
  })

  it("should calculate correct position for single node at origin", () => {
    const generations = new Map<string, GenerationInfo>([
      ["p1", { personId: "p1", generation: 0, xOffset: 0, isSpouse: false }],
    ])

    const result = calculatePositions(generations)

    expect(result.get("p1")).toEqual({ x: 0, y: 0 })
  })

  it("should calculate correct X position based on xOffset", () => {
    const generations = new Map<string, GenerationInfo>([
      ["p1", { personId: "p1", generation: 0, xOffset: 0, isSpouse: false }],
      ["p2", { personId: "p2", generation: 0, xOffset: 1, isSpouse: false }],
      ["p3", { personId: "p3", generation: 0, xOffset: 2, isSpouse: false }],
    ])

    const result = calculatePositions(generations)

    const expectedGap = NODE_WIDTH + HORIZONTAL_GAP // 180 + 100 = 280
    expect(result.get("p1")).toEqual({ x: 0, y: 0 })
    expect(result.get("p2")).toEqual({ x: expectedGap, y: 0 })
    expect(result.get("p3")).toEqual({ x: expectedGap * 2, y: 0 })
  })

  it("should calculate correct Y position based on generation", () => {
    const generations = new Map<string, GenerationInfo>([
      ["p1", { personId: "p1", generation: 0, xOffset: 0, isSpouse: false }],
      ["p2", { personId: "p2", generation: 1, xOffset: 0, isSpouse: false }],
      ["p3", { personId: "p3", generation: 2, xOffset: 0, isSpouse: false }],
    ])

    const result = calculatePositions(generations)

    const expectedGap = NODE_HEIGHT + VERTICAL_GAP // 200 + 150 = 350
    expect(result.get("p1")).toEqual({ x: 0, y: 0 })
    expect(result.get("p2")).toEqual({ x: 0, y: expectedGap })
    expect(result.get("p3")).toEqual({ x: 0, y: expectedGap * 2 })
  })

  it("should calculate correct positions for the example family tree", () => {
    // From the walkthrough:
    // father: (gen=0, xOffset=0)
    // sib1_self: (gen=1, xOffset=0)
    // self: (gen=1, xOffset=1)
    // spouse: (gen=1, xOffset=2)
    // sib1_son: (gen=2, xOffset=0)
    // son: (gen=2, xOffset=2)
    const generations = new Map<string, GenerationInfo>([
      ["father", { personId: "father", generation: 0, xOffset: 0, isSpouse: false }],
      ["sib1_self", { personId: "sib1_self", generation: 1, xOffset: 0, isSpouse: false }],
      ["self", { personId: "self", generation: 1, xOffset: 1, isSpouse: false }],
      ["spouse", { personId: "spouse", generation: 1, xOffset: 2, isSpouse: true, spouseOfId: "self" }],
      ["sib1_son", { personId: "sib1_son", generation: 2, xOffset: 0, isSpouse: false }],
      ["son", { personId: "son", generation: 2, xOffset: 2, isSpouse: false }],
    ])

    const result = calculatePositions(generations)

    const xGap = NODE_WIDTH + HORIZONTAL_GAP // 280
    const yGap = NODE_HEIGHT + VERTICAL_GAP // 350

    expect(result.get("father")).toEqual({ x: 0, y: 0 })
    expect(result.get("sib1_self")).toEqual({ x: 0, y: yGap })
    expect(result.get("self")).toEqual({ x: xGap, y: yGap })
    expect(result.get("spouse")).toEqual({ x: xGap * 2, y: yGap })
    expect(result.get("sib1_son")).toEqual({ x: 0, y: yGap * 2 })
    expect(result.get("son")).toEqual({ x: xGap * 2, y: yGap * 2 })
  })
})

describe("layoutCalculator - getGenerationY", () => {
  it("should return 0 for generation 0", () => {
    expect(getGenerationY(0)).toBe(0)
  })

  it("should return correct Y for positive generations", () => {
    const expectedGap = NODE_HEIGHT + VERTICAL_GAP
    expect(getGenerationY(1)).toBe(expectedGap)
    expect(getGenerationY(2)).toBe(expectedGap * 2)
    expect(getGenerationY(3)).toBe(expectedGap * 3)
  })
})

describe("layoutCalculator - isSameGeneration", () => {
  it("should return true for same Y coordinates", () => {
    expect(isSameGeneration(0, 0)).toBe(true)
    expect(isSameGeneration(350, 350)).toBe(true)
  })

  it("should return false for different Y coordinates", () => {
    expect(isSameGeneration(0, 350)).toBe(false)
    expect(isSameGeneration(350, 700)).toBe(false)
  })
})

describe("layoutCalculator - isParentOf", () => {
  it("should return true when parent Y is less than child Y", () => {
    expect(isParentOf(0, 350)).toBe(true)
    expect(isParentOf(350, 700)).toBe(true)
  })

  it("should return false when parent Y is greater than or equal to child Y", () => {
    expect(isParentOf(350, 0)).toBe(false)
    expect(isParentOf(350, 350)).toBe(false)
  })
})

describe("layoutCalculator - getSpouseXOffset", () => {
  it("should return NODE_WIDTH + SPOUSE_GAP", () => {
    expect(getSpouseXOffset()).toBe(NODE_WIDTH + SPOUSE_GAP)
  })
})

describe("layoutCalculator - getEdgeHandles", () => {
  describe("Same column (sx === tx)", () => {
    it("should return bottom→top when target is below source", () => {
      const result = getEdgeHandles({ x: 0, y: 0 }, { x: 0, y: 350 })
      expect(result).toEqual({ sourceHandle: "bottom", targetHandle: "top" })
    })

    it("should return top→bottom when target is above source", () => {
      const result = getEdgeHandles({ x: 0, y: 350 }, { x: 0, y: 0 })
      expect(result).toEqual({ sourceHandle: "top", targetHandle: "bottom" })
    })
  })

  describe("Same row (sy === ty)", () => {
    it("should return right→left when target is to the right", () => {
      const result = getEdgeHandles({ x: 0, y: 0 }, { x: 280, y: 0 })
      expect(result).toEqual({ sourceHandle: "right", targetHandle: "left" })
    })

    it("should return left→right when target is to the left", () => {
      const result = getEdgeHandles({ x: 280, y: 0 }, { x: 0, y: 0 })
      expect(result).toEqual({ sourceHandle: "left", targetHandle: "right" })
    })
  })

  describe("Diagonal positions", () => {
    it("should return bottom→top when target is south-east (below and right)", () => {
      const result = getEdgeHandles({ x: 0, y: 0 }, { x: 280, y: 350 })
      expect(result).toEqual({ sourceHandle: "bottom", targetHandle: "top" })
    })

    it("should return top→left when target is north-east (above and right)", () => {
      const result = getEdgeHandles({ x: 0, y: 350 }, { x: 280, y: 0 })
      expect(result).toEqual({ sourceHandle: "top", targetHandle: "left" })
    })

    it("should return bottom→top when target is south-west (below and left)", () => {
      const result = getEdgeHandles({ x: 280, y: 0 }, { x: 0, y: 350 })
      expect(result).toEqual({ sourceHandle: "bottom", targetHandle: "top" })
    })

    it("should return top→right when target is north-west (above and left)", () => {
      const result = getEdgeHandles({ x: 280, y: 350 }, { x: 0, y: 0 })
      expect(result).toEqual({ sourceHandle: "top", targetHandle: "right" })
    })
  })

  describe("Real-world edge cases from example", () => {
    it("should handle father→self edge (diagonal south-east)", () => {
      // father at (0, 0), self at (280, 350) - diagonal south-east
      const result = getEdgeHandles({ x: 0, y: 0 }, { x: 280, y: 350 })
      expect(result).toEqual({ sourceHandle: "bottom", targetHandle: "top" })
    })

    it("should handle self→spouse edge (same row, target right)", () => {
      // self at (280, 350), spouse at (560, 350)
      const result = getEdgeHandles({ x: 280, y: 350 }, { x: 560, y: 350 })
      expect(result).toEqual({ sourceHandle: "right", targetHandle: "left" })
    })

    it("should handle spouse→son edge (same column, target below)", () => {
      // spouse at (560, 350), son at (560, 700)
      const result = getEdgeHandles({ x: 560, y: 350 }, { x: 560, y: 700 })
      expect(result).toEqual({ sourceHandle: "bottom", targetHandle: "top" })
    })

    it("should handle sib1_self→father edge (same column, target above)", () => {
      // sib1_self at (0, 350), father at (0, 0)
      const result = getEdgeHandles({ x: 0, y: 350 }, { x: 0, y: 0 })
      expect(result).toEqual({ sourceHandle: "top", targetHandle: "bottom" })
    })
  })
})
