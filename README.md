# FastAPI Server

A modern, scalable FastAPI server with clean architecture.

## Features

- FastAPI framework with async support
- Clean architecture with separation of concerns
- Repository pattern with interfaces
- DTOs (Data Transfer Objects) separated from domain models
- Standardized response format
- Dependency injection
- Proper exception handling

## Clean Architecture with PostgreSQL + SQLAlchemy + Alembic

The project follows clean architecture principles with clear separation of concerns:

### Architecture
- **Entities**: `app/entities/` contains SQLAlchemy ORM models and base classes
- **DTOs**: `app/dto/` contains Data Transfer Objects for API communication
- **Repository Interface**: `app/repository/user_repository.py` defines the contract
- **PostgreSQL Implementation**: `app/infrastructure/postgresql_user_repository.py`
- **In-Memory Implementation**: `app/infrastructure/in_memory_user_repository.py` for testing
- **Infrastructure**: `app/infrastructure/` contains configuration and database engine setup
- **Migrations**: `alembic/` contains database migration scripts

### Configuration

The application uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management with the following hierarchy:
1. Environment variables (highest priority)
2. `.env` file values
3. Default values from .env.example (lowest priority)

Required configuration is validated at startup.

### Running with PostgreSQL

1. Create your `.env` file based on `.env.example`:
```bash
cp .env.example .env
# Edit .env to add your database credentials
```

2. Run the application:
```bash
pdm run uvicorn app.main:app --reload
```

### Running Migrations
```bash
# Apply all migrations
pdm run alembic upgrade head

# Create new migration after model changes
export ALEMBIC_CMD=revision
pdm run alembic revision --autogenerate -m "Description of changes"
```