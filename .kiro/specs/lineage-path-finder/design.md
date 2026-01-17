# Design Document: Lineage Path Finder

## Overview

The Lineage Path Finder feature provides an API to discover how two persons in a family tree are connected. It uses a Bidirectional Breadth-First Search (BFS) algorithm to find the shortest path through family relationships, returning a bidirectional linked list structure suitable for UI rendering. The graph contains PersonNodes ordered from person A to person B, with each node having `from_person` and `to_person` connections to form the linked list.

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
    
    def find_path(
        self, 
        person_a_id: UUID, 
        person_b_id: UUID
    ) -> LineagePathResponse:
        """Main entry point for finding lineage path."""
    
    def _bfs_find_common_ancestor(
        self,
        person_a_id: UUID,
        person_b_id: UUID
    ) -> tuple[UUID | None, dict[UUID, UUID | None], dict[UUID, UUID | None]]:
        """BFS to find common point and visited maps for path reconstruction."""
    
    def _build_final_ordered_list(
        self,
        common_person_id: UUID,
        visited_map_a_to_common: dict[UUID, UUID | None],
        visited_map_b_to_common: dict[UUID, UUID | None]
    ) -> list[UUID]:
        """Build ordered path from person A to person B through common point."""
    
    def _build_bidirectional_linked_list(
        self,
        ordered_person_ids: list[UUID]
    ) -> dict[UUID, PersonNode]:
        """Build bidirectional linked list of PersonNodes from ordered IDs."""
    
    def _get_relationship_type(
        self,
        from_person_id: UUID,
        to_person_id: UUID
    ) -> str:
        """Get relationship type label between two persons."""
    
    def _get_relationships(
        self, 
        person_id: UUID
    ) -> list[UUID]:
        """Get all active relationships for a person."""
    
    def _get_person(
        self,
        person_id: UUID
    ) -> Person | None:
        """Get a person by ID."""
    
    def _enrich_person_data(
        self, 
        person_id: UUID
    ) -> PersonNode:
        """Fetch and format person details including address and religion."""
    
    def _get_address_string(
        self,
        person_id: UUID
    ) -> str:
        """Get comma-separated address string for a person."""
    
    def _get_religion_string(
        self,
        person_id: UUID
    ) -> str:
        """Get comma-separated religion string for a person."""
```

### 3. Schema Definitions (lineage_path_schemas.py)

```python
class LineagePathRequest(BaseModel):
    """Request body for lineage path query."""
    person_a_id: UUID
    person_b_id: UUID

class ConnectionInfo(BaseModel):
    """Represents a connection to another person.
    
    Note: The full PersonNode details can be looked up from the graph
    using the person_id.
    """
    person_id: UUID
    relationship: str  # e.g., "Father", "Mother", "Son"

class PersonNode(BaseModel):
    """A node in the lineage path graph (bidirectional linked list)."""
    person_id: UUID
    first_name: str
    last_name: str
    birth_year: int | None
    death_year: int | None
    address: str  # Comma-separated: "Village, District, State, Country"
    religion: str  # Comma-separated: "Religion, Category, SubCategory"
    from_person: ConnectionInfo | None  # Previous person in path
    to_person: ConnectionInfo | None    # Next person in path

class LineagePathResponse(BaseModel):
    """Response for lineage path query."""
    connection_found: bool
    message: str
    common_ancestor_id: UUID | None
    graph: dict[UUID, PersonNode]  # person_id -> PersonNode (ordered linked list)
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
    "message": "Connection found",
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
            "from_person": null,
            "to_person": {"person_id": "uuid-parent-a", "relationship": "Father"}
        },
        "uuid-parent-a": {
            "person_id": "uuid-parent-a",
            "first_name": "Robert",
            "last_name": "Doe",
            "birth_year": 1965,
            "death_year": null,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "from_person": {"person_id": "uuid-person-a", "relationship": "Son"},
            "to_person": {"person_id": "uuid-grandparent", "relationship": "Father"}
        },
        "uuid-grandparent": {
            "person_id": "uuid-grandparent",
            "first_name": "William",
            "last_name": "Doe",
            "birth_year": 1940,
            "death_year": 2020,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "from_person": {"person_id": "uuid-parent-a", "relationship": "Son"},
            "to_person": {"person_id": "uuid-parent-b", "relationship": "Son"}
        },
        "uuid-parent-b": {
            "person_id": "uuid-parent-b",
            "first_name": "James",
            "last_name": "Doe",
            "birth_year": 1968,
            "death_year": null,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "from_person": {"person_id": "uuid-grandparent", "relationship": "Father"},
            "to_person": {"person_id": "uuid-person-b", "relationship": "Son"}
        },
        "uuid-person-b": {
            "person_id": "uuid-person-b",
            "first_name": "Mike",
            "last_name": "Doe",
            "birth_year": 1995,
            "death_year": null,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "from_person": {"person_id": "uuid-parent-b", "relationship": "Father"},
            "to_person": null
        }
    }
}
```

### No Connection Found

```json
{
    "connection_found": false,
    "message": "No relation found up to 10th connection",
    "common_ancestor_id": null,
    "graph": {
        "uuid-person-a": {
            "person_id": "uuid-person-a",
            "first_name": "John",
            "last_name": "Doe",
            "birth_year": 1990,
            "death_year": null,
            "address": "",
            "religion": "",
            "from_person": null,
            "to_person": null
        },
        "uuid-person-b": {
            "person_id": "uuid-person-b",
            "first_name": "Jane",
            "last_name": "Smith",
            "birth_year": 1992,
            "death_year": null,
            "address": "",
            "religion": "",
            "from_person": null,
            "to_person": null
        }
    }
}
```

### Same Person

```json
{
    "connection_found": true,
    "message": "Same person provided for both inputs",
    "common_ancestor_id": "uuid-person-a",
    "graph": {
        "uuid-person-a": {
            "person_id": "uuid-person-a",
            "first_name": "John",
            "last_name": "Doe",
            "birth_year": 1990,
            "death_year": null,
            "address": "Village1, District1, State1, India",
            "religion": "Hindu, Brahmin, Sharma",
            "from_person": null,
            "to_person": null
        }
    }
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
*For any* valid pair of person IDs, the response SHALL contain all required fields: connection_found (boolean), message (non-empty string), common_ancestor_id (UUID or null), graph (dictionary).
**Validates: Requirements 2.8, 2.9, 2.10**

### Property 2: Valid Person Node Structure
*For any* Person_Node in the graph, it SHALL contain: person_id, first_name, last_name, birth_year (or null), death_year (or null), address (string, can be empty), religion (string, can be empty), from_person (ConnectionInfo or null), to_person (ConnectionInfo or null).
**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**

### Property 3: Connection Found Implies Common Ancestor
*For any* response where connection_found is true, the common_ancestor_id SHALL be a valid UUID that exists in the graph.
**Validates: Requirements 1.2**

### Property 4: Bidirectional Linked List Consistency
*For any* response where connection_found is true, the graph SHALL form a valid bidirectional linked list where:
- The first node (person A) has from_person = null
- The last node (person B) has to_person = null
- Each intermediate node's to_person.person_id matches the next node's person_id
- Each intermediate node's from_person.person_id matches the previous node's person_id
**Validates: Requirements 2.1, 2.5, 2.6**

### Property 5: Missing Enrichment Data Returns Empty String
*For any* person without address or religion data, the corresponding fields SHALL be empty strings (not null).
**Validates: Requirements 3.4**

## Testing Strategy

### Unit Tests
- Test BFS algorithm with known graph structures
- Test person data enrichment with missing data
- Test relationship type filtering (active only)
- Test edge cases: same person, invalid IDs
- Test bidirectional linked list building
- Test ordered path construction from visited maps

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
*For any* valid request with two person IDs, the response SHALL contain: connection_found (boolean), message (non-empty string), common_ancestor_id (UUID or null), and graph (dictionary).
**Validates: Requirements 2.8, 2.9, 2.10**

Property 2: Person Node Completeness
*For any* PersonNode in the response graph, it SHALL contain: person_id, first_name, last_name, birth_year (or null), death_year (or null), address (string, possibly empty), religion (string, possibly empty), from_person (ConnectionInfo or null), and to_person (ConnectionInfo or null).
**Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6, 2.7**

Property 3: Connection Found Implies Common Ancestor
*For any* response where connection_found is true, the common_ancestor_id SHALL be a valid UUID present in the graph.
**Validates: Requirements 1.2, 2.1**

Property 4: Bidirectional Linked List Validity
*For any* response with a connection found, the graph SHALL form a valid bidirectional linked list from person A to person B with consistent from_person/to_person references.
**Validates: Requirements 2.1, 2.5, 2.6**

Property 5: Same Person Returns Single Node
*For any* request where person_a_id equals person_b_id, the response graph SHALL contain exactly one PersonNode with from_person=null and to_person=null, and connection_found SHALL be true.
**Validates: Requirement 3.1**

### Unit Tests
- Test BFS algorithm with known graph structures
- Test edge cases: same person, invalid IDs, no connection
- Test person data enrichment with missing address/religion
- Test bidirectional linked list construction
- Test relationship type lookup

### Integration Tests
- Test full API endpoint with database
- Test authentication requirements
- Test 404 responses for invalid person IDs
