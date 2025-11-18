# FastAPI Enterprise Template - Project Documentation

## Overview
This is an enterprise-ready FastAPI template that implements Clean Architecture with Domain-Driven Design (DDD) principles. It provides a solid foundation for building scalable, maintainable Python web applications with clear separation of concerns.

## Architecture

### Layers

1. **Domain Layer (`app/domain/`)**
   - Pure business logic with no dependencies on other layers
   - Entities with rich domain models containing business logic
   - Value Objects for immutable domain concepts
   - Domain Events representing domain occurrences
   - Domain Services for business logic that doesn't belong to a single entity
   - Domain Exceptions for domain-specific error handling

2. **Application Layer (`app/application/`)**
   - Use cases orchestrating domain operations
   - Data Transfer Objects (DTOs) for API communication
   - Interfaces defining abstractions for infrastructure
   - Application-level event handlers

3. **Infrastructure Layer (`app/infrastructure/`)**
   - Database models and sessions
   - Concrete implementations of repository interfaces
   - Caching implementations
   - Event bus implementations

4. **API/Presentation Layer (`app/api/`)**
   - HTTP endpoints and request handling
   - FastAPI route handlers
   - Dependency injection setup

### Key Patterns Implemented

**Use Case Pattern**: Each use case is a single class with an `execute` method that orchestrates business operations.

**Repository Pattern**: Interfaces defined in the application layer, with concrete implementations in the infrastructure layer.

**Domain Events**: Events raised in use cases and handled asynchronously via an event bus.

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

## Features

- **Clean Architecture** with clear separation of concerns
- **Domain-Driven Design** with rich domain models
- **Use Case Pattern** for single-purpose use cases
- **Repository Pattern** for abstraction over data access
- **Event-Driven** architecture with domain events
- **Async/Await** full async support throughout
- **Type Safety** with type hints and Pydantic validation
- **Comprehensive Testing** infrastructure
- **Docker Ready** containerization support

## Dependencies & Tech Stack

### Core Framework
- FastAPI: Web framework for building APIs
- uvicorn: ASGI server
- SQLAlchemy: ORM for database operations
- Pydantic: Data validation and settings management

### Database & Persistence
- asyncpg: Async PostgreSQL driver
- aiosqlite: Async SQLite driver
- alembic: Database migration tool
- psycopg2-binary: PostgreSQL database adapter

### Authentication & Security
- python-jose: JWT token handling
- passlib: Password hashing
- bcrypt: Password hashing library

### API Features
- fastapi-pagination: Pagination support
- python-multipart: Multipart form data handling

### Development & Quality
- pytest: Testing framework
- black: Code formatter
- ruff: Fast Python linter
- mypy: Static type checker
- isort: Import sorting

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

## Development Commands

### Using PDM (Python Dependency Manager)
```bash
# Install dependencies
pdm install

# Run the application
pdm run uvicorn app.main:app --reload

# Run tests
pdm run pytest

# Format code
pdm run black .

# Lint code
pdm run ruff check .

# Type checking
pdm run mypy app

# Sort imports
pdm run isort .
```

### Using Makefile
```bash
# Run development server
make run

# Run tests
make test

# Run with coverage
make test-cov

# Format code
make format

# Run linters
make lint

# Check types
make type-check

# Create database
make create-db

# Run migrations
make migrate
```

## Configuration

Application configuration is managed through:
- `app/core/config.py`: Settings class using Pydantic Settings
- `.env` file: Environment variables (copy from `.env.example`)

Key settings include:
- Project name and version
- Secret key for JWT tokens
- CORS origins configuration
- Database URL
- Redis configuration (optional)

## Testing

The project includes comprehensive testing infrastructure:
- Unit tests for domain entities, value objects and use cases
- Integration tests for repository implementations and API endpoints
- End-to-end tests for full API flows

## Deployment

The application is containerization-ready with Docker support. It follows 12-factor app principles and is designed to run in containerized environments like Kubernetes.

## Security

- JWT-based authentication
- Password hashing with bcrypt
- Input validation through Pydantic models
- CORS configuration
- Dependency security through proper isolation

## Monitoring & Observability

- Built-in health check endpoints
- Prometheus metrics support
- Structured logging
- Error handling with proper HTTP status codes

## Next Steps

1. Add Redis cache implementation for production use
2. Add background task processing (Celery)
3. Add OpenTelemetry tracing
4. Add more domain entities and use cases
5. Implement Authentication layer from scratch in a modern way (as per TODO)
6. Add comprehensive documentation and API examples