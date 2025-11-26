# Resource Construction Algorithm

This document outlines the algorithm for creating new resources in the FastAPI template following the clean architecture pattern. The algorithm is based on the existing `item` resource as a reference implementation and aligns with the Clean Architecture and Domain-Driven Design principles outlined in the architecture document.

## Algorithm Summary

To create a new resource (e.g., `user`, `product`, `order`, etc.), follow these steps in order:

## Step 1: Define Domain Entity

1. Create a domain entity in `app/domain/entities/[resource].py`
2. Extend from `BaseEntity` to inherit common properties (id, created_at, updated_at)
3. Include private attributes for all resource properties
4. Implement property getters for all attributes
5. Add business logic methods that encapsulate domain rules
6. Implement validation methods for business rules
7. Include domain exceptions for specific error cases

**Example structure:**
```python
from datetime import datetime
from app.domain.entities.base import BaseEntity
from app.domain.exceptions.[resource]_exceptions import SpecificException

class [Resource](BaseEntity):
    def __init__(
        self,
        property1: str,
        property2: float,
        optional_property: bool = False,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ):
        super().__init__(id, created_at, updated_at)
        self._validate_property1(property1)
        self._validate_property2(property2)

        self._property1 = property1
        self._property2 = property2
        self._optional_property = optional_property

    @property
    def property1(self) -> str:
        """Property 1 getter"""
        return self._property1

    @property
    def property2(self) -> float:
        """Property 2 getter"""
        return self._property2

    def update_property1(self, new_property1: str) -> None:
        """Update property1 with validation"""
        self._validate_property1(new_property1)
        self._property1 = new_property1
        self.mark_as_updated()

    def _validate_property1(self, property1: str) -> None:
        """Validate property1 business rule"""
        if not property1 or not property1.strip():
            raise SpecificException()
```

## Step 2: Define Value Objects (Optional)

1. If needed, create value objects in `app/domain/value_objects/[value_object].py`
2. Represent immutable domain concepts like Email, Money, Price
3. Include validation and business logic specific to the value object
4. Value objects should be immutable after creation

**Example structure:**
```python
from dataclasses import dataclass
from app.domain.exceptions.base import DomainException

@dataclass(frozen=True)
class Money:
    """Value object for monetary amounts"""
    amount: float
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise DomainException("Amount cannot be negative")

        if len(self.currency) != 3:  # ISO 4217 currency code
            raise DomainException("Currency must be a 3-letter code")
```

## Step 3: Define Domain Services (Optional)

1. If needed, create domain services in `app/domain/services/[domain_service].py`
2. Implement business logic that doesn't belong to a single entity
3. Domain services should be stateless and focused on a specific domain concern
4. Use domain services for operations involving multiple entities or complex business rules

**Example structure:**
```python
from app.domain.entities.user import User

class [Resource]DomainService:
    """Domain service for [resource]-related business logic"""

    @staticmethod
    def calculate_total_cost(items: list[Item], user: User) -> float:
        """Calculate total cost with user-based discounts"""
        base_cost = sum(item.price for item in items)
        discount = user.get_discount_rate() if user.is_premium else 0
        return base_cost * (1 - discount)
```

## Step 4: Define Domain Exceptions

1. Create exceptions in `app/domain/exceptions/[resource]_exceptions.py`
2. Extend from `DomainException` for consistent error handling
3. Define exceptions for specific domain scenarios

**Example structure:**
```python
from app.domain.exceptions.base import DomainException

class [Resource]NotFoundException(DomainException):
    def __init__(self, resource_id: int):
        super().__init__(f"[Resource] with id {resource_id} not found", {"resource_id": resource_id})

class Invalid[Resource]Exception(DomainException):
    def __init__(self, message: str):
        super().__init__(f"Invalid [resource]: {message}")
```

## Step 5: Create Database Model

1. Create ORM model in `app/infrastructure/database/models/[resource].py`
2. Extend from `Base` to inherit common database functionality
3. Define columns matching domain entity properties
4. Include proper constraints and indexes

**Example structure:**
```python
from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from app.infrastructure.database.base import Base

class [Resource]Model(Base):
    __tablename__ = "[resources]"

    id = Column(Integer, primary_key=True, index=True)
    property1 = Column(String(255), nullable=False, index=True)
    property2 = Column(Float, nullable=False)
    optional_property = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

## Step 6: Create Repository Interface

1. Add interface to `app/application/interfaces/repositories.py`
2. Extend from `RepositoryInterface[T]` to get base CRUD operations
3. Add any custom query methods specific to the resource

**Example structure:**
```python
# In repositories.py
from app.domain.entities.[resource] import [Resource]

class [Resource]RepositoryInterface(RepositoryInterface[[Resource]], ABC):
    @abstractmethod
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[[Resource]]:
        """List all [resources] with pagination"""
        pass
```

## Step 7: Create Repository Implementation

1. Create implementation in `app/infrastructure/repositories/[resource]_repository.py`
2. Implement the interface methods using SQLAlchemy
3. Include `_to_domain` and `_to_model` conversion methods
4. Handle database operations with proper error handling

**Example structure:**
```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.application.interfaces.repositories import [Resource]RepositoryInterface
from app.domain.entities.[resource] import [Resource]
from app.infrastructure.database.models.[resource] import [Resource]Model

class SQLAlchemy[Resource]Repository([Resource]RepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: [Resource]Model) -> [Resource]:
        """Convert ORM model to domain entity"""
        return [Resource](
            id=model.id,
            property1=model.property1,
            property2=model.property2,
            optional_property=model.optional_property,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: [Resource]) -> [Resource]Model:
        """Convert domain entity to ORM model"""
        return [Resource]Model(
            id=entity.id,
            property1=entity.property1,
            property2=entity.property2,
            optional_property=entity.optional_property
        )

    async def create(self, entity: [Resource]) -> [Resource]:
        """Create a new [resource]"""
        model = self._to_model(entity)
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return self._to_domain(model)

    # Implement other required methods...
```

## Step 8: Create Data Transfer Objects (DTOs)

1. Create DTOs in `app/application/dto/[resource]_dto.py`
2. Define Create, Update, and Response DTOs
3. Use Pydantic for validation and serialization
4. Include proper typing and configuration

**Example structure:**
```python
from datetime import datetime
from pydantic import BaseModel

class [Resource]CreateDTO(BaseModel):
    """DTO for creating a [resource]"""
    property1: str
    property2: float
    optional_property: bool = False

class [Resource]UpdateDTO(BaseModel):
    """DTO for updating a [resource]"""
    property1: str | None = None
    property2: float | None = None
    optional_property: bool | None = None

class [Resource]DTO(BaseModel):
    """DTO for [resource] response"""
    id: int
    property1: str
    property2: float
    optional_property: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

## Step 9: Create Use Cases

1. Create use case files in `app/application/use_cases/[resources]/`
2. Implement each CRUD operation as a separate use case class
3. Inject repository and other dependencies through constructor
4. Follow the single responsibility principle
5. Handle domain events if required

**Example structure:**
```python
# In create_[resource].py
from app.application.dto.[resource]_dto import [Resource]CreateDTO, [Resource]DTO
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import [Resource]RepositoryInterface
from app.domain.entities.[resource] import [Resource]

class Create[Resource]UseCase:
    def __init__(
        self,
        repository: [Resource]RepositoryInterface,
        event_bus: EventBusInterface
    ):
        self.repository = repository
        self.event_bus = event_bus

    async def execute(self, dto: [Resource]CreateDTO) -> [Resource]DTO:
        """Execute the create [resource] use case"""
        # Create domain entity
        resource = [Resource](
            property1=dto.property1,
            property2=dto.property2,
            optional_property=dto.optional_property
        )

        # Persist entity
        created_resource = await self.repository.create(resource)

        # Publish domain event if needed
        # event = [Resource]CreatedEvent(...)
        # await self.event_bus.publish(event)

        # Convert to DTO
        return [Resource]DTO.model_validate(created_resource)
```

## Step 10: Create Domain Events (Optional)

1. If needed, create domain events in `app/domain/events/[resource]_created.py`
2. Define event classes that extend from `DomainEvent`
3. Use dataclasses with frozen=True to ensure immutability

**Example structure:**
```python
from dataclasses import dataclass
from app.domain.events.base import DomainEvent

@dataclass(frozen=True)
class [Resource]CreatedEvent(DomainEvent):
    """Event raised when a [resource] is created"""
    resource_id: int
    name: str
    created_at: str
```

## Step 11: Create Event Handlers (Optional)

1. Create handlers in `app/application/events/handlers.py` or a dedicated module
2. Implement handlers for domain events
3. Use handlers for side effects like caching, notifications, etc.

**Example structure:**
```python
from app.domain.events.[resource]_created import [Resource]CreatedEvent

async def handle_[resource]_created(event: [Resource]CreatedEvent) -> None:
    """Handle [Resource] created event"""
    # e.g., update cache, send notification, trigger background task
    print(f"[Resource] with ID {event.resource_id} was created")
```

## Step 12: Create API Endpoints

1. Create endpoint file in `app/api/v1/endpoints/[resources].py`
2. Define CRUD routes using FastAPI
3. Use proper HTTP status codes
4. Add request validation through DTOs
5. Handle exceptions appropriately
6. Use dependency injection for use cases

**Example structure:**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, Params
from app.api.dependencies import (
    get_create_[resource]_use_case,
    get_delete_[resource]_use_case,
    get_get_[resource]_use_case,
    get_list_[resources]_use_case,
    get_update_[resource]_use_case,
)
from app.application.dto.[resource]_dto import [Resource]CreateDTO, [Resource]DTO, [Resource]UpdateDTO
from app.application.use_cases.[resources].create_[resource] import Create[Resource]UseCase
# Import other use cases...

router = APIRouter()

@router.post(
    "/",
    response_model=StandardResponse[[Resource]DTO],
    status_code=status.HTTP_201_CREATED
)
async def create_[resource](
    payload: [Resource]CreateDTO,
    use_case: Create[Resource]UseCase = Depends(get_create_[resource]_use_case)
):
    """Create a new [resource]"""
    try:
        result = await use_case.execute(payload)
        return success(result, message="[Resource] created successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Define other endpoints: GET, PUT, DELETE...
```

## Step 13: Add Dependencies

1. Add dependency functions in `app/api/dependencies.py`
2. Create functions for repository and each use case
3. Use proper dependency injection patterns

**Example structure:**
```python
# In dependencies.py
from app.application.interfaces.repositories import [Resource]RepositoryInterface
from app.application.use_cases.[resources].create_[resource] import Create[Resource]UseCase
from app.infrastructure.repositories.[resource]_repository import SQLAlchemy[Resource]Repository

def get_[resource]_repository(db: AsyncSession = Depends(get_db)) -> [Resource]RepositoryInterface:
    """Get [resource] repository"""
    return SQLAlchemy[Resource]Repository(db)

def get_create_[resource]_use_case(
    repository: [Resource]RepositoryInterface = Depends(get_[resource]_repository),
    event_bus: EventBusInterface = Depends(get_event_bus),
) -> Create[Resource]UseCase:
    """Get create [resource] use case"""
    return Create[Resource]UseCase(repository, event_bus)
```

## Step 14: Register Routes

1. Add the new endpoint router to the main API router
2. Usually in `app/api/v1/__init__.py` or similar routing file

## Step 15: Testing Structure - Definition of Done

Exhaustive testing coverage is one of the most important Definition of Done (DOD) criteria of a resource implementation. Testing is not optional but a core requirement that must be implemented at every level for each resource. Create tests for:

1. **Unit Tests**: Domain entity business logic
2. **Integration Tests**: Repository implementations
3. **Use Case Tests**: Business logic orchestration
4. **API Tests**: Endpoint functionality

**Testing Requirements (DOD):**
- Every new resource must include tests at all appropriate layers
- Code coverage should meet project standards
- All tests must pass before merging
- Test-driven development (TDD) is encouraged for complex business logic

## Step 16: Migration

If using database migrations, create and run appropriate Alembic migrations for the new resource table.

## Step 17: Implement Exception Handlers

1. Add exception handlers to `app/utils/error.py` for your domain exceptions
2. Map domain exceptions to appropriate HTTP status codes
3. Use consistent response format with StandardResponse

**Example structure:**
```python
# In app/utils/error.py
from app.domain.exceptions.[resource]_exceptions import [Resource]NotFoundException, Invalid[Resource]Exception

@app.exception_handler([Resource]NotFoundException)
async def [resource]_not_found_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content=StandardResponse(
            success=False, message=str(exc), payload=exc.details
        ).model_dump(),
    )

@app.exception_handler(Invalid[Resource]Exception)
async def invalid_[resource]_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTPStatus.BAD_REQUEST,
        content=StandardResponse(
            success=False, message=str(exc), payload=exc.details
        ).model_dump(),
    )
```

## Architecture Summary

The resource construction algorithm aligns with Clean Architecture and Domain-Driven Design principles:

- **Domain Layer**: Pure business logic with entities, value objects, domain services, and exceptions
- **Application Layer**: Use cases, DTOs, interfaces, and event handlers
- **Infrastructure Layer**: Database models, repositories, cache, and messaging
- **API Layer**: HTTP endpoints and request handling

This ensures:
- Clear separation of concerns
- Testable business logic
- Loose coupling between layers
- Consistent error handling
- Proper dependency injection
- Standardized CRUD operations

The algorithm produces a fully functional, testable resource with all necessary components in the correct architectural layers.
