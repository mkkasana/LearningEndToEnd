import type { PersonDetails } from "@/client"
import { PersonCard } from "./PersonCard"

/**
 * Visual demonstration component to show opacity differences
 * This helps verify that spouse cards have reduced opacity compared to other cards
 */
export function OpacityDemo() {
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

  return (
    <div className="p-8 space-y-8">
      <h2 className="text-2xl font-bold">Opacity Comparison</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">
            Selected Person (Full Opacity)
          </h3>
          <PersonCard
            person={mockPerson}
            variant="selected"
            onClick={() => {}}
            colorVariant="selected"
          />
          <p className="text-sm text-muted-foreground">No opacity reduction</p>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Spouse (75% Opacity)</h3>
          <PersonCard
            person={{ ...mockPerson, first_name: "John" }}
            variant="spouse"
            relationshipType="Husband"
            onClick={() => {}}
            colorVariant="spouse"
          />
          <p className="text-sm text-muted-foreground">opacity-75 applied</p>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold">Sibling (75% Opacity)</h3>
          <PersonCard
            person={{ ...mockPerson, first_name: "Mary" }}
            variant="sibling"
            relationshipType="Sister"
            onClick={() => {}}
            colorVariant="sibling"
          />
          <p className="text-sm text-muted-foreground">
            opacity-75 applied (existing)
          </p>
        </div>
      </div>

      <div className="mt-8 p-4 bg-muted rounded-lg">
        <h3 className="font-semibold mb-2">Visual Hierarchy:</h3>
        <ul className="list-disc list-inside space-y-1 text-sm">
          <li>Selected person: Full opacity (100%) - most prominent</li>
          <li>
            Spouse: Reduced opacity (75%) - de-emphasized to show they're not
            blood relatives
          </li>
          <li>
            Sibling: Reduced opacity (75%) - de-emphasized but still visible
          </li>
          <li>Parents & Children: Full opacity (100%) - direct lineage</li>
        </ul>
      </div>
    </div>
  )
}
