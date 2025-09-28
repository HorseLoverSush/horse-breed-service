# Horse Breed Microservice

A FastAPI-based microservice for managing horse breed information. This service provides RESTful APIs to perform CRUD operations on horse breeds with comprehensive breed data including physical characteristics, temperament, and origin information.

## Features

- **CRUD Operations**: Create, Read, Update, Delete horse breeds
- **Search Functionality**: Search breeds by name with partial matching
- **Data Validation**: Comprehensive input validation using Pydantic models
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Health Checks**: Built-in health monitoring endpoints
- **Containerized**: Docker support for easy deployment
- **Test Coverage**: Comprehensive test suite with pytest

## API Endpoints

### Core Endpoints

- `GET /` - Root endpoint with service information
- `GET /health` - Health check endpoint
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation

### Horse Breed Endpoints

- `GET /api/v1/horse-breeds/` - Get all horse breeds
- `GET /api/v1/horse-breeds/{id}` - Get a specific horse breed by ID
- `GET /api/v1/horse-breeds/search?name={name}` - Search breeds by name
- `POST /api/v1/horse-breeds/` - Create a new horse breed
- `PUT /api/v1/horse-breeds/{id}` - Update an existing horse breed
- `DELETE /api/v1/horse-breeds/{id}` - Delete a horse breed

## Data Model

Each horse breed contains the following information:

```json
{
  "id": 1,
  "name": "Arabian",
  "origin": "Arabian Peninsula",
  "height_min": 14.1,
  "height_max": 15.1,
  "weight_min": 800,
  "weight_max": 1000,
  "temperament": "spirited",
  "colors": ["chestnut", "bay", "black", "gray"],
  "description": "Known for their distinctive head shape and high tail carriage"
}
```

### Temperament Types
- `calm` - Calm and steady temperament
- `energetic` - High energy and active
- `spirited` - Spirited and lively
- `gentle` - Gentle and docile
- `aggressive` - More aggressive temperament

## Quick Start

### Prerequisites

- Python 3.11+
- pip or Docker

### Running Locally

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd horse-breed-service
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Access the API**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Running with Docker

1. **Build and run with docker-compose**
   ```bash
   docker-compose up --build
   ```

2. **Or build and run manually**
   ```bash
   docker build -t horse-breed-service .
   docker run -p 8000:8000 horse-breed-service
   ```

## Development

### Project Structure

```
horse-breed-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── horse_breeds.py  # API endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   └── horse_breed.py   # Data models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── horse_breed.py   # Pydantic schemas
│   └── services/
│       ├── __init__.py
│       └── horse_breed_service.py  # Business logic
├── tests/
│   ├── __init__.py
│   └── test_horse_breeds.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_horse_breeds.py -v
```

### API Usage Examples

#### Get all breeds
```bash
curl http://localhost:8000/api/v1/horse-breeds/
```

#### Get specific breed
```bash
curl http://localhost:8000/api/v1/horse-breeds/1
```

#### Search breeds
```bash
curl "http://localhost:8000/api/v1/horse-breeds/search?name=Arabian"
```

#### Create new breed
```bash
curl -X POST http://localhost:8000/api/v1/horse-breeds/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mustang",
    "origin": "United States",
    "height_min": 14.0,
    "height_max": 15.0,
    "weight_min": 700,
    "weight_max": 900,
    "temperament": "spirited",
    "colors": ["bay", "black", "chestnut"],
    "description": "Wild horses of the American West"
  }'
```

#### Update breed
```bash
curl -X PUT http://localhost:8000/api/v1/horse-breeds/1 \
  -H "Content-Type: application/json" \
  -d '{"description": "Updated description"}'
```

#### Delete breed
```bash
curl -X DELETE http://localhost:8000/api/v1/horse-breeds/1
```

## Sample Data

The service comes pre-loaded with sample data for three horse breeds:
- **Arabian** - Spirited breed from Arabian Peninsula
- **Thoroughbred** - Racing breed from England  
- **Clydesdale** - Draft horse from Scotland

## Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Pydantic** - Data validation and settings management
- **Uvicorn** - ASGI server implementation
- **pytest** - Testing framework
- **Docker** - Containerization

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
