# Requirements Document

## Introduction

The Partner Match Finder feature enables users to discover potential marriage matches within their extended family network. It respects cultural and religious compatibility rules common in traditional societies (like Hindu gotra system, Islamic practices, etc.) where marriages are preferred within the same religion/caste but must exclude certain sub-castes (gotras) - typically the seeker's own, their mother's, and grandmother's lineages.

The system performs a BFS traversal from the seeker through family relationships, filtering candidates based on religion, age, gender, and gotra exclusion rules, returning a traversable graph that shows how each match is connected to the seeker.

## Glossary

- **Seeker**: The person looking for potential marriage matches
- **Match_Candidate**: A person who passes all eligibility filters
- **Partner_Match_Service**: The backend service that performs BFS traversal and filtering
- **Partner_Match_Request**: Input model containing seeker ID and all filter criteria
- **Partner_Match_Response**: Output model containing matches and exploration graph
- **Exploration_Graph**: Tree structure showing all visited nodes with relationship edges
- **Graph_Node**: A person node in the exploration graph with connection metadata
- **Connection_Edge**: Represents the relationship between two adjacent nodes (e.g., "Father", "Son")
- **Gotra**: Sub-caste/clan identifier (religion_sub_category_id in the system)
- **Max_Depth**: Maximum BFS traversal depth (number of relationship hops)

## Requirements

### Requirement 1: Partner Match Search API

**User Story:** As a user, I want to search for potential marriage matches within my family network, so that I can find culturally compatible partners who are connected through known relationships.

#### Acceptance Criteria

1. WHEN a user submits a partner match request with seeker_person_id, THE Partner_Match_Service SHALL validate that the seeker exists in the database
2. IF the seeker_person_id does not exist, THEN THE Partner_Match_Service SHALL return a 404 error with message "Seeker person not found"
3. WHEN a valid request is submitted, THE Partner_Match_Service SHALL perform BFS traversal starting from the seeker up to the specified max_depth
4. THE Partner_Match_Service SHALL return a Partner_Match_Response containing the exploration graph and list of eligible matches

### Requirement 2: Gender Filter

**User Story:** As a user, I want to filter matches by gender, so that I only see candidates of the gender I'm seeking.

#### Acceptance Criteria

1. WHEN target_gender_code is provided in the request, THE Partner_Match_Service SHALL only include candidates whose gender matches the specified code
2. THE Partner_Match_Service SHALL use the gender_id foreign key on Person to lookup gender and compare against the provided gender code

### Requirement 3: Age/Birth Year Filter

**User Story:** As a user, I want to filter matches by birth year range, so that I find age-appropriate candidates.

#### Acceptance Criteria

1. WHEN birth_year_min is provided, THE Partner_Match_Service SHALL exclude candidates born before that year
2. WHEN birth_year_max is provided, THE Partner_Match_Service SHALL exclude candidates born after that year
3. WHEN both birth_year_min and birth_year_max are provided, THE Partner_Match_Service SHALL only include candidates born within that range (inclusive)

### Requirement 4: Religion Inclusion Filter

**User Story:** As a user, I want to filter matches by religion, category, and sub-category inclusion lists, so that I find religiously compatible candidates.

#### Acceptance Criteria

1. WHEN include_religion_ids list is provided and non-empty, THE Partner_Match_Service SHALL only include candidates whose religion_id matches one of the provided IDs
2. WHEN include_category_ids list is provided and non-empty, THE Partner_Match_Service SHALL only include candidates whose religion_category_id matches one of the provided IDs
3. WHEN include_sub_category_ids list is provided and non-empty, THE Partner_Match_Service SHALL only include candidates whose religion_sub_category_id matches one of the provided IDs
4. WHEN multiple inclusion filters are provided, THE Partner_Match_Service SHALL apply them with AND logic (candidate must satisfy all provided filters)

### Requirement 5: Gotra/Sub-Category Exclusion Filter

**User Story:** As a user, I want to exclude specific sub-categories (gotras) from matches, so that I respect cultural rules about prohibited marriages within certain lineages.

#### Acceptance Criteria

1. WHEN exclude_sub_category_ids list is provided and non-empty, THE Partner_Match_Service SHALL exclude any candidate whose religion_sub_category_id matches any of the provided IDs
2. THE Partner_Match_Service SHALL apply exclusion filter after inclusion filters
3. THE Partner_Match_Service SHALL continue BFS traversal through excluded persons (they are not matches but their relatives might be)

### Requirement 6: Living Person Filter

**User Story:** As a user, I want to only see living candidates, so that I get practical match suggestions.

#### Acceptance Criteria

1. THE Partner_Match_Service SHALL exclude any candidate where date_of_death is not null
2. THE Partner_Match_Service SHALL continue BFS traversal through deceased persons (their living relatives might be matches)

### Requirement 7: Marital Status Filter

**User Story:** As a user, I want to only see unmarried candidates, so that I get available match suggestions.

#### Acceptance Criteria

1. THE Partner_Match_Service SHALL check if a candidate has any active relationship of type WIFE, HUSBAND, or SPOUSE
2. THE Partner_Match_Service SHALL check if a candidate has any active relationship of type SON or DAUGHTER (indicating they have children)
3. IF a candidate has any spouse relationship OR has children, THEN THE Partner_Match_Service SHALL exclude them from matches
4. THE Partner_Match_Service SHALL continue BFS traversal through married/parent persons (their unmarried relatives might be matches)

### Requirement 8: Exploration Graph Response

**User Story:** As a user, I want to see how each match is connected to me through the family network, so that I can understand the relationship path.

#### Acceptance Criteria

1. THE Partner_Match_Service SHALL return an exploration_graph containing all visited persons during BFS traversal
2. EACH Graph_Node in the exploration_graph SHALL contain: person_id, first_name, last_name, birth_year, death_year, address, religion, is_match flag, and depth from seeker
3. EACH Graph_Node SHALL contain from_person connection info (parent node in BFS tree) with person_id and relationship type
4. EACH Graph_Node SHALL contain to_persons list (child nodes explored from this node) with person_id and relationship type for each
5. THE exploration_graph SHALL be keyed by person_id for O(1) lookup
6. THE Partner_Match_Service SHALL include the seeker node in the graph with from_person as null

### Requirement 9: Match Summary

**User Story:** As a user, I want a quick summary of matches found, so that I can see results at a glance.

#### Acceptance Criteria

1. THE Partner_Match_Response SHALL include total_matches count
2. THE Partner_Match_Response SHALL include a matches list containing only the person_ids of eligible candidates
3. THE Partner_Match_Response SHALL include the seeker_id for reference

### Requirement 10: Depth Configuration

**User Story:** As a user, I want to control how deep the search goes, so that I can balance between finding more matches and search performance.

#### Acceptance Criteria

1. WHEN max_depth is provided in the request, THE Partner_Match_Service SHALL limit BFS traversal to that many relationship hops
2. IF max_depth is not provided, THE Partner_Match_Service SHALL use a default value from application configuration
3. THE Partner_Match_Service SHALL enforce a maximum allowed depth from configuration to prevent excessive traversal

### Requirement 11: Separate API Route

**User Story:** As a developer, I want the partner match API in a separate route file, so that the codebase remains organized and maintainable.

#### Acceptance Criteria

1. THE Partner_Match_Service SHALL be exposed via a dedicated route file (e.g., `/api/v1/partner-match/`)
2. THE route file SHALL not modify or depend on existing lineage path route files
3. THE Partner_Match_Service SHALL have its own service class, schemas, and repository components

## Future Plans

The following enhancements are planned for future iterations:

### Marital Status Field
- Add explicit `marital_status` field to Person model
- Replace relationship-based marriage detection with direct field check
- Support statuses: Single, Married, Divorced, Widowed

### Background Job Processing
- Convert synchronous API to async job submission
- User submits search request → receives job_id
- Job runs in background, stores results in database
- Results served via paginated API using job_id
- Enables handling of large family networks without timeout issues

### Address Proximity Filters
- Add optional `include_state_ids` filter
- Add optional `include_district_ids` filter
- Allow users to find matches in specific geographic regions

### Match Scoring/Ranking
- Score matches based on multiple factors (distance, age compatibility, etc.)
- Return matches sorted by relevance score

### Saved Searches
- Allow users to save search criteria
- Re-run saved searches periodically
- Notify users of new matches
