# Backend Documentation

Complete documentation for the FastAPI backend.

## 📚 Documentation Index

### Getting Started
- **[../README.md](../README.md)** - Project setup, installation, and running the backend

### Architecture & Design
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Complete architecture guide with layers, patterns, and data flow
- **[PROJECT_GUIDE.md](./PROJECT_GUIDE.md)** - Quick reference for adding features and common tasks
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Code templates and examples

### API Documentation
- **[address/README.md](./address/README.md)** - Address metadata API overview
- **[address/COUNTRIES_API.md](./address/COUNTRIES_API.md)** - Countries API reference
- **[address/STATES_API.md](./address/STATES_API.md)** - States API reference
- **[address/DISTRICTS_API.md](./address/DISTRICTS_API.md)** - Districts API reference
- **[address/SUB_DISTRICTS_API.md](./address/SUB_DISTRICTS_API.md)** - Sub-Districts API reference
- **[address/LOCALITIES_API.md](./address/LOCALITIES_API.md)** - Localities API reference

## 🎯 Quick Links

### I want to...

**Understand the architecture**
→ Read [ARCHITECTURE.md](./ARCHITECTURE.md)

**Add a new feature**
→ Follow [PROJECT_GUIDE.md](./PROJECT_GUIDE.md)

**See code examples**
→ Check [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)

**Use the address API**
→ Start with [address/README.md](./address/README.md)

**Run tests**
→ See `../tests/integration_scripts/`

**View API docs interactively**
→ Visit http://localhost:8000/docs

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│         API Layer (Routes)              │  HTTP handling
├─────────────────────────────────────────┤
│         Service Layer                   │  Business logic
├─────────────────────────────────────────┤
│         Repository Layer                │  Data access
├─────────────────────────────────────────┤
│         Database (PostgreSQL)           │  Persistence
└─────────────────────────────────────────┘
```

## 📁 Project Structure

```
backend/app/
├── api/routes/          # HTTP endpoints (by domain)
├── services/            # Business logic (by domain)
├── repositories/        # Data access (by domain)
├── db_models/           # Database models (by domain)
├── schemas/             # API contracts (by domain)
├── core/                # Configuration & setup
└── utils/               # Shared utilities
```

## 🧪 Testing

### Integration Tests
```bash
# Address API (comprehensive)
python3 tests/integration_scripts/test_address_full_integration.py

# Quick start guide
cat tests/integration_scripts/QUICK_START.md
```

### Unit Tests
```bash
pytest
```

## 🔐 Security

- **Public endpoints:** GET operations (no auth)
- **Protected endpoints:** POST/PATCH/DELETE (superuser only)
- **Authentication:** JWT tokens via `/api/v1/login/access-token`

## 🚀 Development Workflow

1. **Create database model** (`db_models/`)
2. **Create migration** (`alembic revision`)
3. **Create schemas** (`schemas/`)
4. **Create repository** (`repositories/`)
5. **Create service** (`services/`)
6. **Create routes** (`api/routes/`)
7. **Register router** (`api/main.py`)
8. **Test** (`tests/`)

See [PROJECT_GUIDE.md](./PROJECT_GUIDE.md) for detailed examples.

## 📊 API Documentation

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

## 🤝 Contributing

When adding new features:
- Follow the clean architecture pattern
- Organize by domain
- Write tests
- Document APIs
- Use type hints

## 📝 Notes

- All documentation is in Markdown
- Code examples use Python 3.11+
- Database is PostgreSQL 17
- Framework is FastAPI with SQLModel
