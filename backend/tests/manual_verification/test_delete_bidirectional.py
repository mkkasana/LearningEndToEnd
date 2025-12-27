"""Manual verification script for bidirectional relationship deletion."""

import uuid
from datetime import date

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType
from app.models import User
from app.schemas.person import PersonRelationshipCreate
from app.services.person.person_relationship_service import PersonRelationshipService


def test_hard_delete_bidirectional():
    """Test that hard deleting a relationship deletes both directions."""
    print("\n=== Testing Hard Delete ===\n")
    
    with Session(engine) as session:
        # Get test data
        user = session.exec(select(User)).first()
        
        # Try different gender code formats
        male_gender = session.exec(select(Gender).where(Gender.code == "male")).first()
        if not male_gender:
            male_gender = session.exec(select(Gender).where(Gender.code == "M")).first()
        
        female_gender = session.exec(select(Gender).where(Gender.code == "female")).first()
        if not female_gender:
            female_gender = session.exec(select(Gender).where(Gender.code == "F")).first()
        
        # If still not found, just get any two genders
        if not male_gender or not female_gender:
            genders = list(session.exec(select(Gender)).all())
            if len(genders) >= 2:
                male_gender = genders[0]
                female_gender = genders[1]
        
        if not user:
            print("❌ Missing required test data (user)")
            return False
        
        if not male_gender or not female_gender:
            print("❌ Missing required test data (genders)")
            print(f"  Available genders: {list(session.exec(select(Gender)).all())}")
            return False
        
        # Create test persons
        son = Person(
            user_id=None,
            created_by_user_id=user.id,
            is_primary=False,
            first_name="Test",
            last_name="Son",
            gender_id=male_gender.id,
            date_of_birth=date(1990, 1, 1),
        )
        session.add(son)
        
        mother = Person(
            user_id=None,
            created_by_user_id=user.id,
            is_primary=False,
            first_name="Test",
            last_name="Mother",
            gender_id=female_gender.id,
            date_of_birth=date(1960, 1, 1),
        )
        session.add(mother)
        session.commit()
        session.refresh(son)
        session.refresh(mother)
        
        print(f"✓ Created test persons: son={son.id}, mother={mother.id}")
        
        # Create bidirectional relationship
        service = PersonRelationshipService(session)
        relationship_create = PersonRelationshipCreate(
            related_person_id=mother.id,
            relationship_type=RelationshipType.MOTHER,
            is_active=True,
        )
        
        primary = service.create_relationship(son.id, relationship_create)
        primary_id = primary.id
        print(f"✓ Created primary relationship: {primary_id}")
        
        # Find inverse
        inverse = session.exec(
            select(PersonRelationship).where(
                PersonRelationship.person_id == mother.id,
                PersonRelationship.related_person_id == son.id,
            )
        ).first()
        
        if not inverse:
            print("❌ Inverse relationship not found after creation")
            return False
        
        inverse_id = inverse.id
        print(f"✓ Found inverse relationship: {inverse_id}")
        
        # Hard delete the relationship
        service.delete_relationship(primary, soft_delete=False)
        print(f"\n✓ Executed hard delete on primary relationship")
        
        # Verify both are deleted
        primary_check = session.get(PersonRelationship, primary_id)
        inverse_check = session.get(PersonRelationship, inverse_id)
        
        if primary_check is None and inverse_check is None:
            print("✅ SUCCESS: Both relationships hard deleted correctly!")
            success = True
        else:
            print("❌ FAILURE: Relationships not deleted")
            print(f"  Primary exists: {primary_check is not None}")
            print(f"  Inverse exists: {inverse_check is not None}")
            success = False
        
        # Clean up persons
        session.delete(son)
        session.delete(mother)
        session.commit()
        print("\n✓ Cleaned up test data")
        
        return success


def test_soft_delete_bidirectional():
    """Test that soft deleting a relationship soft deletes both directions."""
    print("\n=== Testing Soft Delete ===\n")
    
    with Session(engine) as session:
        # Get test data
        user = session.exec(select(User)).first()
        
        # Try different gender code formats
        male_gender = session.exec(select(Gender).where(Gender.code == "male")).first()
        if not male_gender:
            male_gender = session.exec(select(Gender).where(Gender.code == "M")).first()
        
        female_gender = session.exec(select(Gender).where(Gender.code == "female")).first()
        if not female_gender:
            female_gender = session.exec(select(Gender).where(Gender.code == "F")).first()
        
        # If still not found, just get any two genders
        if not male_gender or not female_gender:
            genders = list(session.exec(select(Gender)).all())
            if len(genders) >= 2:
                male_gender = genders[0]
                female_gender = genders[1]
        
        if not user:
            print("❌ Missing required test data (user)")
            return False
        
        if not male_gender or not female_gender:
            print("❌ Missing required test data (genders)")
            return False
        
        # Create test persons
        daughter = Person(
            user_id=None,
            created_by_user_id=user.id,
            is_primary=False,
            first_name="Test",
            last_name="Daughter",
            gender_id=female_gender.id,
            date_of_birth=date(1995, 1, 1),
        )
        session.add(daughter)
        
        father = Person(
            user_id=None,
            created_by_user_id=user.id,
            is_primary=False,
            first_name="Test",
            last_name="Father",
            gender_id=male_gender.id,
            date_of_birth=date(1965, 1, 1),
        )
        session.add(father)
        session.commit()
        session.refresh(daughter)
        session.refresh(father)
        
        print(f"✓ Created test persons: daughter={daughter.id}, father={father.id}")
        
        # Create bidirectional relationship
        service = PersonRelationshipService(session)
        relationship_create = PersonRelationshipCreate(
            related_person_id=father.id,
            relationship_type=RelationshipType.FATHER,
            is_active=True,
        )
        
        primary = service.create_relationship(daughter.id, relationship_create)
        primary_id = primary.id
        print(f"✓ Created primary relationship: {primary_id}")
        
        # Find inverse
        inverse = session.exec(
            select(PersonRelationship).where(
                PersonRelationship.person_id == father.id,
                PersonRelationship.related_person_id == daughter.id,
            )
        ).first()
        
        if not inverse:
            print("❌ Inverse relationship not found after creation")
            return False
        
        inverse_id = inverse.id
        print(f"✓ Found inverse relationship: {inverse_id}")
        print(f"  Primary: is_active={primary.is_active}")
        print(f"  Inverse: is_active={inverse.is_active}")
        
        # Soft delete the relationship
        service.delete_relationship(primary, soft_delete=True)
        print(f"\n✓ Executed soft delete on primary relationship")
        
        # Verify both are soft deleted (is_active=False)
        primary_check = session.get(PersonRelationship, primary_id)
        inverse_check = session.get(PersonRelationship, inverse_id)
        
        if primary_check and inverse_check:
            if primary_check.is_active == False and inverse_check.is_active == False:
                print("✅ SUCCESS: Both relationships soft deleted correctly!")
                print(f"  Primary: is_active={primary_check.is_active}")
                print(f"  Inverse: is_active={inverse_check.is_active}")
                success = True
            else:
                print("❌ FAILURE: Relationships not soft deleted")
                print(f"  Primary: is_active={primary_check.is_active}")
                print(f"  Inverse: is_active={inverse_check.is_active}")
                success = False
        else:
            print("❌ FAILURE: Relationships were hard deleted instead of soft deleted")
            success = False
        
        # Clean up - delete relationships and persons
        if primary_check:
            session.delete(primary_check)
        if inverse_check:
            session.delete(inverse_check)
        session.commit()
        session.delete(daughter)
        session.delete(father)
        session.commit()
        print("\n✓ Cleaned up test data")
        
        return success


if __name__ == "__main__":
    hard_delete_success = test_hard_delete_bidirectional()
    soft_delete_success = test_soft_delete_bidirectional()
    
    print("\n" + "="*50)
    print("FINAL RESULTS:")
    print(f"  Hard Delete: {'✅ PASS' if hard_delete_success else '❌ FAIL'}")
    print(f"  Soft Delete: {'✅ PASS' if soft_delete_success else '❌ FAIL'}")
    print("="*50 + "\n")
