import type { Node, Edge } from "@xyflow/react"

/**
 * Selected person ID (simplified for direct ID input)
 * In future, this can be expanded to include person details from search
 */
export type SelectedPersonId = string | null

// ============================================
// Person Search Wizard Types
// ============================================

/**
 * Selected person data for display in the wizard
 */
export interface SelectedPerson {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
}

/**
 * Basic info step form data (Step 1)
 */
export interface BasicInfoFormData {
  firstName: string        // Required
  lastName: string         // Required
  genderId?: string        // Optional
  birthYearFrom?: number   // Optional
  birthYearTo?: number     // Optional
}

/**
 * Address step form data (Step 2)
 */
export interface AddressFormData {
  countryId: string        // Required
  stateId: string          // Required
  districtId: string       // Required
  subDistrictId?: string   // Optional
  localityId?: string      // Optional
}

/**
 * Religion step form data (Step 3)
 */
export interface ReligionFormData {
  religionId: string           // Required
  religionCategoryId: string   // Required
  religionSubCategoryId?: string // Optional
}

/**
 * Combined search criteria from all wizard steps
 */
export interface PersonSearchCriteria {
  basicInfo: BasicInfoFormData
  address: AddressFormData
  religion: ReligionFormData
}

/**
 * Wizard step enum for tracking current step
 */
export enum WizardStep {
  BASIC_INFO = 0,
  ADDRESS = 1,
  RELIGION = 2,
  RESULTS = 3,
}

/**
 * Props for RishtePersonSearchDialog component
 */
export interface RishtePersonSearchDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  personLabel: "A" | "B"
  onPersonSelect: (person: SelectedPerson) => void
}

/**
 * Props for RishtePersonButton component
 */
export interface RishtePersonButtonProps {
  label: "A" | "B"
  selectedPerson: SelectedPerson | null
  onSelect: () => void
  onClear: () => void
}

/**
 * Props for RishteBasicInfoStep component
 */
export interface RishteBasicInfoStepProps {
  initialData?: BasicInfoFormData
  onNext: (data: BasicInfoFormData) => void
}

/**
 * Props for RishteAddressStep component
 */
export interface RishteAddressStepProps {
  initialData?: AddressFormData
  defaultAddress?: AddressFormData
  onNext: (data: AddressFormData) => void
  onBack: () => void
}

/**
 * Props for RishteReligionStep component
 */
export interface RishteReligionStepProps {
  initialData?: ReligionFormData
  defaultReligion?: ReligionFormData
  onSearch: (data: ReligionFormData) => void
  onBack: () => void
}

/**
 * Props for RishteResultsStep component
 */
export interface RishteResultsStepProps {
  searchCriteria: PersonSearchCriteria
  onSelect: (person: SelectedPerson) => void
  onBack: () => void
}

/**
 * Data for a person node in the React Flow graph
 */
export interface PersonNodeData extends Record<string, unknown> {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  deathYear: number | null
  isPersonA: boolean // Green border
  isPersonB: boolean // Blue border
  gender?: "male" | "female" // For avatar icon
}

/**
 * React Flow node structure for Rishte graph
 */
export type RishteNode = Node<PersonNodeData, "personNode">

/**
 * Data for a relationship edge in the React Flow graph
 */
export interface RelationshipEdgeData extends Record<string, unknown> {
  relationship: string // "Son", "Father", "Spouse", etc.
  isSpouseEdge: boolean // Horizontal styling
}

/**
 * React Flow edge structure for Rishte graph
 */
export type RishteEdge = Edge<RelationshipEdgeData>

/**
 * Result of path transformation from API response
 */
export interface TransformedPath {
  nodes: RishteNode[]
  edges: RishteEdge[]
}

/**
 * Generation information for layout calculation
 */
export interface GenerationInfo {
  personId: string
  generation: number // 0 = oldest, increases downward
  xOffset: number // Horizontal position within generation
  isSpouse: boolean
  spouseOfId?: string
}

/**
 * Props for PersonSelector component (simplified for direct ID input)
 */
export interface PersonSelectorProps {
  label: string // "Person A" or "Person B"
  value: string | null // Currently entered person ID
  onChange: (personId: string | null) => void
  placeholder?: string
}

/**
 * State for the Rishte graph component
 */
export interface RishteGraphState {
  nodes: RishteNode[]
  edges: RishteEdge[]
  isLoading: boolean
  error: string | null
  pathSummary: string | null
  personCount: number
}

/**
 * API response types (matching backend schema)
 */
export interface ConnectionInfo {
  person_id: string
  relationship: string // "Father", "Mother", "Son", "Daughter", "Spouse", etc.
}

export interface ApiPersonNode {
  person_id: string
  first_name: string
  last_name: string
  birth_year: number | null
  death_year: number | null
  address: string
  religion: string
  from_person: ConnectionInfo | null
  to_person: ConnectionInfo | null
}

export interface LineagePathResponse {
  connection_found: boolean
  message: string
  common_ancestor_id: string | null
  graph: Record<string, ApiPersonNode>
}
