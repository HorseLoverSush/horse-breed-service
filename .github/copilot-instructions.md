# Copilot Instructions - Horse Breed Service

## Architecture Overview

This is a FastAPI microservice following a **layered architecture** with clear separation of concerns:

- **Endpoints** (`app/api/v1/endpoints/`) - HTTP request handling only, no business logic
- **Services** (`app/services/`) - Business logic layer with decorators for logging/performance
- **Models** (`app/models/`) - SQLAlchemy ORM models 
- **Schemas** (`app/schemas/`) - Pydantic models for request/response validation
- **Core** (`app/core/`) - Cross-cutting concerns (config, logging, exceptions, middleware)

**Key Pattern**: All business logic lives in service classes, endpoints are thin wrappers that delegate to services.

## Configuration & Environment

**Critical**: This project uses **environment-based configuration** for security:
- All sensitive data (DB passwords, secrets) come from environment variables
- Never hardcode credentials - use `settings` object from `app.core.config`
- Required env vars are validated at startup in `Settings.__post_init__()`
- Use `.env.example` as template, never commit `.env` file

```python
# Always use this pattern for config
from app.core.config import settings
database_url = settings.DATABASE_URL  # Not hardcoded strings
```

## Enhanced Logging System

This service has a **sophisticated logging system** with:
- **Correlation IDs** for request tracing
- **PII filtering** (passwords, emails, tokens automatically removed)
- **Performance decorators** (`@log_performance`)
- **Business event logging** (`log_business_event()`)
- **Structured JSON output** to `logs/` directory

**Usage Patterns**:
```python
# In service classes - use these decorators and methods
from app.core.enhanced_logging import get_logger, log_performance, log_business_event

class MyService:
    def __init__(self, db: Session):
        self.logger = get_logger("service.my_service")
    
    @log_performance("operation_name", threshold_ms=500.0)
    def my_operation(self):
        # Business logic here
        log_business_event(self.logger, "business_event", {"key": "value"})
```

## Error Handling Strategy

**Custom exception hierarchy** in `app/core/exceptions.py`:
- `NotFoundError` → HTTP 404
- `ConflictError` → HTTP 409  
- `ValidationError` → HTTP 422
- `DatabaseError` → HTTP 500

**Pattern**: Services raise domain exceptions, global handlers in `app/core/error_handlers.py` convert to HTTP responses.

```python
# In services - raise domain exceptions
if not resource:
    raise NotFoundError(resource="Horse breed", identifier=breed_id)

# Never return HTTP responses from services
```

## Database Patterns

- **Soft deletes**: Use `is_active=False` instead of hard deletes
- **Service layer** handles all DB operations, not endpoints
- **Transaction management**: Services handle commit/rollback
- **Connection**: Use `get_db()` dependency for session management

```python
# Standard service pattern
def delete_breed(self, breed_id: int) -> HorseBreed:
    db_breed = self.get_breed_by_id(breed_id)
    if not db_breed:
        raise NotFoundError(resource="Horse breed", identifier=breed_id)
    
    db_breed.is_active = False  # Soft delete
    self.db.commit()
    return db_breed
```

## Development Workflow

**Running the service**:
```bash
python run.py                    # Development server
python start_service.py          # Production-like server
```

**Database setup**:
```bash
python create_tables.py          # Create/recreate tables
python seed_data.py              # Add sample data
```

**Testing** (200+ tests with specific runners):
```bash
python run_tests.py              # Comprehensive test suite
python validate_tests.py         # Quick validation
pytest tests/unit/core/test_exceptions.py -v  # Specific test file
```

**Monitoring & Debugging**:
```bash
python test_pii_filtering.py     # Validate security filtering
python setup_monitoring.py       # Initialize monitoring
python test_monitoring.py        # Test monitoring endpoints
```

## API Design Patterns

**Pagination**: Always use `page`/`size` with `total`/`pages` in responses
**Search**: Use `search` query param for text searches across multiple fields
**Filtering**: Use `active_only` boolean for soft-deleted records

```python
# Standard endpoint pattern
@router.get("/", response_model=HorseBreedListResponse)
async def get_breeds(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    service = HorseBreedService(db)
    breeds, total = service.get_breeds(skip=(page-1)*size, limit=size, search=search, active_only=active_only)
    # Return paginated response
```

## Security & Monitoring

**Security features**:
- PII data automatically filtered from logs
- Sensitive headers (Authorization, API keys) removed
- Environment-based secrets management
- CORS middleware properly configured

**Monitoring endpoints** (check these for system health):
- `/health` - Basic health check
- `/monitoring/health` - Detailed health with DB connectivity  
- `/monitoring/metrics` - Performance metrics
- `/monitoring/logs` - Recent filtered logs

## Testing Architecture

**Test structure**:
- `tests/fixtures/` - Shared test fixtures and mocks
- `tests/unit/` - Fast tests, mocked dependencies
- `tests/integration/` - Full system tests with real DB
- Async testing with `pytest-asyncio`
- Coverage requirements: 80%+ in `pyproject.toml`

**Test markers**: Use `@pytest.mark.unit`, `@pytest.mark.integration`, etc.

## Key Files to Reference

- `app/main.py` - Application factory pattern and middleware setup
- `app/core/config.py` - Environment configuration with validation
- `app/services/horse_breed_service.py` - Complete service example with logging/error handling
- `app/core/enhanced_logging.py` - Logging decorators and utilities
- `tests/fixtures/base_fixtures.py` - Testing patterns and fixtures
- `run_tests.py` - Test execution patterns