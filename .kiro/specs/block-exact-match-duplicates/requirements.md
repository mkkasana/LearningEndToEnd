# Requirements Document

## Introduction

This feature enhances the "Add Family Member" flow to prevent users from creating duplicate person records when an exact match already exists in the system. Currently, users can proceed to create a new person even when a 100% match is found. This enhancement will block that action and require users to connect to the existing person instead.

## Glossary

- **Person_Matching_Service**: The backend service that searches for existing persons matching provided criteria
- **Match_Score**: A numerical value (0-100) representing how closely a person's name matches the search criteria
- **Exact_Match**: A match where the name match score is 100% AND the date of birth matches exactly
- **Connect_Existing_Person_Step**: The frontend component (Step 4) that displays matching persons and allows users to connect or create new
- **High_Confidence_Match**: A match with score ≥95% that strongly suggests the same person
- **Date_Of_Birth_Match**: When the searched date of birth exactly equals the person's date of birth

## Requirements

### Requirement 1: Detect Exact Match Condition

**User Story:** As a system administrator, I want the system to detect when an exact match exists, so that duplicate person records can be prevented.

#### Acceptance Criteria

1. WHEN a person search returns results with a match_score of 100 AND the date_of_birth matches exactly, THE Connect_Existing_Person_Step SHALL identify this as an exact match condition
2. WHEN a person search returns results with a match_score of 100 BUT the date_of_birth does NOT match, THE Connect_Existing_Person_Step SHALL NOT treat this as an exact match
3. WHEN multiple exact matches exist (score = 100 AND date_of_birth match), THE Connect_Existing_Person_Step SHALL treat all of them as blocking matches
4. WHEN no exact match exists (either score < 100 OR date_of_birth mismatch), THE Connect_Existing_Person_Step SHALL allow the user to proceed with creating a new person

### Requirement 2: Block Creation for Exact Matches

**User Story:** As a user, I want to be prevented from creating duplicate persons, so that the family tree data remains clean and accurate.

#### Acceptance Criteria

1. WHEN an exact match (score = 100 AND date_of_birth match) is detected, THE Connect_Existing_Person_Step SHALL disable the "Create New Person" button
2. WHEN an exact match is detected, THE Connect_Existing_Person_Step SHALL display a clear message explaining why creation is blocked
3. WHEN an exact match is detected, THE Connect_Existing_Person_Step SHALL highlight the exact match result visually
4. WHEN no exact match exists (score < 100 OR date_of_birth mismatch), THE Connect_Existing_Person_Step SHALL allow the user to proceed with creating a new person

### Requirement 3: Guide User to Connect

**User Story:** As a user, I want clear guidance on how to proceed when an exact match is found, so that I can complete adding my family member.

#### Acceptance Criteria

1. WHEN an exact match is blocked, THE Connect_Existing_Person_Step SHALL display a message instructing the user to connect to the existing person
2. WHEN an exact match is blocked, THE Connect_Existing_Person_Step SHALL keep the "Connect" button enabled for the exact match
3. WHEN the user connects to an exact match, THE System SHALL create the relationship and complete the flow successfully

### Requirement 4: Handle Already Connected Exact Matches

**User Story:** As a user, I want appropriate handling when an exact match is already connected to me, so that I understand why I cannot proceed.

#### Acceptance Criteria

1. WHEN an exact match (score = 100 AND date_of_birth match) exists AND is already connected to the user, THE Connect_Existing_Person_Step SHALL display a message indicating the person is already in their family
2. WHEN an exact match exists AND is already connected, THE Connect_Existing_Person_Step SHALL disable both "Connect" and "Create New" buttons
3. WHEN an exact match exists AND is already connected, THE Connect_Existing_Person_Step SHALL provide a "Back" option to modify the search criteria

### Requirement 5: Visual Feedback for Exact Matches

**User Story:** As a user, I want visual indicators for exact matches, so that I can easily identify them in the results list.

#### Acceptance Criteria

1. WHEN displaying an exact match result, THE Connect_Existing_Person_Step SHALL show a distinct visual indicator (badge or highlight)
2. WHEN displaying an exact match result, THE Connect_Existing_Person_Step SHALL position it at the top of the results list
3. WHEN displaying match results, THE Connect_Existing_Person_Step SHALL show the match score percentage for each result
