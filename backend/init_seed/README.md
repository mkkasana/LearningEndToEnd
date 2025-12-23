# Initial Seed Scripts

This directory contains scripts for populating initial data in the database.

## Purpose

These scripts are used to:
- Populate reference/metadata tables with initial data
- Set up default configurations
- Provide sample data for development

## Available Scripts

### seed_countries.py

Populates the `country` table with 51 countries.

**Usage:**
```bash
# From backend directory
python init_seed/seed_countries.py

# From Docker
docker-compose exec backend python init_seed/seed_countries.py
```

**What it seeds:**
- 51 countries with ISO codes
- Includes major countries like India, USA, UK, etc.

### seed_states.py

Populates the `state` table with states for India and USA.

**Usage:**
```bash
# From backend directory
python init_seed/seed_states.py

# From Docker
docker-compose exec backend python init_seed/seed_states.py
```

**What it seeds:**
- 36 Indian states and union territories
- 50 US states

## Running All Seeds

```bash
# Run in order (countries first, then states)
python init_seed/seed_countries.py
python init_seed/seed_states.py
```

## Important Notes

1. **Run migrations first:** Always run `alembic upgrade head` before seeding
2. **Idempotent:** Scripts check if data exists before inserting
3. **Order matters:** Seed countries before states (foreign key dependency)
4. **Environment:** Scripts work from both local and Docker environments

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

## Typical Setup Workflow

```bash
# 1. Run migrations
alembic upgrade head

# 2. Seed reference data
python init_seed/seed_countries.py
python init_seed/seed_states.py

# 3. Verify
python -c "from app.core.db import engine; from sqlmodel import Session, select; from app.db_models.country import Country; session = Session(engine); print(f'Countries: {len(session.exec(select(Country)).all())}')"
```
