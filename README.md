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
| `GET` | `/health` | Health check endpoint |
| `GET` | `/docs` | Interactive API documentation (Swagger UI) |
| `GET` | `/redoc` | Alternative API documentation (ReDoc) |

## 🛠️ Technology Stack

- **Backend Framework:** FastAPI 0.117.1
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Validation:** Pydantic v2
- **ASGI Server:** Uvicorn
- **Testing:** pytest with async support
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
├── .github/
│   ├── DEVELOPMENT.md          # Development guidelines
│   └── CONTRIBUTING.md         # Contribution guidelines
├── requirements.txt            # Python dependencies
├── pyproject.toml             # Project configuration
├── .env.example               # Environment variables template
├── run.py                     # Application runner
├── create_tables.py           # Database table creation script
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

## 🔧 Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and update with your values:

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
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_horse_breeds.py -v
```

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

- [ ] Add authentication and authorization
- [ ] Implement caching with Redis
- [ ] Add comprehensive logging
- [ ] Create Docker Compose setup
- [ ] Add API rate limiting
- [ ] Implement breed image upload functionality
- [ ] Add breed comparison features
- [ ] Create admin dashboard

## 🏆 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the amazing web framework
- [Pydantic](https://docs.pydantic.dev/) for data validation
- [SQLAlchemy](https://www.sqlalchemy.org/) for the ORM
- [PostgreSQL](https://www.postgresql.org/) for the database

---

Made with ❤️ for horse enthusiasts and developers alike!
horse-breed-service
