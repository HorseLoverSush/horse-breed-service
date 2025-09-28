# 🐎 Horse Breed Service

A high-performance FastAPI microservice for managing horse breed information with full CRUD operations, built following modern Python development practices.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.117.1-009688.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🚀 Features

- **RESTful API** with full CRUD operations for horse breeds
- **FastAPI framework** with automatic API documentation
- **PostgreSQL database** integration with SQLAlchemy ORM
- **Pydantic models** for request/response validation
- **Pagination and search** functionality
- **Comprehensive error handling** with proper HTTP status codes
- **🔒 Enterprise Security** with PII data filtering and environment-based configuration
- **📊 Enhanced Logging** with structured JSON logs, correlation IDs, and security filtering
- **📈 Monitoring & Metrics** with health checks, performance tracking, and system metrics
- **🛡️ Security Compliance** with sensitive data protection and secure configuration management
- **Modular architecture** following FastAPI best practices
- **Type hints** throughout the codebase
- **Comprehensive documentation** and examples

## 📋 API Endpoints

### Horse Breed Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/breeds` | List all horse breeds with pagination and search |
| `GET` | `/api/v1/breeds/{id}` | Get a specific horse breed by ID |
| `POST` | `/api/v1/breeds` | Create a new horse breed |
| `PUT` | `/api/v1/breeds/{id}` | Update an existing horse breed |
| `DELETE` | `/api/v1/breeds/{id}` | Soft delete a horse breed |

### System Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check endpoint with system status |
| `GET` | `/monitoring/health` | Detailed health check with database connectivity |
| `GET` | `/monitoring/metrics` | Application performance metrics and statistics |
| `GET` | `/monitoring/logs` | Recent application logs (filtered for security) |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |
| `GET` | `/redoc` | Alternative API documentation (ReDoc) |

## 🛠️ Technology Stack

- **Backend Framework:** FastAPI 0.117.1
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Validation:** Pydantic v2
- **ASGI Server:** Uvicorn
- **Security:** Environment-based configuration, PII filtering, CORS protection
- **Logging:** Enhanced JSON logging with correlation IDs and security filtering
- **Monitoring:** Built-in health checks, metrics collection, and system monitoring
- **Testing:** pytest with async support (200+ tests including security validation)
- **Code Quality:** Black, isort, flake8
- **Type Checking:** Python type hints

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
│   │           ├── horse_breeds.py  # Horse breed endpoints
│   │           └── monitoring.py    # Monitoring and health endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Environment-based configuration
│   │   ├── enhanced_logging.py # Structured logging with PII filtering
│   │   ├── error_handlers.py   # Global error handling
│   │   ├── exceptions.py       # Custom exception classes
│   │   └── middleware.py       # Security and request tracking middleware
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
│   ├── __init__.py
│   ├── fixtures/               # Test fixtures and utilities
│   ├── unit/                   # Unit tests (147 total)
│   └── integration/            # Integration tests (17 total)
├── logs/                       # Application logs (JSON structured)
├── .github/
│   ├── DEVELOPMENT.md          # Development guidelines
│   └── CONTRIBUTING.md         # Contribution guidelines
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
├── .env                       # Environment variables (secure, git-ignored)
├── .env.example               # Environment variables template
├── run.py                     # Application runner
├── start_service.py           # Production service starter
├── create_tables.py           # Database table creation script
├── test_pii_filtering.py      # PII filtering validation script
├── SECURITY_PII_CHECKLIST.md  # Security compliance checklist
├── MONITORING_GUIDE.md        # Monitoring and observability guide
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database server
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/HorseLoverSush/horse-breed-service.git
   cd horse-breed-service
   ```

2. **Create and activate virtual environment:**
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
- **Application:** http://localhost:8000
- **Interactive API docs:** http://localhost:8000/docs
- **Alternative docs:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/health
- **Detailed monitoring:** http://localhost:8000/monitoring/health
- **System metrics:** http://localhost:8000/monitoring/metrics

## 🔒 Security & Monitoring

### 🛡️ Security Features

**Environment-Based Configuration:**
- All sensitive configuration stored in environment variables
- No hardcoded secrets or credentials in code
- Required environment variable validation at startup
- Secure default configurations

**PII Data Protection:**
- Automatic filtering of sensitive data in logs (passwords, emails, SSN, credit cards, etc.)
- Sensitive HTTP headers filtered from logs (Authorization, API keys, etc.)
- Query parameter sanitization for sensitive data
- Configurable sensitive field detection

**Security Validation:**
```bash
# Test PII filtering system
python test_pii_filtering.py

# Verify no sensitive data in logs
powershell "Get-Content 'logs\horse_breed_service.log' | Select-Object -Last 10"
```

### 📊 Monitoring & Observability

**Enhanced Logging:**
- Structured JSON logs with correlation IDs
- Request/response tracking with performance metrics
- Error tracking with stack traces and context
- Business event logging with security tagging

**Health Monitoring:**
- Database connectivity checks
- System resource monitoring (CPU, memory)
- Application performance metrics
- Custom health indicators

**Monitoring Endpoints:**
```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system monitoring
curl http://localhost:8000/monitoring/health

# Performance metrics
curl http://localhost:8000/monitoring/metrics

# Recent logs (security filtered)
curl http://localhost:8000/monitoring/logs
```

**Log Analysis:**
```bash
# View recent application logs
tail -f logs/horse_breed_service.log

# Search for specific events
grep "ERROR" logs/horse_breed_service.log

# Monitor request patterns
grep "Request completed" logs/horse_breed_service.log | tail -20
```

## 🔧 Configuration

### 🔒 Secure Environment-Based Configuration

The application uses environment variables for all configuration, ensuring no secrets are hardcoded. Copy `.env.example` to `.env` and update with your secure values:

```bash
# Database Configuration (Required - No defaults for security)
DATABASE_HOST=localhost
DATABASE_PORT=5433
DATABASE_NAME=horse_breeds_db
DATABASE_USER=horselover
DATABASE_PASSWORD=your_secure_database_password_here
AUTO_CREATE_TABLES=true
RECREATE_TABLES=false

# Security Configuration (Required - Minimum 32 characters)
SECRET_KEY=your_super_secure_secret_key_at_least_32_chars_long_for_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_PREFIX=/api/v1
PROJECT_NAME=Horse Breed Service
PROJECT_VERSION=1.0.0
DEBUG=true

# Server Configuration
HOST=0.0.0.0
PORT=8000
RELOAD=true

# CORS Settings (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 🛡️ Security Features

- **Environment Variables**: All sensitive configuration moved to environment variables
- **PII Filtering**: Automatic filtering of sensitive data in logs (passwords, emails, tokens, etc.)
- **Secure Headers**: Sensitive HTTP headers are filtered from logs
- **Query Parameter Filtering**: Sensitive URL parameters are automatically sanitized
- **Configuration Validation**: Required environment variables are validated at startup

## 🧪 Comprehensive Testing

The project includes a robust testing framework with unit tests, integration tests, and comprehensive error handling validation.

### Test Structure

```
tests/
├── fixtures/
│   └── base_fixtures.py          # Shared test fixtures
├── unit/                          # Unit tests (147 total)
│   ├── api/
│   │   ├── test_horse_breed_endpoints.py    # API endpoint tests
│   │   └── test_monitoring_endpoints.py     # Monitoring endpoint tests
│   └── core/
│       ├── test_exceptions.py               # Exception handling tests (36 tests - ✅ ALL PASSING)
│       ├── test_error_handlers.py           # Error handler tests
│       └── test_enhanced_logging.py         # Enhanced logging tests
└── integration/                   # Integration tests (17 total)
    └── test_system_integration.py           # End-to-end system tests
```

### Test Categories

#### ✅ Exception Handling Tests (36/36 passing)
- **Custom Exception Classes**: Complete test coverage for all 9 exception types
- **HTTP Status Mapping**: Validation of proper HTTP status code mapping
- **Error Response Format**: Consistent error response structure testing
- **Performance Testing**: Exception creation and handling performance validation

#### 🔧 Unit Tests (147 total - various status)
- **API Endpoint Tests**: FastAPI route testing with mocked dependencies
- **Service Layer Tests**: Business logic validation
- **Enhanced Logging Tests**: Structured JSON logging with correlation IDs
- **Error Handler Tests**: Global exception handling pipeline
- **Monitoring Tests**: Health checks and metrics collection

#### 🚧 Integration Tests (7/17 passing)
- **System Integration**: End-to-end API flow testing
- **Database Integration**: Transaction handling and rollback testing
- **Logging Integration**: ✅ Structured logging pipeline validation
- **Monitoring Integration**: ✅ Health check and metrics integration
- **Performance Integration**: ✅ Response time and memory monitoring
- **Security Integration**: CORS, error disclosure, and request limits
- **Stress Testing**: Concurrent request handling and resource cleanup

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test categories
pytest tests/unit/core/test_exceptions.py -v     # Exception tests (36 passing)
pytest tests/unit/ -v                           # All unit tests (147 total)
pytest tests/integration/ -v                    # Integration tests (17 total)

# Run tests with virtual environment 
.\horse-breed-service-env\Scripts\python.exe -m pytest tests/unit/core/test_exceptions.py -v

# Run specific integration tests
pytest tests/integration/test_system_integration.py::TestLoggingIntegration -v

# Run with detailed output and timing
pytest -v --tb=short --durations=10
```

### Test Features

- **Async Testing**: Full async/await support with pytest-asyncio
- **Mocking**: Comprehensive mocking with pytest-mock
- **Fixtures**: Reusable test fixtures for database, API clients, and test data
- **Performance Testing**: Built-in performance benchmarks and timing
- **Error Simulation**: Comprehensive error condition testing
- **Logging Validation**: Structured logging output verification
- **Database Testing**: Transaction rollback and concurrent operation testing

## 📖 API Usage Examples

### List Horse Breeds with Pagination

```bash
curl -X GET "http://localhost:8000/api/v1/breeds?page=1&size=10&search=arabian"
```

### Get a Specific Horse Breed

```bash
curl -X GET "http://localhost:8000/api/v1/breeds/1"
```

### Create a New Horse Breed

```bash
curl -X POST "http://localhost:8000/api/v1/breeds" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Arabian",
    "origin_country": "Arabian Peninsula",
    "description": "One of the oldest horse breeds in the world",
    "average_height": "14.1-15.1 hands",
    "average_weight": "800-1000 lbs",
    "temperament": "Intelligent, spirited, gentle",
    "primary_use": "Riding, endurance"
  }'
```

### Update a Horse Breed

```bash
curl -X PUT "http://localhost:8000/api/v1/breeds/1" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Updated description for Arabian horse breed"
  }'
```

### Delete a Horse Breed

```bash
curl -X DELETE "http://localhost:8000/api/v1/breeds/1"
```

## 🐳 Docker Deployment

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

## 📊 Database Schema

### Horse Breed Table

```sql
CREATE TABLE horse_breeds (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    origin_country VARCHAR(100),
    description TEXT,
    average_height VARCHAR(50),
    average_weight VARCHAR(50),
    temperament VARCHAR(200),
    primary_use VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](.github/CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes following our [Development Guidelines](.github/DEVELOPMENT.md)
4. Run tests: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation:** Check the `.github/` folder for detailed guides
- **Issues:** Create an issue on GitHub for bug reports or feature requests
- **Discussions:** Use GitHub Discussions for questions and community support

## 🎯 Roadmap

### ✅ Completed Features
- [x] **Enhanced Logging System** - JSON structured logs with correlation IDs and PII filtering
- [x] **Security Compliance** - Environment-based configuration and sensitive data protection
- [x] **Monitoring & Health Checks** - Comprehensive application and system monitoring
- [x] **Error Handling** - Robust exception handling with proper HTTP status codes
- [x] **Testing Framework** - 200+ tests including unit, integration, and security validation

### 🚧 In Progress
- [ ] Add authentication and authorization (JWT-based)
- [ ] Implement caching with Redis
- [ ] Create Docker Compose setup with PostgreSQL

### 📋 Planned Features
- [ ] Add API rate limiting and throttling
- [ ] Implement breed image upload functionality
- [ ] Add breed comparison features
- [ ] Create admin dashboard
- [ ] Add real-time notifications
- [ ] Implement advanced search with filters

## 🏆 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [Pydantic](https://docs.pydantic.dev/) for data validation
- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM
- [PostgreSQL](https://www.postgresql.org/) for the database

---

Made with ❤️ for horse enthusiasts and developers alike!
horse-breed-service
