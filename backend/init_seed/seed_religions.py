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
            "categories": [
                {
                    "name": "Vaishnavism",
                    "sub_categories": ["ISKCON", "Swaminarayan", "Other"]
                },
                {
                    "name": "Shaivism",
                    "sub_categories": ["Kashmir Shaivism", "Lingayat", "Other"]
                },
                {
                    "name": "Shaktism",
                    "sub_categories": []
                },
                {
                    "name": "Smartism",
                    "sub_categories": []
                },
            ]
        },
        {
            "name": "Islam",
            "categories": [
                {
                    "name": "Sunni",
                    "sub_categories": ["Hanafi", "Maliki", "Shafi'i", "Hanbali"]
                },
                {
                    "name": "Shia",
                    "sub_categories": ["Twelver", "Ismaili", "Zaidi"]
                },
                {
                    "name": "Sufi",
                    "sub_categories": []
                },
            ]
        },
        {
            "name": "Christianity",
            "categories": [
                {
                    "name": "Catholic",
                    "sub_categories": ["Roman Catholic", "Eastern Catholic"]
                },
                {
                    "name": "Protestant",
                    "sub_categories": ["Baptist", "Methodist", "Lutheran", "Presbyterian"]
                },
                {
                    "name": "Orthodox",
                    "sub_categories": ["Eastern Orthodox", "Oriental Orthodox"]
                },
            ]
        },
        {
            "name": "Sikhism",
            "categories": []
        },
        {
            "name": "Buddhism",
            "categories": [
                {
                    "name": "Theravada",
                    "sub_categories": []
                },
                {
                    "name": "Mahayana",
                    "sub_categories": ["Zen", "Pure Land", "Tibetan"]
                },
                {
                    "name": "Vajrayana",
                    "sub_categories": []
                },
            ]
        },
        {
            "name": "Jainism",
            "categories": [
                {
                    "name": "Digambara",
                    "sub_categories": []
                },
                {
                    "name": "Svetambara",
                    "sub_categories": []
                },
            ]
        },
        {
            "name": "Judaism",
            "categories": [
                {
                    "name": "Orthodox",
                    "sub_categories": []
                },
                {
                    "name": "Conservative",
                    "sub_categories": []
                },
                {
                    "name": "Reform",
                    "sub_categories": []
                },
            ]
        },
        {
            "name": "Other",
            "categories": []
        },
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
            religion = Religion(name=religion_data["name"])
            session.add(religion)
            session.flush()  # Get the ID
            
            print(f"  ✓ Created religion: {religion.name}")
            
            # Create categories
            for category_data in religion_data.get("categories", []):
                category = ReligionCategory(
                    name=category_data["name"],
                    religion_id=religion.id
                )
                session.add(category)
                session.flush()
                
                print(f"    ✓ Created category: {category.name}")
                
                # Create sub-categories
                for sub_category_name in category_data.get("sub_categories", []):
                    sub_category = ReligionSubCategory(
                        name=sub_category_name,
                        religion_category_id=category.id
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
