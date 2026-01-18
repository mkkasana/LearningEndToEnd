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
  // Person Search Wizard Types
  SelectedPerson,
  BasicInfoFormData,
  AddressFormData,
  ReligionFormData,
  PersonSearchCriteria,
  RishtePersonSearchDialogProps,
  RishtePersonButtonProps,
  RishteBasicInfoStepProps,
  RishteAddressStepProps,
  RishteReligionStepProps,
  RishteResultsStepProps,
} from "./types"

export { WizardStep } from "./types"

// Components
export { PersonNode, formatBirthDeathYears } from "./PersonNode"
export { RelationshipEdge } from "./RelationshipEdge"
export { PersonSelector } from "./PersonSelector"
export { PathSummary } from "./PathSummary"
export type { PathSummaryProps } from "./PathSummary"
export { GraphControls } from "./GraphControls"
export { RishteGraph } from "./RishteGraph"

// Person Search Wizard Components
export { RishtePersonButton } from "./RishtePersonButton"
export { RishteBasicInfoStep } from "./RishteBasicInfoStep"
export { RishteAddressStep } from "./RishteAddressStep"
export { RishteReligionStep } from "./RishteReligionStep"
export { RishteResultsStep } from "./RishteResultsStep"
export { RishtePersonSearchDialog } from "./RishtePersonSearchDialog"

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

export {
  buildSearchRequest,
  extractBirthYear,
  formatPersonName,
  toSelectedPerson,
  calculateTotalPages,
  isValidBasicInfo,
  isValidAddress,
  isValidReligion,
  formatSelectedPersonDisplay,
} from "./utils/searchUtils"
