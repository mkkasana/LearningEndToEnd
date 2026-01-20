/**
 * Find Partner UI - Barrel Export
 * This module provides components for searching potential marriage matches
 * Requirements: 12.1
 */

// Types
export type {
  TagItem,
  PartnerFilters,
  PartnerFilterPanelProps,
  TagInputProps,
  ActivePersonDefaults,
  LineageSubCategories,
  GenderMetadata,
  PartnerResultsDisplayProps,
} from "./types"

// Components
export { TagInput } from "./TagInput"
export { PartnerFilterPanel } from "./PartnerFilterPanel"
export { PartnerResultsDisplay } from "./PartnerResultsDisplay"

// Hooks
export { usePartnerDefaults } from "./hooks/usePartnerDefaults"

// Utilities
export {
  calculateOppositeGender,
  calculateBirthYearRange,
  validateBirthYearRange,
  buildDefaultFilters,
} from "./utils/defaultsCalculator"
