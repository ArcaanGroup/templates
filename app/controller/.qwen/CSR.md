# Controller-Service-Repository (CSR) Layer Documentation

## Overview
The Controller-Service-Repository (CSR) pattern represents the core architectural layers that handle business logic and data flow in the application. This pattern ensures separation of concerns by dividing responsibilities across multiple distinct layers as part of a 5-layer architecture based on Domain-Driven Design (DDD):

- **Controller Layer**: Handles HTTP requests/responses and API endpoints
- **Service Layer**: Contains business logic and orchestrates operations
- **Repository Interface Layer**: Defines abstract interfaces for repository operations
- **Repository Layer**: Manages data access operations using concrete implementations
- **Model Layer**: Contains domain models with business logic, DTOs, and database entities
- **Mapper Layer**: Handles conversions between different model representations

## Layer Responsibilities

### Controller Layer (`app/controller/`)
The controller layer is the HTTP interface of the application:
- Defines FastAPI routes and endpoints using APIRouter
- Validates HTTP requests using Pydantic models
- Formats HTTP responses following standardized response patterns
- Uses dependency injection to access services
- Handles HTTP-specific concerns (authentication, authorization)
- Translates between API models and domain models

**Key Characteristics:**
- Thin layer focused on HTTP concerns
- No business logic implementation
- Uses dependencies defined in `app/controller/dependencies/`
- Returns standardized responses using the `StandardResponse` pattern

### Service Layer (`app/service/`)
The service layer contains the core business logic:
- Implements business logic and validation rules
- Orchestrates operations between multiple repositories when needed
- Coordinates complex business operations
- Depends on repository interfaces (e.g., `IUserRepository`) rather than concrete implementations
- Handles transactions and cross-cutting business concerns
- Acts as the intermediary between HTTP requests and data operations

**Key Characteristics:**
- Focuses on business logic and validation
- Uses dependency injection for repository access
- Follows the Dependency Inversion Principle by depending on interfaces
- Handles business-specific exceptions (e.g., `ConflictException`, `ResourceNotFoundException`)

### Repository Layer (`app/repository/`)
The repository layer manages data access:
- Provides data access methods (CRUD operations and custom queries)
- Abstracts database interactions from the business logic
- Implements repository interfaces defined in `app/interface/repositories/`
- Handles query construction and execution using SQLAlchemy
- Encapsulates data persistence and retrieval logic
- Follows the Repository pattern with interface abstractions

**Key Characteristics:**
- Contains data access logic only
- Implements interface contracts defined in `app/interface/repositories/`
- Uses SQLAlchemy for database operations
- Converts between domain models and database entities using mappers
- Handles database-specific concerns

### Repository Interfaces (`app/interface/repositories/`)
The interface layer defines contracts for data access:
- Contains abstract interfaces for repository operations
- Follows the Dependency Inversion Principle
- Defines method contracts that implementations must follow
- Allows for dependency injection in the service layer
- Enables testability through mock implementations

**Key Characteristics:**
- Uses ABC (Abstract Base Classes) to define contracts
- Each interface extends `ABC` and uses `@abstractmethod`
- Method signatures match the implementations
- Enables loose coupling between service and repository layers

### Dependencies (`app/controller/dependencies/`)
The dependencies layer manages dependency injection:
- Contains factory functions for creating service and repository instances
- Handles database session injection
- Uses FastAPI's `Depends()` for dependency resolution
- Follows a hierarchical pattern: controller → service → repository → database session

## Standard CSR Pattern Implementation

### Controller Implementation
Controllers follow this standard structure:

```python
from fastapi import APIRouter, Depends

from app.dependencies.user_dependencies import get_user_service
from app.models.user.dto import User, UserCreate, UserUpdate
from app.service.user_service import UserService
from app.models.responses import StandardResponse, success

# Create router with prefix and tags
user_router = APIRouter(prefix="/users", tags=["users"])

@user_router.get("/", response_model=StandardResponse[list[User]])
async def get_users(
    service: UserService = Depends(get_user_service),
    # Additional dependencies (e.g., authentication checks)
):
    """Get a list of all users"""
    users = await service.get_all_users()
    return success(message="Users retrieved successfully", payload=users)
```

Key patterns in controllers:
- Use APIRouter with appropriate prefix and tags
- Use dependency injection for services
- Follow standardized response format
- Include docstrings for API documentation
- Apply authentication/authorization where needed

### Service Implementation
Services follow this standard structure:

```python
from typing import List

from app.error.exceptions import ConflictException, ResourceNotFoundException
from app.interface.repositories.user_repository_interface import IUserRepository
from app.models.user.dto import User, UserCreate, UserUpdate


class UserService:
    """
    Service layer for user operations.
    Contains business logic for user management.
    """

    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user with business validation."""
        # Business validation logic
        existing_user = await self.user_repository.get_user_by_email(user_create.email)
        if existing_user:
            raise ConflictException(f"User with email '{user_create.email}' already exists")

        # Create user via repository
        user = await self.user_repository.create_user(user_create)
        return user
```

Key patterns in services:
- Accept repository interfaces in constructor
- Implement business validation and logic
- Handle business-specific exceptions
- Call repository methods for data operations
- Return DTOs (not domain models or entities)

### Repository Implementation
Repositories follow this standard structure:

```python
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.interface.repositories.user_repository_interface import IUserRepository
from app.models.user.domain import UserDomain
from app.models.user.dto import User, UserCreate, UserUpdate
from app.models.user.entity import UserEntity
from app.models.user.mapper import UserMapper


class UserRepository(IUserRepository):
    """Implementation of user repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user in the repository."""
        # Create domain entity first to validate business rules
        domain_user = UserDomain.create(
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            email=user_create.email,
            username=user_create.username,
            password=user_create.password,
        )

        # Create SQLAlchemy User object from domain entity
        db_user = UserMapper.to_entity(domain_user)

        self.db_session.add(db_user)
        await self.db_session.commit()
        await self.db_session.refresh(db_user)

        # Convert to DTO for return
        return UserMapper.to_dto(UserMapper.from_entity(db_user))
```

Key patterns in repositories:
- Implement the corresponding interface contract
- Accept database session in constructor
- Use domain models for business validation (via domain constructors)
- Use mappers to convert between layers
- Handle SQLAlchemy-specific operations

### Repository Interface Implementation
Interfaces follow this standard structure:

```python
from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.user.dto import User, UserCreate, UserUpdate


class IUserRepository(ABC):
    """Interface for user repository operations."""

    @abstractmethod
    async def create_user(self, user_create: UserCreate) -> User:
        """Create a new user in the repository."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID from the repository."""
        pass
```

Key patterns in interfaces:
- Extend ABC for abstract base class functionality
- Use @abstractmethod decorator for each method
- Define clear, descriptive docstrings
- Use appropriate return types and type hints

### Dependency Injection Implementation
Dependency functions follow this standard structure:

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repository.user_repository import UserRepository
from app.service.user_service import UserService


async def get_user_repository(db_session: AsyncSession = Depends(get_db_session)):
    """Dependency to provide UserRepository instance with database session."""
    return UserRepository(db_session=db_session)


async def get_user_service(
    user_repository: UserRepository = Depends(get_user_repository),
):
    """Dependency to provide UserService instance with repository."""
    return UserService(user_repository)
```

Key patterns in dependencies:
- Hierarchical structure (controller → service → repository → database session)
- Use FastAPI's Depends for dependency resolution
- Clear function names following `get_*` pattern
- Proper typing with async functions

## Standard Methods Pattern

### CRUD Operations
Each CSR implementation typically includes these standard methods:

#### Controller Layer
- `get_resource()` - Retrieve a single resource
- `get_resources()` - Retrieve all/multiple resources
- `create_resource()` - Create a new resource
- `update_resource()` - Update an existing resource
- `delete_resource()` - Delete a resource

#### Service Layer
- `get_resource_by_id()` - Get single resource with business logic
- `get_all_resources()` - Get all resources with business logic
- `create_resource()` - Create resource with business validation
- `update_resource()` - Update resource with business validation
- `delete_resource()` - Delete resource with business checks

#### Repository Layer
- `get_resource_by_id()` - Get from database
- `get_all_resources()` - Get all from database
- `create_resource()` - Create in database
- `update_resource()` - Update in database
- `delete_resource()` - Delete from database

## CSR Layer Recipe

To create new CSR layers for a resource, follow this step-by-step recipe:

### Step 1: Create Repository Interface
In `app/interface/repositories/`:
1. Create interface file `resource_name_repository_interface.py`
2. Define interface extending `ABC` with `IResourceNameRepository` name
3. Add all required abstract methods with proper type hints and docstrings
4. Use DTOs and domain models as parameter/return types

### Step 2: Create Repository Implementation
In `app/repository/`:
1. Create repository file `resource_name_repository.py`
2. Import the interface and implement all methods
3. Use SQLAlchemy for database operations
4. Apply appropriate mappers for conversions
5. Include proper error handling

### Step 3: Create Service Implementation
In `app/service/`:
1. Create service file `resource_name_service.py`
2. Define the service class with required business logic
3. Accept repository interface in constructor
4. Implement all standard CRUD methods with business validation
5. Handle business-specific exceptions

### Step 4: Create Dependencies
In `app/controller/dependencies/`:
1. Create dependency functions for repository and service
2. Follow the hierarchical injection pattern
3. Use proper type hints and docstrings

### Step 5: Create Controller
In `app/controller/`:
1. Create route handlers with proper FastAPI decorators
2. Use dependency injection for the service
3. Apply standardized response format
4. Add proper authentication/authorization where needed

### Example: Creating a Post Resource

#### 1. Interface (`app/interface/repositories/post_repository_interface.py`):
```python
from abc import ABC, abstractmethod
from typing import List, Optional

from app.models.post.dto import Post, PostCreate, PostUpdate


class IPostRepository(ABC):
    """Interface for post repository operations."""

    @abstractmethod
    async def create_post(self, post_create: PostCreate) -> Post:
        """Create a new post in the repository."""
        pass

    @abstractmethod
    async def get_post_by_id(self, post_id: str) -> Optional[Post]:
        """Get a post by ID from the repository."""
        pass

    @abstractmethod
    async def get_all_posts(self) -> List[Post]:
        """Get all posts from the repository."""
        pass

    @abstractmethod
    async def update_post(self, post_id: str, post_update: PostUpdate) -> Optional[Post]:
        """Update a post in the repository."""
        pass

    @abstractmethod
    async def delete_post(self, post_id: str) -> Optional[str]:
        """Delete a post from the repository."""
        pass
```

#### 2. Repository (`app/repository/post_repository.py`):
```python
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.interface.repositories.post_repository_interface import IPostRepository
from app.models.post.domain import PostDomain
from app.models.post.dto import Post, PostCreate, PostUpdate
from app.models.post.entity import PostEntity
from app.models.post.mapper import PostMapper


class PostRepository(IPostRepository):
    """Implementation of post repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_post(self, post_create: PostCreate) -> Post:
        """Create a new post in the repository."""
        # Create domain entity first to validate business rules
        domain_post = PostDomain.create(
            title=post_create.title,
            content=post_create.content,
            author_id=post_create.author_id,
        )

        # Create SQLAlchemy Post object from domain entity
        db_post = PostMapper.to_entity(domain_post)

        self.db_session.add(db_post)
        await self.db_session.commit()
        await self.db_session.refresh(db_post)

        # Convert to DTO for return
        return PostMapper.to_dto(PostMapper.from_entity(db_post))

    # Other methods implementation...
```

#### 3. Service (`app/service/post_service.py`):
```python
from typing import List

from app.error.exceptions import ConflictException, ResourceNotFoundException
from app.interface.repositories.post_repository_interface import IPostRepository
from app.models.post.dto import Post, PostCreate, PostUpdate


class PostService:
    """
    Service layer for post operations.
    Contains business logic for post management.
    """

    def __init__(self, post_repository: IPostRepository):
        self.post_repository = post_repository

    async def get_all_posts(self) -> List[Post]:
        """Get all posts with business logic."""
        posts = await self.post_repository.get_all_posts()
        return posts

    async def get_post_by_id(self, post_id: str) -> Post:
        """Get a specific post by ID with business logic."""
        post = await self.post_repository.get_post_by_id(post_id)
        if not post:
            raise ResourceNotFoundException(resource_type="Post", identifier=post_id)
        return post

    async def create_post(self, post_create: PostCreate) -> Post:
        """Create a new post with business validation."""
        post = await self.post_repository.create_post(post_create)
        return post

    # Other methods implementation...
```

#### 4. Dependencies (`app/controller/dependencies/post_dependencies.py`):
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.repository.post_repository import PostRepository
from app.service.post_service import PostService


async def get_post_repository(db_session: AsyncSession = Depends(get_db_session)):
    """Dependency to provide PostRepository instance with database session."""
    return PostRepository(db_session=db_session)


async def get_post_service(
    post_repository: PostRepository = Depends(get_post_repository),
):
    """Dependency to provide PostService instance with repository."""
    return PostService(post_repository)
```

#### 5. Controller (`app/controller/post_controller.py`):
```python
from fastapi import APIRouter, Depends

from app.dependencies.post_dependencies import get_post_service
from app.models.post.dto import Post, PostCreate, PostUpdate
from app.service.post_service import PostService
from app.models.responses import StandardResponse, success

# Create router with prefix and tags
post_router = APIRouter(prefix="/posts", tags=["posts"])


@post_router.get("/", response_model=StandardResponse[list[Post]])
async def get_posts(
    service: PostService = Depends(get_post_service),
    # Authentication dependencies if needed
):
    """Get a list of all posts"""
    posts = await service.get_all_posts()
    return success(message="Posts retrieved successfully", payload=posts)


@post_router.post("/", response_model=StandardResponse[Post])
async def create_post(
    post_create: PostCreate,
    service: PostService = Depends(get_post_service),
    # Authentication dependencies if needed
):
    """Create a new post"""
    post = await service.create_post(post_create)
    return success(message="Post created successfully", payload=post)

# Other route implementations...
```

## Benefits of CSR Pattern

1. **Separation of Concerns**: Each layer has a well-defined responsibility
2. **Testability**: Layers can be unit tested independently using mocks
3. **Maintainability**: Changes in one layer don't necessarily affect others
4. **Flexibility**: Different implementations can be swapped (e.g., different databases)
5. **Dependency Inversion**: Services depend on abstractions, not concrete implementations
6. **Consistency**: Standardized approach across all resources
7. **Type Safety**: Full type checking through Pydantic and proper typing
