/**
 * Utility to check if a user can assume roles (elevated user check)
 *
 * Only users with SUPERUSER or ADMIN role can assume other persons' roles.
 * This is a frontend check for UI visibility - the backend also validates.
 *
 * _Requirements: 1.1, 1.3_
 */

import type { UserPublic, UserRole } from "@/client"

/**
 * Elevated roles that can assume other persons
 */
const ELEVATED_ROLES: UserRole[] = ["superuser", "admin"]

/**
 * Check if a user role is elevated (can assume other persons)
 *
 * @param role - The user's role
 * @returns true if the role is superuser or admin
 *
 * _Requirements: 1.1_
 */
export function isElevatedRole(role: UserRole | undefined): boolean {
  if (!role) return false
  return ELEVATED_ROLES.includes(role)
}

/**
 * Check if a user can assume other persons' roles
 *
 * @param user - The user object (from useAuth)
 * @returns true if the user has superuser or admin role
 *
 * _Requirements: 1.1, 1.3_
 */
export function canUserAssumeRoles(
  user: UserPublic | null | undefined,
): boolean {
  if (!user) return false
  return isElevatedRole(user.role)
}

/**
 * Check if a user can assume a specific person
 *
 * Frontend check for UI visibility:
 * - User must be elevated (superuser or admin)
 * - User must have created the person (created_by_user_id matches)
 *
 * Note: This is a preliminary check. The backend validates via /can-assume endpoint.
 *
 * @param user - The current user
 * @param createdByUserId - The created_by_user_id of the person to assume
 * @returns true if the user can potentially assume this person
 *
 * _Requirements: 1.1, 1.3, 2.1_
 */
export function canAssumeSpecificPerson(
  user: UserPublic | null | undefined,
  createdByUserId: string | null | undefined,
): boolean {
  if (!user || !createdByUserId) return false

  // Must be elevated user
  if (!canUserAssumeRoles(user)) return false

  // Must have created the person
  return user.id === createdByUserId
}
