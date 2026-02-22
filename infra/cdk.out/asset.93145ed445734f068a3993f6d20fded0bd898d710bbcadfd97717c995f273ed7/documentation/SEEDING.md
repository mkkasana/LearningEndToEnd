# Database Seeding Guide

Quick reference for seeding the database with initial data.

## Quick Start

```bash
# Seed all metadata (religions, castes, gotras)
./scripts/seed-metadata.sh
```

## What Gets Seeded

The master seed script (`seed_all.py`) populates:

- **8 Major Religions** with categories and sub-categories
- **10 Hindu Castes** (Gurjar, Meena, Jat, Rajput, Brahmin, Yadav, SC, ST, OBC, General)
- **11 Gurjar Gotras** (Kasana, Tanwar, Khatana, Bhati, Chauhan, Solanki, Parmar, Rathore, Bainsla, Nagar, Other)

## Individual Seeds

```bash
# Religions only
docker compose exec backend python /app/init_seed/seed_religions.py

# Countries
docker compose exec backend python /app/init_seed/seed_countries.py

# States
docker compose exec backend python /app/init_seed/seed_states.py

# Genders
docker compose exec backend python /app/init_seed/seed_genders.py

# All metadata (recommended)
docker compose exec backend python /app/init_seed/seed_all.py
```

## Full Setup

```bash
# 1. Start services
docker compose up -d

# 2. Run migrations
docker compose exec backend alembic upgrade head

# 3. Seed data
./scripts/seed-metadata.sh
```

## Notes

- All seed scripts are **idempotent** - safe to run multiple times
- Scripts check for existing data before inserting
- See `backend/init_seed/README.md` for detailed documentation
