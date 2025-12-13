# 5-Layer Architecture: Controller-Service-Repository-Domain-Mapper

## Overview

This FastAPI application implements a clean 5-layer architecture pattern based on Domain-Driven Design (DDD) principles that separates concerns and promotes maintainability:

- **Controller Layer**: Handles HTTP requests/responses and API endpoints
- **Service Layer**: Contains business logic and orchestrates operations
- **Repository Layer**: Manages data access operations using interfaces and implementations
- **Model Layer**: Contains domain models with business logic, DTOs, and database entities
- **Mapper Layer**: Handles conversions between different model representations

## Layer Responsibilities

### Controller Layer (`app/controller/`)
- Defines FastAPI routes and endpoints using APIRouter
- Validates HTTP requests using Pydantic models
- Formats HTTP responses following standardized response patterns
- Uses dependency injection to access services
- Handles HTTP-specific concerns (authentication, authorization)
- Translates between API models and domain models

### Service Layer (`app/service/`)
- Contains business logic and validation rules
- Orchestrates operations between multiple repositories when needed
- Coordinates complex business operations
- Depends on repository interfaces (e.g., `IUserRepository`) rather than concrete implementations
- Handles transactions and cross-cutting business concerns
- Implements the Dependency Inversion Principle by depending on abstractions

### Repository Layer (`app/repository/`)
- Provides data access methods (CRUD operations and custom queries)
- Abstracts database interactions from the business logic
- Implements repository interfaces defined in `app/interface/repositories/`
- Handles query construction and execution using SQLAlchemy
- Encapsulates data persistence and retrieval logic

### Repository Interface Layer (`app/interface/repositories/`)
- Contains abstract interfaces for repository operations
- Follows the Dependency Inversion Principle
- Defines method contracts that implementations must follow
- Allows for dependency injection in the service layer
- Enables testability through mock implementations

### Model Layer (`app/models/`)
The models package contains four key components for each resource:

#### Domain Model (`domain.py`)
- Contains rich business logic and validation rules
- Defines the core behavior of the entity
- Includes factory methods for creation (e.g., `create` classmethod)
- May include state-changing methods (e.g., `update_info`, `deactivate`)
- Contains validation methods for business rules

#### Data Transfer Object (DTO) (`dto.py`)
- Pydantic models for API request/response validation
- Separate models for creation (`EntityCreate`), updates (`EntityUpdate`), and responses (`Entity`)
- Base models to share common fields
- Deliberately excludes sensitive data when exposing to clients

#### Entity Model (`entity.py`)
- SQLAlchemy ORM models representing database tables
- Maps to database tables using SQLAlchemy annotations
- Defines table schema (columns, relationships, constraints)
- Contains foreign keys and indexes

### Mapper Layer (`mapper.py`)
- Handles conversions between domain models, DTOs, and entities
- The domain is the core - all conversions go through domain models
- Contains static methods for predictable conversions:
  - `from_dto(dto) -> Domain`
  - `from_entity(entity) -> Domain`
  - `to_dto(domain) -> DTO`
  - `to_entity(domain) -> Entity`
  - `update_from_dto(dto, domain) -> Domain`
  - `update_entity(domain, entity) -> Entity`

## Benefits of This Architecture

1. **Separation of Concerns**: Each layer has a specific, well-defined responsibility
2. **Testability**: Each layer can be unit tested independently using mocks
3. **Maintainability**: Changes in one layer don't necessarily affect others
4. **Flexibility**: Different implementations can be swapped (e.g., different databases)
5. **Domain-Centric**: Business logic remains central and unaffected by external changes
6. **Type Safety**: Full type checking through Pydantic and proper typing
7. **Dependency Inversion**: Services depend on abstractions, not concrete implementations
8. **Consistency**: Standardized approach across all resources

## Example Flow for User Creation

1. **Controller**: Receives HTTP POST request to `/users/` with `UserCreate` DTO
2. **Controller**: Validates input using Pydantic models, applies authentication
3. **Controller**: Calls `UserService.create_user()` method via dependency injection
4. **Service**: Performs business validation (e.g., duplicate checks with repository)
5. **Service**: Calls `IUserRepository.create_user()` method using interface
6. **Repository Implementation**: Creates domain entity via `UserDomain.create()` for validation
7. **Repository**: Uses `UserMapper` to convert domain to entity for database storage
8. **Repository**: Executes SQLAlchemy operation to persist to database
9. **Repository**: Uses `UserMapper` to convert entity back to DTO for return
10. **Service**: Returns the DTO with sensitive data appropriately excluded
11. **Controller**: Formats response using standardized response pattern
12. **Controller**: Returns HTTP response to client

## Complete File Structure

```
app/
├── controller/
│   ├── __init__.py
│   ├── dependencies/
│   │   ├── __init__.py
│   │   └── user_dependencies.py    # Dependency injection functions
│   └── user_controller.py          # Controller layer
├── service/
│   ├── __init__.py
│   └── user_service.py             # Service layer
├── interface/
│   └── repositories/
│       ├── __init__.py
│       └── user_repository_interface.py  # Repository interfaces
├── repository/
│   ├── __init__.py
│   └── user_repository.py          # Repository implementations
├── models/
│   ├── __init__.py
│   ├── base.py                     # Shared SQLAlchemy base
│   └── user/
│       ├── __init__.py
│       ├── domain.py               # Domain model with business logic
│       ├── dto.py                  # Data Transfer Objects
│       ├── entity.py               # Database entity models
│       └── mapper.py               # Conversion logic between models
├── core/
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   └── database.py                 # Database connection and session management
├── error/
│   └── exceptions.py               # Domain-specific exceptions
├── utils/
│   └── ...                         # Utility functions
├── main.py                         # Application entry point
└── responses.py                    # Standard response format
```

## Dependency Injection

The architecture uses FastAPI's built-in dependency injection system with a hierarchical pattern:

- Controllers depend on Services via dependency functions
- Services depend on Repository Interfaces (not concrete implementations)
- Repository implementations depend on database sessions
- Dependencies are resolved using FastAPI's `Depends()` function
- This promotes loose coupling and testability

## Key Design Patterns

1. **Dependency Injection**: FastAPI's built-in dependency injection system used throughout
2. **Repository Pattern with Interface Abstraction**: Repository interface abstractions that follow dependency inversion principle
3. **Domain-Driven Design (DDD)**: Rich domain entities with business logic and validation
4. **Mapper Pattern**: Clean separation between domain entities and DTOs using dedicated mapper classes
5. **DTO Pattern**: Separates API contracts from internal domain models
6. **Interface Segregation**: Repository interfaces provide specific contracts for each resource
7. **Factory Pattern**: Domain models include factory methods (e.g., `create` classmethod)

## Testing Strategy

- **Unit Tests**: Test each layer independently with mocks for dependencies
- **Integration Tests**: Test layer interactions and database operations
- **API Tests**: Test complete request/response cycles
- **Repository Tests**: Test data access operations with database
- **Service Tests**: Test business logic with mock repositories
- **Controller Tests**: Test API endpoints with mock services

## Best Practices Followed

- Single Responsibility Principle: Each layer and component has one clear purpose
- Dependency Inversion Principle: High-level modules depend on abstractions
- Clean separation between business logic and infrastructure concerns
- Consistent error handling across all layers
- Standardized response format for all API endpoints
- Type safety using Pydantic models and proper type hints
- Domain-centric approach with business logic in domain models
- Interface-based design for loose coupling and testability