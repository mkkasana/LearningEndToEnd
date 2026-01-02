#!/usr/bin/env python3
"""Seed script for religions, categories, and sub-categories.

This script seeds:
1. Religions (Hinduism, Islam, Christianity, etc.)
2. Religion Categories (denominations, sects)
3. Religion Sub-Categories (specific traditions)
4. Hindu Castes (as categories under Hinduism)
5. Gurjar Gotras (as sub-categories under Gurjar caste)
"""

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


# Religion data with categories and sub-categories
RELIGIONS_DATA = [
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

# Hindu castes to be added as categories under Hinduism
HINDU_CASTES_DATA = [
    {"name": "Gurjar", "code": "GUR", "description": "Gurjar caste/community"},
    {"name": "Meena", "code": "MEE", "description": "Meena caste/community"},
    {"name": "Jat", "code": "JAT", "description": "Jat caste/community"},
    {"name": "Rajput", "code": "RAJ", "description": "Rajput caste/community"},
    {"name": "Brahmin", "code": "BRA", "description": "Brahmin caste/community"},
    {"name": "Yadav", "code": "YAD", "description": "Yadav caste/community"},
    {"name": "Scheduled Caste", "code": "SC", "description": "Scheduled Caste (SC)"},
    {"name": "Scheduled Tribe", "code": "ST", "description": "Scheduled Tribe (ST)"},
    {"name": "Other Backward Class", "code": "OBC", "description": "Other Backward Class (OBC)"},
    {"name": "General", "code": "GEN", "description": "General category"},
]

# Gurjar gotras to be added as sub-categories under Gurjar caste
GURJAR_GOTRAS_DATA = [
    {"name": "Kasana", "code": "KAS", "description": "Kasana gotra"},
    {"name": "Tanwar", "code": "TAN", "description": "Tanwar gotra"},
    {"name": "Khatana", "code": "KHA", "description": "Khatana gotra"},
    {"name": "Bhati", "code": "BHA", "description": "Bhati gotra"},
    {"name": "Chauhan", "code": "CHA", "description": "Chauhan gotra"},
    {"name": "Solanki", "code": "SOL", "description": "Solanki gotra"},
    {"name": "Parmar", "code": "PAR", "description": "Parmar gotra"},
    {"name": "Rathore", "code": "RAT", "description": "Rathore gotra"},
    {"name": "Bainsla", "code": "BAI", "description": "Bainsla gotra"},
    {"name": "Nagar", "code": "NAG", "description": "Nagar gotra"},
    {"name": "Other", "code": "OTH", "description": "Other gotra"},
]


def seed_religions(session: Session) -> None:
    """Seed religions with categories and sub-categories."""
    existing = session.exec(select(Religion)).first()
    if existing:
        print("✓ Religions already seeded")
        return
    
    print("Seeding religions...")
    
    for religion_data in RELIGIONS_DATA:
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
    print("✅ Successfully seeded religions!")


def seed_hindu_castes(session: Session) -> None:
    """Seed Hindu castes as categories under Hinduism."""
    # Get Hinduism religion
    hinduism = session.exec(select(Religion).where(Religion.name == "Hinduism")).first()
    
    if not hinduism:
        print("❌ Hinduism not found. Please seed religions first.")
        return
    
    print(f"Found Hinduism with ID: {hinduism.id}")
    print("Adding Hindu castes as categories...")
    
    for caste_data in HINDU_CASTES_DATA:
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
                description=caste_data["description"]
            )
            session.add(caste)
            print(f"  ✓ Added {caste_data['name']}")
    
    session.commit()
    print("✅ Successfully added Hindu castes!")


def seed_gurjar_gotras(session: Session) -> None:
    """Seed Gurjar gotras as sub-categories under Gurjar caste."""
    # Get Gurjar category
    gurjar = session.exec(
        select(ReligionCategory).where(ReligionCategory.name == "Gurjar")
    ).first()
    
    if not gurjar:
        print("❌ Gurjar category not found. Please seed Hindu castes first.")
        return
    
    print(f"Found Gurjar category with ID: {gurjar.id}")
    print("Adding Gurjar gotras as sub-categories...")
    
    for gotra_data in GURJAR_GOTRAS_DATA:
        # Check if gotra already exists
        existing = session.exec(
            select(ReligionSubCategory)
            .where(ReligionSubCategory.name == gotra_data["name"])
            .where(ReligionSubCategory.category_id == gurjar.id)
        ).first()
        
        if existing:
            print(f"  ⊘ {gotra_data['name']} already exists")
        else:
            gotra = ReligionSubCategory(
                name=gotra_data["name"],
                code=gotra_data["code"],
                category_id=gurjar.id,
                description=gotra_data["description"]
            )
            session.add(gotra)
            print(f"  ✓ Added {gotra_data['name']}")
    
    session.commit()
    print("✅ Successfully added Gurjar gotras!")


def seed_all_religions() -> None:
    """Seed all religion-related data: religions, castes, and gotras."""
    print("=" * 60)
    print("Starting religion seeding...")
    print("=" * 60)
    print()
    
    with Session(engine) as session:
        # Seed religions with categories and sub-categories
        seed_religions(session)
        print()
        
        # Seed Hindu castes
        seed_hindu_castes(session)
        print()
        
        # Seed Gurjar gotras
        seed_gurjar_gotras(session)
        print()
    
    print("=" * 60)
    print("✅ All religion seeding completed!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        seed_all_religions()
    except Exception as e:
        print(f"❌ Error seeding religions: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
