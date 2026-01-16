# Requirements Document

## Introduction

The Lineage Path Finder feature enables users to discover how two persons in the family tree are connected. Given two person IDs, the system finds their common ancestor(s) and returns a directed graph showing the relationship path from the common ancestor to both persons. This feature helps users understand family connections and visualize lineage relationships.

## Glossary

- **Lineage_Path_Service**: The backend service responsible for finding and computing relationship paths between two persons
- **Path_Graph**: A directed graph structure containing person nodes and their relationship connections
- **Person_Node**: A node in the path graph containing person details and connection information
- **Common_Ancestor**: The person(s) from whom both queried persons descend
- **BFS_Algorithm**: Bidirectional Breadth-First Search algorithm used to find the shortest path
- **Relationship_Type**: The type of family relationship (Father, Mother, Son, Daughter, Wife, Husband, Spouse)

## Requirements

### Requirement 1: Find Lineage Path API

**User Story:** As a user, I want to find how two persons in my family tree are connected, so that I can understand their relationship and visualize the lineage path.

#### Acceptance Criteria

1. WHEN a user provides two valid person IDs, THE Lineage_Path_Service SHALL return a path graph showing the connection between them
2. WHEN a connection is found, THE Lineage_Path_Service SHALL return the first common ancestor discovered via BFS
3. WHEN traversing relationships, THE Lineage_Path_Service SHALL include all relationship types (parent, child, spouse)
4. WHEN traversing relationships, THE Lineage_Path_Service SHALL exclude inactive relationships (is_active=false)
5. THE Lineage_Path_Service SHALL limit the search depth to a configurable maximum (default: 10 levels), driven by environment variable LINEAGE_PATH_MAX_DEPTH, This should be config driven or environment variable driven.

### Requirement 2: Path Graph Response Structure

**User Story:** As a frontend developer, I want a well-structured graph response, so that I can easily render the lineage path on the UI.

#### Acceptance Criteria

1. THE Path_Graph SHALL contain a dictionary of Person_Nodes keyed by person_id
2. WHEN returning a Person_Node, THE Lineage_Path_Service SHALL include: person_id, first_name, last_name, birth_year, death_year (if applicable)
3. WHEN returning a Person_Node, THE Lineage_Path_Service SHALL include address as comma-separated string (empty if not available)
4. WHEN returning a Person_Node, THE Lineage_Path_Service SHALL include religion as comma-separated string (empty if not available)
5. WHEN returning a Person_Node, THE Lineage_Path_Service SHALL include connections_up array with person_id and relationship_type for each parent connection
6. WHEN returning a Person_Node, THE Lineage_Path_Service SHALL include connections_down array with person_id and relationship_type for each child connection
7. WHEN returning a Person_Node, THE Lineage_Path_Service SHALL include connections_spouse array with person_id and relationship_type for each spouse connection
8. THE Path_Graph response SHALL include path_a_to_common array showing person IDs from person A to common ancestor
9. THE Path_Graph response SHALL include path_b_to_common array showing person IDs from person B to common ancestor
10. THE Path_Graph response SHALL include connection_found boolean indicating if a connection was discovered
11. THE Path_Graph response SHALL include a message describing the result

### Requirement 3: Edge Case Handling

**User Story:** As a user, I want clear feedback when edge cases occur, so that I understand the result of my query.

#### Acceptance Criteria

1. IF person_a_id equals person_b_id, THEN THE Lineage_Path_Service SHALL return a single Person_Node with that person's details
2. IF either person_id does not exist in the database, THEN THE Lineage_Path_Service SHALL return a 404 error with descriptive message
3. IF no connection is found within the configured max depth, THEN THE Lineage_Path_Service SHALL return a graph with only person A and person B nodes with message "No relation found up to {max_depth}th connection"
4. IF a person has no address or religion data, THEN THE Lineage_Path_Service SHALL return empty strings for those fields
5. WHEN circular relationships exist in data, THE Lineage_Path_Service SHALL handle them gracefully using visited set tracking

### Requirement 4: API Endpoint Structure

**User Story:** As a developer, I want a clean API endpoint, so that I can easily integrate the lineage path feature.

#### Acceptance Criteria

1. THE Lineage_Path_Service SHALL expose endpoint at POST /api/v1/lineage-path/find
2. THE endpoint SHALL accept a JSON request body with fields: person_a_id (UUID, required) and person_b_id (UUID, required)
3. WHEN parameters are missing or invalid, THE Lineage_Path_Service SHALL return 422 validation error
4. THE endpoint SHALL require authentication

### Requirement 5: Code Organization

**User Story:** As a developer, I want the lineage path code in separate files, so that it doesn't overwhelm existing route files.

#### Acceptance Criteria

1. THE Lineage_Path_Service SHALL have its route file at api/routes/lineage_path/find_path.py
2. THE Lineage_Path_Service SHALL have its service file at services/lineage_path/lineage_path_service.py
3. THE Lineage_Path_Service SHALL have its schema file at schemas/lineage_path/lineage_path_schemas.py

---

## Future Enhancements

### Enhancement 1: Intelligent Path Caching

**Problem Statement:**
Finding lineage paths is computationally expensive, especially for large family trees with deep connections. Each BFS traversal may visit hundreds of nodes, and the same paths may be queried repeatedly.

**Key Insight:**
When finding the path between Person A and Person B, the BFS algorithm traverses and discovers paths to ALL intermediate persons along the way. This "side-effect" data is valuable and currently discarded after each query.

**Example - Single Query Discovers Multiple Paths:**
```
Query: Find path A → B
BFS discovers path: A → C → D → E → B

All paths discovered (and cacheable):
- A ↔ C (depth 1)
- A ↔ D (depth 2)  
- A ↔ E (depth 3)
- A ↔ B (depth 4)
- C ↔ D (depth 1)
- C ↔ E (depth 2)
- C ↔ B (depth 3)
- D ↔ E (depth 1)
- D ↔ B (depth 2)
- E ↔ B (depth 1)

Result: 1 query computes 10 cacheable path pairs!
```

**Proposed Solution: Multi-Tier Caching**

**Tier 1: In-Memory Cache (Redis)**
- TTL: 24 hours
- Fast lookups for frequently accessed paths
- Automatic expiration handles staleness

**Tier 2: Persistent Storage (Database Table)**
```sql
CREATE TABLE lineage_path_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_a_id UUID NOT NULL REFERENCES person(id),
    person_b_id UUID NOT NULL REFERENCES person(id),
    common_ancestor_id UUID REFERENCES person(id),
    path_json JSONB NOT NULL,  -- Full graph response
    depth INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_valid BOOLEAN DEFAULT TRUE,
    UNIQUE(person_a_id, person_b_id)
);

CREATE INDEX idx_lineage_cache_persons ON lineage_path_cache(person_a_id, person_b_id);
CREATE INDEX idx_lineage_cache_valid ON lineage_path_cache(is_valid) WHERE is_valid = TRUE;
```

**Cache Write Strategy:**
After computing a path A→B, extract and store ALL intermediate path pairs discovered during BFS traversal. This turns O(n) queries into O(1) lookups for any previously discovered pair.

**Cache Invalidation Strategy:**
1. **Event-Driven Invalidation:** When a relationship is added/modified/deleted:
   - Mark cache entries involving affected persons as `is_valid = FALSE`
   - Background job rebuilds affected paths lazily or proactively
   
2. **Lazy Rebuild:** On cache miss or stale entry:
   - Recompute path
   - Update cache with fresh data
   - Store all intermediate paths discovered

3. **Proactive Rebuild (Optional):** Background worker periodically:
   - Identifies invalidated entries
   - Recomputes and refreshes cache
   - Runs during low-traffic periods

**Query Flow with Cache:**
```
1. Normalize query: ensure person_a_id < person_b_id (canonical ordering)
2. Check Redis cache
   - If hit and valid → return cached result
3. Check database cache
   - If hit and valid → populate Redis, return result
4. Cache miss → compute BFS
5. Store result in database cache
6. Store ALL intermediate paths discovered
7. Populate Redis cache
8. Return result
```

**Benefits:**
- First query for any pair: O(n) BFS traversal
- Subsequent queries for ANY discovered pair: O(1) lookup
- Family relationships rarely change → high cache hit rate expected
- Single expensive query populates cache for many future queries

**Estimated Impact:**
- For a family tree with 1000 persons
- Average path depth of 5
- Single query discovering 10-20 intermediate paths
- After ~50-100 queries, most common paths are cached
- 90%+ cache hit rate achievable for active family trees

**Implementation Priority:** Medium-High (implement after core feature is stable)
