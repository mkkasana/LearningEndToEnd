# Database Seeding Scripts

This directory contains scripts to seed the database with initial metadata.

## Quick Start

To seed all metadata at once:

```bash
# From project root
./scripts/seed-metadata.sh
```

Or run directly:

```bash
docker compose exec backend python /app/init_seed/seed_all.py
```

## Individual Seed Scripts

You can also run individual seed scripts:

### All Metadata (Recommended)
Seeds religions, castes, and gotras:
```bash
docker compose exec backend python /app/init_seed/seed_all.py
```

### Religions
Seeds all religions with their categories and sub-categories:
```bash
docker compose exec backend python /app/init_seed/seed_religions.py
```

### Countries
Seeds country data:
```bash
docker compose exec backend python /app/init_seed/seed_countries.py
```

### States
Seeds state/province data:
```bash
docker compose exec backend python /app/init_seed/seed_states.py
```

### Genders
Seeds gender options:
```bash
docker compose exec backend python /app/init_seed/seed_genders.py
```

## What Gets Seeded

### seed_all.py (Master Script)
This comprehensive script seeds:

1. **Religions** - Major world religions:
   - Hinduism (with castes: Gurjar, Meena, Jat, Rajput, Brahmin, Yadav, SC, ST, OBC, General)
   - Islam (Sunni, Shia, Sufi)
   - Christianity (Catholic, Protestant, Orthodox)
   - Sikhism
   - Buddhism (Theravada, Mahayana, Vajrayana)
   - Jainism (Digambara, Svetambara)
   - Judaism (Orthodox, Conservative, Reform)
   - Other

2. **Hindu Castes** - Added as categories under Hinduism:
   - Gurjar (with gotras: Kasana, Tanwar, Khatana, Bhati, Chauhan, Solanki, Parmar, Rathore, Bainsla, Nagar, Other)
   - Meena
   - Jat
   - Rajput
   - Brahmin
   - Yadav
   - Scheduled Caste (SC)
   - Scheduled Tribe (ST)
   - Other Backward Class (OBC)
   - General

3. **Gurjar Gotras** - Added as sub-categories under Gurjar:
   - Kasana
   - Tanwar
   - Khatana
   - Bhati
   - Chauhan
   - Solanki
   - Parmar
   - Rathore
   - Bainsla
   - Nagar
   - Other

### seed_countries.py
Populates the `country` table with 51 countries including India, USA, UK, etc.

### seed_states.py
Populates the `state` table with:
- 36 Indian states and union territories
- 50 US states

### seed_genders.py
Populates gender options for user profiles.

## Typical Setup Workflow

```bash
# 1. Start services
docker compose up -d

# 2. Run migrations
docker compose exec backend alembic upgrade head

# 3. Seed all metadata
./scripts/seed-metadata.sh

# Or seed individually
docker compose exec backend python /app/init_seed/seed_countries.py
docker compose exec backend python /app/init_seed/seed_states.py
docker compose exec backend python /app/init_seed/seed_genders.py
docker compose exec backend python /app/init_seed/seed_all.py
```

## Important Notes

1. **Run migrations first:** Always run `alembic upgrade head` before seeding
2. **Idempotent:** All scripts check if data exists before inserting
3. **Order matters:** Seed countries before states (foreign key dependency)
4. **Safe to re-run:** Running the same script multiple times is safe
5. **Environment:** Scripts work from both local and Docker environments

## Adding New Seed Scripts

When creating new seed scripts:

1. Name them `seed_<entity>.py`
2. Make them idempotent (check if data exists)
3. Add path setup for imports:
   ```python
   import sys
   from pathlib import Path
   sys.path.insert(0, str(Path(__file__).parent.parent))
   ```
4. Document in this README
5. Consider dependencies (run order)
6. Add to `seed_all.py` if it's core metadata
