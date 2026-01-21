// Rishte Relationship Visualizer - Barrel Export
// This module provides components for visualizing relationship paths between two persons

export { GraphControls } from "./GraphControls"
export type { PathSummaryProps } from "./PathSummary"
export { PathSummary } from "./PathSummary"
// Components
export { formatBirthDeathYears, PersonNode } from "./PersonNode"
export { PersonSelector } from "./PersonSelector"
export { RelationshipEdge } from "./RelationshipEdge"
export { RishteAddressStep } from "./RishteAddressStep"
export { RishteBasicInfoStep } from "./RishteBasicInfoStep"
export { RishteGraph } from "./RishteGraph"

// Person Search Wizard Components
export { RishtePersonButton } from "./RishtePersonButton"
export { RishtePersonSearchDialog } from "./RishtePersonSearchDialog"
export { RishteReligionStep } from "./RishteReligionStep"
export { RishteResultsStep } from "./RishteResultsStep"
// Types
export type {
  AddressFormData,
  ApiPersonNode,
  BasicInfoFormData,
  ConnectionInfo,
  GenerationInfo,
  LineagePathResponse,
  PersonNodeData,
  PersonSearchCriteria,
  PersonSelectorProps,
  RelationshipEdgeData,
  ReligionFormData,
  RishteAddressStepProps,
  RishteBasicInfoStepProps,
  RishteEdge,
  RishteGraphState,
  RishteNode,
  RishtePersonButtonProps,
  RishtePersonSearchDialogProps,
  RishteReligionStepProps,
  RishteResultsStepProps,
  // Person Search Wizard Types
  SelectedPerson,
  SelectedPersonId,
  TransformedPath,
} from "./types"
export { WizardStep } from "./types"
export {
  calculatePositions,
  getGenerationY,
  getSpouseXOffset,
  HORIZONTAL_GAP,
  isParentOf,
  isSameGeneration,
  NODE_HEIGHT,
  NODE_WIDTH,
  SPOUSE_GAP,
  VERTICAL_GAP,
} from "./utils/layoutCalculator"
// Utilities
export {
  assignGenerations,
  buildPathArray,
  generatePathSummary,
  getPersonCount,
  isChildRelationship,
  isParentRelationship,
  isSpouseRelationship,
  transformApiResponse,
} from "./utils/pathTransformer"

export {
  buildSearchRequest,
  calculateTotalPages,
  extractBirthYear,
  formatPersonName,
  formatSelectedPersonDisplay,
  isValidAddress,
  isValidBasicInfo,
  isValidReligion,
  toSelectedPerson,
} from "./utils/searchUtils"
