# Implementation Plan: Lineage Path Finder

## Overview

This implementation plan covers the backend API for finding lineage paths between two persons in the family tree. The feature uses Bidirectional BFS to find common ancestors and returns a graph structure for UI rendering.

## Tasks

- [x] 1. Set up project structure and configuration
  - [x] 1.1 Add LINEAGE_PATH_MAX_DEPTH configuration to settings
    - Add new field to `app/core/config.py` Settings class
    - Default value: 10
    - Environment variable: `LINEAGE_PATH_MAX_DEPTH`
    - _Requirements: 1.5_

  - [x] 1.2 Create directory structure for lineage_path module
    - Create `app/api/routes/lineage_path/` directory with `__init__.py`
    - Create `app/services/lineage_path/` directory with `__init__.py`
    - Create `app/schemas/lineage_path/` directory with `__init__.py`
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 2. Implement schema definitions
  - [x] 2.1 Create lineage path schemas
    - Create `app/schemas/lineage_path/lineage_path_schemas.py`
    - Implement `ConnectionInfo` model (person_id, relationship)
    - Implement `PersonNode` model (person_id, first_name, last_name, birth_year, death_year, address, religion, connections_up, connections_down, connections_spouse)
    - Implement `LineagePathResponse` model (connection_found, message, common_ancestor_id, graph, path_a_to_common, path_b_to_common)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11_

- [x] 3. Implement service layer
  - [x] 3.1 Create LineagePathService class
    - Create `app/services/lineage_path/lineage_path_service.py`
    - Implement `__init__` with session and max_depth from settings
    - _Requirements: 1.5_

  - [x] 3.2 Implement relationship fetching method
    - Implement `_get_relationships(person_id)` method
    - Query `person_relationship` table for active relationships only
    - Return list of (related_person_id, relationship_type) tuples
    - _Requirements: 1.3, 1.4_

  - [x] 3.3 Implement BFS algorithm
    - Implement `_bfs_find_common_ancestor(person_a_id, person_b_id)` method
    - Use bidirectional BFS from both persons
    - Track visited nodes to handle circular relationships
    - Respect max_depth limit
    - Return common_ancestor_id, path_a, path_b
    - _Requirements: 1.1, 1.2, 1.5, 3.5_

  - [x] 3.4 Implement person data enrichment
    - Implement `_enrich_person_data(person_id)` method
    - Fetch person basic info from `person` table
    - Fetch current address from `person_address` and join with address hierarchy tables
    - Fetch religion from `person_religion` and join with religion hierarchy tables
    - Format address and religion as comma-separated strings (empty if not available)
    - _Requirements: 2.2, 2.3, 2.4, 3.4_

  - [x] 3.5 Implement graph building method
    - Implement `_build_path_graph(person_ids, relationships)` method
    - Create PersonNode for each person in the path
    - Populate connections_up, connections_down, connections_spouse arrays
    - _Requirements: 2.1, 2.5, 2.6, 2.7_

  - [x] 3.6 Implement main find_path method
    - Implement `find_path(person_a_id, person_b_id)` method
    - Handle same person edge case (return single node)
    - Validate both persons exist (raise 404 if not)
    - Call BFS algorithm
    - Build and return LineagePathResponse
    - _Requirements: 1.1, 3.1, 3.2, 3.3_

  - [x] 3.7 Write unit tests for relationship fetching
    - Test fetching active relationships only
    - Test filtering out inactive relationships
    - Test person with no relationships
    - _Requirements: 1.3, 1.4_

  - [x] 3.8 Write unit tests for BFS algorithm
    - Test finding common ancestor in simple tree
    - Test finding common ancestor through spouse
    - Test max depth limit enforcement
    - Test circular relationship handling
    - Test no connection found scenario
    - _Requirements: 1.1, 1.2, 1.5, 3.5_

  - [x] 3.9 Write unit tests for person data enrichment
    - Test enrichment with full address data
    - Test enrichment with missing address data (empty string)
    - Test enrichment with full religion data
    - Test enrichment with missing religion data (empty string)
    - _Requirements: 2.2, 2.3, 2.4, 3.4_

  - [x] 3.10 Write unit tests for graph building
    - Test graph contains all path nodes
    - Test connections_up populated correctly
    - Test connections_down populated correctly
    - Test connections_spouse populated correctly
    - _Requirements: 2.1, 2.5, 2.6, 2.7_

  - [x] 3.11 Write unit tests for main find_path method
    - Test same person edge case returns single node
    - Test invalid person_a returns 404
    - Test invalid person_b returns 404
    - Test successful path finding returns valid response
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Implement API route
  - [x] 4.1 Create route handler
    - Create `app/api/routes/lineage_path/find_path.py`
    - Implement GET `/find` endpoint
    - Accept query parameters: person_a_id (UUID), person_b_id (UUID)
    - Require authentication (CurrentUser dependency)
    - Call LineagePathService.find_path()
    - Return LineagePathResponse
    - _Requirements: 4.1, 4.2, 4.4_

  - [x] 4.2 Register route in API main
    - Update `app/api/main.py` to include lineage_path router
    - Mount at `/api/v1/lineage-path`
    - _Requirements: 4.1_

  - [x] 4.3 Write integration tests for API endpoint
    - Test successful path finding with valid persons
    - Test 404 for invalid person_a_id
    - Test 404 for invalid person_b_id
    - Test 422 for missing parameters
    - Test 422 for invalid UUID format
    - Test authentication requirement (401 without token)
    - Test same person edge case
    - Test no connection found scenario
    - _Requirements: 3.2, 3.3, 4.2, 4.3, 4.4_

- [x] 5. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- All tasks including tests are required for comprehensive coverage
- Each task references specific requirements for traceability
- The implementation uses Python with FastAPI, SQLModel, and PostgreSQL
- Unit tests are organized per component for better maintainability
- Property-based tests can be added as a future enhancement using hypothesis library
