/**
 * Find Partner UI - Defaults Calculator Utilities
 * Pure functions for calculating smart defaults based on active person data
 * Requirements: 3.2, 3.3, 4.2, 4.3, 4.5
 */

import type {
  ActivePersonDefaults,
  GenderMetadata,
  LineageSubCategories,
  PartnerFilters,
  TagItem,
} from "../types"

/**
 * Calculate opposite gender ID
 * Requirements: 3.2, 3.3
 *
 * @param genderId - Active person's gender ID
 * @param genders - List of available genders from API
 * @returns Opposite gender ID or empty string if unknown
 */
export function calculateOppositeGender(
  genderId: string | null,
  genders: GenderMetadata[]
): string {
  if (!genderId || !genders.length) {
    return ""
  }

  const currentGender = genders.find((g) => g.genderId === genderId)
  if (!currentGender) {
    return ""
  }

  // Determine opposite gender code
  const oppositeCode = currentGender.genderCode === "MALE" ? "FEMALE" : "MALE"
  const oppositeGender = genders.find((g) => g.genderCode === oppositeCode)

  return oppositeGender?.genderId || ""
}

/**
 * Calculate birth year range defaults
 * Requirements: 4.2, 4.3
 *
 * @param birthYear - Active person's birth year
 * @returns Object with fromYear and toYear, or undefined values if unknown
 */
export function calculateBirthYearRange(birthYear: number | null): {
  fromYear: number | undefined
  toYear: number | undefined
} {
  if (!birthYear) {
    return { fromYear: undefined, toYear: undefined }
  }

  return {
    fromYear: birthYear - 2,
    toYear: birthYear + 5,
  }
}

/**
 * Validate birth year range
 * Requirements: 4.5
 *
 * @param fromYear - Start of birth year range
 * @param toYear - End of birth year range
 * @returns Error message or null if valid
 */
export function validateBirthYearRange(
  fromYear: number | undefined,
  toYear: number | undefined
): string | null {
  if (fromYear !== undefined && toYear !== undefined && fromYear > toYear) {
    return "From year must be less than or equal to To year"
  }
  return null
}

/**
 * Build default filters from active person data and lineage
 * Requirements: 3.2, 3.3, 4.2, 4.3, 5.2, 6.2, 8.2, 8.3, 8.4
 *
 * @param activePersonDefaults - Active person's profile data
 * @param lineageSubCategories - Sub-categories from family lineage
 * @param genders - List of available genders from API
 * @returns Complete PartnerFilters with smart defaults
 */
export function buildDefaultFilters(
  activePersonDefaults: ActivePersonDefaults,
  lineageSubCategories: LineageSubCategories,
  genders: GenderMetadata[]
): PartnerFilters {
  const { fromYear, toYear } = calculateBirthYearRange(
    activePersonDefaults.birthYear
  )

  // Build include religions default (active person's religion)
  const includeReligions: TagItem[] = []
  if (activePersonDefaults.religionId && activePersonDefaults.religionName) {
    includeReligions.push({
      id: activePersonDefaults.religionId,
      name: activePersonDefaults.religionName,
    })
  }

  // Build include categories default (active person's category)
  const includeCategories: TagItem[] = []
  if (activePersonDefaults.categoryId && activePersonDefaults.categoryName) {
    includeCategories.push({
      id: activePersonDefaults.categoryId,
      name: activePersonDefaults.categoryName,
    })
  }

  // Build exclude sub-categories from lineage (graceful if missing)
  // Includes: self, mother, maternal grandmother
  const excludeSubCategories: TagItem[] = []

  if (lineageSubCategories.selfSubCategory) {
    excludeSubCategories.push(lineageSubCategories.selfSubCategory)
  }

  if (lineageSubCategories.motherSubCategory) {
    // Avoid duplicates
    const isDuplicate = excludeSubCategories.some(
      (sc) => sc.id === lineageSubCategories.motherSubCategory!.id
    )
    if (!isDuplicate) {
      excludeSubCategories.push(lineageSubCategories.motherSubCategory)
    }
  }

  if (lineageSubCategories.grandmotherSubCategory) {
    // Avoid duplicates
    const isDuplicate = excludeSubCategories.some(
      (sc) => sc.id === lineageSubCategories.grandmotherSubCategory!.id
    )
    if (!isDuplicate) {
      excludeSubCategories.push(lineageSubCategories.grandmotherSubCategory)
    }
  }

  return {
    genderId: calculateOppositeGender(activePersonDefaults.genderId, genders),
    birthYearFrom: fromYear,
    birthYearTo: toYear,
    includeReligions,
    includeCategories,
    includeSubCategories: [], // Always starts empty per requirements
    excludeSubCategories,
    searchDepth: 10, // Default depth per requirements 9.2
  }
}
