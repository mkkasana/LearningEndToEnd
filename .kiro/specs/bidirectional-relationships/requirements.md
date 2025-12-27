# Requirements Document

## Introduction

This specification addresses the need for bidirectional relationship management in the family tree system. Currently, when Person A creates a relationship with Person B (e.g., A → B as Son), only the single-direction relationship is stored. This means B's family tree appears incomplete as it doesn't show A as their parent. This refactoring implements automatic creation of inverse relationships to ensure complete family trees from any person's perspective.

## Glossary

- **Person**: An individual in the system, may or may not have a user account
- **Relationship**: A connection between two persons (e.g., father-son, mother-daughter)
- **Primary Relationship**: The relationship created by the user (A → B)
- **Inverse Relationship**: The automatically created reciprocal relationship (B → A)
- **Relationship Type**: The nature of the relationship (Father, Mother, Son, Daughter, Spouse, etc.)
- **Bidirectional Relationship**: A pair of relationships where both directions are stored
- **Gender Mapping**: The system's mapping of gender_id to gender labels (male/female)

## Requirements

### Requirement 1

**User Story:** As a user, I want the system to automatically create reciprocal relationships, so that family trees are complete from any person's perspective.

#### Acceptance Criteria

1. WHEN a user creates a relationship from Person A to Person B THEN the system SHALL create both the primary relationship (A → B) and the inverse relationship (B → A)
2. WHEN the system creates an inverse relationship THEN the system SHALL determine the correct inverse relationship type based on the primary relationship type and both persons' genders
3. WHEN a user queries Person B's relationships THEN the system SHALL return Person A with the correct inverse relationship type
4. WHEN a user creates a Father relationship THEN the system SHALL create a Son or Daughter inverse relationship based on the child's gender
5. WHEN a user creates a Mother relationship THEN the system SHALL create a Son or Daughter inverse relationship based on the child's gender
6. Once implementation complete, Make sure use logger and have proper logging in newly added backend business logic.

### Requirement 2

**User Story:** As a user, I want relationship updates to affect both directions, so that data remains consistent across the family tree.

#### Acceptance Criteria

1. WHEN a user updates a relationship's is_active status THEN the system SHALL update both the primary and inverse relationships
2. WHEN a user updates a relationship's start_date or end_date THEN the system SHALL update both the primary and inverse relationships
3. WHEN a user updates a relationship THEN the system SHALL maintain the correct relationship types for both directions
4. WHEN the system cannot find an inverse relationship during update THEN the system SHALL log a warning and continue with the primary update
5. WHEN a user updates a relationship THEN the system SHALL update the updated_at timestamp for both relationships
6. Once implementation complete, Make sure use logger and have proper logging in newly added backend business logic.

### Requirement 3

**User Story:** As a user, I want relationship deletions to remove both directions, so that orphaned relationships don't exist in the system.

#### Acceptance Criteria

1. WHEN a user deletes a relationship THEN the system SHALL delete both the primary and inverse relationships
2. WHEN the system deletes a relationship THEN the system SHALL use a database transaction to ensure both deletions succeed or both fail
3. WHEN the inverse relationship is not found during deletion THEN the system SHALL log a warning and continue with the primary deletion
4. WHEN a relationship deletion fails THEN the system SHALL rollback all changes and return an error to the user
5. WHEN a user soft-deletes a relationship (sets is_active=false) THEN the system SHALL soft-delete both directions
6. Once implementation complete, Make sure use logger and have proper logging in newly added backend business logic.

### Requirement 4

**User Story:** As a developer, I want a clear mapping of relationship types to their inverses, so that the system correctly determines reciprocal relationships.

#### Relationship Semantics

- `person_id` = the person who owns/creates the relationship
- `related_person_id` = the person they're related to
- `relationship_type` = describes who the related_person IS TO the person
- Example: A → B (Father) means "B is A's father", NOT "A is B's father"
- Inverse: B → A (Son/Daughter based on A's gender) means "A is B's son/daughter"

#### Acceptance Criteria

1. WHEN the system needs an inverse relationship type THEN the system SHALL use a defined mapping function that considers both relationship type and genders
2. WHEN a Father relationship is created (A → B as Father, meaning "B is A's father") THEN the system SHALL create a Son inverse if A is male or Daughter inverse if A is female (B → A as Son/Daughter, meaning "A is B's son/daughter")
3. WHEN a Mother relationship is created (A → B as Mother, meaning "B is A's mother") THEN the system SHALL create a Son inverse if A is male or Daughter inverse if A is female (B → A as Son/Daughter, meaning "A is B's son/daughter")
4. WHEN a Son relationship is created (A → B as Son, meaning "B is A's son") THEN the system SHALL create a Father inverse if A is male or Mother inverse if A is female (B → A as Father/Mother, meaning "A is B's father/mother")
5. WHEN a Daughter relationship is created (A → B as Daughter, meaning "B is A's daughter") THEN the system SHALL create a Father inverse if A is male or Mother inverse if A is female (B → A as Father/Mother, meaning "A is B's father/mother")
6. WHEN a Husband relationship is created (A → B as Husband, meaning "B is A's husband") THEN the system SHALL create a Wife inverse relationship (B → A as Wife, meaning "A is B's wife")
7. WHEN a Wife relationship is created (A → B as Wife, meaning "B is A's wife") THEN the system SHALL create a Husband inverse relationship (B → A as Husband, meaning "A is B's husband")
8. WHEN a Spouse relationship is created (A → B as Spouse, meaning "B is A's spouse") THEN the system SHALL create a Spouse inverse relationship (B → A as Spouse, meaning "A is B's spouse")
9. Once implementation complete, Make sure use logger and have proper logging in newly added backend business logic.

### Requirement 5

**User Story:** As a developer, I want to migrate existing single-direction relationships to bidirectional, so that historical data is complete.

#### Acceptance Criteria

1. WHEN a migration script is executed THEN the system SHALL identify all relationships that lack an inverse relationship
2. WHEN the migration script processes a relationship THEN the system SHALL create the missing inverse relationship with the correct type
3. WHEN the migration script encounters an error THEN the system SHALL log the error and continue processing remaining relationships
4. WHEN the migration script completes THEN the system SHALL report the number of inverse relationships created
5. WHEN the migration script runs on already-migrated data THEN the system SHALL skip relationships that already have inverses

### Requirement 6

**User Story:** As a developer, I want comprehensive tests for bidirectional relationships, so that the system behavior is verified and regressions are prevented.

#### Acceptance Criteria

1. WHEN tests are executed THEN the system SHALL verify that creating a relationship creates both directions
2. WHEN tests are executed THEN the system SHALL verify that updating a relationship updates both directions
3. WHEN tests are executed THEN the system SHALL verify that deleting a relationship deletes both directions
4. WHEN tests are executed THEN the system SHALL verify correct inverse relationship types for all relationship type combinations
5. WHEN tests are executed THEN the system SHALL verify that gender is correctly considered when determining inverse types
