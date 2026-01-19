# Implementation Plan: Partner Match Finder

## Overview

Implementation of the Partner Match Finder backend API using Python/FastAPI. The feature will have its own dedicated route, service, and schema files following the existing project patterns.

## Tasks

- [x] 1. Create schema definitions
  - [x] 1.1 Create `app/schemas/partner_match/__init__.py` and `partner_match_schemas.py`
    - Define `PartnerMatchRequest` with all filter fields
    - Define `MatchConnectionInfo` for relationship edges
    - Define `MatchGraphNode` with person data and connections
    - Define `PartnerMatchResponse` with matches and exploration_graph
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3_

- [x] 2. Create service implementation
  - [x] 2.1 Create `app/services/partner_match/__init__.py` and `partner_match_service.py`
    - Implement `PartnerMatchService` class with session dependency
    - Implement `find_matches()` main entry point
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [x] 2.2 Implement BFS exploration method
    - Implement `_bfs_explore()` with parent_map, depth_map tracking
    - Use deque for level-by-level traversal
    - Respect max_depth limit
    - _Requirements: 1.3, 10.1, 10.2, 10.3_

  - [x] 2.3 Implement filter methods
    - Implement `_is_eligible_match()` orchestrating all filters
    - Implement `_matches_gender()` for gender check
    - Implement `_in_birth_year_range()` for age check
    - Implement `_passes_religion_filters()` for inclusion/exclusion
    - Implement `_is_married_or_has_children()` for marital status
    - _Requirements: 2.1, 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 6.1, 7.1, 7.2, 7.3_

  - [x] 2.4 Implement graph building method
    - Implement `_build_exploration_tree()` from BFS results
    - Set from_person and to_persons for each node
    - Mark is_match flag for eligible candidates
    - Include depth for each node
    - _Requirements: 8.1, 8.3, 8.4, 8.5, 8.6_

  - [x] 2.5 Implement helper methods
    - Implement `_get_person()` for person lookup
    - Implement `_get_relationships()` for relationship traversal
    - Implement `_get_relationship_type()` for edge labels
    - Implement `_get_person_religion()` for religion data lookup
    - Implement `_enrich_node_data()` for person details (reuse patterns from LineagePathService)
    - _Requirements: 2.2, 8.2_

- [x] 3. Create API route
  - [x] 3.1 Create `app/api/routes/partner_match.py`
    - Define POST `/find` endpoint
    - Add request validation
    - Wire up service dependency
    - _Requirements: 11.1, 11.2, 11.3_

  - [x] 3.2 Register route in main router
    - Add partner_match router to `app/api/main.py`
    - Use prefix `/api/v1/partner-match`
    - _Requirements: 11.1_

- [x] 4. Add configuration
  - [x] 4.1 Add config settings for partner match
    - Add `PARTNER_MATCH_DEFAULT_DEPTH` to settings
    - Add `PARTNER_MATCH_MAX_DEPTH` to settings
    - _Requirements: 10.2, 10.3_

- [x] 5. Checkpoint - Verify basic functionality
  - Ensure service can be instantiated
  - Ensure route is accessible
  - Ensure schemas serialize correctly
  - Ask the user if questions arise

- [x] 6. Write unit tests
  - [x] 6.1 Create `tests/services/partner_match/test_partner_match_service.py`
    - Test seeker validation (404 for non-existent)
    - Test gender filter
    - Test birth year range filter
    - Test religion inclusion filters
    - Test gotra exclusion filter
    - Test living person filter
    - Test marital status filter
    - Test graph structure (from_person, to_persons)
    - _Requirements: 1.1, 1.2, 2.1, 3.1, 3.2, 4.1, 5.1, 6.1, 7.1, 7.2, 8.3, 8.4_

  - [ ]* 6.2 Write property test for depth constraint
    - **Property 1: Depth Constraint**
    - **Validates: Requirements 1.3, 10.1**

  - [ ]* 6.3 Write property test for filter correctness
    - **Property 2: Gender Filter Correctness**
    - **Property 3: Birth Year Range Correctness**
    - **Property 5: Gotra Exclusion Correctness**
    - **Property 6: Living Person Correctness**
    - **Property 7: Marital Status Correctness**
    - **Validates: Requirements 2.1, 3.1, 3.2, 5.1, 6.1, 7.1, 7.2**

  - [ ]* 6.4 Write property test for graph integrity
    - **Property 9: Graph Structure Integrity**
    - **Property 10: Response Consistency**
    - **Validates: Requirements 8.1, 8.3, 8.4, 8.6, 9.1, 9.2, 9.3**

- [x] 7. Final checkpoint - Ensure all tests pass
  - Run `hatch run build-all` to verify
  - Ensure all unit tests pass
  - Ask the user if questions arise

- [x] 8. Implement Graph Pruning Optimization
  - [x] 8.1 Add `prune_graph` parameter to `PartnerMatchRequest` schema
    - Default value: `True`
    - _Requirements: 12.1, 12.2_

  - [x] 8.2 Implement `_prune_graph()` method in `PartnerMatchService`
    - Trace back from each match to seeker via `from_person` links
    - Collect all nodes on paths to matches
    - Filter graph to only include collected nodes
    - Update `to_persons` lists to only reference kept nodes
    - Handle edge case: no matches (return only seeker node)
    - _Requirements: 12.1, 12.3, 12.4, 12.5_

  - [x] 8.3 Update `find_matches()` to use pruning
    - Call `_prune_graph()` when `request.prune_graph` is True
    - Pass through unpruned graph when `prune_graph` is False
    - _Requirements: 12.1, 12.2_

  - [x] 8.4 Write unit tests for graph pruning
    - Test pruned graph only contains path nodes
    - Test seeker always included
    - Test no matches returns only seeker
    - Test `prune_graph=False` returns full graph
    - _Requirements: 12.1, 12.2, 12.4, 12.5, 12.6_

- [x] 9. Final checkpoint - Verify pruning tests pass
  - Run `hatch run build-all` to verify
  - Ensure all unit tests pass
  - Regenerate OpenAPI client if schema changed

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Follow existing patterns from `lineage_path` service but keep components separate
