import type { PersonSearchFilterRequest, PersonSearchResult } from "@/client"
import type { BasicInfoFormData, AddressFormData, ReligionFormData, PersonSearchCriteria, SelectedPerson } from "../types"

/**
 * Build search request from wizard criteria
 * Transforms the wizard form data into the API request format
 */
export function buildSearchRequest(
  criteria: PersonSearchCriteria,
  skip: number = 0,
  limit: number = 20
): PersonSearchFilterRequest {
  return {
    first_name: criteria.basicInfo.firstName || undefined,
    last_name: criteria.basicInfo.lastName || undefined,
    gender_id: criteria.basicInfo.genderId || undefined,
    birth_year_from: criteria.basicInfo.birthYearFrom || undefined,
    birth_year_to: criteria.basicInfo.birthYearTo || undefined,
    country_id: criteria.address.countryId,
    state_id: criteria.address.stateId,
    district_id: criteria.address.districtId,
    sub_district_id: criteria.address.subDistrictId || "",
    locality_id: criteria.address.localityId || undefined,
    religion_id: criteria.religion.religionId,
    religion_category_id: criteria.religion.religionCategoryId,
    religion_sub_category_id: criteria.religion.religionSubCategoryId || undefined,
    skip,
    limit,
  }
}

/**
 * Extract birth year from date string
 * Returns null for invalid or empty dates
 */
export function extractBirthYear(dateOfBirth: string | null | undefined): number | null {
  if (!dateOfBirth) return null
  const year = new Date(dateOfBirth).getFullYear()
  return isNaN(year) ? null : year
}

/**
 * Format person name for display
 * Combines first, middle (if present), and last name
 */
export function formatPersonName(person: Pick<PersonSearchResult, 'first_name' | 'middle_name' | 'last_name'>): string {
  const parts = [person.first_name]
  if (person.middle_name) parts.push(person.middle_name)
  parts.push(person.last_name)
  return parts.join(" ")
}

/**
 * Transform PersonSearchResult to SelectedPerson
 * Used when a user selects a person from search results
 */
export function toSelectedPerson(person: PersonSearchResult): SelectedPerson {
  return {
    personId: person.person_id,
    firstName: person.first_name,
    lastName: person.last_name,
    birthYear: extractBirthYear(person.date_of_birth),
  }
}

/**
 * Calculate total pages for pagination
 */
export function calculateTotalPages(total: number, pageSize: number): number {
  if (total <= 0 || pageSize <= 0) return 0
  return Math.ceil(total / pageSize)
}

/**
 * Validate basic info form data
 * Returns true if required fields are present and valid
 */
export function isValidBasicInfo(data: BasicInfoFormData): boolean {
  return (
    data.firstName.trim().length > 0 &&
    data.lastName.trim().length > 0
  )
}

/**
 * Validate address form data
 * Returns true if required fields are present
 */
export function isValidAddress(data: AddressFormData): boolean {
  return (
    data.countryId.length > 0 &&
    data.stateId.length > 0 &&
    data.districtId.length > 0
  )
}

/**
 * Validate religion form data
 * Returns true if required fields are present
 */
export function isValidReligion(data: ReligionFormData): boolean {
  return (
    data.religionId.length > 0 &&
    data.religionCategoryId.length > 0
  )
}

/**
 * Format display name for selected person
 * Used in RishtePersonButton to show selected person info
 */
export function formatSelectedPersonDisplay(person: SelectedPerson): string {
  const name = `${person.firstName} ${person.lastName}`
  if (person.birthYear) {
    return `${name} (${person.birthYear})`
  }
  return name
}
