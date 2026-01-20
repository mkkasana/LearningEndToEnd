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
  genderId: string                    // Single select gender ID
  birthYearFrom: number | undefined   // Minimum birth year
  birthYearTo: number | undefined     // Maximum birth year
  includeReligions: TagItem[]         // Multi-select religions to include
  includeCategories: TagItem[]        // Multi-select categories to include
  includeSubCategories: TagItem[]     // Multi-select sub-categories to include
  excludeSubCategories: TagItem[]     // Multi-select sub-categories to exclude (gotras)
  searchDepth: number                 // BFS traversal depth (1-50)
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
