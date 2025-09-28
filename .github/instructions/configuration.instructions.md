---
applyTo: "app/core/config.py,**/.env*,**/settings.py"
---

# Configuration & Environment Instructions

## Security-First Configuration

**Critical Rule**: Never hardcode sensitive values. All configuration must come from environment variables.

## Required Patterns

**Environment Variables**: Use `os.getenv()` with safe defaults for non-sensitive values:
```python
DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")  # No default for sensitive
```

**Validation**: Always validate required environment variables in `__post_init__()`:
```python
def __post_init__(self):
    if not self.DATABASE_PASSWORD:
        raise ValueError("DATABASE_PASSWORD environment variable is required")
    if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
        raise ValueError("SECRET_KEY must be at least 32 characters long")
```

**Settings Import**: Always use the global settings instance:
```python
from app.core.config import settings
# Use settings.DATABASE_URL, not hardcoded values
```

## Environment File Management

- Use `.env.example` as template with placeholder values
- Never commit actual `.env` files
- Document all required environment variables
- Provide sensible defaults for non-sensitive configuration

## Database URL Construction

Handle special characters in passwords by URL encoding:
```python
@property
def DATABASE_URL(self) -> str:
    from urllib.parse import quote_plus
    encoded_password = quote_plus(self.DATABASE_PASSWORD)
    return f"postgresql://{self.DATABASE_USER}:{encoded_password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
```