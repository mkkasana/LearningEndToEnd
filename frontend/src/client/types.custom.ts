/**
 * Custom TypeScript types for features not yet in the auto-generated OpenAPI types.
 * These types should match the backend Pydantic schemas.
 */

/**
 * Schema for person contribution with statistics.
 * Matches backend: app/schemas/person/person_contribution.py
 */
export interface PersonContributionPublic {
  /** Person ID */
  id: string;
  /** First name */
  first_name: string;
  /** Last name */
  last_name: string;
  /** Date of birth (ISO date string) */
  date_of_birth: string;
  /** Date of death (ISO date string, null if alive) */
  date_of_death: string | null;
  /** Whether the person is active */
  is_active: boolean;
  /** Formatted address string */
  address: string;
  /** Total profile view count */
  total_views: number;
  /** Record creation timestamp (ISO datetime string) */
  created_at: string;
}
