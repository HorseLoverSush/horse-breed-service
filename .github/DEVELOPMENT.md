# FastAPI Horse Breed Service - Development Guidelines

## 📋 Overview

This repository contains a FastAPI microservice for managing horse breed information. The service provides RESTful APIs for CRUD operations on horse breeds with PostgreSQL database integration.

## 🏗️ Project Structure

```
horse-breed-service/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── api.py          # API router configuration
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── horse_breeds.py  # Horse breed endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Application configuration
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py         # Database connection and session
│   ├── models/
│   │   ├── __init__.py
│   │   └── horse_breed.py      # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── horse_breed.py      # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── horse_breed_service.py  # Business logic
├── tests/
│   └── __init__.py
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
├── .env.example               # Environment variables template
├── run.py                     # Application runner
├── create_tables.py           # Database table creation script
└── README.md
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** database server
3. **Git** for version control

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd horse-breed-service
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your actual database credentials
   ```

5. **Create database tables:**
   ```bash
   python create_tables.py
   ```

6. **Run the application:**
   ```bash
   python run.py
   ```

The API will be available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🛠️ Development Guidelines

### Code Style

- **Follow PEP 8** Python style guide
- **Use Black** for code formatting: `black .`
- **Use isort** for import sorting: `isort .`
- **Use type hints** for all function parameters and return values
- **Write docstrings** for all classes and functions

### FastAPI Best Practices

1. **Use Pydantic models** for request/response validation
2. **Implement proper dependency injection** with `Depends()`
3. **Use SQLAlchemy ORM** for database operations
4. **Separate business logic** into service classes
5. **Use APIRouter** for modular endpoint organization
6. **Implement proper error handling** with HTTPException
7. **Add comprehensive API documentation** with docstrings

### Database Guidelines

1. **Use SQLAlchemy models** for database schema
2. **Implement proper database sessions** with dependency injection
3. **Use database migrations** for schema changes
4. **Implement soft deletes** instead of hard deletes
5. **Add proper indexes** for performance optimization

### Testing Guidelines

1. **Write unit tests** for all service methods
2. **Write integration tests** for API endpoints
3. **Use pytest** as testing framework
4. **Mock external dependencies** in tests
5. **Maintain test coverage** above 80%

### API Design Guidelines

1. **Follow RESTful conventions:**
   - GET `/breeds` - List all breeds
   - GET `/breeds/{id}` - Get specific breed
   - POST `/breeds` - Create new breed
   - PUT `/breeds/{id}` - Update existing breed
   - DELETE `/breeds/{id}` - Delete breed

2. **Use appropriate HTTP status codes:**
   - 200 - OK (successful GET, PUT)
   - 201 - Created (successful POST)
   - 204 - No Content (successful DELETE)
   - 400 - Bad Request (validation errors)
   - 404 - Not Found (resource doesn't exist)
   - 422 - Unprocessable Entity (Pydantic validation errors)

3. **Implement pagination** for list endpoints
4. **Add search and filtering** capabilities
5. **Use consistent response formats**

## 🔧 Configuration

### Environment Variables

The application uses the following environment variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/horse_breeds_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=horse_breeds_db
DATABASE_USER=username
DATABASE_PASSWORD=password

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=Horse Breed Service
PROJECT_VERSION=1.0.0
DEBUG=True

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=True

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Settings
ALLOWED_HOSTS=["*"]
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

## 📚 API Documentation

### Horse Breed Endpoints

#### GET /api/v1/breeds
List all horse breeds with pagination and search.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `size` (int): Page size (default: 10, max: 100)
- `search` (str): Search term for name or origin country
- `active_only` (bool): Return only active breeds (default: true)

#### GET /api/v1/breeds/{breed_id}
Get a specific horse breed by ID.

#### POST /api/v1/breeds
Create a new horse breed.

#### PUT /api/v1/breeds/{breed_id}
Update an existing horse breed.

#### DELETE /api/v1/breeds/{breed_id}
Soft delete a horse breed.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_horse_breeds.py

# Run with verbose output
pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Test configuration and fixtures
├── test_horse_breeds_api.py # API endpoint tests
├── test_horse_breeds_service.py # Service layer tests
└── test_models.py           # Model tests
```

## 🚢 Deployment

### Docker Deployment

1. **Create Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "run.py"]
```

2. **Build and run:**
```bash
docker build -t horse-breed-service .
docker run -p 8000:8000 horse-breed-service
```

### Production Considerations

1. **Use environment-specific configurations**
2. **Implement proper logging**
3. **Set up health checks**
4. **Use a reverse proxy** (nginx)
5. **Implement rate limiting**
6. **Set up monitoring and alerting**
7. **Use database connection pooling**
8. **Implement proper security headers**

## 📝 Contributing

1. **Fork the repository**
2. **Create a feature branch:** `git checkout -b feature/new-feature`
3. **Make your changes** following the guidelines above
4. **Write tests** for your changes
5. **Run tests:** `pytest`
6. **Format code:** `black . && isort .`
7. **Commit changes:** `git commit -m "Add new feature"`
8. **Push to branch:** `git push origin feature/new-feature`
9. **Create Pull Request**

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Issues:**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Import Errors:**
   - Verify virtual environment is activated
   - Check all dependencies are installed
   - Verify Python path configuration

3. **Port Already in Use:**
   - Change PORT in `.env` file
   - Kill existing process: `lsof -ti:8000 | xargs kill`

### Logging

The application uses Python's logging module. Logs are output to console by default. For production, configure file-based logging.

## 📞 Support

For questions or issues:
1. Check existing GitHub issues
2. Create new issue with detailed description
3. Include error logs and environment details

---

*This documentation follows FastAPI best practices as outlined in the [official FastAPI documentation](https://fastapi.tiangolo.com/).*