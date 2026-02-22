"""Manual verification script for bidirectional relationship updates."""

import uuid
from datetime import date

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.person.gender import Gender
from app.db_models.person.person import Person
from app.db_models.person.person_relationship import PersonRelationship
from app.enums import RelationshipType
from app.models import User
from app.schemas.person import PersonRelationshipCreate, PersonRelationshipUpdate
from app.services.person.person_relationship_service import PersonRelationshipService


def test_update_bidirectional():
    """Test that updating a relationship updates both directions."""
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
            return
        
        if not male_gender or not female_gender:
            print("❌ Missing required test data (genders)")
            print(f"  Available genders: {list(session.exec(select(Gender)).all())}")
            return
        
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
        print(f"✓ Created primary relationship: {primary.id}")
        
        # Find inverse
        inverse = session.exec(
            select(PersonRelationship).where(
                PersonRelationship.person_id == mother.id,
                PersonRelationship.related_person_id == son.id,
            )
        ).first()
        
        if not inverse:
            print("❌ Inverse relationship not found after creation")
            return
        
        print(f"✓ Found inverse relationship: {inverse.id}")
        print(f"  Primary: is_active={primary.is_active}")
        print(f"  Inverse: is_active={inverse.is_active}")
        
        # Update the relationship to inactive
        relationship_update = PersonRelationshipUpdate(is_active=False)
        updated_primary = service.update_relationship(primary, relationship_update)
        
        print(f"\n✓ Updated relationship to is_active=False")
        
        # Refresh inverse to get updated data
        session.refresh(inverse)
        
        print(f"  Primary: is_active={updated_primary.is_active}")
        print(f"  Inverse: is_active={inverse.is_active}")
        
        # Verify both are updated
        if updated_primary.is_active == False and inverse.is_active == False:
            print("\n✅ SUCCESS: Both relationships updated correctly!")
        else:
            print("\n❌ FAILURE: Relationships not synchronized")
        
        # Clean up - delete relationships first, then persons
        session.delete(primary)
        session.delete(inverse)
        session.commit()
        session.delete(son)
        session.delete(mother)
        session.commit()
        print("\n✓ Cleaned up test data")


if __name__ == "__main__":
    test_update_bidirectional()
