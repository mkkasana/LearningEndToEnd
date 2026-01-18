// Rishte Relationship Visualizer - Barrel Export
// This module provides components for visualizing relationship paths between two persons

// Types
export type {
  SelectedPersonId,
  PersonNodeData,
  RelationshipEdgeData,
  RishteNode,
  RishteEdge,
  TransformedPath,
  GenerationInfo,
  PersonSelectorProps,
  RishteGraphState,
  ConnectionInfo,
  ApiPersonNode,
  LineagePathResponse,
} from "./types"

// Components
export { PersonNode, formatBirthDeathYears } from "./PersonNode"
export { RelationshipEdge } from "./RelationshipEdge"
export { PersonSelector } from "./PersonSelector"
export { PathSummary } from "./PathSummary"
export type { PathSummaryProps } from "./PathSummary"
export { GraphControls } from "./GraphControls"
export { RishteGraph } from "./RishteGraph"

// Utilities
export {
  transformApiResponse,
  buildPathArray,
  assignGenerations,
  generatePathSummary,
  getPersonCount,
  isChildRelationship,
  isParentRelationship,
  isSpouseRelationship,
} from "./utils/pathTransformer"

export {
  calculatePositions,
  getGenerationY,
  isSameGeneration,
  isParentOf,
  getSpouseXOffset,
  NODE_WIDTH,
  NODE_HEIGHT,
  HORIZONTAL_GAP,
  VERTICAL_GAP,
  SPOUSE_GAP,
} from "./utils/layoutCalculator"
