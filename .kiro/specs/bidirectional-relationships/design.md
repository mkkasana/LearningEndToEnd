# Design Document

## Overview

This design implements bidirectional relationship management for the family tree system. When a user creates a relationship between two persons, the system will automatically create both the primary relationship and its inverse, ensuring complete family trees from any person's perspective.

## Architecture

### Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer                                │
│  POST /api/v1/person/me/relationships (create)              │
│  PATCH /api/v1/person/me/relationships/{id} (update)        │
│  DELETE /api/v1/person/me/relationships/{id} (delete)       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              PersonRelationshipService                       │
│  - create_relationship() → creates both directions          │
│  - update_relationship() → updates both directions          │
│  - delete_relationship() → deletes both directions          │
│  - _get_inverse_relationship_type() → determines inverse    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         RelationshipTypeHelper (New Utility)                │
│  - get_inverse_type() → maps relationship types             │
│  - requires_gender_context() → checks if gender needed      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          PersonRelationshipRepository                        │
│  - create() → inserts relationship record                   │
│  - update() → updates relationship record                   │
│  - delete() → removes relationship record                   │
│  - find_inverse() → finds matching inverse relationship     │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. RelationshipTypeHelper (New Utility Class)

```python
class RelationshipTypeHelper:
    """Helper for relationship type operations."""
    
    @staticmethod
    def get_inverse_type(
        relationship_type: RelationshipType,
        person_gender_id: uuid.UUID,
        related_person_gender_id: uuid.UUID,
        gender_mapping: dict[uuid.UUID, str]
    ) -> RelationshipType | None:
        """
        Determine the inverse relationship type.
        
        SEMANTICS:
        - When A → B with relationship_type, we need to create B → A with inverse_type
        - relationship_type describes who B is to A
        - inverse_type describes who A is to B
        - For parent-child relationships, we use person_gender (A's gender) to determine inverse
        
        Example:
        - A → B as Father (B is A's father)
        - If A is male: B → A as Son (A is B's son)
        - If A is female: B → A as Daughter (A is B's daughter)
        
        Args:
            relationship_type: The primary relationship type (describes B to A)
            person_gender_id: Gender ID of person A (who creates the relationship)
            related_person_gender_id: Gender ID of person B (the related person)
            gender_mapping: Mapping of gender_id to gender label (male/female)
            
        Returns:
            The inverse relationship type, or None if cannot be determined
        """
        pass
    
    @staticmethod
    def requires_gender_context(relationship_type: RelationshipType) -> bool:
        """Check if relationship type requires gender to determine inverse."""
        pass
```

### 2. Updated PersonRelationshipService

```python
class PersonRelationshipService:
    """Service for bidirectional relationship management."""
    
    def create_relationship(
        self, 
        person_id: uuid.UUID, 
        relationship_create: PersonRelationshipCreate
    ) -> PersonRelationship:
        """
        Create bidirectional relationship.
        
        Steps:
        1. Fetch both persons to get gender information
        2. Create primary relationship (A → B)
        3. Determine inverse relationship type
        4. Create inverse relationship (B → A)
        5. Return primary relationship
        """
        pass
    
    def update_relationship(
        self, 
        relationship: PersonRelationship, 
        relationship_update: PersonRelationshipUpdate
    ) -> PersonRelationship:
        """
        Update both directions of relationship.
        
        Steps:
        1. Update primary relationship
        2. Find inverse relationship
        3. Update inverse relationship (matching fields only)
        4. Return updated primary relationship
        """
        pass
    
    def delete_relationship(self, relationship: PersonRelationship) -> None:
        """
        Delete both directions of relationship.
        
        Steps:
        1. Find inverse relationship
        2. Delete primary relationship
        3. Delete inverse relationship
        4. Use transaction to ensure atomicity
        """
        pass
```

### 3. Updated PersonRelationshipRepository

```python
class PersonRelationshipRepository:
    """Repository with inverse relationship support."""
    
    def find_inverse(
        self, 
        person_id: uuid.UUID, 
        related_person_id: uuid.UUID
    ) -> PersonRelationship | None:
        """
        Find the inverse relationship.
        
        Query:
        SELECT * FROM person_relationship
        WHERE person_id = related_person_id
          AND related_person_id = person_id
          AND is_active = TRUE
        """
        pass
```

## Data Models

### Gender Mapping

```python
# In-memory mapping (can be cached from database)
GENDER_MAPPING = {
    "gender-uuid-male": "male",
    "gender-uuid-female": "female",
}
```

### Relationship Type Inverse Rules

**CRITICAL SEMANTICS:**
- When A creates relationship with B as "Father": `person_id=A, related_person_id=B, type="Father"`
- This means: "B is A's father"
- Inverse should be: `person_id=B, related_person_id=A, type="Son/Daughter"` (based on A's gender)
- This means: "A is B's son/daughter"

```python
INVERSE_RULES = {
    # Parent-Child relationships (gender-dependent on person_id's gender)
    # When A → B as Father (B is A's father), create B → A as Son/Daughter (A is B's son/daughter)
    (RelationshipType.FATHER, "male"): RelationshipType.SON,      # A is male, so A is B's son
    (RelationshipType.FATHER, "female"): RelationshipType.DAUGHTER,  # A is female, so A is B's daughter
    (RelationshipType.MOTHER, "male"): RelationshipType.SON,      # A is male, so A is B's son
    (RelationshipType.MOTHER, "female"): RelationshipType.DAUGHTER,  # A is female, so A is B's daughter
    
    # Child-Parent relationships (gender-dependent on person_id's gender)
    # When A → B as Son (B is A's son), create B → A as Father/Mother (A is B's father/mother)
    (RelationshipType.SON, "male"): RelationshipType.FATHER,      # A is male, so A is B's father
    (RelationshipType.SON, "female"): RelationshipType.MOTHER,    # A is female, so A is B's mother
    (RelationshipType.DAUGHTER, "male"): RelationshipType.FATHER,  # A is male, so A is B's father
    (RelationshipType.DAUGHTER, "female"): RelationshipType.MOTHER,  # A is female, so A is B's mother
    
    # Spouse relationships (gender-independent)
    # When A → B as Husband (B is A's husband), create B → A as Wife (A is B's wife)
    RelationshipType.HUSBAND: RelationshipType.WIFE,
    RelationshipType.WIFE: RelationshipType.HUSBAND,
    RelationshipType.SPOUSE: RelationshipType.SPOUSE,
}
```

## Error Handling

### Transaction Management

All bidirectional operations use database transactions:

```python
with self.session.begin():
    # Create/Update/Delete primary
    # Create/Update/Delete inverse
    # Commit or rollback together
```

### Error Scenarios

1. **Inverse Not Found During Update/Delete**
   - Log warning
   - Continue with primary operation
   - Don't fail the request

2. **Gender Information Missing**
   - Log error
   - Create primary relationship only
   - Return success with warning

3. **Database Constraint Violation**
   - Rollback transaction
   - Return 400 error to user
   - Log full error details

## Testing Strategy

### Unit Tests

1. **Test RelationshipTypeHelper.get_inverse_type()**
   - Test all relationship type combinations
   - Test with different gender combinations
   - Test edge cases (unknown types, missing genders)

2. **Test PersonRelationshipService.create_relationship()**
   - Verify both relationships are created
   - Verify correct inverse types
   - Verify transaction rollback on error

3. **Test PersonRelationshipService.update_relationship()**
   - Verify both relationships are updated
   - Verify only appropriate fields are synced
   - Verify handling of missing inverse

4. **Test PersonRelationshipService.delete_relationship()**
   - Verify both relationships are deleted
   - Verify transaction atomicity
   - Verify handling of missing inverse

### Integration Tests

1. **End-to-End Relationship Creation**
   - Create relationship via API
   - Query both persons' relationships
   - Verify both see each other correctly

2. **End-to-End Relationship Update**
   - Update relationship via API
   - Verify both directions reflect changes

3. **End-to-End Relationship Deletion**
   - Delete relationship via API
   - Verify both directions are removed

### Migration Testing

1. **Test Migration Script**
   - Create test data with single-direction relationships
   - Run migration
   - Verify inverse relationships created
   - Verify idempotency (can run multiple times)

## Migration Strategy

### Data Migration Script

```python
# scripts/migrate_bidirectional_relationships.py

def migrate_relationships(session: Session):
    """Migrate existing relationships to bidirectional."""
    
    # Get all relationships
    relationships = session.exec(select(PersonRelationship)).all()
    
    created_count = 0
    error_count = 0
    
    for rel in relationships:
        # Check if inverse exists
        inverse = find_inverse(session, rel.person_id, rel.related_person_id)
        
        if not inverse:
            try:
                # Create inverse
                inverse_type = determine_inverse_type(rel)
                create_inverse_relationship(session, rel, inverse_type)
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create inverse for {rel.id}: {e}")
                error_count += 1
    
    logger.info(f"Migration complete: {created_count} created, {error_count} errors")
```

## Deployment Plan

1. **Phase 1: Deploy Code**
   - Deploy updated service layer
   - New relationships will be bidirectional
   - Old relationships still work (read-only)

2. **Phase 2: Run Migration**
   - Run migration script on production database
   - Creates inverse relationships for existing data
   - Monitor for errors

3. **Phase 3: Verification**
   - Verify all relationships have inverses
   - Test family tree queries from multiple perspectives
   - Monitor application logs for warnings

## Performance Considerations

### Database Impact

- **Writes**: 2x (creates two records instead of one)
- **Reads**: Same (still query by person_id)
- **Storage**: 2x (stores two records instead of one)

### Optimization

- Use database transactions to ensure atomicity
- Batch operations where possible
- Index on (person_id, related_person_id) for fast inverse lookups

### Monitoring

- Track relationship creation time
- Monitor transaction rollback rate
- Alert on missing inverse relationships
