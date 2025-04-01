# Testing Guide

This guide provides information about testing in DataStream Pro.

## Overview

We use the following testing tools and frameworks:

- pytest for unit and integration tests
- pytest-asyncio for async tests
- pytest-cov for coverage reporting
- pytest-mock for mocking
- pytest-xdist for parallel testing
- hypothesis for property-based testing

## Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_api.py
│   ├── test_models.py
│   └── test_services.py
├── integration/          # Integration tests
│   ├── test_database.py
│   └── test_external.py
└── e2e/                  # End-to-end tests
    └── test_workflows.py
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run specific test function
pytest tests/test_api.py::test_create_dataset

# Run tests with coverage
pytest --cov=app tests/

# Run tests in parallel
pytest -n auto
```

### Test Categories

```bash
# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run e2e tests only
pytest tests/e2e/
```

## Test Fixtures

### Database Fixture

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base

@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///./test.db")

@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()
```

### Client Fixture

```python
# tests/conftest.py
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)
```

### User Fixture

```python
# tests/conftest.py
from app.models.user import User
from app.core.security import get_password_hash

@pytest.fixture
def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user
```

## Unit Tests

### API Tests

```python
# tests/unit/test_api.py
from fastapi.testclient import TestClient
from app.main import app

def test_create_dataset(client, test_user):
    response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Test Dataset",
            "source": "test",
            "description": "Test description"
        },
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Dataset"
    assert data["source"] == "test"
```

### Service Tests

```python
# tests/unit/test_services.py
from app.services.dataset import DatasetService
from app.models.dataset import Dataset

def test_create_dataset(db_session):
    service = DatasetService(db_session)
    dataset = service.create(
        name="Test Dataset",
        source="test",
        description="Test description"
    )
    assert isinstance(dataset, Dataset)
    assert dataset.name == "Test Dataset"
    assert dataset.source == "test"
```

### Model Tests

```python
# tests/unit/test_models.py
from app.models.dataset import Dataset
from datetime import datetime

def test_dataset_creation():
    dataset = Dataset(
        name="Test Dataset",
        source="test",
        description="Test description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert dataset.name == "Test Dataset"
    assert dataset.source == "test"
    assert dataset.description == "Test description"
```

## Integration Tests

### Database Tests

```python
# tests/integration/test_database.py
from app.core.database import get_db
from app.models.dataset import Dataset

def test_database_connection(db_session):
    dataset = Dataset(
        name="Test Dataset",
        source="test",
        description="Test description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(dataset)
    db_session.commit()
    
    result = db_session.query(Dataset).first()
    assert result.name == "Test Dataset"
    assert result.source == "test"
```

### External Service Tests

```python
# tests/integration/test_external.py
import pytest
from app.services.data_collector import DataCollector

@pytest.mark.asyncio
async def test_fetch_climate_data():
    collector = DataCollector()
    data = await collector.fetch_climate_data(
        location="New York",
        start_date="2024-01-01",
        end_date="2024-01-31"
    )
    assert data is not None
    assert len(data) > 0
```

## End-to-End Tests

### Workflow Tests

```python
# tests/e2e/test_workflows.py
def test_data_analysis_workflow(client, test_user):
    # Create dataset
    dataset_response = client.post(
        "/api/v1/datasets",
        json={
            "name": "Test Dataset",
            "source": "test",
            "description": "Test description"
        },
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    dataset_id = dataset_response.json()["id"]
    
    # Add data points
    client.post(
        f"/api/v1/datasets/{dataset_id}/data",
        json={
            "data_points": [
                {
                    "timestamp": "2024-01-01T00:00:00Z",
                    "value": 25.5
                }
            ]
        },
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    
    # Create analysis
    analysis_response = client.post(
        f"/api/v1/datasets/{dataset_id}/analysis",
        json={
            "type": "trend",
            "parameters": {"window": 7}
        },
        headers={"Authorization": f"Bearer {test_user.token}"}
    )
    assert analysis_response.status_code == 200
```

## Property-Based Testing

```python
# tests/unit/test_properties.py
from hypothesis import given, strategies as st
from app.services.data_processor import DataProcessor

@given(st.lists(st.floats(min_value=-100, max_value=100)))
def test_data_normalization(data):
    processor = DataProcessor()
    normalized = processor.normalize(data)
    assert all(0 <= x <= 1 for x in normalized)
    assert len(normalized) == len(data)
```

## Mocking

```python
# tests/unit/test_mocks.py
from unittest.mock import Mock, patch

def test_external_service_mock():
    with patch("app.services.external.ExternalService") as mock_service:
        mock_service.return_value.get_data.return_value = {"test": "data"}
        
        service = ExternalService()
        result = service.get_data()
        assert result == {"test": "data"}
```

## Test Coverage

### Coverage Configuration

```ini
# .coveragerc
[run]
source = app
omit = 
    */tests/*
    */migrations/*
    */__init__.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
    if __name__ == .__main__.:
    pass
```

### Coverage Reports

```bash
# Generate HTML report
pytest --cov=app --cov-report=html tests/

# Generate XML report
pytest --cov=app --cov-report=xml tests/
```

## Performance Testing

```python
# tests/performance/test_performance.py
import pytest
import time
from app.services.data_processor import DataProcessor

def test_processing_performance():
    processor = DataProcessor()
    data = [i for i in range(1000000)]
    
    start_time = time.time()
    result = processor.process(data)
    end_time = time.time()
    
    assert end_time - start_time < 1.0  # Should complete within 1 second
```

## Security Testing

```python
# tests/security/test_security.py
def test_authentication(client):
    response = client.post(
        "/api/v1/auth/token",
        json={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == 401

def test_authorization(client, test_user):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10]

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest --cov=app tests/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

1. Test Organization
   - Group related tests in test classes
   - Use descriptive test names
   - Follow AAA pattern (Arrange, Act, Assert)

2. Test Independence
   - Each test should be independent
   - Use fixtures for setup
   - Clean up after tests

3. Test Coverage
   - Aim for high coverage
   - Focus on critical paths
   - Test edge cases

4. Performance
   - Keep tests fast
   - Use appropriate fixtures
   - Mock external services

5. Maintainability
   - DRY (Don't Repeat Yourself)
   - Use helper functions
   - Keep tests simple

## Troubleshooting

### Common Issues

1. Database Issues
```python
# Reset database between tests
@pytest.fixture(autouse=True)
def reset_db(db_session):
    yield
    db_session.rollback()
```

2. Async Test Issues
```python
# Handle async tests properly
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

3. Mock Issues
```python
# Reset mocks between tests
@pytest.fixture(autouse=True)
def reset_mocks():
    yield
    Mock.reset_mock()
``` 