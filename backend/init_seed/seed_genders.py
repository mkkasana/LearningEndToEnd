"""Seed script to populate gender data"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.person.gender import Gender


def seed_genders() -> None:
    """Seed gender data with hardcoded UUIDs matching the enum."""
    # These UUIDs must match the hardcoded values in app/enums/gender.py
    genders_data = [
        {
            "id": uuid.UUID("4eb743f7-0a50-4da2-a20d-3473b3b3db83"),
            "name": "Male",
            "code": "MALE",
            "description": "Male gender",
        },
        {
            "id": uuid.UUID("691fde27-f82c-4a84-832f-4243acef4b95"),
            "name": "Female",
            "code": "FEMALE",
            "description": "Female gender",
        },
    ]
    
    with Session(engine) as session:
        # Check if genders already exist
        existing_count = session.exec(select(Gender)).first()
        if existing_count:
            print("✓ Genders already seeded. Skipping...")
            return
        
        print("Seeding genders...")
        # Create gender records
        for gender_data in genders_data:
            gender = Gender(
                id=gender_data["id"],
                name=gender_data["name"],
                code=gender_data["code"],
                description=gender_data["description"],
                is_active=True
            )
            session.add(gender)
            print(f"  ✓ Added {gender_data['name']} ({gender_data['id']})")
        
        session.commit()
        print(f"✅ Successfully seeded {len(genders_data)} genders")


if __name__ == "__main__":
    seed_genders()
