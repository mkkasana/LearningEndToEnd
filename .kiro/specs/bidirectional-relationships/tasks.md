# Implementation Plan

- [x] 1. Create RelationshipTypeHelper utility class
  - [x] 1.1 Create helper file and class structure
    - Create `app/utils/relationship_helper.py`
    - Define `RelationshipTypeHelper` class
    - _Requirements: 4.1_
  
  - [x] 1.2 Implement get_inverse_type method
    - Create method signature with relationship_type, person_gender_id, related_person_gender_id, gender_mapping parameters
    - **SEMANTICS**: When A → B with type, create B → A with inverse_type
    - Implement logic for Father → Son/Daughter based on person_gender (A's gender, not B's)
      - A → B as Father (B is A's father) + A is male → B → A as Son (A is B's son)
      - A → B as Father (B is A's father) + A is female → B → A as Daughter (A is B's daughter)
    - Implement logic for Mother → Son/Daughter based on person_gender (A's gender, not B's)
      - A → B as Mother (B is A's mother) + A is male → B → A as Son (A is B's son)
      - A → B as Mother (B is A's mother) + A is female → B → A as Daughter (A is B's daughter)
    - Implement logic for Son → Father/Mother based on person_gender (A's gender, not B's)
      - A → B as Son (B is A's son) + A is male → B → A as Father (A is B's father)
      - A → B as Son (B is A's son) + A is female → B → A as Mother (A is B's mother)
    - Implement logic for Daughter → Father/Mother based on person_gender (A's gender, not B's)
      - A → B as Daughter (B is A's daughter) + A is male → B → A as Father (A is B's father)
      - A → B as Daughter (B is A's daughter) + A is female → B → A as Mother (A is B's mother)
    - Implement logic for Husband ↔ Wife
      - A → B as Husband (B is A's husband) → B → A as Wife (A is B's wife)
      - A → B as Wife (B is A's wife) → B → A as Husband (A is B's husband)
    - Implement logic for Spouse ↔ Spouse
      - A → B as Spouse (B is A's spouse) → B → A as Spouse (A is B's spouse)
    - Return None for unknown combinations
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_
  
  - [x] 1.3 Implement requires_gender_context method
    - Return True for parent-child relationships (Father, Mother, Son, Daughter)
    - Return False for spouse relationships (Husband, Wife, Spouse)
    - _Requirements: 4.1_
  
  - [x] 1.4 Add gender mapping utility
    - Create method to fetch gender mapping from database
    - Cache gender mapping in memory
    - Handle missing gender IDs gracefully
    - _Requirements: 4.1_

- [ ] 2. Update PersonRelationshipRepository
  - [ ] 2.1 Add find_inverse method
    - Query person_relationship where person_id and related_person_id are swapped
    - Filter by is_active = True
    - Return first match or None
    - _Requirements: 2.4, 3.3_
  
  - [ ] 2.2 Add find_inverse_including_inactive method
    - Same as find_inverse but don't filter by is_active
    - Used for update/delete operations
    - _Requirements: 2.4, 3.3_

- [ ] 3. Update PersonRelationshipService - Create
  - [ ] 3.1 Refactor create_relationship method
    - Add transaction wrapper
    - Fetch person and related_person records
    - Get gender mapping
    - Create primary relationship
    - Determine inverse relationship type using RelationshipTypeHelper
    - Create inverse relationship if type determined
    - Log warning if inverse cannot be created
    - Commit transaction
    - Return primary relationship
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ] 3.2 Handle gender information missing
    - Check if both persons have gender_id
    - If missing, log warning and create primary only
    - Don't fail the request
    - _Requirements: 1.2_
  
  - [ ] 3.3 Add transaction rollback on error
    - Wrap in try-except block
    - Rollback on any exception
    - Re-raise exception to caller
    - _Requirements: 3.4_

- [ ] 4. Update PersonRelationshipService - Update
  - [ ] 4.1 Refactor update_relationship method
    - Add transaction wrapper
    - Update primary relationship
    - Find inverse relationship using repository
    - If inverse found, update matching fields (is_active, start_date, end_date)
    - Do NOT update relationship_type of inverse
    - Update updated_at timestamp for both
    - If inverse not found, log warning and continue
    - Commit transaction
    - Return updated primary relationship
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [ ] 4.2 Handle missing inverse gracefully
    - Check if inverse exists
    - If not found, log warning with relationship ID
    - Continue with primary update
    - Don't fail the request
    - _Requirements: 2.4_

- [ ] 5. Update PersonRelationshipService - Delete
  - [ ] 5.1 Refactor delete_relationship method
    - Add transaction wrapper
    - Find inverse relationship using repository
    - Delete primary relationship
    - If inverse found, delete inverse relationship
    - If inverse not found, log warning and continue
    - Commit transaction
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ] 5.2 Handle soft delete (is_active=false)
    - Check if deletion is soft delete (update is_active)
    - If soft delete, update both relationships
    - If hard delete, remove both records
    - _Requirements: 3.5_

- [ ] 6. Create data migration script
  - [ ] 6.1 Create migration script file
    - Create `scripts/migrate_bidirectional_relationships.py`
    - Add database connection setup
    - Add logging configuration
    - _Requirements: 5.1_
  
  - [ ] 6.2 Implement migration logic
    - Query all existing relationships
    - For each relationship, check if inverse exists
    - If inverse missing, determine inverse type
    - Create inverse relationship
    - Track created count and error count
    - Log progress every 100 relationships
    - _Requirements: 5.1, 5.2, 5.3, 5.4_
  
  - [ ] 6.3 Add idempotency check
    - Skip relationships that already have inverses
    - Allow script to run multiple times safely
    - _Requirements: 5.5_
  
  - [ ] 6.4 Add dry-run mode
    - Add --dry-run flag
    - Report what would be created without creating
    - Useful for testing before actual migration
    - _Requirements: 5.4_

- [ ] 7. Write unit tests
  - [ ] 7.1 Test RelationshipTypeHelper.get_inverse_type
    - Test Father + male person (A) → Son (A → B as Father, B is A's father, A is male → B → A as Son)
    - Test Father + female person (A) → Daughter (A → B as Father, B is A's father, A is female → B → A as Daughter)
    - Test Mother + male person (A) → Son (A → B as Mother, B is A's mother, A is male → B → A as Son)
    - Test Mother + female person (A) → Daughter (A → B as Mother, B is A's mother, A is female → B → A as Daughter)
    - Test Son + male person (A) → Father (A → B as Son, B is A's son, A is male → B → A as Father)
    - Test Son + female person (A) → Mother (A → B as Son, B is A's son, A is female → B → A as Mother)
    - Test Daughter + male person (A) → Father (A → B as Daughter, B is A's daughter, A is male → B → A as Father)
    - Test Daughter + female person (A) → Mother (A → B as Daughter, B is A's daughter, A is female → B → A as Mother)
    - Test Husband → Wife (A → B as Husband, B is A's husband → B → A as Wife, A is B's wife)
    - Test Wife → Husband (A → B as Wife, B is A's wife → B → A as Husband, A is B's husband)
    - Test Spouse → Spouse (A → B as Spouse, B is A's spouse → B → A as Spouse, A is B's spouse)
    - Test unknown type → None
    - _Requirements: 6.4, 6.5_
  
  - [ ] 7.2 Test PersonRelationshipService.create_relationship
    - Test creates both primary and inverse
    - Test correct inverse type determination
    - Test transaction rollback on error
    - Test handling of missing gender information
    - Mock database calls
    - _Requirements: 6.1_
  
  - [ ] 7.3 Test PersonRelationshipService.update_relationship
    - Test updates both relationships
    - Test only syncs appropriate fields
    - Test handles missing inverse gracefully
    - Test updated_at timestamp updated
    - _Requirements: 6.2_
  
  - [ ] 7.4 Test PersonRelationshipService.delete_relationship
    - Test deletes both relationships
    - Test transaction atomicity
    - Test handles missing inverse gracefully
    - Test soft delete affects both
    - _Requirements: 6.3_

- [ ] 8. Write integration tests
  - [ ] 8.1 Test end-to-end relationship creation
    - Create relationship via API
    - Query person A's relationships → verify B appears
    - Query person B's relationships → verify A appears with inverse type
    - Verify both relationship records exist in database
    - _Requirements: 6.1_
  
  - [ ] 8.2 Test end-to-end relationship update
    - Create bidirectional relationship
    - Update via API (change is_active to false)
    - Query both persons → verify both show inactive
    - _Requirements: 6.2_
  
  - [ ] 8.3 Test end-to-end relationship deletion
    - Create bidirectional relationship
    - Delete via API
    - Query both persons → verify neither shows the relationship
    - Verify both records removed from database
    - _Requirements: 6.3_
  
  - [ ] 8.4 Test migration script
    - Create test database with single-direction relationships
    - Run migration script
    - Verify inverse relationships created
    - Run migration again → verify idempotency
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 9. Update API documentation
  - [ ] 9.1 Update API endpoint docstrings
    - Document that relationships are bidirectional
    - Explain inverse relationship creation
    - Add examples showing both directions
    - _Requirements: 1.1_
  
  - [ ] 9.2 Create migration guide
    - Document migration script usage
    - Provide dry-run example
    - Explain rollback procedure if needed
    - _Requirements: 5.1, 5.4_

- [ ] 10. Manual testing and verification
  - [ ] 10.1 Test relationship creation flow
    - Create Father relationship
    - Verify Son/Daughter inverse created based on gender
    - Check database records
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ] 10.2 Test relationship update flow
    - Update relationship is_active
    - Verify both directions updated
    - _Requirements: 2.1, 2.2, 2.3_
  
  - [ ] 10.3 Test relationship deletion flow
    - Delete relationship
    - Verify both directions removed
    - _Requirements: 3.1, 3.2_
  
  - [ ] 10.4 Test migration on development data
    - Run migration script with --dry-run
    - Review what would be created
    - Run actual migration
    - Verify all relationships have inverses
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 11. Final checkpoint
  - Ensure all tests pass, ask the user if questions arise.
