"""Seed script to populate country data"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.country import Country


def seed_countries() -> None:
    """Seed initial country data"""
    
    countries_data = [
        {"name": "Afghanistan", "code": "AFG"},
        {"name": "Albania", "code": "ALB"},
        {"name": "Algeria", "code": "DZA"},
        {"name": "Argentina", "code": "ARG"},
        {"name": "Australia", "code": "AUS"},
        {"name": "Austria", "code": "AUT"},
        {"name": "Bangladesh", "code": "BGD"},
        {"name": "Belgium", "code": "BEL"},
        {"name": "Brazil", "code": "BRA"},
        {"name": "Canada", "code": "CAN"},
        {"name": "China", "code": "CHN"},
        {"name": "Denmark", "code": "DNK"},
        {"name": "Egypt", "code": "EGY"},
        {"name": "Finland", "code": "FIN"},
        {"name": "France", "code": "FRA"},
        {"name": "Germany", "code": "DEU"},
        {"name": "Greece", "code": "GRC"},
        {"name": "India", "code": "IND"},
        {"name": "Indonesia", "code": "IDN"},
        {"name": "Iran", "code": "IRN"},
        {"name": "Iraq", "code": "IRQ"},
        {"name": "Ireland", "code": "IRL"},
        {"name": "Israel", "code": "ISR"},
        {"name": "Italy", "code": "ITA"},
        {"name": "Japan", "code": "JPN"},
        {"name": "Kenya", "code": "KEN"},
        {"name": "Malaysia", "code": "MYS"},
        {"name": "Mexico", "code": "MEX"},
        {"name": "Netherlands", "code": "NLD"},
        {"name": "New Zealand", "code": "NZL"},
        {"name": "Nigeria", "code": "NGA"},
        {"name": "Norway", "code": "NOR"},
        {"name": "Pakistan", "code": "PAK"},
        {"name": "Philippines", "code": "PHL"},
        {"name": "Poland", "code": "POL"},
        {"name": "Portugal", "code": "PRT"},
        {"name": "Russia", "code": "RUS"},
        {"name": "Saudi Arabia", "code": "SAU"},
        {"name": "Singapore", "code": "SGP"},
        {"name": "South Africa", "code": "ZAF"},
        {"name": "South Korea", "code": "KOR"},
        {"name": "Spain", "code": "ESP"},
        {"name": "Sweden", "code": "SWE"},
        {"name": "Switzerland", "code": "CHE"},
        {"name": "Thailand", "code": "THA"},
        {"name": "Turkey", "code": "TUR"},
        {"name": "Ukraine", "code": "UKR"},
        {"name": "United Arab Emirates", "code": "ARE"},
        {"name": "United Kingdom", "code": "GBR"},
        {"name": "United States", "code": "USA"},
        {"name": "Vietnam", "code": "VNM"},
    ]
    
    with Session(engine) as session:
        # Check if countries already exist
        existing_count = session.exec(select(Country)).first()
        if existing_count:
            print("Countries already seeded. Skipping...")
            return
        
        # Create country records
        for country_data in countries_data:
            country = Country(
                id=uuid.uuid4(),
                name=country_data["name"],
                code=country_data["code"],
                is_active=True
            )
            session.add(country)
        
        session.commit()
        print(f"Successfully seeded {len(countries_data)} countries")


if __name__ == "__main__":
    seed_countries()
