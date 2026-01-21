/**
 * Find Partner UI - Barrel Export
 * This module provides components for searching potential marriage matches
 * Requirements: 9.1, 12.1
 */

// Hooks
export { usePartnerDefaults } from "./hooks/usePartnerDefaults"
export { MatchGraph } from "./MatchGraph"
export { MatchGraphControls } from "./MatchGraphControls"
export { MatchPathSummary } from "./MatchPathSummary"
export { MatchPersonNode } from "./MatchPersonNode"
export { MatchRelationshipEdge } from "./MatchRelationshipEdge"
// Match Visualization Components
export { MatchSelector } from "./MatchSelector"
export { PartnerFilterPanel } from "./PartnerFilterPanel"
export { PartnerResultsDisplay } from "./PartnerResultsDisplay"
// Components
export { TagInput } from "./TagInput"
// Types
export type {
  ActivePersonDefaults,
  GenderMetadata,
  LineageSubCategories,
  MatchEdge,
  MatchGenerationInfo,
  MatchGraphProps,
  // Match Visualization Types
  MatchItem,
  MatchNode,
  MatchPathSummaryProps,
  MatchPersonNodeData,
  MatchRelationshipEdgeData,
  MatchSelectorProps,
  PartnerFilterPanelProps,
  PartnerFilters,
  PartnerResultsDisplayProps,
  TagInputProps,
  TagItem,
  TransformedMatchPath,
} from "./types"

// Utilities
export {
  buildDefaultFilters,
  calculateBirthYearRange,
  calculateOppositeGender,
  validateBirthYearRange,
} from "./utils/defaultsCalculator"
export type {
  EdgeHandles,
  HandlePosition,
} from "./utils/matchGraphTransformer"
// Match Graph Transformation Utilities
export {
  assignGenerations,
  calculatePositions,
  getEdgeHandles,
  HORIZONTAL_GAP,
  isChildRelationship,
  isParentRelationship,
  isSpouseRelationship,
  NODE_HEIGHT,
  NODE_WIDTH,
  SPOUSE_GAP,
  transformMatchPath,
  VERTICAL_GAP,
} from "./utils/matchGraphTransformer"
export type {
  MatchConnectionInfo,
  MatchGraphNode,
} from "./utils/matchPathExtractor"
// Match Path Extraction Utilities
export {
  buildMatchItems,
  extractPathToMatch,
  generateMatchPathSummary,
} from "./utils/matchPathExtractor"
