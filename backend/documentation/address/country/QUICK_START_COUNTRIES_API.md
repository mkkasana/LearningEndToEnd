# Countries API - Quick Start

## What You Built

A complete metadata API for countries with GET, POST, and PATCH operations.

## File Purposes

### 1. Migration File
**Location:** `app/alembic/versions/f3a1b2c4d5e6_add_country_table.py`

**Purpose:** Creates the `country` table in your database

**When to use:**
```bash
alembic upgrade head  # Creates the table
```

**What it does:**
- Defines table structure (columns, indexes, constraints)
- Version control for database schema
- Allows rollback if needed

### 2. Seed Script
**Location:** `app/seed_countries.py`

**Purpose:** Populates the country table with 51 countries

**When to use:**
```bash
python -m app.seed_countries  # Fills the table with data
```

**What it does:**
- Inserts initial country data
- Checks if data already exists (idempotent)
- Provides data for dropdowns/forms

### 3. Test Script
**Location:** `tests/integration_scripts/test_countries_api.sh`

**Purpose:** Manual integration testing

**When to use:**
```bash
./tests/integration_scripts/test_countries_api.sh
```

**What it does:**
- Tests GET endpoint
- Validates response format
- Counts returned countries

## Setup Workflow

```bash
# 1. Create table (migration)
alembic upgrade head

# 2. Populate data (seed)
python -m app.seed_countries

# 3. Test API (integration test)
./tests/integration_scripts/test_countries_api.sh
```

## Key Difference: Migration vs Seed

| Migration | Seed |
|-----------|------|
| Schema (structure) | Data (content) |
| Creates tables | Fills tables |
| Version controlled | One-time or refresh |
| Reversible | Usually not |
| Required | Optional |

## Think of it like:

- **Migration** = Building a house (structure)
- **Seed** = Furnishing the house (content)

You need the house before you can add furniture!

## More Info

- Full workflow: `DATABASE_WORKFLOW.md`
- API documentation: `documentation/address/country/`
- Integration tests: `tests/integration_scripts/README.md`
