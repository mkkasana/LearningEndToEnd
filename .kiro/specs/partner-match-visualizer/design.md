# Design Document: Partner Match Visualizer

## Overview

This feature enhances the Find Partner UI by replacing the raw JSON results display with an interactive graph visualization. Users can select a match from a dropdown and see the relationship path from seeker to match rendered as a generation-based family tree using React Flow.

The core challenge is extracting a linear path from the BFS exploration graph (which is a tree structure) by tracing backwards from the selected match to the seeker using `from_person` pointers.

All components are implemented within the `FindPartner/` folder to maintain complete isolation from Rishte components.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Find Partner Page                          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Header + Filter Button                                      ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Searching as: John Doe                                      ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  5 matches found    [▼ Priya Sharma (1992)               ]  ││
│  │                      Match Selector Dropdown                 ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Path: John → Ram → Shyam → Priya                           ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                                                              ││
│  │                   React Flow Canvas                          ││
│  │                   (Match Graph)                              ││
│  │                                                              ││
│  │     [MatchPersonNode] ──edge──> [MatchPersonNode]           ││
│  │                                                              ││
│  └─────────────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Graph Controls                                  ││
│  │  [Zoom In] [Zoom Out] [Fit View]                            ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### File Structure

```
frontend/src/components/FindPartner/
├── index.ts                      # Update exports
├── types.ts                      # Add new types
├── PartnerFilterPanel.tsx        # Existing (no changes)
├── PartnerResultsDisplay.tsx     # REPLACE implementation
├── TagInput.tsx                  # Existing (no changes)
├── MatchSelector.tsx             # NEW - dropdown to select match
├── MatchPathSummary.tsx          # NEW - path text summary
├── MatchGraph.tsx                # NEW - React Flow container
├── MatchPersonNode.tsx           # NEW - custom node component
├── MatchRelationshipEdge.tsx     # NEW - custom edge component
├── MatchGraphControls.tsx        # NEW - zoom controls
├── hooks/
│   └── usePartnerDefaults.ts     # Existing (no changes)
└── utils/
    ├── defaultsCalculator.ts     # Existing (no changes)
    ├── matchPathExtractor.ts     # NEW - extract path from BFS tree
    └── matchGraphTransformer.ts  # NEW - transform to React Flow
```

### TypeScript Interfaces

```typescript
// types.ts - New types to add

/**
 * Match item for dropdown display
 */
export interface MatchItem {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  depth: number
}

/**
 * Data for Match Person Node
 */
export interface MatchPersonNodeData {
  personId: string
  firstName: string
  lastName: string
  birthYear: number | null
  deathYear: number | null
  isSeeker: boolean              // Green border + "Seeker" label
  isMatch: boolean               // Blue border + "Match" label
}

/**
 * Data for Match Relationship Edge
 */
export interface MatchRelationshipEdgeData {
  relationship: string           // "Son", "Father", "Spouse", etc.
  isSpouseEdge: boolean         // Horizontal styling
}

/**
 * React Flow node for match graph
 */
export interface MatchNode {
  id: string
  type: 'matchPersonNode'
  position: { x: number; y: number }
  data: MatchPersonNodeData
}

/**
 * React Flow edge for match graph
 */
export interface MatchEdge {
  id: string
  source: string
  target: string
  sourceHandle?: string
  targetHandle?: string
  type: 'matchRelationshipEdge'
  data: MatchRelationshipEdgeData
  animated?: boolean
}

/**
 * Transformed path result
 */
export interface TransformedMatchPath {
  nodes: MatchNode[]
  edges: MatchEdge[]
}

/**
 * Generation info for layout calculation
 */
export interface MatchGenerationInfo {
  personId: string
  generation: number
  xOffset: number
  isSpouse: boolean
  spouseOfId?: string
}

/**
 * Props for MatchSelector
 */
export interface MatchSelectorProps {
  matches: MatchItem[]
  selectedMatchId: string | null
  onSelectMatch: (matchId: string) => void
  totalMatches: number
}

/**
 * Props for MatchPathSummary
 */
export interface MatchPathSummaryProps {
  pathNames: string[]
}

/**
 * Props for MatchGraph
 */
export interface MatchGraphProps {
  nodes: MatchNode[]
  edges: MatchEdge[]
}
```

### Component: MatchSelector

```typescript
// MatchSelector.tsx (pseudocode)

function MatchSelector({
  matches,
  selectedMatchId,
  onSelectMatch,
  totalMatches
}: MatchSelectorProps) {
  return (
    <div className="flex items-center gap-4">
      <span className="text-sm text-muted-foreground">
        {totalMatches} {totalMatches === 1 ? 'match' : 'matches'} found
      </span>
      
      <Select value={selectedMatchId} onValueChange={onSelectMatch}>
        <SelectTrigger className="w-[300px]">
          <SelectValue placeholder="Select a match" />
        </SelectTrigger>
        <SelectContent>
          {matches.map(match => (
            <SelectItem key={match.personId} value={match.personId}>
              {match.firstName} {match.lastName} ({match.birthYear || 'N/A'})
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  )
}
```

### Component: MatchPersonNode

```typescript
// MatchPersonNode.tsx (pseudocode)

function MatchPersonNode({ data }: { data: MatchPersonNodeData }) {
  const { firstName, lastName, birthYear, deathYear, isSeeker, isMatch } = data
  
  const getBorderClass = () => {
    if (isSeeker) return "border-2 border-green-500"
    if (isMatch) return "border-2 border-blue-500"
    return "border border-border"
  }
  
  const yearsDisplay = formatBirthDeathYears(birthYear, deathYear)
  
  return (
    <>
      {/* Handles for edges - top, bottom, left, right */}
      <Handle type="target" position={Position.Top} id="top" />
      <Handle type="source" position={Position.Bottom} id="bottom" />
      <Handle type="target" position={Position.Left} id="left" />
      <Handle type="source" position={Position.Right} id="right" />
      
      <Card className={cn("flex flex-col items-center p-4", getBorderClass())}>
        <Avatar>
          <AvatarFallback><User /></AvatarFallback>
        </Avatar>
        
        <div className="text-center">
          <div className="font-semibold">{firstName} {lastName}</div>
          {yearsDisplay && <div className="text-xs">{yearsDisplay}</div>}
        </div>
        
        {/* Seeker/Match label */}
        {(isSeeker || isMatch) && (
          <Badge variant={isSeeker ? "success" : "info"}>
            {isSeeker ? "Seeker" : "Match"}
          </Badge>
        )}
      </Card>
    </>
  )
}
```

## Data Models

### API Response (existing)

```typescript
interface PartnerMatchResponse {
  seeker_id: string
  total_matches: number
  matches: string[]                              // Array of match person IDs
  exploration_graph: Record<string, MatchGraphNode>
}

interface MatchGraphNode {
  person_id: string
  first_name: string
  last_name: string
  birth_year: number | null
  death_year: number | null
  is_match: boolean
  depth: number
  from_person: MatchConnectionInfo | null       // Parent in BFS tree
  to_persons: MatchConnectionInfo[]             // Children explored
}

interface MatchConnectionInfo {
  person_id: string
  relationship: string
}
```

## Path Extraction Algorithm

The key algorithm extracts a linear path from the BFS exploration graph by tracing backwards from the selected match to the seeker.

### Step 1: Extract Path from Match to Seeker

```typescript
// utils/matchPathExtractor.ts

/**
 * Extract linear path from seeker to match by tracing from_person backwards
 */
export function extractPathToMatch(
  graph: Record<string, MatchGraphNode>,
  seekerId: string,
  matchId: string
): MatchGraphNode[] {
  const path: MatchGraphNode[] = []
  let current = graph[matchId]
  
  // Trace backwards from match to seeker
  while (current) {
    path.unshift(current)  // Add to front of array
    
    if (current.person_id === seekerId) {
      break  // Reached seeker
    }
    
    if (current.from_person) {
      current = graph[current.from_person.person_id]
    } else {
      break  // No more parents (shouldn't happen if graph is valid)
    }
  }
  
  return path
}

/**
 * Build match items for dropdown from API response
 */
export function buildMatchItems(
  graph: Record<string, MatchGraphNode>,
  matchIds: string[]
): MatchItem[] {
  return matchIds
    .map(id => {
      const node = graph[id]
      if (!node) return null
      return {
        personId: node.person_id,
        firstName: node.first_name,
        lastName: node.last_name,
        birthYear: node.birth_year,
        depth: node.depth
      }
    })
    .filter((item): item is MatchItem => item !== null)
    .sort((a, b) => a.depth - b.depth)  // Sort by depth (closest first)
}

/**
 * Generate path summary string
 */
export function generateMatchPathSummary(path: MatchGraphNode[]): string[] {
  return path.map(node => node.first_name)
}
```

### Step 2: Assign Generations

```typescript
// utils/matchGraphTransformer.ts

/**
 * Check relationship type helpers
 */
function isChildRelationship(rel: string): boolean {
  return ['Son', 'Daughter'].includes(rel)
}

function isParentRelationship(rel: string): boolean {
  return ['Father', 'Mother'].includes(rel)
}

function isSpouseRelationship(rel: string): boolean {
  return ['Spouse', 'Husband', 'Wife'].includes(rel)
}

/**
 * Assign generation levels based on relationships
 */
export function assignGenerations(
  path: MatchGraphNode[]
): Map<string, MatchGenerationInfo> {
  const generations = new Map<string, MatchGenerationInfo>()
  let currentGen = 0
  let currentXAxis = 0
  const generationToXAxis = new Map<number, number>()
  
  for (let i = 0; i < path.length; i++) {
    const node = path[i]
    const prevNode = i > 0 ? path[i - 1] : null
    
    // Get relationship from current node's from_person
    const relationship = node.from_person?.relationship
    
    if (relationship) {
      if (isChildRelationship(relationship)) {
        currentGen--  // Going UP (child → parent)
      } else if (isParentRelationship(relationship)) {
        currentGen++  // Going DOWN (parent → child)
      }
      // Spouse stays same generation
    }
    
    // Calculate X position
    if (relationship && isSpouseRelationship(relationship)) {
      currentXAxis++
    } else if (relationship) {
      const genXAxis = generationToXAxis.get(currentGen) ?? -1
      if (genXAxis >= currentXAxis) {
        currentXAxis = genXAxis + 1
      }
    }
    generationToXAxis.set(currentGen, currentXAxis)
    
    const isSpouse = isSpouseRelationship(relationship || '')
    
    generations.set(node.person_id, {
      personId: node.person_id,
      generation: currentGen,
      xOffset: currentXAxis,
      isSpouse,
      spouseOfId: isSpouse ? prevNode?.person_id : undefined
    })
  }
  
  // Normalize generations (min = 0)
  const minGen = Math.min(...Array.from(generations.values()).map(g => g.generation))
  generations.forEach(info => {
    info.generation -= minGen
  })
  
  return generations
}
```

### Step 3: Calculate Positions

```typescript
// Layout constants
const NODE_WIDTH = 180
const NODE_HEIGHT = 200
const HORIZONTAL_GAP = 100
const VERTICAL_GAP = 150

/**
 * Calculate pixel positions from generation info
 */
export function calculatePositions(
  generations: Map<string, MatchGenerationInfo>
): Map<string, { x: number; y: number }> {
  const positions = new Map<string, { x: number; y: number }>()
  
  generations.forEach((info, id) => {
    const x = info.xOffset * (NODE_WIDTH + HORIZONTAL_GAP)
    const y = info.generation * (NODE_HEIGHT + VERTICAL_GAP)
    positions.set(id, { x, y })
  })
  
  return positions
}
```

### Step 4: Create React Flow Elements

```typescript
/**
 * Transform path to React Flow nodes and edges
 */
export function transformMatchPath(
  path: MatchGraphNode[],
  seekerId: string,
  matchId: string
): TransformedMatchPath {
  if (path.length === 0) {
    return { nodes: [], edges: [] }
  }
  
  const generations = assignGenerations(path)
  const positions = calculatePositions(generations)
  
  // Create nodes
  const nodes: MatchNode[] = path.map(person => ({
    id: person.person_id,
    type: 'matchPersonNode',
    position: positions.get(person.person_id) || { x: 0, y: 0 },
    data: {
      personId: person.person_id,
      firstName: person.first_name,
      lastName: person.last_name,
      birthYear: person.birth_year,
      deathYear: person.death_year,
      isSeeker: person.person_id === seekerId,
      isMatch: person.person_id === matchId
    }
  }))
  
  // Create edges
  const edges: MatchEdge[] = []
  for (let i = 0; i < path.length - 1; i++) {
    const source = path[i]
    const target = path[i + 1]
    const relationship = target.from_person?.relationship || ''
    const isSpouse = isSpouseRelationship(relationship)
    
    const sourcePos = positions.get(source.person_id) || { x: 0, y: 0 }
    const targetPos = positions.get(target.person_id) || { x: 0, y: 0 }
    const { sourceHandle, targetHandle } = getEdgeHandles(sourcePos, targetPos)
    
    edges.push({
      id: `${source.person_id}-${target.person_id}`,
      source: source.person_id,
      target: target.person_id,
      sourceHandle,
      targetHandle,
      type: 'matchRelationshipEdge',
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
| Zero matches | Show "No matches found" message, hide dropdown and graph |
| Invalid match ID selected | Ignore, keep previous selection |
| Path extraction fails | Show error message |
| Graph node not found | Skip node, continue with available data |

## Testing Strategy

### Unit Tests

- `extractPathToMatch` - verify correct path extraction from BFS graph
- `buildMatchItems` - verify sorting by depth
- `assignGenerations` - verify generation assignment logic
- `calculatePositions` - verify position calculations
- `transformMatchPath` - verify complete transformation

### Property-Based Tests

Property-based tests will validate the core transformation logic.



## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Path Extraction Correctness

*For any* valid BFS exploration graph containing a path from seeker to match, the `extractPathToMatch` function SHALL:
- Return an array where the first element has `person_id` equal to `seekerId`
- Return an array where the last element has `person_id` equal to `matchId`
- Return an array where each consecutive pair (path[i], path[i+1]) satisfies: path[i+1].from_person.person_id === path[i].person_id

**Validates: Requirements 3.1, 3.2**

### Property 2: Match Sorting by Depth

*For any* list of match items with depth values, the `buildMatchItems` function SHALL return items sorted in ascending order by depth (closest matches first).

**Validates: Requirements 1.4**

### Property 3: Path Summary Correctness

*For any* extracted path with N persons:
- The path summary SHALL contain exactly N names
- The first name SHALL be the seeker's first name
- The last name SHALL be the match's first name
- When joined with " → ", the result SHALL have exactly N-1 arrow separators

**Validates: Requirements 4.1, 4.2, 4.3**

### Property 4: Generation Layout Correctness

*For any* transformed path:
- All nodes with the same generation level SHALL have the same Y coordinate
- For any parent-child relationship (Father/Mother → Son/Daughter), the child's Y coordinate SHALL be greater than the parent's Y coordinate
- For any spouse relationship, both nodes SHALL have the same Y coordinate but different X coordinates

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 5: Node Label Correctness

*For any* MatchPersonNodeData:
- If `isSeeker` is true, the node SHALL display "Seeker" label with green styling
- If `isMatch` is true, the node SHALL display "Match" label with blue styling
- Exactly one node in any path SHALL have `isSeeker` = true
- Exactly one node in any path SHALL have `isMatch` = true

**Validates: Requirements 6.4, 6.5**

### Property 6: Birth-Death Year Formatting

*For any* MatchPersonNodeData with birth_year and optional death_year:
- If death_year is null, the display SHALL be "{birth_year} -"
- If death_year is not null, the display SHALL be "{birth_year} - {death_year}"

**Validates: Requirements 6.3**

### Property 7: Edge Styling Correctness

*For any* MatchRelationshipEdgeData:
- If `isSpouseEdge` is true, the edge SHALL use horizontal/straight path styling with distinct color (purple/dashed)
- If `isSpouseEdge` is false, the edge SHALL use vertical/bezier path styling
- The edge SHALL display the `relationship` string as a label

**Validates: Requirements 7.1, 7.2, 7.3, 7.5**

### Property 8: Match Count Display Correctness

*For any* API response with `total_matches` = N, the Match_Selector SHALL display "N matches found" (or "N match found" if N = 1).

**Validates: Requirements 1.2**

