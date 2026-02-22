#!/usr/bin/env python3
"""Seed script for Rajasthan districts."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.address import Country, District, State


def seed_rajasthan_districts():
    """Seed all districts of Rajasthan."""
    
    # All 50 districts of Rajasthan (as of 2024)
    districts_data = [
        {"name": "Ajmer", "code": "AJM"},
        {"name": "Alwar", "code": "ALW"},
        {"name": "Banswara", "code": "BAN"},
        {"name": "Baran", "code": "BAR"},
        {"name": "Barmer", "code": "BRM"},
        {"name": "Bharatpur", "code": "BHA"},
        {"name": "Bhilwara", "code": "BHI"},
        {"name": "Bikaner", "code": "BIK"},
        {"name": "Bundi", "code": "BUN"},
        {"name": "Chittorgarh", "code": "CHI"},
        {"name": "Churu", "code": "CHU"},
        {"name": "Dausa", "code": "DAU"},
        {"name": "Dholpur", "code": "DHO"},
        {"name": "Dungarpur", "code": "DUN"},
        {"name": "Hanumangarh", "code": "HAN"},
        {"name": "Jaipur", "code": "JAI"},
        {"name": "Jaisalmer", "code": "JAL"},
        {"name": "Jalore", "code": "JAO"},
        {"name": "Jhalawar", "code": "JHA"},
        {"name": "Jhunjhunu", "code": "JHU"},
        {"name": "Jodhpur", "code": "JOD"},
        {"name": "Karauli", "code": "KAR"},
        {"name": "Kota", "code": "KOT"},
        {"name": "Nagaur", "code": "NAG"},
        {"name": "Pali", "code": "PAL"},
        {"name": "Pratapgarh", "code": "PRA"},
        {"name": "Rajsamand", "code": "RAJ"},
        {"name": "Sawai Madhopur", "code": "SAW"},
        {"name": "Sikar", "code": "SIK"},
        {"name": "Sirohi", "code": "SIR"},
        {"name": "Sri Ganganagar", "code": "SRI"},
        {"name": "Tonk", "code": "TON"},
        {"name": "Udaipur", "code": "UDA"},
    ]
    
    with Session(engine) as session:
        # Get India
        india = session.exec(select(Country).where(Country.code == "IND")).first()
        if not india:
            print("❌ India not found. Please seed countries first.")
            return
        
        # Get Rajasthan
        rajasthan = session.exec(
            select(State)
            .where(State.code == "RJ")
            .where(State.country_id == india.id)
        ).first()
        
        if not rajasthan:
            print("❌ Rajasthan not found. Please seed states first.")
            return
        
        print(f"Found Rajasthan with ID: {rajasthan.id}")
        print("Seeding Rajasthan districts...")
        
        for district_data in districts_data:
            # Check if district already exists
            existing = session.exec(
                select(District)
                .where(District.name == district_data["name"])
                .where(District.state_id == rajasthan.id)
            ).first()
            
            if existing:
                print(f"  ⊘ {district_data['name']} already exists")
            else:
                district = District(
                    id=uuid.uuid4(),
                    name=district_data["name"],
                    code=district_data["code"],
                    state_id=rajasthan.id,
                    is_active=True
                )
                session.add(district)
                print(f"  ✓ Added {district_data['name']}")
        
        session.commit()
        print(f"✅ Successfully seeded {len(districts_data)} Rajasthan districts!")


if __name__ == "__main__":
    try:
        seed_rajasthan_districts()
    except Exception as e:
        print(f"❌ Error seeding districts: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
