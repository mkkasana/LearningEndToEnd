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
    """Seed initial gender data"""
    
    genders_data = [
        {
            "name": "Male",
            "code": "MALE",
            "description": "Male gender",
        },
        {
            "name": "Female",
            "code": "FEMALE",
            "description": "Female gender",
        },
    ]
    
    with Session(engine) as session:
        # Check if genders already exist
        existing_count = session.exec(select(Gender)).first()
        if existing_count:
            print("Genders already seeded. Skipping...")
            return
        
        # Create gender records
        for gender_data in genders_data:
            gender = Gender(
                id=uuid.uuid4(),
                name=gender_data["name"],
                code=gender_data["code"],
                description=gender_data["description"],
                is_active=True
            )
            session.add(gender)
        
        session.commit()
        print(f"Successfully seeded {len(genders_data)} genders")


if __name__ == "__main__":
    seed_genders()
