# Model Package Documentation

## Overview
The `app/models/**` package represents the core data layer of the application, following Domain-Driven Design (DDD) principles. Each resource in the application has its own model package containing four key components: Domain, DTO, Entity, and Mapper. This structure ensures separation of concerns and clean architecture.

## Package Structure
Each model package follows the same structure and contains:
- `domain.py` - Domain entities with business logic and behavior
- `dto.py` - Data Transfer Objects for API communication
- `entity.py` - SQLAlchemy ORM models for database storage
- `mapper.py` - Conversion logic between domain, DTO, and entity models
- `__init__.py` - Exports public interfaces

## Component Responsibilities

### Domain (`domain.py`)
The domain model is the heart of the application's business logic:
- Contains rich business logic and validation rules
- Defines the core behavior of the entity
- Includes factory methods for creation (e.g., `create` classmethod)
- May include state-changing methods (e.g., `update_info`, `deactivate`)
- Contains validation methods for business rules
- Should be technology-agnostic and focused solely on business concerns

### DTO (`dto.py`)
Data Transfer Objects handle API input/output:
- Pydantic models for request/response validation
- Separate models for creation (`EntityCreate`), updates (`EntityUpdate`), and responses (`Entity`)
- Base models to share common fields
- Deliberately excludes sensitive data when exposing to clients
- Provides type safety and automatic validation

### Entity (`entity.py`)
SQLAlchemy ORM models represent database records:
- Maps to database tables using SQLAlchemy annotations
- Defines table schema (columns, relationships, constraints)
- Contains foreign keys and indexes
- Uses the shared `Base` from `app.models.base`
- Defines relationships with other entities using TYPE_CHECKING for circular imports

### Mapper (`mapper.py`)
Handles conversions between different model types:
- The domain is the core - all conversions go through domain models
- No direct conversions between DTOs and entities
- Follows the pattern: DTO ↔ Domain ↔ Entity
- Contains static methods for clear, predictable conversions

## Standard Mapper Methods

Each mapper should implement these standard methods:

### From External Sources to Domain
- `from_dto(dto) -> Domain`: Convert DTO model to domain model
- `from_entity(entity) -> Domain`: Convert entity model to domain model

### From Domain to External Sources  
- `to_dto(domain) -> DTO`: Convert domain model to DTO
- `to_entity(domain) -> Entity`: Convert domain model to entity
- `to_create_dto(domain) -> CreateDTO`: Convert domain model to create DTO (when needed)

### Update Methods
- `update_from_dto(update_dto, domain) -> Domain`: Apply update DTO changes to domain model
- `update_entity(domain, entity) -> Entity`: Apply domain changes to entity for updates

## Package Recipe

To create a new model package for a resource, follow this step-by-step recipe:

### Step 1: Create Directory Structure
```
app/models/resource_name/
├── __init__.py
├── domain.py
├── dto.py
├── entity.py
└── mapper.py
```

### Step 2: Create Domain Model
In `domain.py`:
- Define the domain class with required attributes
- Include business logic and validation methods
- Create a `create` classmethod with validation
- Add state-changing methods as needed
- Use dataclasses or regular classes depending on complexity

### Step 3: Create DTO Models
In `dto.py`:
- Define `ResourceBase` with common fields
- Create `ResourceCreate` inheriting from base (add required creation fields)
- Create `ResourceUpdate` with optional fields
- Create `Resource` response model with all needed fields
- Add any specialized DTOs as needed

### Step 4: Create Entity Model
In `entity.py`:
- Import from `app.models.base import Base`
- Define the SQLAlchemy model inheriting from `Base`
- Specify `__tablename__`
- Define mapped columns with appropriate types and constraints
- Add relationships to other entities using TYPE_CHECKING

### Step 5: Create Mapper
In `mapper.py`:
- Import all required models from the same package
- Create a mapper class (e.g., `ResourceMapper`)
- Implement all standard conversion methods
- Ensure domain is the central hub for all conversions

### Step 6: Export Public Interfaces
In `__init__.py`:
- Import and export public models that other modules might need
- Use `__all__` to explicitly define exports

### Example Implementation

Here's a template for a new Post resource:

**app/models/post/domain.py:**
```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.error.exceptions import ValidationException


@dataclass
class PostDomain:
    """Domain entity for Post with business logic."""

    id: str
    title: str
    content: str
    author_id: str
    published: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        title: str,
        content: str,
        author_id: str,
        published: bool = False,
        post_id: Optional[str] = None,
    ) -> "PostDomain":
        """Create a new PostDomain entity with validation."""
        cls._validate_title(title)
        cls._validate_content(content)

        post_id = post_id or str(uuid4())
        now = datetime.now()

        return cls(
            id=post_id,
            title=title,
            content=content,
            author_id=author_id,
            published=published,
            created_at=now,
            updated_at=now,
            published_at=now if published else None,
        )

    def publish(self) -> None:
        """Publish the post."""
        self.published = True
        self.published_at = datetime.now()
        self.updated_at = datetime.now()

    def unpublish(self) -> None:
        """Unpublish the post."""
        self.published = False
        self.published_at = None
        self.updated_at = datetime.now()

    @staticmethod
    def _validate_title(title: str) -> None:
        """Validate title format."""
        if not title or len(title.strip()) == 0:
            raise ValidationException("Title cannot be empty", field="title")
        if len(title) > 200:
            raise ValidationException("Title is too long", field="title")

    @staticmethod
    def _validate_content(content: str) -> None:
        """Validate content format."""
        if not content or len(content.strip()) == 0:
            raise ValidationException("Content cannot be empty", field="content")
        if len(content) > 10000:
            raise ValidationException("Content is too long", field="content")
```

**app/models/post/dto.py:**
```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PostBase(BaseModel):
    """Base post model with common fields."""

    title: str
    content: str


class PostCreate(PostBase):
    """Post model for creating new posts."""

    author_id: str
    published: bool = False


class PostUpdate(BaseModel):
    """Post model for updating existing posts."""

    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class Post(BaseModel):
    """Public post model."""

    id: str
    title: str
    content: str
    author_id: str
    published: bool
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
```

**app/models/post/entity.py:**
```python
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user.entity import UserEntity


class PostEntity(Base):
    """Post entity for database storage."""

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    published_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # Relationship
    author: Mapped["UserEntity"] = relationship("UserEntity", back_populates="posts")
```

**app/models/post/mapper.py:**
```python
"""
Post Mapper - handles conversion between PostEntity, PostDomain, and Post DTO
The Domain is the core of conversions
The Domain gets converted from DTO and Entity
And DTO and Entity gets converted from Domain
No Direct conversions from Entity to DTO or DTO to Entity
"""

from datetime import datetime
from app.models.post.domain import PostDomain
from app.models.post.dto import Post, PostCreate, PostUpdate
from app.models.post.entity import PostEntity


class PostMapper:
    """Mapper class to handle conversions between post representations."""

    @staticmethod
    def from_dto(dto: PostCreate) -> PostDomain:
        """Convert DTO post to domain."""
        return PostDomain.create(
            title=dto.title,
            content=dto.content,
            author_id=dto.author_id,
            published=dto.published,
        )

    @staticmethod
    def to_dto(domain_post: PostDomain) -> Post:
        """Convert domain post to DTO."""
        return Post(
            id=domain_post.id,
            title=domain_post.title,
            content=domain_post.content,
            author_id=domain_post.author_id,
            published=domain_post.published,
            created_at=domain_post.created_at,
            updated_at=domain_post.updated_at,
            published_at=domain_post.published_at,
        )

    @staticmethod
    def from_entity(entity_post: PostEntity) -> PostDomain:
        """Convert entity post to domain."""
        return PostDomain(
            id=entity_post.id,
            title=entity_post.title,
            content=entity_post.content,
            author_id=entity_post.author_id,
            published=entity_post.published,
            created_at=entity_post.created_at,
            updated_at=entity_post.updated_at,
            published_at=entity_post.published_at,
        )

    @staticmethod
    def to_entity(domain_post: PostDomain) -> PostEntity:
        """Convert domain post to entity."""
        return PostEntity(
            id=domain_post.id,
            title=domain_post.title,
            content=domain_post.content,
            author_id=domain_post.author_id,
            published=domain_post.published,
            created_at=domain_post.created_at,
            updated_at=domain_post.updated_at,
            published_at=domain_post.published_at,
        )

    @staticmethod
    def update_from_dto(post_update: PostUpdate, domain_post: PostDomain) -> PostDomain:
        """Apply PostUpdate DTO to an existing PostDomain and return updated domain entity."""
        update_data = {
            k: v for k, v in post_update.model_dump().items() if v is not None
        }

        # Update fields directly since we're managing the state in the domain
        if "title" in update_data:
            domain_post.title = update_data["title"]
        if "content" in update_data:
            domain_post.content = update_data["content"]
        if "published" in update_data:
            if update_data["published"] != domain_post.published:
                if update_data["published"]:
                    domain_post.publish()
                else:
                    domain_post.unpublish()

        if update_data:  # Only update updated_at if there were actual changes
            domain_post.updated_at = datetime.now()

        return domain_post

    @staticmethod
    def update_entity(domain_post: PostDomain, entity_post: PostEntity) -> PostEntity:
        """Apply updated domain post fields to the entity post."""
        entity_post.title = domain_post.title
        entity_post.content = domain_post.content
        entity_post.published = domain_post.published
        entity_post.updated_at = domain_post.updated_at
        entity_post.published_at = domain_post.published_at

        return entity_post
```

**app/models/post/__init__.py:**
```python
from .dto import Post, PostCreate, PostUpdate
from .domain import PostDomain

__all__ = ["Post", "PostCreate", "PostUpdate", "PostDomain"]
```

## Benefits of This Approach

1. **Clear Separation of Concerns**: Each layer has a well-defined responsibility
2. **Testability**: Each component can be unit tested independently
3. **Maintainability**: Changes in one layer don't affect others unnecessarily
4. **Flexibility**: Different representations for different contexts (API vs DB vs business logic)
5. **Type Safety**: Full type checking through Pydantic and SQLAlchemy
6. **Domain-Centric**: Business logic remains central and unaffected by external changes