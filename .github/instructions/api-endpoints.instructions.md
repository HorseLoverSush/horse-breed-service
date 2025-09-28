---
applyTo: "app/api/**/*.py"
---

# API Endpoint Instructions

## Endpoint Responsibilities

API endpoints should be thin wrappers that only handle:
- HTTP request/response formatting
- Input validation (via Pydantic schemas)
- Dependency injection
- Delegating to service layer

**Never put business logic in endpoints** - delegate everything to services.

## Standard Patterns

**Pagination**: Always use consistent pagination parameters:
```python
async def get_resources(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
    active_only: bool = Query(True, description="Return only active records"),
    db: Session = Depends(get_db)
):
```

**Service Delegation**: Always create service instance and delegate:
```python
service = ResourceService(db)
result = service.operation(parameters)
return result
```

**Error Handling**: Let services raise exceptions - global handlers will convert to HTTP responses.

**Response Models**: Always specify Pydantic response models:
```python
@router.get("/", response_model=ResourceListResponse)
@router.post("/", response_model=ResourceResponse, status_code=201)
```

## Pagination Response Format

Always return paginated responses with this structure:
```python
return ResourceListResponse(
    items=items,
    total=total,
    page=page,
    size=size,
    pages=ceil(total / size) if total > 0 else 1
)
```