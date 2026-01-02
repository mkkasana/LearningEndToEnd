# Design Document: Backend Testing Coverage

## Overview

This design document outlines the architecture and implementation approach for achieving comprehensive backend test coverage. The system will implement a layered testing strategy with unit tests for isolated component verification and integration tests for end-to-end API validation.

## Architecture

The testing architecture follows a pyramid structure:

```
                    ┌─────────────────┐
                    │  Integration    │  ← API endpoint tests
                    │     Tests       │     (fewer, slower)
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │        Unit Tests           │  ← Service/Repository tests
              │   (mocked dependencies)     │     (many, fast)
              └──────────────┬──────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        │           Schema Validation Tests       │  ← Pydantic validation
        │         (property-based testing)        │     (comprehensive)
        └─────────────────────────────────────────┘
```

### Test Directory Structure

```
backend/tests/
├── conftest.py                    # Global fixtures
├── markers.py                     # Pytest marker definitions
├── factories/                     # Test data factories
│   ├── __init__.py
│   ├── user_factory.py
│   ├── person_factory.py
│   └── relationship_factory.py
├── unit/                          # Unit tests (mocked)
│   ├── services/
│   │   ├── test_auth_service.py
│   │   ├── test_user_service.py
│   │   ├── test_person_service.py
│   │   ├── test_person_relationship_service.py
│   │   ├── test_person_address_service.py
│   │   ├── test_person_religion_service.py
│   │   ├── test_person_profession_service.py
│   │   ├── test_person_discovery_service.py
│   │   ├── test_person_matching_service.py
│   │   ├── test_profile_service.py
│   │   ├── test_profile_view_tracking_service.py
│   │   ├── test_support_ticket_service.py
│   │   ├── test_item_service.py
│   │   ├── test_post_service.py
│   │   ├── test_gender_service.py
│   │   ├── address/
│   │   │   └── test_*.py
│   │   └── religion/
│   │       └── test_*.py
│   ├── repositories/
│   │   ├── test_person_repository.py
│   │   ├── test_user_repository.py
│   │   └── ... (all repositories)
│   └── schemas/
│       ├── test_person_schemas.py
│       ├── test_user_schemas.py
│       └── ... (all schemas)
├── integration/                   # Integration tests (real DB)
│   ├── conftest.py               # Integration-specific fixtures
│   ├── test_auth_api.py
│   ├── test_users_api.py
│   ├── test_person_api.py
│   ├── test_relatives_api.py
│   ├── test_profile_api.py
│   ├── test_metadata_api.py
│   ├── test_support_tickets_api.py
│   ├── test_posts_api.py
│   └── test_items_api.py
└── utils/                         # Test utilities
    ├── __init__.py
    ├── assertions.py
    └── helpers.py
```

## Components and Interfaces

### Test Fixtures (conftest.py)

```python
# Global fixtures for all tests
import pytest
from sqlmodel import Session
from fastapi.testclient import TestClient
from app.core.db import engine
from app.main import app

@pytest.fixture(scope="session")
def db_session() -> Generator[Session, None, None]:
    """Session-scoped database session for unit tests."""
    with Session(engine) as session:
        yield session

@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Module-scoped test client."""
    with TestClient(app) as c:
        yield c

@pytest.fixture
def mock_session() -> MagicMock:
    """Mock database session for isolated unit tests."""
    return MagicMock(spec=Session)

@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user."""
    # Uses factory pattern
    return UserFactory.create(db_session)

@pytest.fixture
def auth_headers(client: TestClient, test_user: User) -> dict[str, str]:
    """Get authentication headers for test user."""
    # Login and return headers
    pass
```

### Test Factories

```python
# factories/user_factory.py
from app.models import User
from app.core.security import get_password_hash

class UserFactory:
    @staticmethod
    def create(
        session: Session,
        email: str | None = None,
        password: str = "testpassword123",
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        email = email or f"test_{uuid.uuid4()}@example.com"
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            is_active=is_active,
            is_superuser=is_superuser,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# factories/person_factory.py
class PersonFactory:
    @staticmethod
    def create(
        session: Session,
        user: User,
        first_name: str | None = None,
        last_name: str | None = None,
        gender_id: UUID | None = None,
        **kwargs
    ) -> Person:
        # Create person with defaults
        pass
```

### Pytest Markers

```python
# markers.py - Define custom markers
import pytest

# Register markers in pytest.ini or pyproject.toml
# [tool.pytest.ini_options]
# markers = [
#     "unit: Unit tests (mocked dependencies)",
#     "integration: Integration tests (real database)",
#     "slow: Slow running tests",
# ]
```

### Unit Test Pattern

```python
# unit/services/test_person_service.py
import pytest
from unittest.mock import MagicMock, patch
from app.services.person.person_service import PersonService

@pytest.mark.unit
class TestPersonService:
    """Unit tests for PersonService."""

    def test_create_person_success(self, mock_session: MagicMock):
        """Test successful person creation."""
        # Arrange
        service = PersonService(mock_session)
        mock_repo = MagicMock()
        
        with patch.object(service, 'person_repo', mock_repo):
            # Act
            result = service.create_person(user_id, person_data)
            
            # Assert
            mock_repo.create.assert_called_once()
            assert result is not None

    def test_create_person_invalid_gender_raises_error(self, mock_session: MagicMock):
        """Test that invalid gender_id raises ValueError."""
        service = PersonService(mock_session)
        
        with pytest.raises(ValueError, match="Invalid gender"):
            service.create_person(user_id, invalid_person_data)
```

### Integration Test Pattern

```python
# integration/test_person_api.py
import pytest
from fastapi.testclient import TestClient

@pytest.mark.integration
class TestPersonAPI:
    """Integration tests for Person API endpoints."""

    def test_create_person_success(
        self, 
        client: TestClient, 
        auth_headers: dict[str, str]
    ):
        """Test POST /person/ creates person successfully."""
        # Arrange
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "gender_id": str(MALE_GENDER_ID),
            "date_of_birth": "1990-01-01"
        }
        
        # Act
        response = client.post(
            "/api/v1/person/",
            json=person_data,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "John"
        assert data["last_name"] == "Doe"

    def test_create_person_invalid_gender_returns_400(
        self,
        client: TestClient,
        auth_headers: dict[str, str]
    ):
        """Test POST /person/ with invalid gender returns 400."""
        person_data = {
            "first_name": "John",
            "last_name": "Doe",
            "gender_id": str(uuid.uuid4()),  # Non-existent
            "date_of_birth": "1990-01-01"
        }
        
        response = client.post(
            "/api/v1/person/",
            json=person_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
```

## Data Models

### Test Configuration (pyproject.toml additions)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
markers = [
    "unit: Unit tests with mocked dependencies",
    "integration: Integration tests with real database",
    "slow: Slow running tests",
]
addopts = "-v --strict-markers"

[tool.coverage.run]
source = ["app"]
omit = [
    "app/alembic/*",
    "app/tests_pre_start.py",
    "app/backend_pre_start.py",
    "app/initial_data.py",
]

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Schema Validation Round-Trip

*For any* valid data object that conforms to a schema's constraints, serializing to JSON and deserializing back should produce an equivalent object.

**Validates: Requirements 4.1-4.6**

### Property 2: Non-Existent Resource Returns 404

*For any* API request that references a resource ID that does not exist in the database, the API should return a 404 Not Found response.

**Validates: Requirements 7.10, 8.11, 9.10, 11.11, 12.8, 13.7, 14.7**

### Property 3: Unauthorized Access Returns 403

*For any* API request where the authenticated user does not have permission to access or modify the requested resource, the API should return a 403 Forbidden response.

**Validates: Requirements 7.9, 8.10, 12.7, 13.6, 14.6**

### Property 4: Invalid Input Returns 400

*For any* API request with invalid input data (wrong types, missing required fields, constraint violations), the API should return a 400 Bad Request response with descriptive error details.

**Validates: Requirements 8.9, 9.9**

### Property 5: Self-View Does Not Increment Count

*For any* profile view request where the viewer is the profile owner, the view count should not be incremented.

**Validates: Requirements 10.7**

### Property 6: Profile Completion Percentage Accuracy

*For any* user profile, the completion percentage should accurately reflect the ratio of filled required fields to total required fields.

**Validates: Requirements 10.8**

## Error Handling

### Test Error Categories

| Error Type | HTTP Status | Test Approach |
|------------|-------------|---------------|
| Validation Error | 400 | Property-based testing with invalid inputs |
| Authentication Error | 401 | Test with missing/invalid tokens |
| Authorization Error | 403 | Test with unauthorized user access |
| Not Found Error | 404 | Test with non-existent resource IDs |
| Conflict Error | 409 | Test with duplicate creation attempts |
| Server Error | 500 | Test with mocked failures |

### Error Response Schema

```python
class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    field: str | None = None
```

## Testing Strategy

### Unit Testing Approach

- **Framework**: pytest with hypothesis for property-based testing
- **Mocking**: unittest.mock for dependency isolation
- **Coverage Target**: 90% for services and repositories
- **Execution**: Fast, no external dependencies required

### Integration Testing Approach

- **Framework**: pytest with FastAPI TestClient
- **Database**: Real PostgreSQL via Docker
- **Data Setup**: Use seeded data from init_seed scripts
- **Cleanup**: Transaction rollback or explicit cleanup after tests
- **Coverage Target**: 85% for API routes

### Property-Based Testing Configuration

```python
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

@settings(
    max_examples=100,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    email=st.emails(),
    password=st.text(min_size=8, max_size=50),
)
def test_user_schema_validation(email: str, password: str):
    """Property: Valid email and password should create valid UserCreate."""
    # Test implementation
    pass
```

### Test Execution Commands

```bash
# Run all tests
pytest tests/

# Run only unit tests
pytest tests/ -m unit

# Run only integration tests
pytest tests/ -m integration

# Run with coverage
coverage run -m pytest tests/
coverage report --fail-under=80

# Run specific test file
pytest tests/unit/services/test_person_service.py -v
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest tests/ -m unit --cov=app --cov-report=xml

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
    steps:
      - uses: actions/checkout@v4
      - name: Run integration tests
        run: pytest tests/ -m integration
```
