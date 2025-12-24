#!/usr/bin/env python3
"""Quick script to seed test religion data via direct DB access."""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

import os
os.chdir(backend_path)

from sqlmodel import Session, select
from app.core.db import engine
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.db_models.religion.religion_sub_category import ReligionSubCategory


def seed_test_religions():
    """Seed minimal test religion data."""
    
    with Session(engine) as session:
        # Check if data exists
        existing = session.exec(select(Religion)).first()
        if existing:
            print("✓ Religions already exist")
            return
        
        # Create Hinduism
        hinduism = Religion(name="Hinduism")
        session.add(hinduism)
        session.flush()
        
        # Create Vaishnavism category
        vaishnavism = ReligionCategory(name="Vaishnavism", religion_id=hinduism.id)
        session.add(vaishnavism)
        session.flush()
        
        # Create ISKCON sub-category
        iskcon = ReligionSubCategory(name="ISKCON", religion_category_id=vaishnavism.id)
        session.add(iskcon)
        
        # Create Islam
        islam = Religion(name="Islam")
        session.add(islam)
        session.flush()
        
        # Create Sunni category
        sunni = ReligionCategory(name="Sunni", religion_id=islam.id)
        session.add(sunni)
        
        session.commit()
        print("✅ Test religions seeded successfully!")


if __name__ == "__main__":
    try:
        seed_test_religions()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
