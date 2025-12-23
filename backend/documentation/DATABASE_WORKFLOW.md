# Database Workflow Guide

## Overview

This project uses **Alembic** for database migrations and separate seed scripts for initial data.

## Key Concepts

### Migrations vs Seeds

| Aspect | Migrations | Seeds |
|--------|-----------|-------|
| **Purpose** | Schema changes (structure) | Data population (content) |
| **Location** | `app/alembic/versions/` | `app/seed_*.py` |
| **Tool** | Alembic | Python scripts |
| **When** | Every schema change | Initial setup, data refresh |
| **Reversible** | Yes (upgrade/downgrade) | Usually no |

## Workflow

### 1. Creating a New Feature with Database Table

**Step 1: Create the model**
```python
# app/db_models/country.py
from sqlmodel import Field, SQLModel
import uuid

class Country(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255)
    code: str = Field(max_length=3)
    is_active: bool = True
```

**Step 2: Generate migration**
```bash
cd backend
alembic revision -m "add_country_table"
```

This creates a file like: `app/alembic/versions/abc123_add_country_table.py`

**Step 3: Edit the migration**
```python
def upgrade():
    op.create_table(
        'country',
        sa.Column('id', UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('country')
```

**Step 4: Apply migration**
```bash
alembic upgrade head
```

**Step 5: Create seed script (optional)**
```python
# app/seed_countries.py
from sqlmodel import Session
from app.core.db import engine
from app.db_models.country import Country

def seed_countries():
    with Session(engine) as session:
        countries = [
            Country(name="India", code="IND"),
            Country(name="United States", code="USA"),
        ]
        for country in countries:
            session.add(country)
        session.commit()

if __name__ == "__main__":
    seed_countries()
```

**Step 6: Run seed script**
```bash
python -m app.seed_countries
```

### 2. Modifying Existing Tables

**Example: Add a new column**

```bash
# Generate migration
alembic revision -m "add_country_phone_code"
```

Edit the migration:
```python
def upgrade():
    op.add_column('country', sa.Column('phone_code', sa.String(length=5)))

def downgrade():
    op.drop_column('country', 'phone_code')
```

Apply:
```bash
alembic upgrade head
```

### 3. Rolling Back Changes

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

## Common Commands

### Alembic Commands

```bash
# Check current version
alembic current

# View migration history
alembic history

# Generate new migration
alembic revision -m "description"

# Auto-generate migration from model changes (use with caution)
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade abc123

# Rollback one migration
alembic downgrade -1

# Show SQL without executing
alembic upgrade head --sql
```

### Seed Commands

```bash
# Run seed script
python -m app.seed_countries

# Run from Docker
docker-compose exec backend python -m app.seed_countries
```

## File Structure

```
backend/
├── app/
│   ├── alembic/
│   │   ├── versions/
│   │   │   ├── abc123_initial.py
│   │   │   ├── def456_add_country_table.py
│   │   │   └── ghi789_add_phone_code.py
│   │   ├── env.py              # Alembic configuration
│   │   └── script.py.mako      # Migration template
│   ├── db_models/
│   │   ├── user.py
│   │   ├── item.py
│   │   └── country.py          # SQLModel definitions
│   ├── seed_countries.py       # Country seed data
│   └── seed_users.py           # User seed data (if needed)
├── alembic.ini                 # Alembic config file
└── DATABASE_WORKFLOW.md        # This file
```

## Best Practices

### Migrations

1. **Always review auto-generated migrations** - They may not be perfect
2. **Test migrations on dev first** - Never run untested migrations in production
3. **Keep migrations small** - One logical change per migration
4. **Write reversible migrations** - Always implement `downgrade()`
5. **Don't modify old migrations** - Create new ones instead
6. **Commit migrations with code** - They're part of your codebase

### Seeds

1. **Make seeds idempotent** - Check if data exists before inserting
2. **Separate by entity** - One seed file per major entity
3. **Use realistic data** - Helps with testing
4. **Document seed order** - If seeds depend on each other
5. **Different seeds for environments** - Dev vs staging vs prod

## Example: Countries Feature

### Files Created

1. **Model:** `app/db_models/country.py`
   - Defines Country table structure

2. **Migration:** `app/alembic/versions/f3a1b2c4d5e6_add_country_table.py`
   - Creates country table in database
   - Run with: `alembic upgrade head`

3. **Seed:** `app/seed_countries.py`
   - Populates 51 countries
   - Run with: `python -m app.seed_countries`

### Setup Sequence

```bash
# 1. Apply migration (creates table)
alembic upgrade head

# 2. Seed data (populates table)
python -m app.seed_countries

# 3. Verify
psql -d your_db -c "SELECT COUNT(*) FROM country;"
```

## Troubleshooting

### Migration fails with "relation already exists"

The table was created outside of Alembic. Options:
```bash
# Option 1: Mark migration as applied without running
alembic stamp head

# Option 2: Drop table and re-run migration
psql -d your_db -c "DROP TABLE country;"
alembic upgrade head
```

### Seed script fails with "duplicate key"

Data already exists. Either:
- Add existence check in seed script
- Clear table first: `DELETE FROM country;`
- Skip seeding if not needed

### Can't rollback migration

Check if data exists that depends on the schema:
```bash
# View what would be rolled back
alembic downgrade -1 --sql

# If safe, proceed
alembic downgrade -1
```

## Production Deployment

### Recommended Process

1. **Backup database** before any migration
2. **Test migration on staging** with production-like data
3. **Run migration during maintenance window** if needed
4. **Monitor application** after migration
5. **Have rollback plan ready**

### Deployment Script Example

```bash
#!/bin/bash
set -e

echo "Backing up database..."
pg_dump your_db > backup_$(date +%Y%m%d_%H%M%S).sql

echo "Running migrations..."
alembic upgrade head

echo "Seeding data (if needed)..."
python -m app.seed_countries

echo "Verifying..."
python -c "from app.core.db import engine; from sqlmodel import Session, select; from app.db_models.country import Country; session = Session(engine); print(f'Countries: {session.exec(select(Country)).all().__len__()}')"

echo "Deployment complete!"
```

## Additional Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
