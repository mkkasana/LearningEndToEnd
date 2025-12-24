#!/usr/bin/env python3
"""Seed script for religions, categories, and sub-categories."""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlmodel import Session, select

from app.core.db import engine
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
        print("\n✅ Successfully seeded all religions!")


if __name__ == "__main__":
    try:
        seed_religions()
    except Exception as e:
        print(f"❌ Error seeding religions: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
