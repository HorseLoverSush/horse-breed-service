---
applyTo: "tests/**/*.py,conftest.py,**/test_*.py,**/*_test.py"
---

# Testing Instructions

## Test Organization

**Test Structure**:
- `tests/fixtures/` - Shared fixtures and test utilities
- `tests/unit/` - Fast tests with mocked dependencies
- `tests/integration/` - Full system tests with real database

**Test Markers**: Always use appropriate pytest markers:
```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.performance
@pytest.mark.monitoring
```

## Required Patterns

**Async Testing**: Use `pytest-asyncio` for async operations:
```python
@pytest.mark.asyncio
async def test_async_operation():
    # Test implementation
```

**Fixture Usage**: Use shared fixtures from `tests/fixtures/base_fixtures.py`:
```python
def test_operation(db_session, sample_horse_breed):
    # Test using fixtures
```

**Mocking**: Mock external dependencies in unit tests:
```python
@patch('app.services.horse_breed_service.get_logger')
def test_service_operation(mock_logger, db_session):
    # Test with mocked logger
```

## Test Execution

**Use specific test runners** for different scenarios:
- `python run_tests.py` - Full comprehensive test suite
- `python validate_tests.py` - Quick validation
- `pytest tests/unit/core/test_exceptions.py -v` - Specific test files

**Coverage Requirements**: Maintain 80%+ test coverage as defined in `pyproject.toml`.

## Integration Test Patterns

**Database Testing**: Use transaction rollback for clean test isolation:
```python
@pytest.fixture
def db_session():
    # Setup transaction
    yield session
    # Rollback transaction
```

**API Testing**: Test full request/response cycle:
```python
async def test_api_endpoint(async_client):
    response = await async_client.get("/api/v1/breeds")
    assert response.status_code == 200
```