# Development Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- Virtual environment (recommended)

## Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/datastream-pro.git
cd datastream-pro
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

5. Copy environment variables:
```bash
cp .env.example .env
```

6. Update `.env` with your configuration.

## Project Structure

```
datastream-pro/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── tests/
├── docs/
├── scripts/
└── config/
```

## Development Workflow

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:
```bash
git add .
git commit -m "feat: add your feature"
```

3. Push your changes:
```bash
git push origin feature/your-feature-name
```

4. Create a Pull Request on GitHub.

## Code Style

We follow PEP 8 style guide and use the following tools:

- Black for code formatting
- Flake8 for linting
- isort for import sorting
- mypy for type checking

Run code style checks:
```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8

# Type checking
mypy .
```

## Testing

We use pytest for testing. Run tests:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run specific test function
pytest tests/test_api.py::test_create_dataset
```

## Documentation

We use Sphinx for documentation. Build docs:
```bash
cd docs
make html
```

View documentation:
```bash
open docs/_build/html/index.html
```

## Database Migrations

We use Alembic for database migrations:

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## API Development

1. Define your schema in `app/schemas/`
2. Create your model in `app/models/`
3. Implement your service in `app/services/`
4. Create your API endpoint in `app/api/v1/`
5. Add tests in `tests/`

Example:

```python
# app/schemas/dataset.py
from pydantic import BaseModel

class DatasetCreate(BaseModel):
    name: str
    source: str
    description: str | None = None

# app/models/dataset.py
from sqlalchemy import Column, String, DateTime
from app.core.database import Base

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    source = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

# app/services/dataset.py
from app.models.dataset import Dataset
from app.schemas.dataset import DatasetCreate

class DatasetService:
    def create(self, data: DatasetCreate) -> Dataset:
        # Implementation
        pass

# app/api/v1/datasets.py
from fastapi import APIRouter, Depends
from app.schemas.dataset import DatasetCreate
from app.services.dataset import DatasetService

router = APIRouter()

@router.post("/")
def create_dataset(
    data: DatasetCreate,
    service: DatasetService = Depends()
):
    return service.create(data)

# tests/test_datasets.py
def test_create_dataset():
    # Test implementation
    pass
```

## Debugging

1. Use VS Code debugger:
   - Set breakpoints in your code
   - Press F5 to start debugging
   - Use debug console to inspect variables

2. Use logging:
```python
import logging

logger = logging.getLogger(__name__)

def your_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

3. Use pytest debugger:
```bash
pytest --pdb
```

## Performance Optimization

1. Use async/await for I/O operations
2. Implement caching where appropriate
3. Use database indexes
4. Profile your code:
```bash
python -m cProfile -o profile.stats your_script.py
python -m pstats profile.stats
```

## Security

1. Follow OWASP guidelines
2. Use parameterized queries
3. Validate input data
4. Implement rate limiting
5. Use secure headers
6. Regular security audits

## Deployment

1. Build Docker image:
```bash
docker build -t datastream-pro .
```

2. Run container:
```bash
docker run -p 8000:8000 datastream-pro
```

3. Deploy to production:
```bash
# Update dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start application
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## Troubleshooting

Common issues and solutions:

1. Database connection issues:
   - Check database URL in .env
   - Verify database is running
   - Check network connectivity

2. Authentication issues:
   - Verify API key/token
   - Check token expiration
   - Validate credentials

3. Performance issues:
   - Check database indexes
   - Monitor resource usage
   - Profile code

## Support

For support:
- Open an issue on GitHub
- Contact maintainers
- Check documentation
- Join community chat 