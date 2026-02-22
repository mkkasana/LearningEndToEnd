#!/usr/bin/env python3
"""Seed script for Sikrai sub-district villages."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.address import Locality, SubDistrict


def seed_sikrai_villages():
    """Seed all villages/localities of Sikrai sub-district."""
    
    # Villages in Sikrai sub-district
    villages_data = [
        {"name": "Bhojpura", "code": "BHO"},
        {"name": "Sikrai", "code": "SIK"},
        {"name": "Bandikui", "code": "BAN"},
        {"name": "Khanpur Mewan", "code": "KHA"},
        {"name": "Mandawar", "code": "MAN"},
        {"name": "Mehandipur Balaji", "code": "MEH"},
        {"name": "Nangal Rajawatan", "code": "NAN"},
        {"name": "Paparda", "code": "PAP"},
        {"name": "Raisis", "code": "RAI"},
        {"name": "Sainthal", "code": "SAI"},
        {"name": "Toda Bhim", "code": "TOD"},
        {"name": "Lalsot", "code": "LAL"},
        {"name": "Mahwa", "code": "MAH"},
        {"name": "Baswa", "code": "BAS"},
        {"name": "Dausa", "code": "DAU"},
        {"name": "Ramgarh", "code": "RAM"},
        {"name": "Kho Nagoriyan", "code": "KHO"},
        {"name": "Gothda", "code": "GOT"},
        {"name": "Kalyanpura", "code": "KAL"},
        {"name": "Khera", "code": "KHE"},
    ]
    
    with Session(engine) as session:
        # Get Sikrai sub-district
        sikrai = session.exec(
            select(SubDistrict).where(SubDistrict.name == "Sikrai")
        ).first()
        
        if not sikrai:
            print("❌ Sikrai sub-district not found. Please seed Dausa sub-districts first.")
            return
        
        print(f"Found Sikrai sub-district with ID: {sikrai.id}")
        print("Seeding Sikrai villages...")
        
        for village_data in villages_data:
            # Check if village already exists
            existing = session.exec(
                select(Locality)
                .where(Locality.name == village_data["name"])
                .where(Locality.sub_district_id == sikrai.id)
            ).first()
            
            if existing:
                print(f"  ⊘ {village_data['name']} already exists")
            else:
                village = Locality(
                    id=uuid.uuid4(),
                    name=village_data["name"],
                    code=village_data["code"],
                    sub_district_id=sikrai.id,
                    is_active=True
                )
                session.add(village)
                print(f"  ✓ Added {village_data['name']}")
        
        session.commit()
        print(f"✅ Successfully seeded {len(villages_data)} Sikrai villages!")


if __name__ == "__main__":
    try:
        seed_sikrai_villages()
    except Exception as e:
        print(f"❌ Error seeding villages: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
