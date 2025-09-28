# Contributing to Horse Breed Service

Thank you for your interest in contributing to the Horse Breed Service! This document provides guidelines and instructions for contributing to this FastAPI microservice.

## 🤝 How to Contribute

### Types of Contributions

We welcome the following types of contributions:

- **Bug fixes** - Fix issues in the codebase
- **Feature additions** - Add new functionality
- **Documentation improvements** - Enhance or fix documentation
- **Performance optimizations** - Improve application performance
- **Code quality improvements** - Refactoring, better practices
- **Test coverage improvements** - Add or improve tests

### Before You Start

1. **Check existing issues** to see if your contribution is already being worked on
2. **Create an issue** to discuss major changes before implementing
3. **Fork the repository** and create a feature branch
4. **Read the development guidelines** in `.github/DEVELOPMENT.md`

## 🛠️ Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL database
- Git

### Setup Steps

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/yourusername/horse-breed-service.git
   cd horse-breed-service
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Create database tables:**
   ```bash
   python create_tables.py
   ```

6. **Run tests to ensure everything works:**
   ```bash
   pytest
   ```

## 📋 Contribution Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

### 2. Make Your Changes

- Follow the [code style guidelines](#code-style-guidelines)
- Write tests for new functionality
- Update documentation if needed
- Ensure all tests pass

### 3. Commit Your Changes

Use descriptive commit messages following the conventional commits format:

```bash
git commit -m "feat: add horse breed search functionality"
git commit -m "fix: resolve database connection timeout issue"
git commit -m "docs: update API documentation for breed endpoints"
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots (if applicable)
- Test results

## 📏 Code Style Guidelines

### Python Code Style

- **Follow PEP 8** Python style conventions
- **Use Black** for code formatting: `black .`
- **Use isort** for import sorting: `isort .`
- **Use type hints** for all function parameters and return values
- **Maximum line length:** 88 characters (Black default)

### FastAPI Specific Guidelines

1. **Use Pydantic models** for request/response validation:
   ```python
   class HorseBreedCreate(BaseModel):
       name: str = Field(..., min_length=1, max_length=100)
       origin_country: Optional[str] = None
   ```

2. **Implement proper dependency injection:**
   ```python
   @router.get("/breeds")
   async def get_breeds(db: Session = Depends(get_db)):
       pass
   ```

3. **Use proper HTTP status codes:**
   ```python
   @router.post("/breeds", status_code=201)
   async def create_breed():
       pass
   ```

4. **Add comprehensive docstrings:**
   ```python
   async def get_breeds(skip: int = 0, limit: int = 100):
       """
       Get list of horse breeds with pagination.
       
       Args:
           skip: Number of records to skip
           limit: Maximum number of records to return
           
       Returns:
           List of horse breeds
       """
   ```

### Database Guidelines

1. **Use SQLAlchemy models** with proper column definitions:
   ```python
   class HorseBreed(Base):
       __tablename__ = "horse_breeds"
       
       id = Column(Integer, primary_key=True, index=True)
       name = Column(String(100), unique=True, index=True, nullable=False)
   ```

2. **Implement proper session management:**
   ```python
   def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   ```

## 🧪 Testing Guidelines

### Writing Tests

1. **Test all new functionality** with unit and integration tests
2. **Use pytest** as the testing framework
3. **Mock external dependencies** in tests
4. **Follow AAA pattern** (Arrange, Act, Assert)

### Test Structure

```python
def test_create_horse_breed():
    # Arrange
    breed_data = HorseBreedCreate(name="Test Breed")
    
    # Act
    result = service.create_breed(breed_data)
    
    # Assert
    assert result.name == "Test Breed"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_horse_breeds.py -v
```

## 📚 Documentation Standards

### Code Documentation

- **Add docstrings** to all classes and functions
- **Use Google docstring format:**
  ```python
  def create_breed(breed_data: HorseBreedCreate) -> HorseBreed:
      """
      Create a new horse breed.
      
      Args:
          breed_data: The breed data to create
          
      Returns:
          Created HorseBreed object
          
      Raises:
          ValueError: If breed with same name already exists
      """
  ```

### API Documentation

- **Use FastAPI's automatic documentation features**
- **Add response models** to all endpoints
- **Include example values** in Pydantic models
- **Add proper descriptions** to path parameters and query parameters

## 🔍 Code Review Process

### Pull Request Requirements

Your pull request should:

1. **Pass all tests** and checks
2. **Include appropriate tests** for new functionality
3. **Follow code style guidelines**
4. **Update documentation** if needed
5. **Have a clear description** of changes made

### Review Criteria

Reviewers will check for:

- **Code quality** and adherence to guidelines
- **Test coverage** and quality
- **Documentation** completeness
- **Performance** implications
- **Security** considerations
- **Backward compatibility**

## 🚫 What NOT to Contribute

Please avoid:

- **Breaking changes** without discussion
- **Code without tests**
- **Uncommented complex code**
- **Non-standard coding practices**
- **Large refactoring** without prior discussion
- **Dependencies** not essential to functionality

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, include:

1. **Description** of the issue
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment details** (Python version, OS, etc.)
6. **Error logs** or screenshots

### Feature Requests

When requesting features:

1. **Describe the problem** you're trying to solve
2. **Explain the proposed solution**
3. **Consider alternatives**
4. **Assess the impact** on existing functionality

## 🏆 Recognition

Contributors will be:

- **Listed in the project contributors**
- **Mentioned in release notes** for significant contributions
- **Invited to be maintainers** for consistent, high-quality contributions

## 📞 Getting Help

If you need help:

1. **Check existing documentation** and issues
2. **Create a discussion** for questions
3. **Join our community** channels (if available)
4. **Reach out to maintainers** for guidance

## 📜 Code of Conduct

### Our Standards

- **Be respectful** and inclusive
- **Accept constructive criticism** gracefully
- **Focus on what's best** for the community
- **Show empathy** towards other contributors

### Unacceptable Behavior

- **Harassment** or discrimination
- **Trolling** or inflammatory comments
- **Publishing private information**
- **Any conduct** that could reasonably be considered inappropriate

## 🎉 Thank You!

Thank you for contributing to the Horse Breed Service! Your contributions help make this project better for everyone.

---

*For more detailed technical information, see [DEVELOPMENT.md](.github/DEVELOPMENT.md)*