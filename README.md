# FastAPI Enterprise Template

Enterprise-ready FastAPI starter template with **Clean Architecture** and **Domain-Driven Design (DDD)**.

## Features

- ✅ **Clean Architecture** - Clear separation of concerns
- ✅ **Domain-Driven Design** - Rich domain models with business logic
- ✅ **Use Case Pattern** - Single-purpose use cases
- ✅ **Repository Pattern** - Abstraction over data access
- ✅ **Event-Driven** - Domain events for decoupling
- ✅ **Async/Await** - Full async support throughout
- ✅ **Type Safety** - Type hints and Pydantic validation
- ✅ **Testing** - Comprehensive test infrastructure as a core architectural principle
- ✅ **Docker Ready** - Containerization support

## Quick Start

### Prerequisites

- Python 3.12+
- PDM (Python Dependency Manager)

### Installation

1. **Install PDM** (if not already installed):
   ```bash
   pip install pdm
   ```

2. **Clone and setup the project**:
   ```bash
   cd fastapi_template
   pdm install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run the application**:
   ```bash
   pdm run uvicorn app.main:app --reload
   ```

5. **Visit API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Development

### Using PDM

PDM is used for dependency management. Common commands:

```bash
# Install dependencies
pdm install

# Add a new dependency
pdm add package-name

# Add a development dependency
pdm add -dG dev package-name

# Run commands in PDM environment
pdm run uvicorn app.main:app --reload
pdm run pytest
pdm run black .
pdm run ruff check .
```

### Database Setup

1. **Create database** (PostgreSQL):
   ```bash
   pdm run python scripts/create_db.py
   ```

2. **Run migrations**:
   ```bash
   pdm run alembic upgrade head
   ```

3. **Create new migration**:
   ```bash
   pdm run alembic revision --autogenerate -m "description"
   ```

### Testing

```bash
# Run all tests
pdm run pytest

# Run with coverage
pdm run pytest --cov=app --cov-report=html

# Run specific test file
pdm run pytest app/tests/integration/api/test_items.py
```

**Important Testing Notes:**
- The project uses FastAPI's TestClient for API integration tests, which is synchronous
- Do not use `@pytest.mark.asyncio` decorator when using TestClient
- Avoid using `async/await` with synchronous TestClient operations
- For async testing with httpx, use httpx.AsyncClient with ASGI transport

**Testing Requirements:**
- Testing is a core architectural principle, not optional
- Every new feature must include tests at appropriate layers
- Refactoring must not break existing tests
- All tests must pass before merging any changes
- Code coverage should be maintained at acceptable levels

### Code Quality

```bash
# Format code
pdm run black .

# Lint code
pdm run ruff check .

# Type checking
pdm run mypy app

# Sort imports
pdm run isort .
```

## Project Structure

```
app/
├── domain/              # Domain layer (business logic)
│   ├── entities/        # Domain entities
│   ├── value_objects/   # Value objects
│   ├── events/          # Domain events
│   ├── services/        # Domain services
│   └── exceptions/      # Domain exceptions
├── application/         # Application layer (use cases)
│   ├── use_cases/       # Use cases
│   ├── dto/             # Data Transfer Objects
│   ├── interfaces/      # Repository/Cache interfaces
│   └── events/          # Event handlers
├── infrastructure/      # Infrastructure layer
│   ├── database/        # Database models & sessions
│   ├── repositories/    # Repository implementations
│   ├── cache/           # Cache implementations
│   └── messaging/       # Event bus
├── api/                 # API/Presentation layer
│   └── v1/              # API version 1
│       └── endpoints/   # Route handlers
├── core/                # Core utilities
│   ├── config.py        # Configuration
│   ├── security.py      # Security utilities
│   └── logging.py       # Logging setup
└── tests/               # Test suite
```

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## API Endpoints

### Items
- `POST /api/v1/items/` - Create item
- `GET /api/v1/items/` - List items (paginated)
- `GET /api/v1/items/{id}` - Get item by ID
- `PUT /api/v1/items/{id}` - Update item
- `DELETE /api/v1/items/{id}` - Delete item

### Authentication
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/auth/protected` - Protected route example

### Health
- `GET /api/v1/health/` - Health check
- `GET /api/v1/health/ready` - Readiness probe
- `GET /api/v1/health/live` - Liveness probe

## Environment Variables

See `.env.example` for all available configuration options.

## License

MIT

