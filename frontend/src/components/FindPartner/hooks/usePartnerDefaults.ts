// @ts-nocheck
/**
 * usePartnerDefaults Hook - Fetches active person defaults for partner search
 * Requirements: 2.4, 5.2, 6.2, 8.2, 8.3, 8.4
 *
 * Fetches the active person's profile data and lineage sub-categories
 * to calculate smart defaults for the partner filter panel.
 */

import { useQuery } from "@tanstack/react-query"
import {
  PersonMetadataService,
  PersonService,
  RelativesService,
  ReligionMetadataService,
} from "@/client"
import { useActivePersonContext } from "@/contexts"
import type {
  ActivePersonDefaults,
  GenderMetadata,
  LineageSubCategories,
  PartnerFilters,
} from "../types"
import { buildDefaultFilters } from "../utils/defaultsCalculator"

/**
 * Extract birth year from date string
 */
function extractBirthYear(
  dateOfBirth: string | null | undefined,
): number | null {
  if (!dateOfBirth) return null
  try {
    const year = new Date(dateOfBirth).getFullYear()
    return Number.isNaN(year) ? null : year
  } catch {
    return null
  }
}

/**
 * Hook to fetch and calculate partner search defaults
 *
 * Returns:
 * - defaultFilters: Calculated default filter values
 * - isLoading: Whether data is still being fetched
 * - error: Any error that occurred during fetching
 */
export function usePartnerDefaults() {
  const { activePersonId, activePerson } = useActivePersonContext()

  // Fetch genders for opposite gender calculation
  const { data: genders, isLoading: isGendersLoading } = useQuery({
    queryKey: ["genders"],
    queryFn: () => PersonMetadataService.getGenders(),
  })

  // Fetch active person's complete details (includes religion with names and IDs)
  const { data: personDetails, isLoading: isPersonDetailsLoading } = useQuery({
    queryKey: ["personCompleteDetails", activePersonId],
    queryFn: () =>
      PersonService.getPersonCompleteDetails({ personId: activePersonId! }),
    enabled: !!activePersonId,
  })

  // Fetch parents to find mother (using person_id based endpoint)
  const { data: parents, isLoading: isParentsLoading } = useQuery({
    queryKey: ["parentsByPersonId", activePersonId],
    queryFn: () =>
      RelativesService.getParentsByPersonId({ personId: activePersonId! }),
    enabled: !!activePersonId,
  })

  // Find mother from parents (relationship_type === "MOTHER")
  const motherRelation = parents?.find((p) => p.relationship_type === "MOTHER")
  const motherId = motherRelation?.related_person_id

  // Fetch mother's complete details
  const { data: motherDetails, isLoading: isMotherDetailsLoading } = useQuery({
    queryKey: ["personCompleteDetails", motherId],
    queryFn: () =>
      PersonService.getPersonCompleteDetails({ personId: motherId! }),
    enabled: !!motherId,
  })

  // Fetch mother's parents to find maternal grandmother (using person_id based endpoint)
  const { data: motherParents, isLoading: isMotherParentsLoading } = useQuery({
    queryKey: ["parentsByPersonId", motherId],
    queryFn: () =>
      RelativesService.getParentsByPersonId({ personId: motherId! }),
    enabled: !!motherId,
  })

  // Find maternal grandmother (mother's mother)
  const grandmotherRelation = motherParents?.find(
    (p) => p.relationship_type === "MOTHER",
  )
  const grandmotherId = grandmotherRelation?.related_person_id

  // Fetch grandmother's complete details
  const { data: grandmotherDetails, isLoading: isGrandmotherDetailsLoading } =
    useQuery({
      queryKey: ["personCompleteDetails", grandmotherId],
      queryFn: () =>
        PersonService.getPersonCompleteDetails({ personId: grandmotherId! }),
      enabled: !!grandmotherId,
    })

  // Fetch religion metadata to get IDs from names (fallback)
  const { data: religions, isLoading: isReligionsLoading } = useQuery({
    queryKey: ["religions"],
    queryFn: () => ReligionMetadataService.getReligions(),
  })

  // Calculate loading state
  const isLoading =
    isGendersLoading ||
    isPersonDetailsLoading ||
    isParentsLoading ||
    (!!motherId && isMotherDetailsLoading) ||
    (!!motherId && isMotherParentsLoading) ||
    (!!grandmotherId && isGrandmotherDetailsLoading) ||
    isReligionsLoading

  // Build active person defaults - now using IDs directly from API
  const activePersonDefaults: ActivePersonDefaults = {
    genderId: activePerson?.gender_id || null,
    birthYear: extractBirthYear(activePerson?.date_of_birth),
    religionId: personDetails?.religion?.religion_id || null,
    religionName: personDetails?.religion?.religion_name || null,
    categoryId: personDetails?.religion?.category_id || null,
    categoryName: personDetails?.religion?.category_name || null,
    subCategoryId: personDetails?.religion?.sub_category_id || null,
    subCategoryName: personDetails?.religion?.sub_category_name || null,
  }

  // Build lineage sub-categories for exclusion - now with IDs from API
  const lineageSubCategories: LineageSubCategories = {
    selfSubCategory: null,
    motherSubCategory: null,
    grandmotherSubCategory: null,
  }

  // Self sub-category (with ID from API)
  if (personDetails?.religion?.sub_category_name) {
    lineageSubCategories.selfSubCategory = {
      id: personDetails.religion.sub_category_id || "",
      name: personDetails.religion.sub_category_name,
    }
  }

  // Mother's sub-category (with ID from API)
  if (motherDetails?.religion?.sub_category_name) {
    lineageSubCategories.motherSubCategory = {
      id: motherDetails.religion.sub_category_id || "",
      name: motherDetails.religion.sub_category_name,
    }
  }

  // Grandmother's sub-category (with ID from API)
  if (grandmotherDetails?.religion?.sub_category_name) {
    lineageSubCategories.grandmotherSubCategory = {
      id: grandmotherDetails.religion.sub_category_id || "",
      name: grandmotherDetails.religion.sub_category_name,
    }
  }

  // Convert genders to GenderMetadata format
  const genderMetadata: GenderMetadata[] =
    genders?.map((g) => ({
      genderId: g.genderId,
      genderCode: g.genderCode,
      genderName: g.genderName,
    })) || []

  // Build default filters
  const defaultFilters: PartnerFilters = buildDefaultFilters(
    activePersonDefaults,
    lineageSubCategories,
    genderMetadata,
  )

  return {
    defaultFilters,
    isLoading,
    activePersonDefaults,
    lineageSubCategories,
    genders: genderMetadata,
  }
}
