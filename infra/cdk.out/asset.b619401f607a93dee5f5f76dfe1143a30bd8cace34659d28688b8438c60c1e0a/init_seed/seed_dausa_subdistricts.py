#!/usr/bin/env python3
"""Seed script for Dausa sub-districts (tehsils)."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.address import District, SubDistrict


def seed_dausa_subdistricts():
    """Seed all sub-districts (tehsils) of Dausa district."""
    
    # Sub-districts of Dausa
    subdistricts_data = [
        {"name": "Bandikui", "code": "BAN"},
        {"name": "Baswa", "code": "BAS"},
        {"name": "Dausa", "code": "DAU"},
        {"name": "Lalsot", "code": "LAL"},
        {"name": "Mahwa", "code": "MAH"},
        {"name": "Mandawar", "code": "MAN"},
        {"name": "Sikrai", "code": "SIK"},
    ]
    
    with Session(engine) as session:
        # Get Dausa district
        dausa = session.exec(
            select(District).where(District.name == "Dausa")
        ).first()
        
        if not dausa:
            print("❌ Dausa district not found. Please seed Rajasthan districts first.")
            return
        
        print(f"Found Dausa district with ID: {dausa.id}")
        print("Seeding Dausa sub-districts...")
        
        for subdistrict_data in subdistricts_data:
            # Check if sub-district already exists
            existing = session.exec(
                select(SubDistrict)
                .where(SubDistrict.name == subdistrict_data["name"])
                .where(SubDistrict.district_id == dausa.id)
            ).first()
            
            if existing:
                print(f"  ⊘ {subdistrict_data['name']} already exists")
            else:
                subdistrict = SubDistrict(
                    id=uuid.uuid4(),
                    name=subdistrict_data["name"],
                    code=subdistrict_data["code"],
                    district_id=dausa.id,
                    is_active=True
                )
                session.add(subdistrict)
                print(f"  ✓ Added {subdistrict_data['name']}")
        
        session.commit()
        print(f"✅ Successfully seeded {len(subdistricts_data)} Dausa sub-districts!")


if __name__ == "__main__":
    try:
        seed_dausa_subdistricts()
    except Exception as e:
        print(f"❌ Error seeding sub-districts: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
