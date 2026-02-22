#!/usr/bin/env python3
"""Master script to seed the database with all required data.

This script runs all individual seed scripts in the correct order,
respecting dependencies between entities.

Execution Order:
1. Genders (required for person creation)
2. Countries
3. States (depends on countries)
4. Rajasthan Districts (depends on states)
5. Dausa Sub-districts (depends on districts)
6. Sikrai Villages (depends on sub-districts)
7. Religions with categories and sub-categories
8. Family data (user, persons, demographics, relationships)

Usage:
    docker compose exec backend python /app/init_seed/seed_database.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


def main():
    """Run all seed scripts in order."""
    print("=" * 70)
    print("  DATABASE SEEDING - Full Setup")
    print("=" * 70)
    print()
    
    try:
        # 1. Seed genders
        print("[1/8] Seeding genders...")
        print("-" * 50)
        from init_seed.seed_genders import seed_genders
        seed_genders()
        print()
        
        # 2. Seed countries
        print("[2/8] Seeding countries...")
        print("-" * 50)
        from init_seed.seed_countries import seed_countries
        seed_countries()
        print()
        
        # 3. Seed states
        print("[3/8] Seeding states...")
        print("-" * 50)
        from init_seed.seed_states import seed_indian_states, seed_us_states
        seed_indian_states()
        seed_us_states()
        print()
        
        # 4. Seed Rajasthan districts
        print("[4/8] Seeding Rajasthan districts...")
        print("-" * 50)
        from init_seed.seed_rajasthan_districts import seed_rajasthan_districts
        seed_rajasthan_districts()
        print()
        
        # 5. Seed Dausa sub-districts
        print("[5/8] Seeding Dausa sub-districts...")
        print("-" * 50)
        from init_seed.seed_dausa_subdistricts import seed_dausa_subdistricts
        seed_dausa_subdistricts()
        print()
        
        # 6. Seed Sikrai villages
        print("[6/8] Seeding Sikrai villages...")
        print("-" * 50)
        from init_seed.seed_sikrai_villages import seed_sikrai_villages
        seed_sikrai_villages()
        print()
        
        # 7. Seed religions (includes categories, sub-categories, castes, gotras)
        print("[7/8] Seeding religions...")
        print("-" * 50)
        from init_seed.seed_religions import seed_all_religions
        seed_all_religions()
        print()
        
        # 8. Seed family data (user, persons, demographics, relationships)
        print("[8/8] Seeding family data...")
        print("-" * 50)
        from init_seed.seed_family import seed_family
        seed_family()
        print()
        
        print("=" * 70)
        print("  ✅ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("Summary of seeded data:")
        print("  • Genders: Male, Female")
        print("  • Countries: 51 countries")
        print("  • States: 36 Indian states/UTs + 50 US states")
        print("  • Districts: 50 Rajasthan districts")
        print("  • Sub-districts: Dausa sub-districts")
        print("  • Villages: Sikrai villages")
        print("  • Religions: 8 religions with categories and sub-categories")
        print("  • Hindu castes: 10 castes under Hinduism")
        print("  • Gurjar gotras: 11 gotras under Gurjar")
        print("  • Test family: 1 user + 6 persons with relationships")
        print()
        print("Test User Credentials:")
        print("  Email: testfamily@example.com")
        print("  Password: TestFamily123!")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"  ❌ ERROR DURING SEEDING: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
