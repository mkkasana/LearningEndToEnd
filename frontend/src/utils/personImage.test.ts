import { describe, expect, it } from "vitest"
import { getPersonImageUrl } from "./personImage"

const BASE = import.meta.env.VITE_API_URL || ""

describe("getPersonImageUrl", () => {
  it("returns undefined for null key", () => {
    expect(getPersonImageUrl(null)).toBeUndefined()
  })

  it("returns undefined for undefined key", () => {
    expect(getPersonImageUrl(undefined)).toBeUndefined()
  })

  it("returns undefined for empty string key", () => {
    expect(getPersonImageUrl("")).toBeUndefined()
  })

  it("returns thumbnail URL by default", () => {
    const url = getPersonImageUrl("abc123.jpg")
    expect(url).toBe(`${BASE}/api/v1/uploads/person-images/abc123_thumb.jpg`)
  })

  it("returns thumbnail URL when variant is thumbnail", () => {
    const url = getPersonImageUrl("abc123.jpg", "thumbnail")
    expect(url).toBe(`${BASE}/api/v1/uploads/person-images/abc123_thumb.jpg`)
  })

  it("returns main URL when variant is main", () => {
    const url = getPersonImageUrl("abc123.jpg", "main")
    expect(url).toBe(`${BASE}/api/v1/uploads/person-images/abc123.jpg`)
  })

  it("only replaces trailing .jpg for thumbnail derivation", () => {
    const url = getPersonImageUrl("file.jpg.jpg", "thumbnail")
    expect(url).toBe(`${BASE}/api/v1/uploads/person-images/file.jpg_thumb.jpg`)
  })

  it("does not modify non-.jpg keys for thumbnail", () => {
    const url = getPersonImageUrl("abc123.png", "thumbnail")
    expect(url).toBe(`${BASE}/api/v1/uploads/person-images/abc123.png`)
  })

  it("includes the full key path in the URL", () => {
    const url = getPersonImageUrl("some-uuid-key.jpg", "main")
    expect(url).toContain("/api/v1/uploads/person-images/some-uuid-key.jpg")
  })
})
