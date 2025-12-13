# FastAPI Template Project Documentation

## Project Overview
This is a modern, scalable FastAPI server template with clean architecture principles. It implements a 5-layer architecture pattern based on Domain-Driven Design (DDD) that separates concerns and promotes maintainability:

- **Controller Layer**: Handles HTTP requests/responses and API endpoints
- **Service Layer**: Contains business logic and orchestrates operations
- **Repository Layer**: Manages data access operations using concrete implementations
- **Repository Interface Layer**: Defines abstract interfaces for repository operations
- **Model Layer**: Contains domain models with business logic, DTOs, and database entities
- **Mapper Layer**: Handles conversions between different model representations

The project is designed with clean architecture principles, featuring separation of concerns, repository pattern with interfaces, DTOs (Data Transfer Objects) separated from domain models, standardized response format, dependency injection, and proper exception handling.

## Project Structure

```
fastapi-template/
├── .env.example                           # Example environment configuration
├── .gitignore                             # Git ignore rules
├── alembic.ini                            # Alembic configuration file
├── ARCHITECTURE.md                        # Detailed architecture documentation
├── Makefile                               # Make commands for common operations
├── pdm.lock                               # PDM lock file
├── pyproject.toml                         # Project dependencies and configuration
├── README.md                              # Project overview and setup guide
├── responses.py                           # Standardized response format
├── alembic/                               # Database migration scripts
├── app/                                   # Main application source code
│   ├── __init__.py
│   ├── api.py                             # API router configuration
│   ├── config_validator.py
│   ├── main.py                            # Application entry point
│   ├── controller/                        # API controllers (HTTP layer)
│   │   ├── __init__.py
│   │   ├── api.py                         # API router configuration
│   │   ├── auth_controller.py             # Authentication endpoints
│   │   ├── default_controller.py          # Default endpoints
│   │   ├── dependencies/                  # Dependency injection functions
│   │   └── user_controller.py             # User management endpoints
│   ├── core/                              # Core configuration and utilities
│   ├── dependencies/                      # Global dependency functions
│   ├── dto/                               # Legacy DTOs (being migrated to model packages)
│   ├── entities/                          # Legacy database entities (being migrated to model packages)
│   ├── error/                             # Exception handling
│   ├── interface/                         # Abstract interfaces
│   │   └── repositories/                  # Repository interfaces
│   ├── models/                            # Domain-Driven Design models
│   │   ├── __init__.py
│   │   ├── auth/                          # Authentication models
│   │   ├── csr/                           # CSR examples/models
│   │   ├── item/                          # Item models
│   │   ├── permission/                    # Permission models
│   │   ├── policy/                        # Policy models
│   │   ├── refresh_token/                 # Refresh token models
│   │   ├── role/                          # Role models
│   │   ├── user/                          # User models
│   │   ├── base.py                        # Shared SQLAlchemy base
│   │   └── responses.py                   # Standard response format
│   ├── repository/                        # Data access layer (repository implementations)
│   ├── service/                           # Business logic layer
│   └── utils/                             # Utility functions
└── tests/                                 # Test files
    ├── __init__.py
    ├── conftest.py                        # pytest configuration
    ├── integration/                       # Integration tests
    └── unit/                              # Unit tests
```

## Core Technologies and Dependencies

### Runtime Dependencies
- **FastAPI==0.115.6**: Modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints
- **uvicorn[standard]>=0.38.0**: ASGI server for running FastAPI applications
- **passlib[bcrypt]>=1.7.4**: Password hashing library
- **sqlalchemy[asyncio]>=2.0.0**: Python SQL toolkit and ORM with asyncio support
- **asyncpg>=0.29.0**: Fast PostgreSQL driver for Python/asyncio
- **alembic>=1.13.0**: Database migration tool for SQLAlchemy
- **psycopg2-binary>=2.9.0**: PostgreSQL adapter for Python
- **pydantic-settings>=2.0.0**: Settings management using pydantic
- **aiosqlite>=0.19.0**: SQLite adapter for asyncio

### Development Dependencies
- **pytest>=8.0.0**: Testing framework
- **pytest-asyncio>=0.23.0**: Pytest plugin for asyncio
- **httpx>=0.27.0**: HTTP client for making requests in tests
- **pytest-cov>=7.0.0**: Coverage reporting plugin

## Architecture Details

### Layer Responsibilities

#### 1. Controller Layer (`app/controller/`)
- Defines FastAPI routes and endpoints
- Validates HTTP requests and formats responses
- Uses dependency injection to access services
- Translates between API models and domain models
- Handles HTTP-specific concerns

#### 2. Service Layer (`app/service/`)
- Contains business logic and validation rules
- Orchestrates operations between multiple repositories if needed
- Coordinates complex business operations
- Handles transactions and cross-cutting concerns
- Depends on repository interfaces (IUserRepository) rather than concrete implementations

#### 3. Repository Interface Layer (`app/interface/repositories/`)
- Contains abstract interfaces for repository operations
- Follows the Dependency Inversion Principle
- Defines method contracts that implementations must follow
- Allows for dependency injection in the service layer
- Enables testability through mock implementations

#### 4. Repository Layer (`app/repository/`)
- Provides data access methods (CRUD operations)
- Concrete implementations that follow repository interfaces
- Abstracts database interactions from the business logic
- Handles query construction and execution using SQLAlchemy
- Encapsulates data persistence and retrieval logic

#### 5. Model Layer (`app/models/`)
The models package contains four key components for each resource:

##### Domain Model (`domain.py`)
- Contains rich business logic and validation rules
- Defines the core behavior of the entity
- Includes factory methods for creation (e.g., `create` classmethod)
- May include state-changing methods (e.g., `update_info`, `deactivate`)
- Contains validation methods for business rules

##### Data Transfer Object (DTO) (`dto.py`)
- Pydantic models for API request/response validation
- Separate models for creation (`EntityCreate`), updates (`EntityUpdate`), and responses (`Entity`)
- Base models to share common fields
- Deliberately excludes sensitive data when exposing to clients

##### Entity Model (`entity.py`)
- SQLAlchemy ORM models representing database tables
- Maps to database tables using SQLAlchemy annotations
- Defines table schema (columns, relationships, constraints)
- Contains foreign keys and indexes

##### Mapper Model (`mapper.py`)
- Handles conversions between domain models, DTOs, and entities
- The domain is the core - all conversions go through domain models
- Contains static methods for predictable conversions

#### 6. Error Handling (`app/error/`)
- Domain-specific exception classes
- Exception handlers for standardized responses
- Proper HTTP status code mapping

### Key Design Patterns

1. **Dependency Injection**: FastAPI's built-in dependency injection system is used throughout the application
2. **Repository Pattern with Interface Abstraction**: Repository interface abstractions that follow dependency inversion principle
3. **Domain-Driven Design (DDD)**: Rich domain entities with business logic and validation
4. **Mapper Pattern**: Clean separation between domain entities and DTOs using dedicated mapper classes
5. **DTO Pattern**: Separates API contracts from internal domain models
6. **Interface Segregation**: Repository interfaces provide specific contracts for each resource
7. **Factory Pattern**: Domain models include factory methods (e.g., `create` classmethod)
8. **Standardized Response Format**: All API responses follow the same structure

## Configuration Management

The application uses [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for configuration management with the following hierarchy:
1. Environment variables (highest priority)
2. `.env` file values
3. Default values from .env.example (lowest priority)

Configuration includes:
- PostgreSQL database connection settings
- Database URL construction with proper URL encoding

## Database Architecture

### Database Engine
- PostgreSQL with SQLAlchemy async support
- Connection pooling configuration (pool_size=10, max_overflow=20)
- Session management with async_sessionmaker

### Migration System
- Alembic for database migrations
- Automatic migration generation with `alembic revision --autogenerate`

## API Structure

### Standard Response Format (`responses.py`)
All API responses follow a standardized format:
```python
class StandardResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    payload: Optional[T] = None
```

### Example API Flow for User Creation
1. **Controller**: Receives HTTP POST request to `/users/`
2. **Controller**: Validates input using Pydantic models
3. **Controller**: Calls `UserService.create_user()` method
4. **Service**: Performs business validation (e.g., duplicate checks)
5. **Service**: Calls `UserRepository.create_user()` method
6. **Repository**: Handles the data persistence logic
7. **Service**: Transforms the result to the appropriate domain model
8. **Controller**: Formats the response using the standard response pattern
9. **Controller**: Returns the HTTP response to the client

## Error Handling

The system implements a comprehensive exception handling framework:

### Domain Exception Hierarchy
- `DomainException`: Base class for all domain-specific exceptions
- `ValidationException`: For validation errors
- `ResourceNotFoundException`: When a requested resource is not found
- `UnauthorizedException`: For unauthorized access attempts
- `ForbiddenException`: When access is forbidden
- `ConflictException`: For domain conflicts (e.g. duplicate resources)
- `BusinessException`: For business logic violations

### Exception Response Format
All exceptions return a properly formatted response with:
- Appropriate HTTP status codes
- Machine-readable error codes
- Human-readable messages
- Additional details as needed

## Available Commands

### Using Make
- `make help`: Show available commands
- `make install`: Install dependencies with PDM
- `make dev`: Run development server with reload
- `make run`: Run server in production mode
- `make test`: Run tests with pytest
- `make test-cov`: Run tests with coverage
- `make test-verbose`: Run tests in verbose mode
- `make lint`: Basic code format check
- `make clean`: Clean Python cache files
- `make check`: Check project status
- `make shell`: Open Python shell with project environment

### Using PDM directly
- `pdm run uvicorn app.main:app --reload`: Run development server
- `pdm run pytest`: Run tests
- `pdm run alembic upgrade head`: Apply migrations

## Testing Strategy

- **Unit Tests**: Test each layer independently
- **Integration Tests**: Test layer interactions
- **API Tests**: Test complete request/response cycles
- All layers can be mocked for isolated testing

## Development Workflow

1. Create `.env` file based on `.env.example`
2. Install dependencies: `make install` or `pdm install`
3. Run migrations: `pdm run alembic upgrade head`
4. Start development server: `make dev`
5. Run tests: `make test`

## Environment Variables

Required environment variables (found in `.env.example`):
- `DB_USER`: PostgreSQL database user
- `DB_PASSWORD`: PostgreSQL database password
- `DB_HOST`: PostgreSQL database host
- `DB_PORT`: PostgreSQL database port
- `DB_NAME`: PostgreSQL database name

## API Routes

The application currently includes:
- Default routes (root and health check) at `/`
- User management routes at `/users/` with standard CRUD operations
  - `GET /users/` - Get all users
  - `POST /users/` - Create a new user
  - `GET /users/{user_id}` - Get a specific user
  - `PUT /users/{user_id}` - Update a specific user
  - `DELETE /users/{user_id}` - Delete a specific user

## Architectural Improvements

The template has been enhanced with modern architectural best practices:

- **Dependency Inversion Principle**: Services depend on repository interfaces (IUserRepository) rather than concrete implementations
- **Domain-Driven Design (DDD)**: Introduction of rich domain entities with behavior and validation within dedicated model packages
- **Clean Architecture**: Proper separation with interfaces and abstractions
- **Mapper Pattern**: Dedicated mapping layer for conversion between domain entities, DTOs, and database entities
- **Modular Model Packages**: DDD model components grouped together by resource (domain, DTO, entity, mapper)
- **Enhanced Testability**: Services can be properly unit tested with mock repositories
- **Interface-Based Design**: Repository interfaces provide specific contracts for each resource
- **Lazy Configuration Loading**: Database configuration is only loaded when actually needed to avoid import-time errors

## Key Features

- Asynchronous request handling with async/await
- Clean separation of concerns using 5-layer architecture with interface abstractions
- Domain-driven design with rich domain entities organized in modular packages
- Comprehensive error handling with standardized responses
- Type safety with Pydantic models
- Database migration support with Alembic
- Password hashing with bcrypt
- Dependency injection for better testability
- Configuration management with Pydantic Settings
- Proper HTTP status code handling
- Comprehensive documentation of architecture patterns

## File Organization Principles

- Each layer has its own directory with clear separation of concerns
- Repository interfaces are separated from implementations to follow dependency inversion
- Model components (domain, DTO, entity, mapper) are organized in resource-specific packages
- Domain entities contain business logic separate from database entities
- Mappers handle conversion between domain, DTO, and entity layers
- Configuration is centralized in the core directory
- Exception handling is defined with clear domain-specific exceptions
- Repository implementations follow interface contracts for data access logic
- Services contain business logic while depending on repository interfaces (abstractions)