# Relationship Semantics Correction

## Critical Understanding

### Database Schema
```
person_id: UUID          # The person who owns/creates the relationship
related_person_id: UUID  # The person they're related to
relationship_type: Enum  # Describes who the related_person IS TO the person
```

### Correct Interpretation

When Person A creates a relationship with Person B:
- `person_id = A`
- `related_person_id = B`
- `relationship_type = "Father"`

**This means:** "B is A's father" (NOT "A is B's father")

### Inverse Relationship Logic

When creating the inverse relationship, we swap the person IDs and determine the inverse type based on **person A's gender** (not B's):

**Example 1: A adds B as Father**
- Primary: `person_id=A, related_person_id=B, type=Father` → "B is A's father"
- If A is male: Inverse = `person_id=B, related_person_id=A, type=Son` → "A is B's son"
- If A is female: Inverse = `person_id=B, related_person_id=A, type=Daughter` → "A is B's daughter"

**Example 2: A adds B as Son**
- Primary: `person_id=A, related_person_id=B, type=Son` → "B is A's son"
- If A is male: Inverse = `person_id=B, related_person_id=A, type=Father` → "A is B's father"
- If A is female: Inverse = `person_id=B, related_person_id=A, type=Mother` → "A is B's mother"

## Complete Inverse Mapping Rules

### Parent-Child Relationships (Gender-Dependent)

| Primary Relationship | Person A Gender | Inverse Relationship | Meaning |
|---------------------|-----------------|---------------------|---------|
| A → B as Father | Male | B → A as Son | B is A's father, A is B's son |
| A → B as Father | Female | B → A as Daughter | B is A's father, A is B's daughter |
| A → B as Mother | Male | B → A as Son | B is A's mother, A is B's son |
| A → B as Mother | Female | B → A as Daughter | B is A's mother, A is B's daughter |
| A → B as Son | Male | B → A as Father | B is A's son, A is B's father |
| A → B as Son | Female | B → A as Mother | B is A's son, A is B's mother |
| A → B as Daughter | Male | B → A as Father | B is A's daughter, A is B's father |
| A → B as Daughter | Female | B → A as Mother | B is A's daughter, A is B's mother |

### Spouse Relationships (Gender-Independent)

| Primary Relationship | Inverse Relationship | Meaning |
|---------------------|---------------------|---------|
| A → B as Husband | B → A as Wife | B is A's husband, A is B's wife |
| A → B as Wife | B → A as Husband | B is A's wife, A is B's husband |
| A → B as Spouse | B → A as Spouse | B is A's spouse, A is B's spouse |

## What Was Corrected

### Before (Incorrect)
The original implementation checked the **related_person's gender** (B's gender) for parent-child relationships:
- A → B as Father + B is male → Inverse: Son ❌ WRONG
- This would mean "if the father is male, create son relationship" which doesn't make sense

### After (Correct)
The corrected implementation checks the **person's gender** (A's gender) for parent-child relationships:
- A → B as Father + A is male → Inverse: Son ✅ CORRECT
- This means "if the child is male, they are the father's son" which is correct

## Files Updated

1. ✅ `requirements.md` - Updated Requirement 4 with correct semantics and examples
2. ✅ `design.md` - Updated inverse mapping rules with correct logic and detailed comments
3. ✅ `tasks.md` - Updated task 1.2 with correct implementation logic and examples
4. ✅ `tasks.md` - Updated task 7.1 test descriptions with correct semantics
5. ✅ `relationship_helper.py` - Fixed the `get_inverse_type()` method implementation

## Next Steps

Now that the semantics are corrected, you can proceed with implementing the remaining tasks:
- Task 2: Update PersonRelationshipRepository
- Task 3: Update PersonRelationshipService - Create
- Task 4: Update PersonRelationshipService - Update
- Task 5: Update PersonRelationshipService - Delete
- Task 6: Create data migration script
- Task 7: Write unit tests
- Task 8: Write integration tests
- Task 9: Update API documentation
- Task 10: Manual testing and verification
