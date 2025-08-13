# Lumen Backend Testing Guide

This document explains how to run and write tests for the Lumen photography platform backend.

## Overview

The testing strategy includes:

- **Unit Tests**: Fast, isolated tests for individual functions and classes
- **Integration Tests**: Tests for API endpoints, database operations, and component interactions
- **Test Coverage**: Aiming for 70%+ code coverage
- **Continuous Testing**: Automated test runs on code changes

## Test Structure

```
tests/
├── README.md                      # This file
├── __init__.py                    # Tests package
├── conftest.py                    # Global pytest fixtures
├── unit/                          # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_user_model.py        # User model tests
│   ├── test_photo_model.py       # Photo model tests
│   └── test_auth_middleware.py   # Auth middleware tests
├── integration/                   # Integration tests (slower, with dependencies)
│   ├── __init__.py
│   ├── test_auth_endpoints.py    # Authentication API tests
│   ├── test_photo_endpoints.py   # Photo API tests
│   └── test_database_integration.py # Database operation tests
└── fixtures/                     # Test data and utilities
    └── __init__.py
```

## Running Tests

### Prerequisites

1. Install test dependencies:
   ```bash
   cd lumen-gcp/backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Ensure you're in the backend directory:
   ```bash
   cd lumen-gcp/backend
   ```

### Basic Test Execution

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_user_model.py

# Run specific test class
pytest tests/unit/test_user_model.py::TestUserModel

# Run specific test method
pytest tests/unit/test_user_model.py::TestUserModel::test_user_model_creation
```

### Test Filtering by Markers

```bash
# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only authentication tests
pytest -m auth

# Run only photo-related tests
pytest -m photos

# Exclude slow tests
pytest -m "not slow"

# Run external service tests only
pytest -m external
```

### Coverage Reports

```bash
# Run tests with coverage report
pytest --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# View HTML report (opens in browser)
open htmlcov/index.html
```

### Parallel Testing

```bash
# Install pytest-xdist for parallel execution
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Test Categories and Markers

### Available Markers

- `@pytest.mark.unit` - Fast unit tests (< 1 second each)
- `@pytest.mark.integration` - Integration tests with dependencies
- `@pytest.mark.auth` - Authentication and authorization tests
- `@pytest.mark.photos` - Photo management functionality tests
- `@pytest.mark.slow` - Slow tests (> 5 seconds each)
- `@pytest.mark.external` - Tests requiring external services

### When to Use Each Type

#### Unit Tests (`@pytest.mark.unit`)
- Individual function behavior
- Model validation and business logic
- Utility functions
- Isolated class methods
- No database or external service dependencies

#### Integration Tests (`@pytest.mark.integration`)
- API endpoint functionality
- Database operations with real data
- Authentication flows
- File upload and processing
- Service layer interactions

## Test Fixtures

### Available Fixtures (from `conftest.py`)

#### Database Fixtures
- `db_session` - Fresh database session for each test
- `sample_user_data` - Example user data dictionary
- `sample_photo_data` - Example photo data dictionary

#### Authentication Fixtures  
- `mock_firebase_auth` - Mocked Firebase authentication
- `auth_headers` - Authorization headers for API tests
- `mock_cloud_storage` - Mocked Google Cloud Storage

#### API Testing Fixtures
- `client` - FastAPI test client with database override
- `async_client` - Async test client for async endpoints
- `mock_file_upload` - Mock file upload for photo tests

### Using Fixtures in Tests

```python
def test_user_creation(db_session, sample_user_data):
    """Example of using fixtures in tests."""
    user = User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == sample_user_data["email"]

def test_api_endpoint(client, auth_headers):
    """Example of API testing with fixtures."""
    response = client.get("/api/v1/users/profile", headers=auth_headers)
    assert response.status_code == 200
```

## Writing New Tests

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `TestClassName`
- Test methods: `test_specific_behavior`
- Use descriptive names that explain what is being tested

### Example Unit Test

```python
import pytest
from app.models.user import User, CreateUserRequest

@pytest.mark.unit
class TestUserModel:
    """Test User model functionality."""
    
    def test_user_creation_with_valid_data(self, db_session, sample_user_data):
        """Test creating user with valid data succeeds."""
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.created_at is not None
        assert user.firebase_uid == sample_user_data["firebase_uid"]
    
    def test_user_validation_fails_with_invalid_email(self):
        """Test user validation fails with invalid email."""
        with pytest.raises(ValueError):
            CreateUserRequest(
                handle="testuser",
                display_name="Test User",
                email="invalid-email",  # Invalid format
                city_id=1,
                user_type="photographer"
            )
```

### Example Integration Test

```python
import pytest
from unittest.mock import patch

@pytest.mark.integration
@pytest.mark.auth
class TestAuthEndpoints:
    """Test authentication API endpoints."""
    
    @patch('app.auth_middleware.get_current_user')
    def test_protected_endpoint_success(self, mock_auth, client):
        """Test protected endpoint with valid authentication."""
        # Mock authenticated user
        mock_auth.return_value = {
            'uid': 'test-uid',
            'email': 'test@example.com'
        }
        
        response = client.get("/api/v1/auth/profile")
        
        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == "test-uid"
        assert data["email"] == "test@example.com"
    
    def test_protected_endpoint_unauthorized(self, client):
        """Test protected endpoint without authentication fails."""
        response = client.get("/api/v1/auth/profile")
        assert response.status_code == 401
```

## Mocking External Services

### Firebase Authentication

```python
@patch('app.auth_middleware.firebase_config')
def test_with_mocked_firebase(mock_firebase):
    mock_firebase.verify_token.return_value = {
        'uid': 'test-uid',
        'email': 'test@example.com'
    }
    # Test code here
```

### Google Cloud Storage

```python
@patch('app.services.photo_service.storage_client')
def test_photo_upload(mock_storage, mock_file_upload):
    mock_bucket = Mock()
    mock_blob = Mock()
    mock_storage.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    
    # Test photo upload logic
```

## Database Testing

### Test Data Isolation

Each test gets a fresh database session that is rolled back after the test:

```python
def test_user_operations(db_session):
    """Each test starts with clean database."""
    # Create test data
    user = User(firebase_uid="test", email="test@example.com", ...)
    db_session.add(user)
    db_session.commit()
    
    # Test operations
    found_user = db_session.query(User).filter_by(firebase_uid="test").first()
    assert found_user is not None
    
    # Data automatically cleaned up after test
```

### Testing Relationships

```python
def test_user_photo_relationship(db_session):
    """Test database relationships work correctly."""
    user = User(...)
    db_session.add(user)
    db_session.flush()  # Get user.id
    
    photo = Photo(user_id=user.id, title="Test Photo")
    db_session.add(photo)
    db_session.commit()
    
    # Test relationship loading
    assert len(user.photos) == 1
    assert photo.user == user
```

## Continuous Integration

### GitHub Actions

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Scheduled nightly runs

### Local Pre-commit Testing

```bash
# Run quick tests before committing
pytest -m unit

# Run full test suite before pushing
pytest --cov=app --cov-fail-under=70
```

## Debugging Tests

### Running Single Test with Debug Output

```bash
# Run with maximum verbosity and no capture
pytest -vvv -s tests/unit/test_user_model.py::TestUserModel::test_specific_method

# Run with pdb debugger on failure
pytest --pdb tests/unit/test_user_model.py

# Run with debug logging
pytest --log-level=DEBUG tests/unit/test_user_model.py
```

### Common Issues and Solutions

#### 1. Import Errors
```bash
# Make sure you're in the backend directory
cd lumen-gcp/backend

# Install packages in development mode
pip install -e .
```

#### 2. Database Connection Issues
```bash
# Check database is accessible
python -c "from app.database.connection import get_db; print('DB OK')"
```

#### 3. Firebase Mock Issues
```bash
# Ensure Firebase is properly mocked in tests
# Check conftest.py fixtures are being used
```

## Test Performance

### Benchmarking

```bash
# Time test execution
time pytest tests/unit/

# Profile test performance
pytest --durations=10  # Show 10 slowest tests
```

### Optimization Tips

1. Use unit tests for business logic (faster)
2. Use integration tests for API/database interactions (slower)
3. Mock external services (Firebase, Cloud Storage)
4. Use database transactions for test isolation
5. Parallelize test execution for large test suites

## Contributing Tests

### Test Requirements for New Features

1. **Unit tests** for all business logic
2. **Integration tests** for API endpoints
3. **Authentication tests** for protected endpoints
4. **Error handling tests** for edge cases
5. **Performance tests** for critical paths

### Test Review Checklist

- [ ] Tests cover happy path and edge cases
- [ ] Appropriate markers are applied
- [ ] External services are properly mocked
- [ ] Test data is isolated and cleaned up
- [ ] Tests are deterministic (not flaky)
- [ ] Test names clearly describe what's being tested

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)