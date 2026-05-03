# FastAPI Server

An e-commerce for Datasets.

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
- **Entities / Domain**: `app/models/**/domain.py` contains rich domain entities with business rules
- **DTOs**: `app/models/**/dto.py` contains request and response payload models
- **Mappers**: `app/models/**/mapper.py` converts between entities, domain models, and DTOs
- **Use Cases**: `app/use_cases/` contains application business logic interactors
- **Repository Interfaces**: `app/interface/repositories/` defines persistence contracts
- **Framework Adapters**: `app/repository/` contains SQLAlchemy and JSON persistence implementations
- **Delivery / Controllers**: `app/controller/` contains FastAPI route adapters
- **Dependency Wiring**: `app/dependencies/` connects the framework layer to use case and repository boundaries
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
