# Design Document: Lineage Path Finder

## Overview

The Lineage Path Finder feature provides an API to discover how two persons in a family tree are connected. It uses a Bidirectional Breadth-First Search (BFS) algorithm to find the shortest path through family relationships, returning a directed graph structure suitable for UI rendering.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│  POST /api/v1/lineage-path/find                                 │
│  Body: { "person_a_id": "uuid", "person_b_id": "uuid" }         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Route Handler                               │
│              api/routes/lineage_path/find_path.py               │
│  - Validate input parameters                                     │
│  - Check authentication                                          │
│  - Call service layer                                            │
│  - Return response                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Service Layer                               │
│          services/lineage_path/lineage_path_service.py          │
│  - Implement BFS algorithm                                       │
│  - Build path graph                                              │
│  - Enrich person data                                            │
│  - Handle edge cases                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  - person table                                                  │
│  - person_relationship table                                     │
│  - person_address table                                          │
│  - person_religion table                                         │
│  - address_* tables (country, state, district, etc.)            │
│  - religion_* tables                                             │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. Route Handler (find_path.py)

```python
@router.post("/find", response_model=LineagePathResponse)
async def find_lineage_path(
    request: LineagePathRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> LineagePathResponse:
    """Find the lineage path between two persons."""
```

### 2. Service Layer (lineage_path_service.py)

```python
class LineagePathService:
    def __init__(self, session: Session):
        self.session = session
        self.max_depth = settings.LINEAGE_PATH_MAX_DEPTH
    
    async def find_path(
        self, 
        person_a_id: UUID, 
        person_b_id: UUID
    ) -> LineagePathResponse:
        """Main entry point for finding lineage path."""
    
    def _bfs_find_common_ancestor(
        self,
        person_a_id: UUID,
        person_b_id: UUID
    ) -> tuple[UUID | None, dict, dict]:
        """BFS to find common ancestor and paths."""
    
    def _get_relationships(
        self, 
        person_id: UUID
    ) -> list[tuple[UUID, RelationshipType]]:
        """Get all active relationships for a person."""
    
    def _build_path_graph(
        self,
        person_ids: set[UUID],
        path_a: list[UUID],
        path_b: list[UUID]
    ) -> dict[str, PersonNode]:
        """Build the graph with enriched person data."""
    
    def _enrich_person_data(
        self, 
        person_id: UUID
    ) -> PersonNode:
        """Fetch and format person details including address and religion."""
```

### 3. Schema Definitions (lineage_path_schemas.py)

```python
class LineagePathRequest(BaseModel):
    """Request body for lineage path query."""
    person_a_id: UUID
    person_b_id: UUID

class ConnectionInfo(BaseModel):
    """Represents a connection to another person."""
    person_id: UUID
    relationship: str  # e.g., "Father", "Mother", "Son"

class PersonNode(BaseModel):
    """A node in the lineage path graph."""
    person_id: UUID
    first_name: str
    last_name: str
    birth_year: int
    death_year: int | None
    address: str  # Comma-separated: "Village, District, State, Country"
    religion: str  # Comma-separated: "Religion, Category, SubCategory"
    connections_up: list[ConnectionInfo]    # Parents
    connections_down: list[ConnectionInfo]  # Children
    connections_spouse: list[ConnectionInfo]  # Spouses

class LineagePathResponse(BaseModel):
    """Response for lineage path query."""
    connection_found: bool
    message: str
    common_ancestor_id: UUID | None
    graph: dict[str, PersonNode]  # person_id -> PersonNode
    path_a_to_common: list[UUID]
    path_b_to_common: list[UUID]
```

## Data Models

### Existing Tables Used

1. **person** - Core person information
2. **person_relationship** - Relationships between persons (with is_active filter)
3. **person_address** - Address associations (current address)
4. **person_religion** - Religion associations
5. **address_country/state/district/sub_district/locality** - Address hierarchy
6. **religion/religion_category/religion_sub_category** - Religion hierarchy

### Configuration

```python
# In app/core/config.py
class Settings:
    LINEAGE_PATH_MAX_DEPTH: int = Field(
        default=10,
        description="Maximum depth for lineage path search"
    )
```

Environment variable: `LINEAGE_PATH_MAX_DEPTH`

## Algorithm: Bidirectional BFS

```
FUNCTION find_common_ancestor(person_a_id, person_b_id):
    IF person_a_id == person_b_id:
        RETURN person_a_id as common ancestor
    
    visited_a = {person_a_id: None}  # person_id -> parent in path
    visited_b = {person_b_id: None}
    queue_a = [person_a_id]
    queue_b = [person_b_id]
    depth = 0
    
    WHILE depth < max_depth AND (queue_a OR queue_b):
        # Expand from A
        IF queue_a:
            next_queue_a = []
            FOR person IN queue_a:
                FOR (related_id, rel_type) IN get_relationships(person):
                    IF related_id IN visited_b:
                        RETURN related_id as common ancestor
                    IF related_id NOT IN visited_a:
                        visited_a[related_id] = person
                        next_queue_a.append(related_id)
            queue_a = next_queue_a
        
        # Expand from B (similar logic)
        ...
        
        depth += 1
    
    RETURN None (no connection found)
```

### Relationship Traversal

The BFS traverses ALL relationship types bidirectionally:
- **Parent relationships:** FATHER, MOTHER (traverse up)
- **Child relationships:** SON, DAUGHTER (traverse down)
- **Spouse relationships:** WIFE, HUSBAND, SPOUSE (traverse laterally)

Only active relationships (`is_active=true`) are considered.

## Response Examples

### Successful Connection Found

```json
{
    "connection_found": true,
    "message": "Connection found via common ancestor",
    "common_ancestor_id": "uuid-grandparent",
    "graph": {
        "uuid-person-a": {
            "person_id": "uuid-person-a",
            "first_name": "John",
            "last_name": "Doe",
            "birth_year": 1990,
            "death_year": null,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "connections_up": [
                {"person_id": "uuid-parent-a", "relationship": "Father"}
            ],
            "connections_down": [],
            "connections_spouse": []
        },
        "uuid-parent-a": {
            "person_id": "uuid-parent-a",
            "first_name": "Robert",
            "last_name": "Doe",
            "birth_year": 1965,
            "death_year": null,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "connections_up": [
                {"person_id": "uuid-grandparent", "relationship": "Father"}
            ],
            "connections_down": [
                {"person_id": "uuid-person-a", "relationship": "Son"}
            ],
            "connections_spouse": []
        },
        "uuid-grandparent": {
            "person_id": "uuid-grandparent",
            "first_name": "William",
            "last_name": "Doe",
            "birth_year": 1940,
            "death_year": 2020,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "connections_up": [],
            "connections_down": [
                {"person_id": "uuid-parent-a", "relationship": "Son"},
                {"person_id": "uuid-parent-b", "relationship": "Son"}
            ],
            "connections_spouse": []
        }
    },
    "path_a_to_common": ["uuid-person-a", "uuid-parent-a", "uuid-grandparent"],
    "path_b_to_common": ["uuid-person-b", "uuid-parent-b", "uuid-grandparent"]
}
```

### No Connection Found

```json
{
    "connection_found": false,
    "message": "No relation found up to 10th connection",
    "common_ancestor_id": null,
    "graph": {
        "uuid-person-a": { ... },
        "uuid-person-b": { ... }
    },
    "path_a_to_common": [],
    "path_b_to_common": []
}
```

### Same Person

```json
{
    "connection_found": true,
    "message": "Same person provided for both inputs",
    "common_ancestor_id": "uuid-person-a",
    "graph": {
        "uuid-person-a": { ... }
    },
    "path_a_to_common": ["uuid-person-a"],
    "path_b_to_common": ["uuid-person-a"]
}
```

## Error Handling

| Error Case | HTTP Status | Response |
|------------|-------------|----------|
| Missing person_a_id or person_b_id | 422 | Validation error |
| Invalid UUID format | 422 | Validation error |
| Person A not found | 404 | `{"detail": "Person A not found"}` |
| Person B not found | 404 | `{"detail": "Person B not found"}` |
| Unauthenticated | 401 | `{"detail": "Not authenticated"}` |

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Valid Response Structure
*For any* valid pair of person IDs, the response SHALL contain all required fields: connection_found (boolean), message (non-empty string), common_ancestor_id (UUID or null), graph (dictionary), path_a_to_common (array), path_b_to_common (array).
**Validates: Requirements 2.8, 2.9, 2.10, 2.11**

### Property 2: Valid Person Node Structure
*For any* Person_Node in the graph, it SHALL contain: person_id, first_name, last_name, birth_year, death_year (or null), address (string, can be empty), religion (string, can be empty), connections_up (array), connections_down (array), connections_spouse (array).
**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**

### Property 3: Connection Found Implies Common Ancestor
*For any* response where connection_found is true, the common_ancestor_id SHALL be a valid UUID that exists in the graph.
**Validates: Requirements 1.2**

### Property 4: Path Consistency
*For any* response where connection_found is true, all person IDs in path_a_to_common and path_b_to_common SHALL exist as keys in the graph dictionary.
**Validates: Requirements 2.1, 2.8, 2.9**

### Property 5: Missing Enrichment Data Returns Empty String
*For any* person without address or religion data, the corresponding fields SHALL be empty strings (not null).
**Validates: Requirements 3.4**

## Testing Strategy

### Unit Tests
- Test BFS algorithm with known graph structures
- Test person data enrichment with missing data
- Test relationship type filtering (active only)
- Test edge cases: same person, invalid IDs

### Integration Tests
- Test full API endpoint with database
- Test authentication requirement
- Test 404 responses for invalid person IDs
- Test max depth configuration

### Property-Based Tests
- Use pytest with hypothesis library
- Minimum 100 iterations per property test
- Tag format: **Feature: lineage-path-finder, Property {number}: {property_text}**

Property 1: Valid Response Structure
*For any* valid request with two person IDs, the response SHALL contain: connection_found (boolean), message (non-empty string), common_ancestor_id (UUID or null), graph (dictionary), path_a_to_common (list), and path_b_to_common (list).
**Validates: Requirements 2.8, 2.9, 2.10, 2.11**

Property 2: Person Node Completeness
*For any* PersonNode in the response graph, it SHALL contain: person_id, first_name, last_name, birth_year, death_year (or null), address (string, possibly empty), religion (string, possibly empty), connections_up (list), connections_down (list), and connections_spouse (list).
**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**

Property 3: Connection Found Implies Common Ancestor
*For any* response where connection_found is true, the common_ancestor_id SHALL be a valid UUID present in the graph, and both path_a_to_common and path_b_to_common SHALL be non-empty lists ending with the common_ancestor_id.
**Validates: Requirements 1.2, 2.1**

Property 4: Graph Contains Path Nodes
*For any* response with a connection found, all person IDs in path_a_to_common and path_b_to_common SHALL exist as keys in the graph dictionary.
**Validates: Requirements 2.1, 2.8, 2.9**

Property 5: Same Person Returns Single Node
*For any* request where person_a_id equals person_b_id, the response graph SHALL contain exactly one PersonNode, and connection_found SHALL be true.
**Validates: Requirement 3.1**

## Testing Strategy

### Unit Tests
- Test BFS algorithm with known graph structures
- Test edge cases: same person, invalid IDs, no connection
- Test person data enrichment with missing address/religion

### Property-Based Tests
- Use Hypothesis library for Python
- Generate random valid person ID pairs
- Verify response structure properties
- Minimum 100 iterations per property test

### Integration Tests
- Test full API endpoint with database
- Test authentication requirements
- Test 404 responses for invalid person IDs
