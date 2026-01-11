# Requirements Document

## Introduction

This document defines requirements for improving backend unit test coverage for files currently below 80% coverage. The goal is to achieve comprehensive test coverage across all backend modules to ensure code reliability and maintainability.

## Glossary

- **Test_Coverage_System**: The pytest and coverage tooling that measures code execution during tests
- **Unit_Test**: An automated test that verifies a single unit of code in isolation
- **Integration_Test**: An automated test that verifies multiple components working together
- **API_Route**: A FastAPI endpoint that handles HTTP requests
- **Service**: A business logic layer component that orchestrates operations
- **Repository**: A data access layer component that interacts with the database

## Requirements

### Requirement 1: Person Relatives API Coverage (75% → 90%+)

**User Story:** As a developer, I want comprehensive tests for the person relatives API routes, so that I can ensure family relationship queries work correctly.

#### Acceptance Criteria

1. WHEN a GET request is made to `/{user_id}/parents` with a valid user_id, THE Test_Coverage_System SHALL verify the endpoint returns parent relationships
2. WHEN a GET request is made to `/{user_id}/parents` with a non-existent user_id, THE Test_Coverage_System SHALL verify a 404 error is returned
3. WHEN a GET request is made to `/{user_id}/children` with a valid user_id, THE Test_Coverage_System SHALL verify the endpoint returns child relationships
4. WHEN a GET request is made to `/{user_id}/children` with a non-existent user_id, THE Test_Coverage_System SHALL verify a 404 error is returned
5. WHEN a GET request is made to `/{user_id}/spouses` with a valid user_id, THE Test_Coverage_System SHALL verify the endpoint returns spouse relationships
6. WHEN a GET request is made to `/{user_id}/spouses` with a non-existent user_id, THE Test_Coverage_System SHALL verify a 404 error is returned
7. WHEN a GET request is made to `/{user_id}/siblings` with a valid user_id, THE Test_Coverage_System SHALL verify the endpoint returns sibling relationships
8. WHEN a GET request is made to `/{user_id}/siblings` with a non-existent user_id, THE Test_Coverage_System SHALL verify a 404 error is returned

### Requirement 2: Person Service Coverage (74% → 90%+)

**User Story:** As a developer, I want comprehensive tests for the person service, so that I can ensure person management operations work correctly.

#### Acceptance Criteria

1. WHEN `get_person_complete_details` is called with a valid person_id, THE Test_Coverage_System SHALL verify complete person details including gender, address, and religion are returned
2. WHEN `get_person_complete_details` is called with a non-existent person_id, THE Test_Coverage_System SHALL verify None is returned
3. WHEN `_resolve_address_details` is called for a person with a current address, THE Test_Coverage_System SHALL verify all location names are resolved correctly
4. WHEN `_resolve_address_details` is called for a person without an address, THE Test_Coverage_System SHALL verify None is returned
5. WHEN `_resolve_religion_details` is called for a person with religion data, THE Test_Coverage_System SHALL verify religion names are resolved correctly
6. WHEN `_resolve_religion_details` is called for a person without religion data, THE Test_Coverage_System SHALL verify None is returned

### Requirement 3: Relationship Type Enum Coverage (74% → 90%+)

**User Story:** As a developer, I want comprehensive tests for the relationship type enum, so that I can ensure relationship type lookups work correctly.

#### Acceptance Criteria

1. WHEN `from_label` is called with a valid label like "Father", THE Test_Coverage_System SHALL verify the correct RelationshipType enum is returned
2. WHEN `from_label` is called with an invalid label, THE Test_Coverage_System SHALL verify None is returned
3. WHEN `get_all_labels` is called, THE Test_Coverage_System SHALL verify all relationship labels are returned as a dictionary
4. WHEN `label_id_relation` function is called, THE Test_Coverage_System SHALL verify the ID to label mapping is returned
5. WHEN `relation_label_id` function is called, THE Test_Coverage_System SHALL verify the label to ID mapping is returned

### Requirement 4: Person Relationship Service Coverage (81% → 90%+)

**User Story:** As a developer, I want comprehensive tests for the person relationship service, so that I can ensure bidirectional relationship management works correctly.

#### Acceptance Criteria

1. WHEN `create_relationship` is called with valid data, THE Test_Coverage_System SHALL verify both primary and inverse relationships are created
2. WHEN `create_relationship` is called with missing gender information, THE Test_Coverage_System SHALL verify only the primary relationship is created with a warning
3. WHEN `update_relationship` is called, THE Test_Coverage_System SHALL verify both primary and inverse relationships are updated
4. WHEN `update_relationship` is called and inverse relationship is not found, THE Test_Coverage_System SHALL verify the primary relationship is still updated
5. WHEN `delete_relationship` is called with soft_delete=True, THE Test_Coverage_System SHALL verify both relationships are marked inactive
6. WHEN `delete_relationship` is called with soft_delete=False, THE Test_Coverage_System SHALL verify both relationships are hard deleted

### Requirement 5: Person Matching Service Coverage (64% → 85%+)

**User Story:** As a developer, I want comprehensive tests for the person matching service, so that I can ensure duplicate detection works correctly.

#### Acceptance Criteria

1. WHEN `calculate_name_match_score` is called with identical names, THE Test_Coverage_System SHALL verify a score of 100 is returned
2. WHEN `calculate_name_match_score` is called with completely different names, THE Test_Coverage_System SHALL verify a low score is returned
3. WHEN `_find_persons_by_address` is called with required criteria only, THE Test_Coverage_System SHALL verify persons matching country, state, and district are returned
4. WHEN `_find_persons_by_address` is called with all criteria, THE Test_Coverage_System SHALL verify exact address matches are returned
5. WHEN `_find_persons_by_religion` is called with required criteria only, THE Test_Coverage_System SHALL verify persons matching religion are returned
6. WHEN `search_matching_persons` is called, THE Test_Coverage_System SHALL verify results are filtered, scored, and sorted correctly

### Requirement 6: Person Discovery Service Coverage (56% → 85%+)

**User Story:** As a developer, I want comprehensive tests for the person discovery service, so that I can ensure family member suggestions work correctly.

#### Acceptance Criteria

1. WHEN `discover_family_members` is called for a user with spouses, THE Test_Coverage_System SHALL verify spouse's children are suggested as user's children
2. WHEN `discover_family_members` is called for a user with parents, THE Test_Coverage_System SHALL verify parent's spouse is suggested as user's parent
3. WHEN `discover_family_members` is called for a user with children, THE Test_Coverage_System SHALL verify child's other parent is suggested as user's spouse
4. WHEN `_infer_child_relationship` is called with a female gender_id, THE Test_Coverage_System SHALL verify DAUGHTER is returned
5. WHEN `_infer_child_relationship` is called with a male gender_id, THE Test_Coverage_System SHALL verify SON is returned
6. WHEN `_infer_parent_relationship` is called with a female gender_id, THE Test_Coverage_System SHALL verify MOTHER is returned
7. WHEN `_infer_parent_relationship` is called with a male gender_id, THE Test_Coverage_System SHALL verify FATHER is returned
8. WHEN `_sort_and_limit_discoveries` is called with duplicate persons, THE Test_Coverage_System SHALL verify deduplication keeps the best result

### Requirement 7: Relationship Helper Coverage (82% → 90%+)

**User Story:** As a developer, I want comprehensive tests for the relationship helper utilities, so that I can ensure inverse relationship type determination works correctly.

#### Acceptance Criteria

1. WHEN `get_inverse_type` is called for a FATHER relationship, THE Test_Coverage_System SHALL verify SON or DAUGHTER is returned based on person's gender
2. WHEN `get_inverse_type` is called for a MOTHER relationship, THE Test_Coverage_System SHALL verify SON or DAUGHTER is returned based on person's gender
3. WHEN `get_inverse_type` is called for a SPOUSE relationship, THE Test_Coverage_System SHALL verify SPOUSE is returned
4. WHEN `get_inverse_type` is called with unknown relationship type, THE Test_Coverage_System SHALL verify None is returned

### Requirement 8: Person Metadata API Coverage (68% → 85%+)

**User Story:** As a developer, I want comprehensive tests for the person metadata API routes, so that I can ensure metadata management works correctly.

#### Acceptance Criteria

1. WHEN metadata endpoints are called with valid data, THE Test_Coverage_System SHALL verify successful responses
2. WHEN metadata endpoints are called with invalid data, THE Test_Coverage_System SHALL verify appropriate error responses
3. WHEN metadata endpoints are called without authentication, THE Test_Coverage_System SHALL verify 401 errors are returned

### Requirement 9: Person API Routes Coverage (53% → 80%+)

**User Story:** As a developer, I want comprehensive tests for the main person API routes, so that I can ensure person CRUD operations work correctly.

#### Acceptance Criteria

1. WHEN person creation endpoints are called with valid data, THE Test_Coverage_System SHALL verify persons are created correctly
2. WHEN person update endpoints are called with valid data, THE Test_Coverage_System SHALL verify persons are updated correctly
3. WHEN person deletion endpoints are called, THE Test_Coverage_System SHALL verify persons are deleted correctly
4. WHEN person query endpoints are called, THE Test_Coverage_System SHALL verify correct data is returned
5. WHEN endpoints are called without proper authorization, THE Test_Coverage_System SHALL verify appropriate error responses
