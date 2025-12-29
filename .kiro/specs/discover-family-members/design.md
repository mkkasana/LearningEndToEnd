# Design Document

## Overview

This feature implements an intelligent family member discovery system that proactively suggests potential family connections when users click "Add Family Member". The system analyzes existing relationships to identify persons who are connected to the user's family members but not yet directly connected to the user, enabling quick connection establishment without manual data entry.

The discovery system implements three relationship inference patterns:
1. **Spouse's Children** → Suggest as user's Son/Daughter
2. **Parent's Spouse** → Suggest as user's Father/Mother
3. **Child's Parent** → Suggest as user's Spouse

## Architecture

### System Components

**Backend:**
- `PersonDiscoveryService` - Core discovery logic and relationship traversal
- `GET /api/v1/person/discover-family-members` - Discovery API endpoint
- `PersonDiscoveryResult` - Response schema for discovered persons

**Frontend:**
- `DiscoverFamilyMembersDialog.tsx` - Main discovery dialog component
- Updated `AddFamilyMemberDialog.tsx` - Integration point for discovery flow
- Reused `ConnectConfirmationDialog.tsx` - Connection confirmation

### Data Flow

```
User clicks "Add Family Member"
         ↓
Call Discovery API
         ↓
   Has suggestions?
    ↙         ↘
  Yes          No
   ↓            ↓
Show Discovery  Show Multi-step
Dialog          Wizard
   ↓
User connects or skips
   ↓
Multi-step Wizard (if skipped)
```

## Components and Interfaces

### Backend Components

#### 1. PersonDiscoveryService

```python
class PersonDiscoveryService:
    """Service for discovering potential family member connections."""
    
    def __init__(self, session: Session):
        """Initialize the discovery service.
        
        Args:
            session: Database session
        """
        self.session = session
        self.person_repo = PersonRepository(session)
        self.relationship_repo = PersonRelationshipRepository(session)
        self.address_repo = PersonAddressRepository(session)
        self.religion_repo = PersonReligionRepository(session)
    
    def discover_family_members(
        self,
        current_user_id: uuid.UUID
    ) -> list[PersonDiscoveryResult]:
        """Discover potential family member connections.
        
        Implements three discovery patterns:
        1. Spouse's children → User's children
        2. Parent's spouse → User's parent
        3. Child's parent → User's spouse
        
        Args:
            current_user_id: Current user's ID
            
        Returns:
            List of discovered persons with inferred relationships
        """
        pass
    
    def _discover_spouses_children(
        self,
        person_id: uuid.UUID,
        connected_person_ids: set[uuid.UUID]
    ) -> list[PersonDiscoveryResult]:
        """Discover children of user's spouse.
        
        Logic:
        1. Find all persons connected to user as Spouse/Wife/Husband
        2. For each spouse, find their children (Son/Daughter relationships)
        3. Filter out children already connected to user
        4. Infer relationship type based on child's gender
        
        Args:
            person_id: User's person ID
            connected_person_ids: Set of already-connected person IDs
            
        Returns:
            List of discovered children
        """
        pass
    
    def _discover_parents_spouse(
        self,
        person_id: uuid.UUID,
        connected_person_ids: set[uuid.UUID]
    ) -> list[PersonDiscoveryResult]:
        """Discover spouse of user's parent.
        
        Logic:
        1. Find all persons connected to user as Father/Mother
        2. For each parent, find their spouse (Spouse/Wife/Husband relationships)
        3. Filter out spouses already connected to user
        4. Infer relationship type based on spouse's gender
        
        Args:
            person_id: User's person ID
            connected_person_ids: Set of already-connected person IDs
            
        Returns:
            List of discovered parents
        """
        pass
    
    def _discover_childs_parent(
        self,
        person_id: uuid.UUID,
        connected_person_ids: set[uuid.UUID]
    ) -> list[PersonDiscoveryResult]:
        """Discover parent of user's child.
        
        Logic:
        1. Find all persons connected to user as Son/Daughter
        2. For each child, find their parents (Father/Mother relationships)
        3. Filter out parents already connected to user
        4. Infer relationship type as "Spouse" (gender-neutral)
        
        Args:
            person_id: User's person ID
            connected_person_ids: Set of already-connected person IDs
            
        Returns:
            List of discovered spouses
        """
        pass
    
    def _build_discovery_result(
        self,
        person_id: uuid.UUID,
        inferred_relationship_type: str,
        connection_path: str
    ) -> PersonDiscoveryResult | None:
        """Build a discovery result with person details.
        
        Args:
            person_id: Discovered person's ID
            inferred_relationship_type: Inferred relationship type ID
            connection_path: Human-readable connection path
            
        Returns:
            PersonDiscoveryResult or None if person not found
        """
        pass
    
    def _infer_child_relationship(self, gender_id: uuid.UUID) -> str:
        """Infer Son or Daughter based on gender.
        
        Args:
            gender_id: Gender ID of the child
            
        Returns:
            Relationship type ID (Son or Daughter)
        """
        pass
    
    def _infer_parent_relationship(self, gender_id: uuid.UUID) -> str:
        """Infer Father or Mother based on gender.
        
        Args:
            gender_id: Gender ID of the parent
            
        Returns:
            Relationship type ID (Father or Mother)
        """
        pass
```

#### 2. API Endpoint

```python
@router.get("/discover-family-members", response_model=list[PersonDiscoveryResult])
@log_route
def discover_family_members(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Discover potential family member connections for the current user.
    
    This endpoint analyzes existing relationships to find persons who are:
    - Connected to the user's family members
    - Not yet directly connected to the user
    
    Discovery patterns:
    1. Spouse's children → Suggested as user's Son/Daughter
    2. Parent's spouse → Suggested as user's Father/Mother
    3. Child's parent → Suggested as user's Spouse
    
    Returns:
        List of discovered persons with inferred relationship types,
        sorted by relationship proximity and type priority.
        Limited to top 20 results.
    """
    logger.info(f"Discovery request from user {current_user.email}")
    
    try:
        discovery_service = PersonDiscoveryService(session)
        discoveries = discovery_service.discover_family_members(current_user.id)
        
        logger.info(
            f"Found {len(discoveries)} potential connections for user {current_user.email}"
        )
        return discoveries
        
    except Exception as e:
        logger.exception(
            f"Error in family member discovery for user {current_user.email}: {str(e)}"
        )
        raise HTTPException(
            status_code=500,
            detail="An error occurred while discovering family members",
        )
```

### Frontend Components

#### 1. DiscoverFamilyMembersDialog Component

```typescript
interface DiscoverFamilyMembersDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSkip: () => void
}

export function DiscoverFamilyMembersDialog({
  open,
  onOpenChange,
  onSkip,
}: DiscoverFamilyMembersDialogProps) {
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const queryClient = useQueryClient()
  const [showConnectDialog, setShowConnectDialog] = useState(false)
  const [selectedPerson, setSelectedPerson] = useState<PersonDiscoveryResult | null>(null)

  // Fetch discovered family members
  const {
    data: discoveries,
    isLoading,
    isError,
    error,
  } = useQuery({
    queryKey: ["discoverFamilyMembers"],
    queryFn: () => PersonService.discoverFamilyMembers(),
    enabled: open,
  })

  // Mutation for creating relationship
  const createRelationshipMutation = useMutation({
    mutationFn: (data: { relatedPersonId: string; relationshipType: string }) =>
      PersonService.createMyRelationship({
        requestBody: {
          related_person_id: data.relatedPersonId,
          relationship_type: data.relationshipType,
          is_active: true,
        },
      }),
    onSuccess: () => {
      showSuccessToast("Successfully connected to family member!")
      queryClient.invalidateQueries({ queryKey: ["myRelationshipsWithDetails"] })
      queryClient.invalidateQueries({ queryKey: ["discoverFamilyMembers"] })
      setShowConnectDialog(false)
      
      // If no more discoveries, close dialog
      if (discoveries && discoveries.length <= 1) {
        onOpenChange(false)
      }
    },
    onError: (error: any) => {
      showErrorToast(error.message || "Failed to create relationship")
    },
  })

  const handleConnect = (person: PersonDiscoveryResult) => {
    setSelectedPerson(person)
    setShowConnectDialog(true)
  }

  const handleConfirmConnect = () => {
    if (selectedPerson) {
      createRelationshipMutation.mutate({
        relatedPersonId: selectedPerson.person_id,
        relationshipType: selectedPerson.inferred_relationship_type,
      })
    }
  }

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Discover Family Members</DialogTitle>
            <DialogDescription>
              We found some family members you might want to connect with
            </DialogDescription>
          </DialogHeader>

          {/* Loading state */}
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
            </div>
          )}

          {/* Error state */}
          {isError && (
            <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
              <p className="text-sm text-destructive">
                {error?.message || "Failed to discover family members"}
              </p>
            </div>
          )}

          {/* Results */}
          {!isLoading && !isError && discoveries && discoveries.length > 0 && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Found {discoveries.length} potential family member(s)
              </p>

              {/* Scrollable list */}
              <div className="max-h-96 overflow-y-auto space-y-3">
                {discoveries.map((person) => (
                  <div
                    key={person.person_id}
                    className="border rounded-lg p-4 space-y-2 hover:bg-muted/50 transition-colors"
                  >
                    {/* Name and relationship */}
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium">
                          {person.first_name}{" "}
                          {person.middle_name && `${person.middle_name} `}
                          {person.last_name}
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          Suggested as: {person.inferred_relationship_label}
                        </p>
                      </div>
                    </div>

                    {/* Connection path */}
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">Connection:</span>{" "}
                      {person.connection_path}
                    </div>

                    {/* Date of birth */}
                    <div className="text-sm text-muted-foreground">
                      <span className="font-medium">DOB:</span>{" "}
                      {new Date(person.date_of_birth).toLocaleDateString()}
                    </div>

                    {/* Address */}
                    {person.address_display && (
                      <div className="text-sm text-muted-foreground">
                        <span className="font-medium">Address:</span>{" "}
                        {person.address_display}
                      </div>
                    )}

                    {/* Religion */}
                    {person.religion_display && (
                      <div className="text-sm text-muted-foreground">
                        <span className="font-medium">Religion:</span>{" "}
                        {person.religion_display}
                      </div>
                    )}

                    {/* Connect button */}
                    <div className="pt-2">
                      <Button
                        size="sm"
                        onClick={() => handleConnect(person)}
                      >
                        Connect as {person.inferred_relationship_label}
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer buttons */}
          <div className="flex justify-between pt-4">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
            <Button onClick={onSkip}>
              Skip: Move to create new
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Connect Confirmation Dialog */}
      {selectedPerson && (
        <ConnectConfirmationDialog
          open={showConnectDialog}
          onOpenChange={setShowConnectDialog}
          personId={selectedPerson.person_id}
          personName={`${selectedPerson.first_name} ${selectedPerson.middle_name ? selectedPerson.middle_name + ' ' : ''}${selectedPerson.last_name}`}
          relationshipType={selectedPerson.inferred_relationship_label}
          onConfirm={handleConfirmConnect}
          isLoading={createRelationshipMutation.isPending}
        />
      )}
    </>
  )
}
```

#### 2. Updated AddFamilyMemberDialog Integration

```typescript
// In family.tsx (or wherever "Add Family Member" button is)
const [showDiscoveryDialog, setShowDiscoveryDialog] = useState(false)
const [showAddDialog, setShowAddDialog] = useState(false)

const handleAddFamilyMember = () => {
  // First show discovery dialog
  setShowDiscoveryDialog(true)
}

const handleSkipDiscovery = () => {
  // Close discovery and open manual wizard
  setShowDiscoveryDialog(false)
  setShowAddDialog(true)
}

return (
  <>
    <Button onClick={handleAddFamilyMember}>
      <UserPlus className="mr-2 h-4 w-4" />
      Add Family Member
    </Button>

    <DiscoverFamilyMembersDialog
      open={showDiscoveryDialog}
      onOpenChange={setShowDiscoveryDialog}
      onSkip={handleSkipDiscovery}
    />

    <AddFamilyMemberDialog
      open={showAddDialog}
      onOpenChange={setShowAddDialog}
    />
  </>
)
```

## Data Models

### PersonDiscoveryResult Schema

```python
class PersonDiscoveryResult(BaseModel):
    """Result of family member discovery."""
    
    person_id: uuid.UUID
    first_name: str
    middle_name: str | None = None
    last_name: str
    date_of_birth: date
    date_of_death: date | None = None
    gender_id: uuid.UUID
    
    # Address information
    address_display: str | None = None
    
    # Religion information
    religion_display: str | None = None
    
    # Discovery metadata
    inferred_relationship_type: str  # Relationship type ID (e.g., "rel-6a0ede824d104")
    inferred_relationship_label: str  # Human-readable label (e.g., "Son")
    connection_path: str  # e.g., "Connected to your spouse Maria Garcia"
    
    # Sorting metadata
    proximity_score: int  # 1 = direct connection, 2 = 2 degrees, etc.
    relationship_priority: int  # 1 = children, 2 = parents, 3 = spouses
```

### Relationship Type Constants

```python
# From existing codebase
class RelationshipType(str, Enum):
    FATHER = "rel-6a0ede824d101"
    MOTHER = "rel-6a0ede824d102"
    DAUGHTER = "rel-6a0ede824d103"
    SON = "rel-6a0ede824d104"
    WIFE = "rel-6a0ede824d105"
    HUSBAND = "rel-6a0ede824d106"
    SPOUSE = "rel-6a0ede824d107"
```

### Gender Constants

```python
# Assuming from existing codebase
GENDER_MALE = "gender-id-male"
GENDER_FEMALE = "gender-id-female"
```

## Discovery Logic Details

### Pattern 1: Spouse's Children

**SQL Query Logic:**
```sql
-- Find user's spouses
SELECT related_person_id 
FROM person_relationship 
WHERE person_id = :user_person_id 
  AND relationship_type IN ('rel-6a0ede824d105', 'rel-6a0ede824d106', 'rel-6a0ede824d107')
  AND is_active = true

-- For each spouse, find their children
SELECT related_person_id, relationship_type
FROM person_relationship
WHERE person_id = :spouse_person_id
  AND relationship_type IN ('rel-6a0ede824d103', 'rel-6a0ede824d104')
  AND is_active = true
  AND related_person_id NOT IN (
    -- Exclude already connected
    SELECT related_person_id 
    FROM person_relationship 
    WHERE person_id = :user_person_id
  )
```

**Relationship Inference:**
- If child's gender is male → Infer "Son" (`rel-6a0ede824d104`)
- If child's gender is female → Infer "Daughter" (`rel-6a0ede824d103`)
- If gender unknown → Default to "Son"

**Connection Path:**
- Format: `"Connected to your spouse {spouse_name}"`
- Example: `"Connected to your spouse Maria Garcia"`

### Pattern 2: Parent's Spouse

**SQL Query Logic:**
```sql
-- Find user's parents
SELECT related_person_id 
FROM person_relationship 
WHERE person_id = :user_person_id 
  AND relationship_type IN ('rel-6a0ede824d101', 'rel-6a0ede824d102')
  AND is_active = true

-- For each parent, find their spouse
SELECT related_person_id, relationship_type
FROM person_relationship
WHERE person_id = :parent_person_id
  AND relationship_type IN ('rel-6a0ede824d105', 'rel-6a0ede824d106', 'rel-6a0ede824d107')
  AND is_active = true
  AND related_person_id NOT IN (
    -- Exclude already connected
    SELECT related_person_id 
    FROM person_relationship 
    WHERE person_id = :user_person_id
  )
```

**Relationship Inference:**
- If spouse's gender is male → Infer "Father" (`rel-6a0ede824d101`)
- If spouse's gender is female → Infer "Mother" (`rel-6a0ede824d102`)
- If gender unknown → Default to "Father"

**Connection Path:**
- Format: `"Connected to your parent {parent_name}"`
- Example: `"Connected to your parent John Smith"`

### Pattern 3: Child's Parent

**SQL Query Logic:**
```sql
-- Find user's children
SELECT related_person_id 
FROM person_relationship 
WHERE person_id = :user_person_id 
  AND relationship_type IN ('rel-6a0ede824d103', 'rel-6a0ede824d104')
  AND is_active = true

-- For each child, find their parents
SELECT related_person_id, relationship_type
FROM person_relationship
WHERE person_id = :child_person_id
  AND relationship_type IN ('rel-6a0ede824d101', 'rel-6a0ede824d102')
  AND is_active = true
  AND related_person_id NOT IN (
    -- Exclude already connected
    SELECT related_person_id 
    FROM person_relationship 
    WHERE person_id = :user_person_id
  )
```

**Relationship Inference:**
- Always infer "Spouse" (`rel-6a0ede824d107`) - gender-neutral

**Connection Path:**
- Format: `"Connected to your child {child_name}"`
- Example: `"Connected to your child Emma Johnson"`

## Sorting and Filtering

### Sorting Priority

Results are sorted by:
1. **Proximity Score** (ascending): Direct connections first
   - 1 = Direct connection (1 degree of separation)
   - 2 = 2 degrees of separation
   
2. **Relationship Priority** (ascending): Children, then parents, then spouses
   - 1 = Children (Son/Daughter)
   - 2 = Parents (Father/Mother)
   - 3 = Spouses (Spouse/Wife/Husband)
   
3. **Alphabetical** (ascending): By first name

### Filtering Rules

- **Exclude current user**: Never suggest user's own person record
- **Exclude already connected**: Filter out persons with existing active relationships
- **Limit results**: Return maximum 20 suggestions
- **Active relationships only**: Only consider `is_active = true` relationships

### Deduplication

If a person appears through multiple paths:
- Keep only the most direct connection (lowest proximity score)
- If same proximity, keep highest priority relationship type
- Include connection path from the kept result

## Error Handling

### Backend Error Scenarios

1. **User has no person record**
   - Return empty list
   - Log warning

2. **Database query fails**
   - Return 500 error
   - Log exception with full stack trace

3. **Person details not found**
   - Skip that discovery result
   - Continue with other results
   - Log warning

### Frontend Error Scenarios

1. **API call fails**
   - Show error message in dialog
   - Provide "Try Again" button
   - Allow user to skip to manual wizard

2. **No discoveries found**
   - Automatically proceed to manual wizard
   - No dialog shown

3. **Connection creation fails**
   - Show error toast
   - Keep discovery dialog open
   - Allow retry

## Testing Strategy

### Unit Tests

**Backend:**
- Test each discovery pattern independently
- Test relationship inference logic
- Test sorting and filtering
- Test deduplication logic
- Test error handling

**Frontend:**
- Test dialog rendering with mock data
- Test connection flow
- Test skip functionality
- Test error states

### Integration Tests

- Test complete discovery flow end-to-end
- Test with various family structures:
  - User with spouse and spouse's children
  - User with parents and parent's spouse
  - User with children and child's parent
  - User with multiple patterns
  - User with no discoveries
- Test connection creation after discovery
- Test bidirectional relationship creation

### Edge Cases

- User with no relationships → Empty list
- Circular relationships → Prevent infinite loops
- Deceased persons → Include in suggestions
- Multiple spouses → Show children from all
- Step-parent scenarios → Correctly infer relationships
- Gender unknown → Use default inference
- Duplicate discoveries → Deduplicate correctly

## Performance Considerations

### Database Optimization

- **Indexes**: Ensure indexes on:
  - `person_relationship.person_id`
  - `person_relationship.related_person_id`
  - `person_relationship.relationship_type`
  - `person_relationship.is_active`

- **Query Optimization**:
  - Use `IN` clauses for batch lookups
  - Eager load person details to minimize queries
  - Limit result set early in query

### Caching Strategy

- **Cache discovery results**: 5 minutes TTL
- **Cache key**: `discovery:{user_id}`
- **Invalidate on**:
  - New relationship created
  - Relationship deleted
  - Relationship updated

### Frontend Optimization

- **Lazy loading**: Only fetch when dialog opens
- **Query invalidation**: Refresh after connection
- **Optimistic updates**: Update UI before API response

## Security Considerations

- **Authentication required**: Endpoint requires valid user session
- **Authorization**: Users can only discover their own family members
- **Data privacy**: Only return persons connected to user's family
- **Rate limiting**: Apply standard API rate limits

## Future Enhancements

1. **Extended discovery patterns**:
   - Siblings of parents (aunts/uncles)
   - Children of siblings (nieces/nephews)
   - Siblings of spouse (in-laws)

2. **Smart suggestions**:
   - ML-based relationship prediction
   - Confidence scores for suggestions

3. **Batch connections**:
   - Allow connecting to multiple persons at once
   - "Connect All" button

4. **Discovery history**:
   - Track dismissed suggestions
   - Don't show again option
