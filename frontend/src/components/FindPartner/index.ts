/**
 * Find Partner UI - Barrel Export
 * This module provides components for searching potential marriage matches
 * Requirements: 9.1, 12.1
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
  // Match Visualization Types
  MatchItem,
  MatchPersonNodeData,
  MatchRelationshipEdgeData,
  MatchNode,
  MatchEdge,
  TransformedMatchPath,
  MatchGenerationInfo,
  MatchSelectorProps,
  MatchPathSummaryProps,
  MatchGraphProps,
} from "./types"

// Components
export { TagInput } from "./TagInput"
export { PartnerFilterPanel } from "./PartnerFilterPanel"
export { PartnerResultsDisplay } from "./PartnerResultsDisplay"

// Match Visualization Components
export { MatchSelector } from "./MatchSelector"
export { MatchPathSummary } from "./MatchPathSummary"
export { MatchGraph } from "./MatchGraph"
export { MatchPersonNode } from "./MatchPersonNode"
export { MatchRelationshipEdge } from "./MatchRelationshipEdge"
export { MatchGraphControls } from "./MatchGraphControls"

// Hooks
export { usePartnerDefaults } from "./hooks/usePartnerDefaults"

// Utilities
export {
  calculateOppositeGender,
  calculateBirthYearRange,
  validateBirthYearRange,
  buildDefaultFilters,
} from "./utils/defaultsCalculator"

// Match Path Extraction Utilities
export {
  extractPathToMatch,
  buildMatchItems,
  generateMatchPathSummary,
} from "./utils/matchPathExtractor"
export type {
  MatchConnectionInfo,
  MatchGraphNode,
} from "./utils/matchPathExtractor"

// Match Graph Transformation Utilities
export {
  transformMatchPath,
  assignGenerations,
  calculatePositions,
  getEdgeHandles,
  isChildRelationship,
  isParentRelationship,
  isSpouseRelationship,
  NODE_WIDTH,
  NODE_HEIGHT,
  HORIZONTAL_GAP,
  VERTICAL_GAP,
  SPOUSE_GAP,
} from "./utils/matchGraphTransformer"
export type {
  HandlePosition,
  EdgeHandles,
} from "./utils/matchGraphTransformer"
