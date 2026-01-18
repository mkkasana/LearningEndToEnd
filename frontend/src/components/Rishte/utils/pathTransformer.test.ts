import { describe, expect, it } from "vitest"
import type { PersonNode as ApiPersonNode } from "@/client"
import {
  buildPathArray,
  assignGenerations,
  isChildRelationship,
  isParentRelationship,
  isSpouseRelationship,
  generatePathSummary,
  getPersonCount,
} from "./pathTransformer"

// Helper to create a mock PersonNode
function createMockPerson(
  id: string,
  firstName: string,
  fromPersonId: string | null,
  fromRelationship: string | null,
  toPersonId: string | null,
  toRelationship: string | null
): ApiPersonNode {
  return {
    person_id: id,
    first_name: firstName,
    last_name: `${firstName}L`,
    birth_year: 1990,
    death_year: null,
    address: "Test Address",
    religion: "Test Religion",
    from_person: fromPersonId
      ? { person_id: fromPersonId, relationship: fromRelationship! }
      : null,
    to_person: toPersonId
      ? { person_id: toPersonId, relationship: toRelationship! }
      : null,
  }
}

describe("pathTransformer - Relationship Type Helpers", () => {
  describe("isChildRelationship", () => {
    it("should return true for Son", () => {
      expect(isChildRelationship("Son")).toBe(true)
    })

    it("should return true for Daughter", () => {
      expect(isChildRelationship("Daughter")).toBe(true)
    })

    it("should return false for Father", () => {
      expect(isChildRelationship("Father")).toBe(false)
    })

    it("should return false for Mother", () => {
      expect(isChildRelationship("Mother")).toBe(false)
    })

    it("should return false for Spouse", () => {
      expect(isChildRelationship("Spouse")).toBe(false)
    })
  })

  describe("isParentRelationship", () => {
    it("should return true for Father", () => {
      expect(isParentRelationship("Father")).toBe(true)
    })

    it("should return true for Mother", () => {
      expect(isParentRelationship("Mother")).toBe(true)
    })

    it("should return false for Son", () => {
      expect(isParentRelationship("Son")).toBe(false)
    })

    it("should return false for Daughter", () => {
      expect(isParentRelationship("Daughter")).toBe(false)
    })

    it("should return false for Spouse", () => {
      expect(isParentRelationship("Spouse")).toBe(false)
    })
  })

  describe("isSpouseRelationship", () => {
    it("should return true for Spouse", () => {
      expect(isSpouseRelationship("Spouse")).toBe(true)
    })

    it("should return true for Husband", () => {
      expect(isSpouseRelationship("Husband")).toBe(true)
    })

    it("should return true for Wife", () => {
      expect(isSpouseRelationship("Wife")).toBe(true)
    })

    it("should return false for Father", () => {
      expect(isSpouseRelationship("Father")).toBe(false)
    })

    it("should return false for Son", () => {
      expect(isSpouseRelationship("Son")).toBe(false)
    })
  })
})

describe("pathTransformer - buildPathArray", () => {
  it("should return empty array when personAId not found in graph", () => {
    const graph: Record<string, ApiPersonNode> = {}
    const result = buildPathArray(graph, "non-existent-id")
    expect(result).toEqual([])
  })

  it("should return single node when path has only one person", () => {
    const person = createMockPerson("p1", "Person1", null, null, null, null)
    const graph: Record<string, ApiPersonNode> = { p1: person }

    const result = buildPathArray(graph, "p1")

    expect(result).toHaveLength(1)
    expect(result[0].person_id).toBe("p1")
  })

  it("should build correct path following to_person pointers", () => {
    const p1 = createMockPerson("p1", "Person1", null, null, "p2", "Father")
    const p2 = createMockPerson("p2", "Person2", "p1", "Son", "p3", "Spouse")
    const p3 = createMockPerson("p3", "Person3", "p2", "Spouse", null, null)

    const graph: Record<string, ApiPersonNode> = { p1, p2, p3 }

    const result = buildPathArray(graph, "p1")

    expect(result).toHaveLength(3)
    expect(result[0].person_id).toBe("p1")
    expect(result[1].person_id).toBe("p2")
    expect(result[2].person_id).toBe("p3")
  })

  it("should handle the example path: sib1_son → sib1_self → father → self → spouse → son", () => {
    // Create the example graph from the user's test case
    const graph: Record<string, ApiPersonNode> = {
      "sib1_son": createMockPerson("sib1_son", "sib1_son", null, null, "sib1_self", "Mother"),
      "sib1_self": createMockPerson("sib1_self", "sib1_self", "sib1_son", "Son", "father", "Father"),
      "father": createMockPerson("father", "father", "sib1_self", "Daughter", "self", "Son"),
      "self": createMockPerson("self", "self", "father", "Father", "spouse", "Spouse"),
      "spouse": createMockPerson("spouse", "spouse", "self", "Spouse", "son", "Son"),
      "son": createMockPerson("son", "son", "spouse", "Mother", null, null),
    }

    const result = buildPathArray(graph, "sib1_son")

    expect(result).toHaveLength(6)
    expect(result.map(p => p.first_name)).toEqual([
      "sib1_son", "sib1_self", "father", "self", "spouse", "son"
    ])
  })

  it("should prevent infinite loops with circular references", () => {
    // Create a circular graph (shouldn't happen in practice, but good to test)
    const p1 = createMockPerson("p1", "Person1", null, null, "p2", "Father")
    const p2 = createMockPerson("p2", "Person2", "p1", "Son", "p1", "Son") // Points back to p1

    const graph: Record<string, ApiPersonNode> = { p1, p2 }

    const result = buildPathArray(graph, "p1")

    // Should stop at p2 since p1 was already visited
    expect(result).toHaveLength(2)
    expect(result[0].person_id).toBe("p1")
    expect(result[1].person_id).toBe("p2")
  })
})

describe("pathTransformer - assignGenerations", () => {
  it("should assign generation 0 to single person path", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("p1", "Person1", null, null, null, null)
    ]

    const result = assignGenerations(path)

    expect(result.get("p1")?.generation).toBe(0)
    expect(result.get("p1")?.xOffset).toBe(0)
  })

  it("should decrease generation when going UP (child → parent via Son/Daughter)", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("child", "Child", null, null, "parent", "Father"),
      createMockPerson("parent", "Parent", "child", "Son", null, null),
    ]

    const result = assignGenerations(path)

    // After normalization, parent (older) should be gen 0, child should be gen 1
    expect(result.get("parent")?.generation).toBe(0)
    expect(result.get("child")?.generation).toBe(1)
  })

  it("should increase generation when going DOWN (parent → child via Father/Mother)", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("parent", "Parent", null, null, "child", "Son"),
      createMockPerson("child", "Child", "parent", "Father", null, null),
    ]

    const result = assignGenerations(path)

    // Parent is gen 0, child is gen 1
    expect(result.get("parent")?.generation).toBe(0)
    expect(result.get("child")?.generation).toBe(1)
  })

  it("should keep same generation for spouse relationships", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("person", "Person", null, null, "spouse", "Spouse"),
      createMockPerson("spouse", "Spouse", "person", "Spouse", null, null),
    ]

    const result = assignGenerations(path)

    expect(result.get("person")?.generation).toBe(result.get("spouse")?.generation)
    expect(result.get("spouse")?.isSpouse).toBe(true)
    expect(result.get("spouse")?.spouseOfId).toBe("person")
  })

  it("should correctly assign generations for complex path: sib1_son → sib1_self → father → self → spouse → son", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("sib1_son", "sib1_son", null, null, "sib1_self", "Mother"),
      createMockPerson("sib1_self", "sib1_self", "sib1_son", "Son", "father", "Father"),
      createMockPerson("father", "father", "sib1_self", "Daughter", "self", "Son"),
      createMockPerson("self", "self", "father", "Father", "spouse", "Spouse"),
      createMockPerson("spouse", "spouse", "self", "Spouse", "son", "Son"),
      createMockPerson("son", "son", "spouse", "Mother", null, null),
    ]

    const result = assignGenerations(path)

    // Expected generations after normalization:
    // father: 0 (oldest)
    // sib1_self, self, spouse: 1 (middle)
    // sib1_son, son: 2 (youngest)
    expect(result.get("father")?.generation).toBe(0)
    expect(result.get("sib1_self")?.generation).toBe(1)
    expect(result.get("self")?.generation).toBe(1)
    expect(result.get("spouse")?.generation).toBe(1)
    expect(result.get("sib1_son")?.generation).toBe(2)
    expect(result.get("son")?.generation).toBe(2)
  })

  it("should correctly assign xOffset to avoid overlaps", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("sib1_son", "sib1_son", null, null, "sib1_self", "Mother"),
      createMockPerson("sib1_self", "sib1_self", "sib1_son", "Son", "father", "Father"),
      createMockPerson("father", "father", "sib1_self", "Daughter", "self", "Son"),
      createMockPerson("self", "self", "father", "Father", "spouse", "Spouse"),
      createMockPerson("spouse", "spouse", "self", "Spouse", "son", "Son"),
      createMockPerson("son", "son", "spouse", "Mother", null, null),
    ]

    const result = assignGenerations(path)

    // Expected xOffsets:
    // sib1_son: 0, sib1_self: 0, father: 0
    // self: 1 (shifted to avoid sib1_self)
    // spouse: 2 (spouse shifts right)
    // son: 2
    expect(result.get("sib1_son")?.xOffset).toBe(0)
    expect(result.get("sib1_self")?.xOffset).toBe(0)
    expect(result.get("father")?.xOffset).toBe(0)
    expect(result.get("self")?.xOffset).toBe(1)
    expect(result.get("spouse")?.xOffset).toBe(2)
    expect(result.get("son")?.xOffset).toBe(2)
  })

  it("should handle reverse path and avoid overlaps: son → spouse → self → father → sib1_self → sib1_son", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("son", "son", null, null, "spouse", "Mother"),
      createMockPerson("spouse", "spouse", "son", "Son", "self", "Spouse"),
      createMockPerson("self", "self", "spouse", "Spouse", "father", "Father"),
      createMockPerson("father", "father", "self", "Son", "sib1_self", "Daughter"),
      createMockPerson("sib1_self", "sib1_self", "father", "Father", "sib1_son", "Son"),
      createMockPerson("sib1_son", "sib1_son", "sib1_self", "Mother", null, null),
    ]

    const result = assignGenerations(path)

    // Verify no two nodes in the same generation have the same xOffset
    const genXOffsets = new Map<number, Set<number>>()
    result.forEach((info) => {
      if (!genXOffsets.has(info.generation)) {
        genXOffsets.set(info.generation, new Set())
      }
      const offsets = genXOffsets.get(info.generation)!
      expect(offsets.has(info.xOffset)).toBe(false) // No duplicates
      offsets.add(info.xOffset)
    })

    // Verify spouse updates genToXAxis (the bug fix)
    // self and sib1_self should have different xOffsets
    expect(result.get("self")?.xOffset).not.toBe(result.get("sib1_self")?.xOffset)
  })
})

describe("pathTransformer - generatePathSummary", () => {
  it("should return empty string for empty path", () => {
    expect(generatePathSummary([])).toBe("")
  })

  it("should return single name for single person path", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("p1", "John", null, null, null, null)
    ]
    expect(generatePathSummary(path)).toBe("John")
  })

  it("should join names with arrow for multiple persons", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("p1", "John", null, null, "p2", "Father"),
      createMockPerson("p2", "Jane", "p1", "Son", "p3", "Spouse"),
      createMockPerson("p3", "Bob", "p2", "Spouse", null, null),
    ]
    expect(generatePathSummary(path)).toBe("John → Jane → Bob")
  })
})

describe("pathTransformer - getPersonCount", () => {
  it("should return 0 for empty path", () => {
    expect(getPersonCount([])).toBe(0)
  })

  it("should return correct count for path", () => {
    const path: ApiPersonNode[] = [
      createMockPerson("p1", "Person1", null, null, "p2", "Father"),
      createMockPerson("p2", "Person2", "p1", "Son", "p3", "Spouse"),
      createMockPerson("p3", "Person3", "p2", "Spouse", null, null),
    ]
    expect(getPersonCount(path)).toBe(3)
  })
})
