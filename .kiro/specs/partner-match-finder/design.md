# Design Document: Partner Match Finder

## Overview

The Partner Match Finder is a backend service that discovers potential marriage matches within a user's extended family network. Starting from a seeker person, it performs BFS traversal through family relationships up to a configurable depth, applying cultural/religious compatibility filters, and returns a tree-structured graph showing all visited persons with eligible matches flagged.

The design follows similar patterns to the existing LineagePathService but with key differences:
- Single-source BFS (not bidirectional)
- Full tree exploration (not shortest path)
- Multi-criteria filtering during traversal
- Tree structure response (not linear path)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Layer                                │
│  POST /api/v1/partner-match/find                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PartnerMatchService                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  find_matches(request: PartnerMatchRequest)              │   │
│  │    → PartnerMatchResponse                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         ▼                    ▼                    ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────┐     │
│  │ BFS Engine  │    │  Filters    │    │ Graph Builder   │     │
│  │ _bfs_explore│    │ _is_eligible│    │ _build_tree     │     │
│  └─────────────┘    └─────────────┘    └─────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Database Layer                              │
│  Person, PersonRelationship, PersonReligion, PersonAddress      │
│  Gender, Religion, ReligionCategory, ReligionSubCategory        │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. API Route (`/api/v1/partner-match/`)

New dedicated route file: `app/api/routes/partner_match.py`

```python
@router.post("/find", response_model=PartnerMatchResponse)
def find_partner_matches(
    request: PartnerMatchRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> PartnerMatchResponse:
    """Find potential partner matches for a seeker."""
    service = PartnerMatchService(session)
    return service.find_matches(request)
```

### 2. PartnerMatchService

Location: `app/services/partner_match/partner_match_service.py`

Core methods:
- `find_matches(request)` - Main entry point
- `_bfs_explore(seeker_id, max_depth)` - BFS traversal building parent map
- `_is_eligible_match(person_id, filters)` - Check all filter criteria
- `_is_married(person_id)` - Check spouse/children relationships
- `_get_person_religion_ids(person_id)` - Get religion/category/sub-category IDs
- `_build_exploration_tree(visited_map, matches, seeker_id)` - Build response graph
- `_prune_graph(graph, matches, seeker_id)` - Remove nodes not on path to any match
- `_enrich_node_data(person_id)` - Fetch person details for node

### 3. Filter Logic

Filters are applied in this order:
1. **Gender** - Must match target_gender_code
2. **Living** - date_of_death must be null
3. **Age** - birth_year within range
4. **Religion Inclusion** - religion_id in include list (if provided)
5. **Category Inclusion** - category_id in include list (if provided)
6. **Sub-category Inclusion** - sub_category_id in include list (if provided)
7. **Sub-category Exclusion** - sub_category_id NOT in exclude list
8. **Marital Status** - No WIFE/HUSBAND/SPOUSE/SON/DAUGHTER relationships

```python
def _is_eligible_match(self, person_id: UUID, filters: PartnerMatchFilters) -> bool:
    person = self._get_person(person_id)
    if not person:
        return False
    
    # 1. Gender check
    if not self._matches_gender(person, filters.target_gender_code):
        return False
    
    # 2. Living check
    if person.date_of_death is not None:
        return False
    
    # 3. Age check
    birth_year = person.date_of_birth.year if person.date_of_birth else None
    if not self._in_birth_year_range(birth_year, filters):
        return False
    
    # 4-7. Religion filters
    if not self._passes_religion_filters(person_id, filters):
        return False
    
    # 8. Marital status
    if self._is_married_or_has_children(person_id):
        return False
    
    return True
```

## Data Models

### Request Schema

```python
class PartnerMatchRequest(BaseModel):
    seeker_person_id: UUID
    target_gender_code: str  # "M" or "F"
    
    # Age filters
    birth_year_min: int | None = None
    birth_year_max: int | None = None
    
    # Religion inclusion (AND logic between different levels)
    include_religion_ids: list[UUID] | None = None
    include_category_ids: list[UUID] | None = None
    include_sub_category_ids: list[UUID] | None = None
    
    # Gotra exclusion
    exclude_sub_category_ids: list[UUID] = []
    
    # Search depth
    max_depth: int = 5
    
    # Graph pruning (default: True)
    prune_graph: bool = True
```

### Response Schema

```python
class PartnerMatchResponse(BaseModel):
    seeker_id: UUID
    total_matches: int
    matches: list[UUID]  # Person IDs of eligible matches
    exploration_graph: dict[UUID, MatchGraphNode]

class MatchGraphNode(BaseModel):
    person_id: UUID
    first_name: str
    last_name: str
    birth_year: int | None
    death_year: int | None
    address: str
    religion: str
    is_match: bool  # True if this person is an eligible match
    depth: int  # Hops from seeker
    from_person: MatchConnectionInfo | None  # Parent in BFS tree
    to_persons: list[MatchConnectionInfo]  # Children explored from this node

class MatchConnectionInfo(BaseModel):
    person_id: UUID
    relationship: str  # "Father", "Son", etc.
```

### Example Response

```json
{
  "seeker_id": "uuid-seeker",
  "total_matches": 2,
  "matches": ["uuid-match1", "uuid-match2"],
  "exploration_graph": {
    "uuid-seeker": {
      "person_id": "uuid-seeker",
      "first_name": "Rahul",
      "last_name": "Sharma",
      "is_match": false,
      "depth": 0,
      "from_person": null,
      "to_persons": [
        {"person_id": "uuid-father", "relationship": "Father"},
        {"person_id": "uuid-mother", "relationship": "Mother"}
      ]
    },
    "uuid-father": {
      "person_id": "uuid-father",
      "first_name": "Ramesh",
      "is_match": false,
      "depth": 1,
      "from_person": {"person_id": "uuid-seeker", "relationship": "Son"},
      "to_persons": [
        {"person_id": "uuid-uncle", "relationship": "Brother"}
      ]
    },
    "uuid-uncle": {
      "person_id": "uuid-uncle",
      "is_match": false,
      "depth": 2,
      "from_person": {"person_id": "uuid-father", "relationship": "Brother"},
      "to_persons": [
        {"person_id": "uuid-match1", "relationship": "Daughter"}
      ]
    },
    "uuid-match1": {
      "person_id": "uuid-match1",
      "first_name": "Priya",
      "is_match": true,
      "depth": 3,
      "from_person": {"person_id": "uuid-uncle", "relationship": "Father"},
      "to_persons": []
    }
  }
}
```

## BFS Algorithm

```python
def _bfs_explore(
    self, 
    seeker_id: UUID, 
    max_depth: int,
    filters: PartnerMatchFilters
) -> tuple[dict[UUID, UUID | None], dict[UUID, int], list[UUID]]:
    """
    Perform BFS from seeker, tracking parent relationships and finding matches.
    
    Returns:
        - parent_map: {person_id: parent_person_id} for tree reconstruction
        - depth_map: {person_id: depth} distance from seeker
        - matches: list of eligible match person_ids
    """
    parent_map: dict[UUID, UUID | None] = {seeker_id: None}
    depth_map: dict[UUID, int] = {seeker_id: 0}
    matches: list[UUID] = []
    
    queue: deque[UUID] = deque([seeker_id])
    current_depth = 0
    
    while queue and current_depth < max_depth:
        level_size = len(queue)
        current_depth += 1
        
        for _ in range(level_size):
            current_id = queue.popleft()
            relationships = self._get_relationships(current_id)
            
            for related_id in relationships:
                if related_id in parent_map:
                    continue  # Already visited
                
                parent_map[related_id] = current_id
                depth_map[related_id] = current_depth
                queue.append(related_id)
                
                # Check if eligible match
                if self._is_eligible_match(related_id, filters):
                    matches.append(related_id)
    
    return parent_map, depth_map, matches
```

## Error Handling

| Scenario | HTTP Status | Error Message |
|----------|-------------|---------------|
| Seeker not found | 404 | "Seeker person not found" |
| Invalid gender code | 400 | "Invalid gender code. Use 'M' or 'F'" |
| max_depth exceeds limit | 400 | "max_depth cannot exceed {MAX_ALLOWED}" |
| birth_year_min > birth_year_max | 400 | "birth_year_min cannot be greater than birth_year_max" |

## Graph Pruning Algorithm

When `prune_graph=True` (default), the service removes nodes that don't contribute to any path from seeker to a match. This reduces response payload size and simplifies frontend visualization.

### Algorithm

```python
def _prune_graph(
    self,
    graph: dict[UUID, MatchGraphNode],
    matches: list[UUID],
    seeker_id: UUID,
) -> dict[UUID, MatchGraphNode]:
    """
    Prune the exploration graph to only include nodes on paths to matches.
    
    Algorithm:
    1. Start with empty set of nodes_to_keep
    2. For each match, trace back to seeker via from_person links
    3. Add all nodes on each path to nodes_to_keep
    4. Filter graph to only include nodes_to_keep
    5. Update to_persons lists to only reference kept nodes
    """
    if not matches:
        # No matches - return only seeker node
        seeker_node = graph[seeker_id]
        seeker_node.to_persons = []
        return {seeker_id: seeker_node}
    
    # Collect all nodes on paths from matches back to seeker
    nodes_to_keep: set[UUID] = {seeker_id}
    
    for match_id in matches:
        current_id = match_id
        while current_id is not None:
            nodes_to_keep.add(current_id)
            node = graph[current_id]
            current_id = node.from_person.person_id if node.from_person else None
    
    # Build pruned graph
    pruned_graph: dict[UUID, MatchGraphNode] = {}
    for person_id in nodes_to_keep:
        node = graph[person_id]
        # Filter to_persons to only include kept nodes
        node.to_persons = [
            conn for conn in node.to_persons 
            if conn.person_id in nodes_to_keep
        ]
        pruned_graph[person_id] = node
    
    return pruned_graph
```

### Example

Given this exploration tree:
```
Seeker → Father → Uncle → Match1
              ↘ Aunt (no match descendants)
       → Mother → Cousin (no match)
```

With `prune_graph=True`, the response only includes:
```
Seeker → Father → Uncle → Match1
```

The Aunt, Mother, and Cousin nodes are removed because they don't lead to any matches.

## Testing Strategy

### Unit Tests
- Filter logic tests (each filter in isolation)
- BFS traversal tests (correct depth, parent tracking)
- Graph building tests (correct from_person/to_persons)
- Edge cases (seeker has no relationships, all filtered out)

### Property-Based Tests
- See Correctness Properties section below


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system - essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Depth Constraint

*For any* valid partner match request and response, all nodes in the exploration_graph SHALL have depth less than or equal to the requested max_depth.

**Validates: Requirements 1.3, 10.1**

### Property 2: Gender Filter Correctness

*For any* match in the response matches list, the person's gender code SHALL equal the requested target_gender_code.

**Validates: Requirements 2.1**

### Property 3: Birth Year Range Correctness

*For any* match in the response matches list, if birth_year_min is provided then the person's birth_year SHALL be >= birth_year_min, and if birth_year_max is provided then birth_year SHALL be <= birth_year_max.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 4: Religion Inclusion Correctness

*For any* match in the response matches list:
- If include_religion_ids is non-empty, the person's religion_id SHALL be in include_religion_ids
- If include_category_ids is non-empty, the person's religion_category_id SHALL be in include_category_ids  
- If include_sub_category_ids is non-empty, the person's religion_sub_category_id SHALL be in include_sub_category_ids

**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

### Property 5: Gotra Exclusion Correctness

*For any* match in the response matches list, if exclude_sub_category_ids is non-empty, the person's religion_sub_category_id SHALL NOT be in exclude_sub_category_ids.

**Validates: Requirements 5.1**

### Property 6: Living Person Correctness

*For any* match in the response matches list, the person's date_of_death SHALL be null.

**Validates: Requirements 6.1**

### Property 7: Marital Status Correctness

*For any* match in the response matches list, the person SHALL NOT have any active relationship of type WIFE, HUSBAND, SPOUSE, SON, or DAUGHTER.

**Validates: Requirements 7.1, 7.2, 7.3**

### Property 8: BFS Continues Through Filtered Persons

*For any* match in the response, if the match's depth > 1, then there SHALL exist a path from seeker to match in the exploration_graph, and this path MAY contain persons who are not matches (filtered out but traversed through).

**Validates: Requirements 5.3, 6.2, 7.4**

### Property 9: Graph Structure Integrity

*For any* exploration_graph in the response:
- The seeker node SHALL be present with from_person = null and depth = 0
- For any non-seeker node, from_person SHALL reference a valid node in the graph
- For any node, all person_ids in to_persons SHALL reference valid nodes in the graph
- The from_person/to_persons relationships SHALL form a valid tree rooted at seeker

**Validates: Requirements 8.1, 8.3, 8.4, 8.6**

### Property 10: Response Consistency

*For any* partner match response:
- total_matches SHALL equal len(matches)
- seeker_id SHALL equal the requested seeker_person_id
- All person_ids in matches SHALL have is_match = true in exploration_graph
- All nodes with is_match = true in exploration_graph SHALL be in matches list

**Validates: Requirements 9.1, 9.2, 9.3**

### Property 11: Seeker Validation

*For any* request with a non-existent seeker_person_id, the service SHALL return HTTP 404 with message "Seeker person not found".

**Validates: Requirements 1.1, 1.2**

### Property 12: Graph Pruning Correctness

*For any* partner match response where prune_graph=True:
- All nodes in exploration_graph SHALL be on at least one path from seeker to a match
- The seeker node SHALL always be present
- If no matches exist, exploration_graph SHALL contain only the seeker node
- For any match, tracing from_person links back to seeker SHALL only traverse nodes in the graph

**Validates: Requirements 12.1, 12.3, 12.4, 12.5**
