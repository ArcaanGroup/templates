# FastAPI Enterprise Template - Onboarding Guide

Welcome to the FastAPI Enterprise Template project! This guide will help you get started from scratch and progress to mastering the architecture and development practices.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Project Structure Overview](#project-structure-overview)
4. [Understanding the Architecture](#understanding-the-architecture)
5. [Development Workflow](#development-workflow)
6. [Testing Strategy](#testing-strategy)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Topics](#advanced-topics)

## Prerequisites

Before starting with this project, you should have:

- **Python 3.12+**: Verify with `python --version`
- **PDM (Python Dependency Manager)**: Install with `pip install pdm`
- **Git**: For version control
- **Docker (optional)**: For containerized deployment
- Basic understanding of:
  - **FastAPI**: Modern Python web framework
  - **Async/Await**: Python asynchronous programming
  - **SQLAlchemy**: Python SQL toolkit and ORM
  - **Pydantic**: Data validation library
  - **Clean Architecture & DDD**: Architectural patterns (covered in detail below)

## Initial Setup

### 1. Clone and Set Up the Project

```bash
# Clone the repository
git clone <repository-url>
cd fastapi_template

# Install dependencies
pdm install

# Configure environment
cp .env.example .env
# Edit .env with your settings (database URL, secret keys, etc.)

# Run the application
pdm run uvicorn app.main:app --reload
```

### 2. Verify the Setup

After running the application, visit:
- API Documentation: http://localhost:8000/docs
- API Redoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/api/v1/health/

### 3. Run Tests

```bash
# Run all tests
pdm run pytest

# Run with coverage
pdm run pytest --cov=app --cov-report=html
```

### 4. Run Code Quality Checks

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

## Project Structure Overview

The project follows Clean Architecture and Domain-Driven Design (DDD) principles:

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

## Understanding the Architecture

### Clean Architecture Layers

#### 1. Domain Layer (`app/domain/`)
This is the core of your application. It contains:
- **Entities**: Rich domain models with business logic
- **Value Objects**: Immutable domain concepts (e.g., Email, Money)
- **Domain Events**: Events that represent domain occurrences
- **Domain Services**: Business logic that doesn't belong to a single entity
- **Exceptions**: Domain-specific exceptions

**Key Principle**: This layer is pure business logic with no dependencies on other layers.

#### 2. Application Layer (`app/application/`)
This orchestrates the business logic:
- **Use Cases**: Single-purpose classes that execute specific business operations
- **DTOs**: Data Transfer Objects for API communication
- **Interfaces**: Abstractions for infrastructure (Repository, Cache, EventBus)
- **Events**: Application-level event handlers

**Key Principle**: This layer coordinates between the domain and infrastructure.

#### 3. Infrastructure Layer (`app/infrastructure/`)
This handles external concerns:
- **Database**: SQLAlchemy models and sessions
- **Repositories**: Concrete implementations of repository interfaces
- **Cache**: Caching implementations (Memory, Redis-ready)
- **Messaging**: Event bus implementation

**Key Principle**: This layer implements the interfaces defined in the application layer.

#### 4. API/Presentation Layer (`app/api/`)
This handles HTTP requests and responses:
- **Endpoints**: FastAPI route handlers
- **Dependencies**: Dependency injection setup
- **Router**: API route aggregation

**Key Principle**: This is the entry point for external systems.

### Key Design Patterns

#### Use Case Pattern
Each business operation is encapsulated in a single-purpose use case class:

```python
from app.application.interfaces.repository import ItemRepositoryInterface
from app.application.dto.item import ItemCreateDTO
from app.domain.entities.item import Item

class CreateItemUseCase:
    def __init__(self, repository: ItemRepositoryInterface):
        self.repository = repository

    async def execute(self, dto: ItemCreateDTO) -> Item:
        # Business logic here
        item = Item(name=dto.name, description=dto.description)
        # Additional validation, business rules, etc.
        return await self.repository.create(item)
```

#### Repository Pattern
Abstracts data access with interfaces in the application layer and implementations in the infrastructure layer:

```python
# Interface (Application)
from app.application.interfaces.repository import RepositoryInterface
from app.domain.entities.item import Item

class ItemRepositoryInterface(RepositoryInterface[Item]):
    ...

# Implementation (Infrastructure)
from app.infrastructure.database.models.item import ItemModel
from app.domain.entities.item import Item

class SQLAlchemyItemRepository(ItemRepositoryInterface):
    async def create(self, entity: Item) -> Item:
        # SQLAlchemy implementation
        db_item = ItemModel(name=entity.name, description=entity.description)
        self.session.add(db_item)
        await self.session.commit()
        await self.session.refresh(db_item)
        return Item(id=db_item.id, name=db_item.name, description=db_item.description)
```

#### Domain Events
Events represent occurrences in the domain and enable loose coupling:

```python
from dataclasses import dataclass
from app.domain.events.base import DomainEvent

@dataclass(frozen=True)
class ItemCreatedEvent(DomainEvent):
    item_id: int
    name: str

# Use case publishes event
from app.application.interfaces.event_bus import EventBusInterface

class CreateItemUseCase:
    def __init__(self, repository, event_bus: EventBusInterface):
        self.repository = repository
        self.event_bus = event_bus

    async def execute(self, dto):
        # Create item
        item = Item(name=dto.name)
        created_item = await self.repository.create(item)
        
        # Publish event
        event = ItemCreatedEvent(item_id=created_item.id, name=created_item.name)
        await self.event_bus.publish(event)
```

## Development Workflow

### Adding a New Feature

1. **Define Domain Entities**: Start by modeling the business concepts in the domain layer
2. **Create Use Case**: Implement the business logic in the application layer
3. **Define Repository Interface**: Create interfaces in the application layer
4. **Implement Repository**: Add concrete implementation in the infrastructure layer
5. **Create API Endpoint**: Expose functionality through API endpoints
6. **Write Tests**: Cover all layers with appropriate tests

### Example: Adding a User Feature

1. **Create Domain Entity** (`app/domain/entities/user.py`):
```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: Optional[int] = None
    name: str
    email: str

    def validate_email(self):
        # Business rule
        if "@" not in self.email:
            raise ValueError("Invalid email format")
```

2. **Create Use Case** (`app/application/use_cases/user/create_user.py`):
```python
from app.application.dto.user import UserCreateDTO
from app.domain.entities.user import User
from app.application.interfaces.repository import UserRepositoryInterface

class CreateUserUseCase:
    def __init__(self, repository: UserRepositoryInterface):
        self.repository = repository

    async def execute(self, dto: UserCreateDTO) -> User:
        user = User(name=dto.name, email=dto.email)
        user.validate_email()
        return await self.repository.create(user)
```

3. **Create DTO** (`app/application/dto/user.py`):
```python
from pydantic import BaseModel

class UserCreateDTO(BaseModel):
    name: str
    email: str
```

4. **Update API Endpoint** (`app/api/v1/endpoints/users.py`):
```python
from fastapi import APIRouter, Depends
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.api.dependencies import get_create_user_use_case

router = APIRouter()

@router.post("/users/")
async def create_user(
    dto: UserCreateDTO,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case)
):
    user = await use_case.execute(dto)
    return user
```

### Dependency Injection Configuration

All dependencies are configured in `app/api/dependencies.py`:

```python
from app.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from app.application.use_cases.user.create_user import CreateUserUseCase

def get_user_repository() -> UserRepositoryInterface:
    return SQLAlchemyUserRepository(session=get_db_session())

def get_create_user_use_case() -> CreateUserUseCase:
    return CreateUserUseCase(repository=get_user_repository())
```

## Testing Strategy

### Test Organization

Tests are organized in layers matching the architecture:

```
tests/
├── unit/
│   ├── domain/
│   │   └── test_user_entity.py
│   └── application/
│       └── test_create_user_use_case.py
├── integration/
│   ├── repository/
│   │   └── test_sqlalchemy_user_repository.py
│   └── api/
│       └── test_user_endpoints.py
└── e2e/
    └── test_user_flow.py
```

### Writing Tests

#### Unit Tests (Domain Layer)
Test business logic in isolation:

```python
import pytest
from app.domain.entities.user import User

def test_user_valid_email():
    user = User(name="John Doe", email="john@example.com")
    user.validate_email()  # Should not raise an exception

def test_user_invalid_email():
    user = User(name="John Doe", email="invalid-email")
    with pytest.raises(ValueError, match="Invalid email format"):
        user.validate_email()
```

#### Unit Tests (Application Layer)
Test use cases with mocked dependencies:

```python
import pytest
from unittest.mock import AsyncMock
from app.application.use_cases.user.create_user import CreateUserUseCase
from app.application.dto.user import UserCreateDTO

@pytest.mark.asyncio
async def test_create_user_use_case():
    mock_repository = AsyncMock()
    use_case = CreateUserUseCase(repository=mock_repository)
    
    dto = UserCreateDTO(name="John Doe", email="john@example.com")
    await use_case.execute(dto)
    
    mock_repository.create.assert_called_once()
```

#### Integration Tests
Test integrations between components:

```python
import pytest
from app.infrastructure.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository

@pytest.mark.asyncio
async def test_create_user_integration(get_db_session):
    repository = SQLAlchemyUserRepository(session=get_db_session)
    user = User(name="John Doe", email="john@example.com")
    
    created_user = await repository.create(user)
    
    assert created_user.id is not None
    assert created_user.name == "John Doe"
```

## Best Practices

### 1. Follow Clean Architecture Principles
- Keep business logic in the Domain layer
- Depend on abstractions, not concretions
- Ensure dependencies flow inward (from outer layers toward Domain)

### 2. Domain-Driven Design
- Model entities with rich behavior
- Use Value Objects for immutable concepts
- Represent domain occurrences as Domain Events
- Encapsulate business rules within entities

### 3. Use Case Design
- Each use case should have a single responsibility
- Use DTOs to transfer data between layers
- Avoid business logic in use cases (delegate to domain entities)

### 4. Repository Pattern
- Define repository interfaces in the application layer
- Implement concrete repositories in the infrastructure layer
- Return domain entities from repository methods, not database models

### 5. Error Handling
- Use domain-specific exceptions for business rule violations
- Handle infrastructure errors at the infrastructure layer
- Use HTTP status codes appropriately in API layer

### 6. Async Programming
- Use async/await throughout the application
- Avoid blocking operations in async code
- Use asyncio for concurrent operations

### 7. Testing
- Write tests for each architectural layer
- Test business logic thoroughly in unit tests
- Use integration tests to verify component collaboration
- Mock external dependencies in unit tests

### 8. Code Quality
- Follow PEP 8 style guidelines
- Use type hints consistently
- Run code quality tools (black, ruff, mypy) regularly
- Use meaningful names for variables, functions, and classes

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you installed dependencies with `pdm install`
2. **Database Connection**: Verify your database URL in `.env`
3. **Port Already in Use**: Change the port in your server configuration
4. **Type Errors**: Run `pdm run mypy app` to check for type issues
5. **Test Failures**: Check if database migrations are applied

### Debugging Tips

1. **Use Logging**: The project has structured logging configured in `app/core/logging.py`
2. **Debug Endpoints**: Add logging to your endpoints for debugging
3. **Database Sessions**: Be careful with database session management in async code
4. **Dependency Injection**: Verify that your dependency injection configuration is correct

### Running Commands

Common development commands (use these instead of direct Python execution):

```bash
# Development server
pdm run uvicorn app.main:app --reload

# Run tests
pdm run pytest

# Format code
pdm run black .

# Lint code
pdm run ruff check .

# Type checking
pdm run mypy app

# Create database
pdm run python scripts/create_db.py

# Run migrations
pdm run alembic upgrade head
```

## Advanced Topics

### Event-Driven Architecture

The template supports domain events for loose coupling between components:

1. Define domain events in `app/domain/events/`
2. Publish events from use cases
3. Create event handlers in `app/application/events/`
4. Configure the event bus in `app/api/dependencies.py`

### Caching

The infrastructure layer is prepared for caching:

1. Implement cache interfaces in `app/infrastructure/cache/`
2. Use memory cache for development
3. Add Redis implementation for production
4. Use caching strategy in use cases where appropriate

### Background Tasks

Plan for background task processing using Celery:

1. Add Celery configuration to the project
2. Implement task queue pattern
3. Use background tasks for long-running operations

### Monitoring & Observability

- **Logging**: Structured logging is configured
- **Metrics**: Prometheus metrics can be added
- **Tracing**: OpenTelemetry tracing can be implemented
- **Health Checks**: Built-in health check endpoints

### Security

1. **Authentication**: JWT-based authentication is implemented
2. **Authorization**: Role-based access control can be added
3. **Input Validation**: Pydantic models provide validation
4. **Secret Management**: Use environment variables for secrets

## Next Steps for Mastery

1. **Deep Dive into Domain Models**: Work on implementing several domain models with rich business logic
2. **Event-Driven Design**: Practice creating complex domain events and event handlers
3. **Testing Strategies**: Master unit, integration, and end-to-end testing approaches
4. **Performance Optimization**: Learn to profile and optimize async code
5. **Deployment**: Study Docker configuration and deployment strategies
6. **CI/CD**: Implement continuous integration and deployment pipelines

### Contributing to the Project

1. Fork the repository
2. Create a feature branch
3. Make your changes following the architecture patterns
4. Write tests for your changes
5. Run all code quality checks
6. Submit a pull request with a clear description

This project follows modern Python development practices and Clean Architecture principles. Take time to understand these patterns as they form the foundation for maintaining a scalable, testable, and maintainable codebase.