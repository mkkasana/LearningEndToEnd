/**
 * Custom API services for features not yet in the auto-generated OpenAPI SDK.
 * These services should match the backend API endpoints.
 */

import type { CancelablePromise } from './core/CancelablePromise';
import { OpenAPI } from './core/OpenAPI';
import { request as __request } from './core/request';
import type { PersonContributionPublic } from './types.custom';

/**
 * Custom Person Service for contribution stats.
 * Extends the auto-generated PersonService with additional methods.
 */
export class PersonContributionService {
  /**
   * Get My Contributions
   * Get all persons created by the current user with view statistics.
   * 
   * Returns list of contributed persons with:
   * - Person details (name, dates, status)
   * - Formatted address
   * - Total view count
   * 
   * Results are sorted by view count descending (most viewed first).
   * @returns PersonContributionPublic[] Successful Response
   * @throws ApiError
   */
  public static getMyContributions(): CancelablePromise<Array<PersonContributionPublic>> {
    return __request(OpenAPI, {
      method: 'GET',
      url: '/api/v1/person/my-contributions',
    });
  }
}
