# Modern Architecture Implementation

## Overview

This FastAPI template now implements **Clean Architecture** with **Domain-Driven Design (DDD)** principles.

## Architecture Layers

### 1. Domain Layer (`app/domain/`)
**Pure business logic - no dependencies on other layers**

- **Entities** (`entities/`): Rich domain models with business logic
- **Value Objects** (`value_objects/`): Immutable domain concepts (Email, Money, Price)
- **Domain Events** (`events/`): Events that represent domain occurrences
- **Domain Services** (`services/`): Business logic that doesn't belong to a single entity
- **Exceptions** (`exceptions/`): Domain-specific exceptions

### 2. Application Layer (`app/application/`)
**Use cases and application logic**

- **Use Cases** (`use_cases/`): Single-purpose classes that orchestrate domain operations
- **DTOs** (`dto/`): Data Transfer Objects for API communication
- **Interfaces** (`interfaces/`): Abstractions for infrastructure (Repository, Cache, EventBus)
- **Events** (`events/`): Application-level event handlers

### 3. Infrastructure Layer (`app/infrastructure/`)
**External concerns and implementations**

- **Database** (`database/`): SQLAlchemy models, sessions, Unit of Work
- **Repositories** (`repositories/`): Concrete implementations of repository interfaces
- **Cache** (`cache/`): Caching implementations (Memory, Redis-ready)
- **Messaging** (`messaging/`): Event bus implementation

### 4. API/Presentation Layer (`app/api/`)
**HTTP endpoints and request handling**

- **Endpoints** (`v1/endpoints/`): FastAPI route handlers
- **Dependencies** (`dependencies.py`): Dependency injection setup
- **Router** (`v1/router.py`): API route aggregation

## Key Patterns

### Use Case Pattern
Each use case is a single class with an `execute` method:

```python
class CreateItemUseCase:
    def __init__(self, repository, event_bus):
        self.repository = repository
        self.event_bus = event_bus
    
    async def execute(self, dto: ItemCreateDTO) -> ItemDTO:
        # Business logic here
        pass
```

### Repository Pattern
Interfaces in application layer, implementations in infrastructure:

```python
# Interface (Application)
class ItemRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, entity: Item) -> Item:
        pass

# Implementation (Infrastructure)
class SQLAlchemyItemRepository(ItemRepositoryInterface):
    async def create(self, entity: Item) -> Item:
        # SQLAlchemy implementation
        pass
```

### Domain Events
Events are raised in use cases and handled asynchronously:

```python
# Domain Event
@dataclass(frozen=True)
class ItemCreatedEvent(DomainEvent):
    item_id: int
    name: str

# Use Case
event = ItemCreatedEvent(item_id=item.id, name=item.name)
await self.event_bus.publish(event)
```

### Exception Handling
Domain exceptions are raised in domain layer and properly mapped to HTTP responses via global exception handlers:

```python
# Domain Exception
class UserAlreadyExistsException(DomainException):
    def __init__(self, identifier: str):
        super().__init__(
            f"User already exists with identifier: {identifier}",
            {"identifier": identifier}
        )

# Exception Handler in app/utils/error.py
@app.exception_handler(UserAlreadyExistsException)
async def user_already_exists_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT,
        content=StandardResponse(
            success=False, message=str(exc), payload=exc.details
        ).model_dump(),
    )
```

## Dependency Flow

```
API Layer
    ↓ (depends on)
Application Layer (Use Cases, Interfaces)
    ↓ (depends on)
Domain Layer (Entities, Events)
    ↑ (implemented by)
Infrastructure Layer (Repositories, Database)
```

## Usage Example

### Creating an Item

1. **API Endpoint** receives request
2. **Dependency Injection** provides use case with dependencies
3. **Use Case** creates domain entity, validates business rules
4. **Repository** persists entity
5. **Event Bus** publishes domain event
6. **Event Handlers** process event (cache, notifications, etc.)

## Testing

- **Unit Tests**: Test domain entities, value objects, use cases in isolation
- **Integration Tests**: Test repository implementations, API endpoints
- **E2E Tests**: Test full flows through API

## Next Steps

1. Add Alembic migrations (update `alembic/env.py` to import from `app.infrastructure.database.base`)
2. Add Redis cache implementation
3. Add background task processing (Celery)
4. Add Prometheus metrics
5. Add OpenTelemetry tracing
6. Add more domain entities and use cases

