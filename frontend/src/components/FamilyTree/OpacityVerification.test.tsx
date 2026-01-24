import { describe, expect, it } from "vitest"
import type { PersonDetails } from "@/client"
import { renderWithProviders } from "@/test-utils"
import { PersonCard } from "./PersonCard"

describe("Spouse Opacity Verification", () => {
  const mockPerson: PersonDetails = {
    id: "123e4567-e89b-12d3-a456-426614174000",
    first_name: "Jane",
    middle_name: null,
    last_name: "Doe",
    gender_id: "123e4567-e89b-12d3-a456-426614174001",
    date_of_birth: "1990-01-01",
    date_of_death: null,
    user_id: null,
    created_by_user_id: "123e4567-e89b-12d3-a456-426614174002",
    is_primary: false,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  }

  it("spouse card should have opacity-40 class in className string", () => {
    const { container } = renderWithProviders(
      <PersonCard
        person={mockPerson}
        variant="spouse"
        relationshipType="Wife"
        onClick={() => {}}
        colorVariant="spouse"
      />,
    )

    const card = container.querySelector('[data-slot="card"]')
    const className = card?.className || ""

    console.log("Spouse card className:", className)
    console.log("Contains opacity-40:", className.includes("opacity-40"))
    console.log("Contains bg-purple-100:", className.includes("bg-purple-100"))

    expect(className).toContain("opacity-40")
  })

  it("selected person should NOT have opacity-75 class", () => {
    const { container } = renderWithProviders(
      <PersonCard
        person={mockPerson}
        variant="selected"
        onClick={() => {}}
        colorVariant="selected"
      />,
    )

    const card = container.querySelector('[data-slot="card"]')
    const className = card?.className || ""

    console.log("Selected card className:", className)
    console.log("Contains opacity-75:", className.includes("opacity-75"))

    expect(className).not.toContain("opacity-75")
  })

  it("sibling card should have opacity-75 class", () => {
    const { container } = renderWithProviders(
      <PersonCard
        person={mockPerson}
        variant="sibling"
        relationshipType="Sister"
        onClick={() => {}}
        colorVariant="sibling"
      />,
    )

    const card = container.querySelector('[data-slot="card"]')
    const className = card?.className || ""

    console.log("Sibling card className:", className)
    console.log("Contains opacity-75:", className.includes("opacity-75"))

    expect(className).toContain("opacity-75")
  })
})
