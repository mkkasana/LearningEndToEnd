# Countries API - Complete Flow Diagram

## Request Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Client Request                                                  │
│  GET http://localhost:8000/api/v1/metadata/address/countries   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI App (main.py)                                          │
│  - CORS middleware                                              │
│  - Routes to api_router with prefix /api/v1                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  API Router (api/main.py)                                       │
│  - Includes metadata.router                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Metadata Router (api/routes/metadata.py)                       │
│  @router.get("/address/countries")                              │
│  def get_countries(session: SessionDep)                         │
│                                                                  │
│  Dependencies Injected:                                         │
│  - session: Database session from get_db()                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Country Service (services/country_service.py)                  │
│  country_service = CountryService(session)                      │
│  countries = country_service.get_countries()                    │
│                                                                  │
│  Business Logic:                                                │
│  - Fetch active countries                                       │
│  - Transform to API response format                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Country Repository (repositories/country_repository.py)        │
│  country_repo = CountryRepository(session)                      │
│  countries = country_repo.get_active_countries()                │
│                                                                  │
│  Data Access:                                                   │
│  - SELECT * FROM country WHERE is_active = true                 │
│  - ORDER BY name                                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Database (PostgreSQL)                                          │
│  Table: country                                                 │
│  Columns: id (UUID), name, code, is_active                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼ (Returns List[Country])
┌─────────────────────────────────────────────────────────────────┐
│  Country Service (Transform)                                    │
│  [CountryPublic(                                                │
│    countryId=country.id,                                        │
│    countryName=country.name                                     │
│  ) for country in countries]                                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼ (Returns List[CountryPublic])
┌─────────────────────────────────────────────────────────────────┐
│  FastAPI Response                                               │
│  - Validates response against schema                            │
│  - Serializes to JSON                                           │
│  - Returns HTTP 200 with JSON body                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Client Response                                                │
│  [                                                              │
│    {                                                            │
│      "countryId": "uuid-here",                                  │
│      "countryName": "India"                                     │
│    },                                                           │
│    {                                                            │
│      "countryId": "uuid-here",                                  │
│      "countryName": "United States"                             │
│    }                                                            │
│  ]                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
backend/
├── app/
│   ├── db_models/
│   │   └── country.py              # Database table definition
│   ├── schemas/
│   │   └── country.py              # API request/response schemas
│   ├── repositories/
│   │   └── country_repository.py   # Data access layer
│   ├── services/
│   │   └── country_service.py      # Business logic layer
│   ├── api/
│   │   ├── main.py                 # Router aggregation
│   │   └── routes/
│   │       └── metadata.py         # API endpoints
│   ├── alembic/
│   │   └── versions/
│   │       └── f3a1b2c4d5e6_add_country_table.py  # Migration
│   └── seed_countries.py           # Data seeding script
└── test_countries_api.sh           # Test script
```

## Key Components

### 1. Database Model (ORM)
```python
class Country(SQLModel, table=True):
    id: uuid.UUID
    name: str
    code: str
    is_active: bool
```

### 2. API Schema (Validation)
```python
class CountryPublic(SQLModel):
    countryId: uuid.UUID
    countryName: str
```

### 3. Repository (Data Access)
```python
def get_active_countries(self) -> list[Country]:
    statement = select(Country).where(Country.is_active == True).order_by(Country.name)
    return list(self.session.exec(statement).all())
```

### 4. Service (Business Logic)
```python
def get_countries(self) -> list[CountryPublic]:
    countries = self.country_repo.get_active_countries()
    return [CountryPublic(countryId=c.id, countryName=c.name) for c in countries]
```

### 5. Route (API Endpoint)
```python
@router.get("/address/countries")
def get_countries(session: SessionDep) -> Any:
    country_service = CountryService(session)
    return country_service.get_countries()
```

## Testing Checklist

- [ ] Run migration: `alembic upgrade head`
- [ ] Seed data: `python -m app.seed_countries`
- [ ] Start server: `uvicorn app.main:app --reload`
- [ ] Test endpoint: `./test_countries_api.sh`
- [ ] Check Swagger docs: `http://localhost:8000/docs`
- [ ] Verify response format matches schema
- [ ] Test from frontend application
