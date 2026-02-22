#!/usr/bin/env python3
"""Master seed script for all metadata."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import uuid

from sqlmodel import Session, select

from app.core.db import engine
from app.db_models.address import Country, District, Locality, State, SubDistrict
from app.db_models.religion.religion import Religion
from app.db_models.religion.religion_category import ReligionCategory
from app.db_models.religion.religion_sub_category import ReligionSubCategory


def seed_religions():
    """Seed religions with categories and sub-categories."""
    
    religions_data = [
        {
            "name": "Hinduism",
            "code": "HIN",
            "categories": [
                {
                    "name": "Vaishnavism",
                    "code": "VAIS",
                    "sub_categories": [
                        {"name": "ISKCON", "code": "ISK"},
                        {"name": "Swaminarayan", "code": "SWA"},
                        {"name": "Other", "code": "OTH"}
                    ]
                },
                {
                    "name": "Shaivism",
                    "code": "SHAI",
                    "sub_categories": [
                        {"name": "Kashmir Shaivism", "code": "KAS"},
                        {"name": "Lingayat", "code": "LIN"},
                        {"name": "Other", "code": "OTH"}
                    ]
                },
                {"name": "Shaktism", "code": "SHAK"},
                {"name": "Smartism", "code": "SMAR"},
            ]
        },
        {
            "name": "Islam",
            "code": "ISL",
            "categories": [
                {
                    "name": "Sunni",
                    "code": "SUN",
                    "sub_categories": [
                        {"name": "Hanafi", "code": "HAN"},
                        {"name": "Maliki", "code": "MAL"},
                        {"name": "Shafi'i", "code": "SHA"},
                        {"name": "Hanbali", "code": "HNB"}
                    ]
                },
                {
                    "name": "Shia",
                    "code": "SHI",
                    "sub_categories": [
                        {"name": "Twelver", "code": "TWE"},
                        {"name": "Ismaili", "code": "ISM"},
                        {"name": "Zaidi", "code": "ZAI"}
                    ]
                },
                {"name": "Sufi", "code": "SUF"},
            ]
        },
        {
            "name": "Christianity",
            "code": "CHR",
            "categories": [
                {
                    "name": "Catholic",
                    "code": "CAT",
                    "sub_categories": [
                        {"name": "Roman Catholic", "code": "ROM"},
                        {"name": "Eastern Catholic", "code": "EAS"}
                    ]
                },
                {
                    "name": "Protestant",
                    "code": "PRO",
                    "sub_categories": [
                        {"name": "Baptist", "code": "BAP"},
                        {"name": "Methodist", "code": "MET"},
                        {"name": "Lutheran", "code": "LUT"},
                        {"name": "Presbyterian", "code": "PRE"}
                    ]
                },
                {
                    "name": "Orthodox",
                    "code": "ORT",
                    "sub_categories": [
                        {"name": "Eastern Orthodox", "code": "EOR"},
                        {"name": "Oriental Orthodox", "code": "OOR"}
                    ]
                },
            ]
        },
        {"name": "Sikhism", "code": "SIK"},
        {
            "name": "Buddhism",
            "code": "BUD",
            "categories": [
                {"name": "Theravada", "code": "THE"},
                {
                    "name": "Mahayana",
                    "code": "MAH",
                    "sub_categories": [
                        {"name": "Zen", "code": "ZEN"},
                        {"name": "Pure Land", "code": "PUR"},
                        {"name": "Tibetan", "code": "TIB"}
                    ]
                },
                {"name": "Vajrayana", "code": "VAJ"},
            ]
        },
        {
            "name": "Jainism",
            "code": "JAI",
            "categories": [
                {"name": "Digambara", "code": "DIG"},
                {"name": "Svetambara", "code": "SVE"},
            ]
        },
        {
            "name": "Judaism",
            "code": "JUD",
            "categories": [
                {"name": "Orthodox", "code": "ORT"},
                {"name": "Conservative", "code": "CON"},
                {"name": "Reform", "code": "REF"},
            ]
        },
        {"name": "Other", "code": "OTH"},
    ]
    
    with Session(engine) as session:
        # Check if data already exists
        existing = session.exec(select(Religion)).first()
        if existing:
            print("✓ Religions already seeded")
            return
        
        print("Seeding religions...")
        
        for religion_data in religions_data:
            # Create religion
            religion = Religion(
                name=religion_data["name"],
                code=religion_data["code"]
            )
            session.add(religion)
            session.flush()  # Get the ID
            
            print(f"  ✓ Created religion: {religion.name}")
            
            # Create categories
            for category_data in religion_data.get("categories", []):
                category = ReligionCategory(
                    name=category_data["name"],
                    code=category_data.get("code"),
                    religion_id=religion.id
                )
                session.add(category)
                session.flush()
                
                print(f"    ✓ Created category: {category.name}")
                
                # Create sub-categories
                for sub_category_data in category_data.get("sub_categories", []):
                    sub_category = ReligionSubCategory(
                        name=sub_category_data["name"],
                        code=sub_category_data.get("code"),
                        category_id=category.id
                    )
                    session.add(sub_category)
                    print(f"      ✓ Created sub-category: {sub_category.name}")
        
        session.commit()
        print("✅ Successfully seeded all religions!")


def seed_hindu_castes():
    """Seed Hindu castes as categories."""
    
    castes_data = [
        {"name": "Gurjar", "code": "GUR"},
        {"name": "Meena", "code": "MEE"},
        {"name": "Jat", "code": "JAT"},
        {"name": "Rajput", "code": "RAJ"},
        {"name": "Brahmin", "code": "BRA"},
        {"name": "Yadav", "code": "YAD"},
        {"name": "Scheduled Caste", "code": "SC"},
        {"name": "Scheduled Tribe", "code": "ST"},
        {"name": "Other Backward Class", "code": "OBC"},
        {"name": "General", "code": "GEN"},
    ]
    
    with Session(engine) as session:
        # Get Hinduism religion
        hinduism = session.exec(select(Religion).where(Religion.name == "Hinduism")).first()
        
        if not hinduism:
            print("❌ Hinduism not found in database")
            return
        
        print(f"Found Hinduism with ID: {hinduism.id}")
        print("Adding castes as categories...")
        
        for caste_data in castes_data:
            # Check if caste already exists
            existing = session.exec(
                select(ReligionCategory)
                .where(ReligionCategory.name == caste_data["name"])
                .where(ReligionCategory.religion_id == hinduism.id)
            ).first()
            
            if existing:
                print(f"  ⊘ {caste_data['name']} already exists")
            else:
                caste = ReligionCategory(
                    name=caste_data["name"],
                    code=caste_data["code"],
                    religion_id=hinduism.id,
                    description=f"{caste_data['name']} caste/community"
                )
                session.add(caste)
                print(f"  ✓ Added {caste_data['name']}")
        
        session.commit()
        print("✅ Successfully added castes to Hinduism!")


def seed_gurjar_gotras():
    """Seed Gurjar sub-categories (gotras)."""
    
    gurjar_sub_categories = [
        {"name": "Kasana", "code": "KAS"},
        {"name": "Tanwar", "code": "TAN"},
        {"name": "Khatana", "code": "KHA"},
        {"name": "Bhati", "code": "BHA"},
        {"name": "Chauhan", "code": "CHA"},
        {"name": "Solanki", "code": "SOL"},
        {"name": "Parmar", "code": "PAR"},
        {"name": "Rathore", "code": "RAT"},
        {"name": "Bainsla", "code": "BAI"},
        {"name": "Nagar", "code": "NAG"},
        {"name": "Other", "code": "OTH"},
    ]
    
    with Session(engine) as session:
        # Get Gurjar category
        gurjar = session.exec(
            select(ReligionCategory).where(ReligionCategory.name == "Gurjar")
        ).first()
        
        if not gurjar:
            print("❌ Gurjar category not found in database")
            return
        
        print(f"Found Gurjar category with ID: {gurjar.id}")
        print("Adding Gurjar sub-categories (gotras)...")
        
        for sub_cat_data in gurjar_sub_categories:
            # Check if sub-category already exists
            existing = session.exec(
                select(ReligionSubCategory)
                .where(ReligionSubCategory.name == sub_cat_data["name"])
                .where(ReligionSubCategory.category_id == gurjar.id)
            ).first()
            
            if existing:
                print(f"  ⊘ {sub_cat_data['name']} already exists")
            else:
                sub_cat = ReligionSubCategory(
                    name=sub_cat_data["name"],
                    code=sub_cat_data["code"],
                    category_id=gurjar.id,
                    description=f"{sub_cat_data['name']} gotra"
                )
                session.add(sub_cat)
                print(f"  ✓ Added {sub_cat_data['name']}")
        
        session.commit()
        print("✅ Successfully added Gurjar sub-categories!")


def seed_countries():
    """Seed countries."""
    countries_data = [
        {"name": "India", "code": "IND"},
        {"name": "United States", "code": "USA"},
        {"name": "United Kingdom", "code": "GBR"},
        {"name": "Canada", "code": "CAN"},
        {"name": "Australia", "code": "AUS"},
    ]
    
    with Session(engine) as session:
        existing = session.exec(select(Country)).first()
        if existing:
            print("✓ Countries already seeded")
            return
        
        print("Seeding countries...")
        for country_data in countries_data:
            country = Country(
                id=uuid.uuid4(),
                name=country_data["name"],
                code=country_data["code"],
                is_active=True
            )
            session.add(country)
            print(f"  ✓ Added {country_data['name']}")
        
        session.commit()
        print("✅ Successfully seeded countries!")


def seed_indian_states():
    """Seed Indian states."""
    states_data = [
        {"name": "Rajasthan", "code": "RJ"},
        {"name": "Delhi", "code": "DL"},
        {"name": "Maharashtra", "code": "MH"},
        {"name": "Karnataka", "code": "KA"},
        {"name": "Tamil Nadu", "code": "TN"},
    ]
    
    with Session(engine) as session:
        india = session.exec(select(Country).where(Country.code == "IND")).first()
        if not india:
            print("❌ India not found")
            return
        
        existing = session.exec(
            select(State).where(State.country_id == india.id)
        ).first()
        if existing:
            print("✓ Indian states already seeded")
            return
        
        print("Seeding Indian states...")
        for state_data in states_data:
            state = State(
                id=uuid.uuid4(),
                name=state_data["name"],
                code=state_data["code"],
                country_id=india.id,
                is_active=True
            )
            session.add(state)
            print(f"  ✓ Added {state_data['name']}")
        
        session.commit()
        print("✅ Successfully seeded Indian states!")


def seed_rajasthan_districts():
    """Seed Rajasthan districts."""
    districts_data = [
        {"name": "Dausa", "code": "DAU"},
        {"name": "Jaipur", "code": "JAI"},
        {"name": "Ajmer", "code": "AJM"},
        {"name": "Jodhpur", "code": "JOD"},
        {"name": "Udaipur", "code": "UDA"},
    ]
    
    with Session(engine) as session:
        india = session.exec(select(Country).where(Country.code == "IND")).first()
        if not india:
            print("❌ India not found")
            return
        
        rajasthan = session.exec(
            select(State)
            .where(State.code == "RJ")
            .where(State.country_id == india.id)
        ).first()
        if not rajasthan:
            print("❌ Rajasthan not found")
            return
        
        existing = session.exec(
            select(District).where(District.state_id == rajasthan.id)
        ).first()
        if existing:
            print("✓ Rajasthan districts already seeded")
            return
        
        print("Seeding Rajasthan districts...")
        for district_data in districts_data:
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
        print("✅ Successfully seeded Rajasthan districts!")


def seed_dausa_subdistricts():
    """Seed Dausa sub-districts."""
    subdistricts_data = [
        {"name": "Sikrai", "code": "SIK"},
        {"name": "Dausa", "code": "DAU"},
        {"name": "Bandikui", "code": "BAN"},
        {"name": "Lalsot", "code": "LAL"},
    ]
    
    with Session(engine) as session:
        dausa = session.exec(select(District).where(District.name == "Dausa")).first()
        if not dausa:
            print("❌ Dausa district not found")
            return
        
        existing = session.exec(
            select(SubDistrict).where(SubDistrict.district_id == dausa.id)
        ).first()
        if existing:
            print("✓ Dausa sub-districts already seeded")
            return
        
        print("Seeding Dausa sub-districts...")
        for subdistrict_data in subdistricts_data:
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
        print("✅ Successfully seeded Dausa sub-districts!")


def seed_sikrai_villages():
    """Seed Sikrai villages."""
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
    ]
    
    with Session(engine) as session:
        sikrai = session.exec(select(SubDistrict).where(SubDistrict.name == "Sikrai")).first()
        if not sikrai:
            print("❌ Sikrai sub-district not found")
            return
        
        existing = session.exec(
            select(Locality).where(Locality.sub_district_id == sikrai.id)
        ).first()
        if existing:
            print("✓ Sikrai villages already seeded")
            return
        
        print("Seeding Sikrai villages...")
        for village_data in villages_data:
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
        print("✅ Successfully seeded Sikrai villages!")


def main():
    """Run all seed functions."""
    print("=" * 60)
    print("Starting database seeding...")
    print("=" * 60)
    print()
    
    try:
        # Seed address hierarchy first (dependencies)
        seed_countries()
        print()
        
        seed_indian_states()
        print()
        
        seed_rajasthan_districts()
        print()
        
        seed_dausa_subdistricts()
        print()
        
        seed_sikrai_villages()
        print()
        
        # Seed religions
        seed_religions()
        print()
        
        # Seed Hindu castes
        seed_hindu_castes()
        print()
        
        # Seed Gurjar gotras
        seed_gurjar_gotras()
        print()
        
        print("=" * 60)
        print("✅ All seeding completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
