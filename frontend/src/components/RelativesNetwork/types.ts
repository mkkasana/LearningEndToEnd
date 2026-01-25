/**
 * Relatives Network UI - TypeScript Interfaces
 * Requirements: 2.2, 2.3, 2.4, 12.1
 */

/**
 * Relatives filter state
 * Contains all filter values for the relatives network search
 */
export interface RelativesFilters {
  depth: number // Search depth (1 to max, default: 3)
  depthMode: "up_to" | "only_at" // 'up_to' returns all from 1 to N, 'only_at' returns only at N
  livingOnly: boolean // If true, exclude deceased relatives (default: true)
  genderId?: string // Filter by gender ID (optional)
  countryId?: string // Filter by country ID (optional)
  stateId?: string // Filter by state ID (optional)
  districtId?: string // Filter by district ID (optional)
  subDistrictId?: string // Filter by sub-district ID (optional)
  localityId?: string // Filter by locality ID (optional)
}

/**
 * Default filter values for relatives network search
 * Requirements: 2.2, 2.3, 2.4
 */
export const DEFAULT_FILTERS: RelativesFilters = {
  depth: 3,
  depthMode: "up_to",
  livingOnly: true,
}
