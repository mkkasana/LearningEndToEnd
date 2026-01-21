import type { PersonMatchResult } from "@/client"

/**
 * Threshold for considering a match as "high confidence" (95% or above)
 */
const HIGH_CONFIDENCE_THRESHOLD = 90

/**
 * Normalizes a date string to YYYY-MM-DD format for comparison.
 * Handles both ISO date strings (with time component) and simple date strings.
 *
 * @param dateStr - The date string to normalize
 * @returns Normalized date string in YYYY-MM-DD format
 */
function normalizeDateString(dateStr: string): string {
  // If the date string contains a time component (T), extract just the date part
  if (dateStr.includes("T")) {
    return dateStr.split("T")[0]
  }
  // Otherwise return as-is (already in YYYY-MM-DD format)
  return dateStr
}

/**
 * Determines if a person match is a high-confidence match.
 * A high-confidence match requires:
 * - match_score >= 95 (high confidence name match)
 * - date_of_birth matches the search criteria exactly
 *
 * @param person - The person match result to check
 * @param searchDateOfBirth - The date of birth from the search criteria
 * @returns true if the person is a high-confidence match, false otherwise
 */
export function isExactMatch(
  person: PersonMatchResult,
  searchDateOfBirth: string,
): boolean {
  const isHighConfidenceMatch = person.match_score >= HIGH_CONFIDENCE_THRESHOLD
  const normalizedPersonDob = normalizeDateString(person.date_of_birth)
  const normalizedSearchDob = normalizeDateString(searchDateOfBirth)
  const isDateOfBirthMatch = normalizedPersonDob === normalizedSearchDob
  return isHighConfidenceMatch && isDateOfBirthMatch
}

/**
 * Finds all high-confidence matches from the search results.
 * A high-confidence match requires:
 * - match_score >= 95 (high confidence name match)
 * - date_of_birth matches the search criteria exactly
 *
 * @param persons - Array of person match results to filter
 * @param searchDateOfBirth - The date of birth from the search criteria
 * @returns Array of persons that are high-confidence matches
 */
export function findExactMatches(
  persons: PersonMatchResult[],
  searchDateOfBirth: string,
): PersonMatchResult[] {
  return persons.filter((person) => isExactMatch(person, searchDateOfBirth))
}
