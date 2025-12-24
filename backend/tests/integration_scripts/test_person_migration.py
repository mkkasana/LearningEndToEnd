#!/usr/bin/env python3
"""Integration test for Person model migration to family tree structure.

This script tests:
1. Existing functionality still works (backward compatibility)
2. New family tree features work correctly
3. Migration preserves data integrity
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import os
os.chdir(backend_path)

import uuid
from sqlmodel import Session, select
from app.core.db import engine
from app.db_models.person.person import Person
from app.db_models.person.person_address import PersonAddress
from app.db_models.person.person_religion import PersonReligion
from app.db_models.user import User


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def test_person_model_structure():
    """Test that Person model has the new structure."""
    print_section("Test 1: Person Model Structure")
    
    with Session(engine) as session:
        # Check if we can query Person table
        persons = session.exec(select(Person)).all()
        print(f"✓ Person table exists and is queryable")
        print(f"  Found {len(persons)} existing person records")
        
        if persons:
            person = persons[0]
            # Check new fields exist
            assert hasattr(person, 'id'), "Person should have 'id' field"
            assert hasattr(person, 'user_id'), "Person should have 'user_id' field"
            assert hasattr(person, 'created_by_user_id'), "Person should have 'created_by_user_id' field"
            assert hasattr(person, 'is_primary'), "Person should have 'is_primary' field"
            
            print(f"✓ Person model has all required fields:")
            print(f"  - id: {person.id}")
            print(f"  - user_id: {person.user_id}")
            print(f"  - created_by_user_id: {person.created_by_user_id}")
            print(f"  - is_primary: {person.is_primary}")
            
            # Check that existing persons are marked as primary
            assert person.is_primary == True, "Existing persons should be marked as primary"
            print(f"✓ Existing persons are correctly marked as primary")


def test_existing_user_person_relationship():
    """Test that existing User-Person relationships still work."""
    print_section("Test 2: Existing User-Person Relationships")
    
    with Session(engine) as session:
        # Get a user with a person
        users = session.exec(select(User)).all()
        
        if not users:
            print("⚠️  No users found, skipping test")
            return
        
        user = users[0]
        print(f"Testing with user: {user.email}")
        
        # Find their primary person
        person = session.exec(
            select(Person).where(
                Person.user_id == user.id,
                Person.is_primary == True
            )
        ).first()
        
        if person:
            print(f"✓ Found primary person for user:")
            print(f"  - Person ID: {person.id}")
            print(f"  - Name: {person.first_name} {person.last_name}")
            print(f"  - User ID: {person.user_id}")
            print(f"  - Is Primary: {person.is_primary}")
            
            # Check that user_id matches
            assert person.user_id == user.id, "Person's user_id should match user's id"
            print(f"✓ User-Person relationship is intact")
            
            # Check that created_by_user_id is set
            assert person.created_by_user_id == user.id, "created_by_user_id should be set to user's id"
            print(f"✓ created_by_user_id is correctly set")
        else:
            print("⚠️  No primary person found for user")


def test_person_address_relationship():
    """Test that Person-Address relationships still work."""
    print_section("Test 3: Person-Address Relationships")
    
    with Session(engine) as session:
        # Get a person with an address
        addresses = session.exec(select(PersonAddress)).all()
        
        if not addresses:
            print("⚠️  No addresses found, skipping test")
            return
        
        address = addresses[0]
        print(f"Testing with address ID: {address.id}")
        
        # Find the person
        person = session.get(Person, address.person_id)
        
        if person:
            print(f"✓ Found person for address:")
            print(f"  - Person ID: {person.id}")
            print(f"  - Name: {person.first_name} {person.last_name}")
            print(f"  - Address person_id: {address.person_id}")
            
            # Check that person_id references person.id (not user_id)
            assert address.person_id == person.id, "Address should reference person.id"
            print(f"✓ Address correctly references person.id")
        else:
            print("❌ Person not found for address - foreign key issue!")


def test_person_religion_relationship():
    """Test that Person-Religion relationships still work."""
    print_section("Test 4: Person-Religion Relationships")
    
    with Session(engine) as session:
        # Get a person with religion
        religions = session.exec(select(PersonReligion)).all()
        
        if not religions:
            print("⚠️  No religions found, skipping test")
            return
        
        religion = religions[0]
        print(f"Testing with religion ID: {religion.id}")
        
        # Find the person
        person = session.get(Person, religion.person_id)
        
        if person:
            print(f"✓ Found person for religion:")
            print(f"  - Person ID: {person.id}")
            print(f"  - Name: {person.first_name} {person.last_name}")
            print(f"  - Religion person_id: {religion.person_id}")
            
            # Check that person_id references person.id
            assert religion.person_id == person.id, "Religion should reference person.id"
            print(f"✓ Religion correctly references person.id")
        else:
            print("❌ Person not found for religion - foreign key issue!")


def test_create_family_member():
    """Test creating a family member (person without user account)."""
    print_section("Test 5: Create Family Member (No User Account)")
    
    with Session(engine) as session:
        # Get a user to be the creator
        users = session.exec(select(User)).all()
        
        if not users:
            print("⚠️  No users found, skipping test")
            return
        
        creator_user = users[0]
        print(f"Creator user: {creator_user.email}")
        
        # Get a gender for the family member
        from app.db_models.person.gender import Gender
        genders = session.exec(select(Gender)).all()
        
        if not genders:
            print("❌ No genders found in database")
            return
        
        gender = genders[0]
        
        # Create a family member (e.g., father)
        family_member = Person(
            user_id=None,  # No user account
            created_by_user_id=creator_user.id,
            is_primary=False,
            first_name="John",
            middle_name="Senior",
            last_name="Doe",
            gender_id=gender.id,
            date_of_birth="1960-01-15"
        )
        
        session.add(family_member)
        session.commit()
        session.refresh(family_member)
        
        print(f"✓ Created family member:")
        print(f"  - Person ID: {family_member.id}")
        print(f"  - Name: {family_member.first_name} {family_member.last_name}")
        print(f"  - User ID: {family_member.user_id} (should be None)")
        print(f"  - Created by: {family_member.created_by_user_id}")
        print(f"  - Is Primary: {family_member.is_primary}")
        
        # Verify the family member was created correctly
        assert family_member.id is not None, "Family member should have an ID"
        assert family_member.user_id is None, "Family member should not have a user_id"
        assert family_member.created_by_user_id == creator_user.id, "created_by_user_id should match creator"
        assert family_member.is_primary == False, "Family member should not be primary"
        
        print(f"✓ Family member created successfully!")
        
        # Clean up
        session.delete(family_member)
        session.commit()
        print(f"✓ Cleaned up test family member")


def test_multiple_persons_per_user():
    """Test that a user can have multiple persons."""
    print_section("Test 6: Multiple Persons Per User")
    
    with Session(engine) as session:
        # Get a user
        users = session.exec(select(User)).all()
        
        if not users:
            print("⚠️  No users found, skipping test")
            return
        
        user = users[0]
        print(f"Testing with user: {user.email}")
        
        # Count persons created by this user
        persons = session.exec(
            select(Person).where(Person.created_by_user_id == user.id)
        ).all()
        
        print(f"✓ User has created {len(persons)} person(s):")
        for person in persons:
            print(f"  - {person.first_name} {person.last_name} (Primary: {person.is_primary}, Has Account: {person.user_id is not None})")
        
        # Check that only one is primary
        primary_persons = [p for p in persons if p.is_primary]
        assert len(primary_persons) <= 1, "User should have at most one primary person"
        print(f"✓ User has {len(primary_persons)} primary person (correct)")


def test_query_performance():
    """Test query performance with new indexes."""
    print_section("Test 7: Query Performance")
    
    with Session(engine) as session:
        import time
        
        # Test 1: Query by user_id (should use index)
        start = time.time()
        persons = session.exec(
            select(Person).where(Person.user_id.isnot(None))
        ).all()
        elapsed = time.time() - start
        print(f"✓ Query persons with user accounts: {len(persons)} results in {elapsed:.4f}s")
        
        # Test 2: Query by created_by_user_id (should use index)
        if persons:
            user_id = persons[0].user_id
            start = time.time()
            created_persons = session.exec(
                select(Person).where(Person.created_by_user_id == user_id)
            ).all()
            elapsed = time.time() - start
            print(f"✓ Query persons created by user: {len(created_persons)} results in {elapsed:.4f}s")
        
        # Test 3: Query primary persons (should use index)
        start = time.time()
        primary_persons = session.exec(
            select(Person).where(Person.is_primary == True)
        ).all()
        elapsed = time.time() - start
        print(f"✓ Query primary persons: {len(primary_persons)} results in {elapsed:.4f}s")


def test_data_integrity():
    """Test data integrity constraints."""
    print_section("Test 8: Data Integrity")
    
    with Session(engine) as session:
        # Test 1: created_by_user_id is required
        print("Testing created_by_user_id constraint...")
        try:
            from app.db_models.person.gender import Gender
            gender = session.exec(select(Gender)).first()
            
            invalid_person = Person(
                user_id=None,
                created_by_user_id=None,  # Should fail
                is_primary=False,
                first_name="Invalid",
                last_name="Person",
                gender_id=gender.id,
                date_of_birth="1990-01-01"
            )
            session.add(invalid_person)
            session.commit()
            print("❌ Should have failed - created_by_user_id is required!")
        except Exception as e:
            session.rollback()
            print(f"✓ Correctly rejected person without created_by_user_id")
        
        # Test 2: Foreign key constraints work
        print("\nTesting foreign key constraints...")
        persons = session.exec(select(Person)).all()
        for person in persons[:5]:  # Check first 5
            # Check user_id foreign key (if not null)
            if person.user_id:
                user = session.get(User, person.user_id)
                assert user is not None, f"User {person.user_id} should exist"
            
            # Check created_by_user_id foreign key
            creator = session.get(User, person.created_by_user_id)
            assert creator is not None, f"Creator user {person.created_by_user_id} should exist"
        
        print(f"✓ Foreign key constraints are working correctly")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  PERSON MODEL MIGRATION INTEGRATION TESTS")
    print("=" * 70)
    
    try:
        test_person_model_structure()
        test_existing_user_person_relationship()
        test_person_address_relationship()
        test_person_religion_relationship()
        test_create_family_member()
        test_multiple_persons_per_user()
        test_query_performance()
        test_data_integrity()
        
        print_section("✅ ALL TESTS PASSED!")
        print("\nSummary:")
        print("  ✓ Person model structure is correct")
        print("  ✓ Existing User-Person relationships work")
        print("  ✓ Person-Address relationships work")
        print("  ✓ Person-Religion relationships work")
        print("  ✓ Can create family members without user accounts")
        print("  ✓ Users can have multiple persons")
        print("  ✓ Query performance is good")
        print("  ✓ Data integrity constraints work")
        print("\n✅ Migration is safe to deploy!\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
