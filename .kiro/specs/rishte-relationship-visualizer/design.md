# Design Document: Rishte Relationship Visualizer

## Overview

The Rishte feature provides an interactive visualization of relationship paths between two persons in the family database. It uses React Flow to render a generation-based family tree diagram that shows how two people are connected through their lineage.

The core challenge is transforming the linear linked-list response from the `/lineage-path/find` API into a proper tree structure with correct generational positioning, where spouses appear side-by-side and children appear below their parents.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Rishte Page                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Person Selection Header                     │   │
│  │  [Person A Selector]  [Person B Selector]  [Find Button]│   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Path Summary                           │   │
│  │  "5 persons: sib1_son → sib1_self → father → self..."   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │                   React Flow Canvas                      │   │
│  │                   (Lineage Graph)                        │   │
│  │                                                          │   │
│  │     [PersonNode] ──edge──> [PersonNode]                 │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Graph Controls                              │   │
│  │  [Zoom In] [Zoom Out] [Fit View]                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### File Structure

```
src/components/Rishte/
├── index.ts                    # Barrel export
├── RishteGraph.tsx             # Main React Flow container
├── PersonNode.tsx              # Custom node component
├── RelationshipEdge.tsx        # Custom edge component
├── PersonSelector.tsx          # Searchable person dropdown
├── PathSummary.tsx             # Path summary display
├── GraphControls.tsx           # Zoom/pan controls
├── types.ts                    # TypeScript interfaces
└── utils/
    ├── pathTransformer.ts      # API response → tree structure
    └── layoutCalculator.ts     # Node positioning logic

src/routes/_layout/
└── rishte.tsx                  # Route page component
```

### Component Interfaces

#### PersonSelector

```typescript
interface PersonSelectorProps {
  label: string                           // "Person A" or "Person B"
  value: SelectedPerson | null            // Currently selected person
  onChange: (person: SelectedPerson | null) => void
  placeholder?: string
}

interface SelectedPerson {
  id: string
  firstName: string
  lastName: string
  birthYear: number | null
}
```

#### PersonNode (React Flow Custom Node)

```typescript
interface PersonNodeData {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  deathYear: number | null
  isPersonA: boolean              // Green border
  isPersonB: boolean              // Blue border
  gender?: 'male' | 'female'      // For avatar icon
}

// React Flow node structure
interface RishteNode extends Node<PersonNodeData> {
  type: 'personNode'
  position: { x: number; y: number }
}
```

#### RelationshipEdge (React Flow Custom Edge)

```typescript
interface RelationshipEdgeData {
  relationship: string            // "Son", "Father", "Spouse", etc.
  isSpouseEdge: boolean          // Horizontal styling
}

// React Flow edge structure
interface RishteEdge extends Edge<RelationshipEdgeData> {
  type: 'relationshipEdge'
  animated?: boolean              // Path animation
}
```

#### Path Transformer

```typescript
interface TransformedPath {
  nodes: RishteNode[]
  edges: RishteEdge[]
}

interface GenerationInfo {
  personId: string
  generation: number              // 0 = oldest, increases downward
  xOffset: number                 // Horizontal position within generation
  isSpouse: boolean
  spouseOfId?: string
}

function transformApiResponse(
  response: LineagePathResponse,
  personAId: string,
  personBId: string
): TransformedPath
```

## Data Models

### API Response (from backend)

```typescript
// Existing API response structure
interface LineagePathResponse {
  connection_found: boolean
  message: string
  common_ancestor_id: string | null
  graph: Record<string, PersonNode>
}

interface PersonNode {
  person_id: string
  first_name: string
  last_name: string
  birth_year: number | null
  death_year: number | null
  address: string
  religion: string
  from_person: ConnectionInfo | null
  to_person: ConnectionInfo | null
}

interface ConnectionInfo {
  person_id: string
  relationship: string            // "Father", "Mother", "Son", "Daughter", "Spouse", etc.
}
```

### Internal Graph State

```typescript
interface RishteGraphState {
  nodes: RishteNode[]
  edges: RishteEdge[]
  isLoading: boolean
  error: string | null
  pathSummary: string | null
  personCount: number
}
```

## Path Transformation Algorithm

The core algorithm transforms the linear API response into a generation-based tree:

### Step 1: Build Path Array

Extract the ordered path from the linked list:

```typescript
function buildPathArray(graph: Record<string, PersonNode>): PersonNode[] {
  // Find start node (from_person is null)
  const startNode = Object.values(graph).find(n => n.from_person === null)
  
  const path: PersonNode[] = []
  let current = startNode
  
  while (current) {
    path.push(current)
    if (current.to_person) {
      current = graph[current.to_person.person_id]
    } else {
      current = null
    }
  }
  
  return path
}
```

### Step 2: Assign Generations

Determine generation levels based on relationship types:

```typescript
function assignGenerations(path: PersonNode[]): Map<string, GenerationInfo> {
  const generations = new Map<string, GenerationInfo>()
  let currentGen = 0
  
  for (let i = 0; i < path.length; i++) {
    const node = path[i]
    const prevNode = i > 0 ? path[i - 1] : null
    const relationship = node.from_person?.relationship
    
    // Determine generation change
    if (relationship) {
      if (isChildRelationship(relationship)) {
        // Going UP the tree (child → parent)
        currentGen--
      } else if (isParentRelationship(relationship)) {
        // Going DOWN the tree (parent → child)
        currentGen++
      }
      // Spouse relationships stay at same generation
    }
    
    generations.set(node.person_id, {
      personId: node.person_id,
      generation: currentGen,
      xOffset: 0,  // Calculated later
      isSpouse: relationship === 'Spouse' || relationship === 'Husband' || relationship === 'Wife',
      spouseOfId: isSpouseRelationship(relationship) ? prevNode?.person_id : undefined
    })
  }
  
  // Normalize generations (make minimum = 0)
  const minGen = Math.min(...Array.from(generations.values()).map(g => g.generation))
  generations.forEach(g => g.generation -= minGen)
  
  return generations
}

function isChildRelationship(rel: string): boolean {
  return ['Son', 'Daughter'].includes(rel)
}

function isParentRelationship(rel: string): boolean {
  return ['Father', 'Mother'].includes(rel)
}

function isSpouseRelationship(rel: string): boolean {
  return ['Spouse', 'Husband', 'Wife'].includes(rel)
}
```

### Step 3: Calculate Positions

Position nodes with generations as rows and proper horizontal spacing:

```typescript
const NODE_WIDTH = 180
const NODE_HEIGHT = 200
const HORIZONTAL_GAP = 100
const VERTICAL_GAP = 150
const SPOUSE_GAP = 50

function calculatePositions(
  path: PersonNode[],
  generations: Map<string, GenerationInfo>
): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>()
  
  // Group nodes by generation
  const genGroups = new Map<number, string[]>()
  generations.forEach((info, id) => {
    if (!genGroups.has(info.generation)) {
      genGroups.set(info.generation, [])
    }
    genGroups.get(info.generation)!.push(id)
  })
  
  // Calculate positions for each generation
  genGroups.forEach((nodeIds, gen) => {
    const y = gen * (NODE_HEIGHT + VERTICAL_GAP)
    
    // Sort nodes: non-spouses first, then spouses next to their partners
    const sorted = sortNodesInGeneration(nodeIds, generations)
    
    sorted.forEach((nodeId, index) => {
      const info = generations.get(nodeId)!
      let x: number
      
      if (info.isSpouse && info.spouseOfId) {
        // Position spouse next to their partner
        const spousePos = positions.get(info.spouseOfId)
        x = spousePos ? spousePos.x + NODE_WIDTH + SPOUSE_GAP : index * (NODE_WIDTH + HORIZONTAL_GAP)
      } else {
        x = index * (NODE_WIDTH + HORIZONTAL_GAP)
      }
      
      positions.set(nodeId, { x, y })
    })
  })
  
  return positions
}
```

### Step 4: Create React Flow Elements

Convert to React Flow nodes and edges:

```typescript
function createReactFlowElements(
  path: PersonNode[],
  positions: Map<string, { x: number; y: number }>,
  generations: Map<string, GenerationInfo>,
  personAId: string,
  personBId: string
): TransformedPath {
  const nodes: RishteNode[] = path.map(person => ({
    id: person.person_id,
    type: 'personNode',
    position: positions.get(person.person_id)!,
    data: {
      personId: person.person_id,
      firstName: person.first_name,
      lastName: person.last_name,
      birthYear: person.birth_year,
      deathYear: person.death_year,
      isPersonA: person.person_id === personAId,
      isPersonB: person.person_id === personBId,
    }
  }))
  
  const edges: RishteEdge[] = []
  for (let i = 0; i < path.length - 1; i++) {
    const source = path[i]
    const target = path[i + 1]
    const relationship = target.from_person?.relationship || ''
    const isSpouse = isSpouseRelationship(relationship)
    
    edges.push({
      id: `${source.person_id}-${target.person_id}`,
      source: source.person_id,
      target: target.person_id,
      type: 'relationshipEdge',
      data: {
        relationship,
        isSpouseEdge: isSpouse
      },
      animated: true
    })
  }
  
  return { nodes, edges }
}
```

## Error Handling

| Scenario | Handling |
|----------|----------|
| API error | Display error message with retry option |
| No connection found | Display "No connection found" message |
| Same person selected | Disable Find button, show validation message |
| Empty selection | Disable Find button |
| Network timeout | Show timeout error with retry option |

## Testing Strategy

### Unit Tests

- Path transformation logic (pathTransformer.ts)
- Generation assignment algorithm
- Position calculation logic
- Relationship type detection helpers

### Property-Based Tests

Property-based tests will validate the core transformation logic using fast-check.

### Integration Tests

- Full flow from person selection to graph rendering
- API integration with mock responses
- React Flow rendering with custom nodes/edges


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Find Button State

*For any* combination of Person A and Person B selections, the "Find Relationship" button SHALL be enabled if and only if both Person A and Person B are selected (non-null).

**Validates: Requirements 3.5**

### Property 2: Path Transformation Validity

*For any* valid LineagePathResponse from the API where `connection_found` is true, the Path_Transformer SHALL produce:
- A non-empty array of RishteNode objects
- A non-empty array of RishteEdge objects (if path has more than one person)
- The number of nodes equals the number of entries in the API response graph
- Each node has a valid position (x, y coordinates are finite numbers)

**Validates: Requirements 5.1, 5.2**

### Property 3: Generation-Based Layout Correctness

*For any* transformed path:
- All nodes with the same generation level SHALL have the same Y coordinate
- For any parent-child relationship in the path, the child's Y coordinate SHALL be greater than the parent's Y coordinate
- For any siblings in the same generation, they SHALL have the same Y coordinate but different X coordinates

**Validates: Requirements 5.5, 6.1, 6.3, 6.4**

### Property 4: Spouse Positioning Correctness

*For any* path containing spouse relationships:
- Spouses SHALL have the same Y coordinate (same generation level)
- Spouses SHALL be positioned adjacent to each other (X coordinates differ by NODE_WIDTH + SPOUSE_GAP)

**Validates: Requirements 5.3, 6.2**

### Property 5: Birth-Death Year Formatting

*For any* PersonNodeData with birth_year and optional death_year:
- If death_year is null, the display SHALL be "{birth_year} -"
- If death_year is not null, the display SHALL be "{birth_year} - {death_year}"

**Validates: Requirements 7.3**

### Property 6: Path Summary Accuracy

*For any* valid transformed path:
- The person count SHALL equal the number of nodes in the path
- The path summary string SHALL contain all person names in the correct order (from Person A to Person B)
- The path summary SHALL use "→" as the separator between names

**Validates: Requirements 11.1, 11.2**
