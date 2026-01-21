/**
 * Find Partner UI - TypeScript Interfaces
 * Requirements: 12.1
 */

/**
 * Selected tag item for multi-select inputs
 * Used in religion, category, and sub-category tag inputs
 */
export interface TagItem {
  id: string
  name: string
}

/**
 * Partner filter state
 * Contains all filter values for the partner search
 */
export interface PartnerFilters {
  genderId: string // Single select gender ID
  birthYearFrom: number | undefined // Minimum birth year
  birthYearTo: number | undefined // Maximum birth year
  includeReligions: TagItem[] // Multi-select religions to include
  includeCategories: TagItem[] // Multi-select categories to include
  includeSubCategories: TagItem[] // Multi-select sub-categories to include
  excludeSubCategories: TagItem[] // Multi-select sub-categories to exclude (gotras)
  searchDepth: number // BFS traversal depth (1-50)
}

/**
 * Props for PartnerFilterPanel component
 */
export interface PartnerFilterPanelProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  filters: PartnerFilters
  defaultFilters: PartnerFilters
  onApply: (filters: PartnerFilters) => void
  onReset: () => void
}

/**
 * Props for TagInput component
 * Reusable multi-select tag input with dropdown
 */
export interface TagInputProps {
  label: string
  selectedItems: TagItem[]
  availableItems: TagItem[]
  onAdd: (item: TagItem) => void
  onRemove: (itemId: string) => void
  placeholder?: string
  disabled?: boolean
}

/**
 * Active person data needed for calculating defaults
 * Fetched from the active person context
 */
export interface ActivePersonDefaults {
  genderId: string | null
  birthYear: number | null
  religionId: string | null
  religionName: string | null
  categoryId: string | null
  categoryName: string | null
  subCategoryId: string | null
  subCategoryName: string | null
}

/**
 * Lineage sub-categories for exclusion defaults
 * Fetched from active person's family relationships
 */
export interface LineageSubCategories {
  selfSubCategory: TagItem | null
  motherSubCategory: TagItem | null
  grandmotherSubCategory: TagItem | null
}

/**
 * Gender metadata from API
 */
export interface GenderMetadata {
  genderId: string
  genderCode: string
  genderName: string
}

/**
 * Props for PartnerResultsDisplay component
 */
export interface PartnerResultsDisplayProps {
  data: unknown | null
  isLoading: boolean
  error: Error | null
  totalMatches: number | null
}

// ============================================
// Match Visualization Types
// Requirements: 1.1, 6.1-6.5, 7.1-7.5
// ============================================

import type { Edge, Node } from "@xyflow/react"

/**
 * Match item for dropdown display
 * Used in MatchSelector to list all matches
 */
export interface MatchItem {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  depth: number
}

/**
 * Data for Match Person Node
 * Contains all information needed to render a person in the match graph
 * Extends Record<string, unknown> for React Flow compatibility
 */
export interface MatchPersonNodeData extends Record<string, unknown> {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  deathYear: number | null
  isSeeker: boolean // Green border + "Seeker" label
  isMatch: boolean // Blue border + "Match" label
}

/**
 * Data for Match Relationship Edge
 * Contains relationship type and styling information
 * Extends Record<string, unknown> for React Flow compatibility
 */
export interface MatchRelationshipEdgeData extends Record<string, unknown> {
  relationship: string // "Son", "Father", "Spouse", etc.
  isSpouseEdge: boolean // Horizontal styling
}

/**
 * React Flow node for match graph
 * Custom node type for displaying persons in the path
 */
export type MatchNode = Node<MatchPersonNodeData, "matchPersonNode">

/**
 * React Flow edge for match graph
 * Custom edge type for displaying relationships between persons
 */
export type MatchEdge = Edge<MatchRelationshipEdgeData>

/**
 * Transformed path result
 * Contains React Flow nodes and edges for rendering
 */
export interface TransformedMatchPath {
  nodes: MatchNode[]
  edges: MatchEdge[]
}

/**
 * Generation info for layout calculation
 * Used to position nodes based on family generation
 */
export interface MatchGenerationInfo {
  personId: string
  generation: number
  xOffset: number
  isSpouse: boolean
  spouseOfId?: string
}

/**
 * Props for MatchSelector component
 * Dropdown to select which match's path to display
 */
export interface MatchSelectorProps {
  matches: MatchItem[]
  selectedMatchId: string | null
  onSelectMatch: (matchId: string) => void
  totalMatches: number
}

/**
 * Props for MatchPathSummary component
 * Displays the path as "Name1 → Name2 → Name3..."
 */
export interface MatchPathSummaryProps {
  pathNames: string[]
}

/**
 * Props for MatchGraph component
 * React Flow container for rendering the match visualization
 */
export interface MatchGraphProps {
  nodes: MatchNode[]
  edges: MatchEdge[]
}
