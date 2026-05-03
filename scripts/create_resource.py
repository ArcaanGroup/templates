#!/usr/bin/env python3
"""
Script to create all necessary files for a new resource following the CSR architecture with Entity-Driven Design.
Creates model (domain, entity, dto, mapper), service, repository, interface, and controller files.
"""

import sys
from pathlib import Path


def to_camel_case(snake_str):
    """Convert snake_case to camelCase."""
    parts = snake_str.lower().split("_")
    return parts[0] + "".join(x.capitalize() for x in parts[1:])


def to_pascal_case(snake_str):
    """Convert snake_case to PascalCase."""
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def create_resource(resource_name):
    """Create all files for a new resource."""
    resource_name = resource_name.strip().lower()
    if not resource_name:
        print("Resource name cannot be empty")
        return

    # Convert to different cases
    resource_snake = resource_name
    resource_pascal = to_pascal_case(resource_name)

    # Create directory structure
    model_dir = Path(f"app/models/{resource_snake}")
    interface_dir = Path("app/interface/repositories")
    repository_dir = Path("app/repository")
    service_dir = Path("app/service")
    controller_dir = Path("app/controller")
    dependencies_dir = Path("app/dependencies")

    # Create directories if they don't exist
    for directory in [
        model_dir,
        interface_dir,
        repository_dir,
        service_dir,
        controller_dir,
        dependencies_dir,
    ]:
        directory.mkdir(exist_ok=True)

    # Create model files
    create_model_files(resource_snake, resource_pascal, model_dir)

    # Create repository interface
    create_repository_interface(resource_snake, resource_pascal, interface_dir)

    # Create repository implementation
    create_repository_implementation(resource_snake, resource_pascal, repository_dir)

    # Create service
    create_service(resource_snake, resource_pascal, service_dir)

    # Create controller dependencies
    create_controller_dependencies(resource_snake, resource_pascal, dependencies_dir)

    # Create controller
    create_controller(resource_snake, resource_pascal, controller_dir)

    print(f"Successfully created all files for resource: {resource_name}")
    print("Files created:")
    print(f"  - {model_dir}/__init__.py")
    print(f"  - {model_dir}/domain.py")
    print(f"  - {model_dir}/dto.py")
    print(f"  - {model_dir}/entity.py")
    print(f"  - {model_dir}/mapper.py")
    print(f"  - {interface_dir}/{resource_snake}_repository_interface.py")
    print(f"  - {repository_dir}/{resource_snake}_repository.py")
    print(f"  - {service_dir}/{resource_snake}_service.py")
    print(f"  - {dependencies_dir}/{resource_snake}_dependencies.py")
    print(f"  - {controller_dir}/{resource_snake}_controller.py")

    # Add router to api.py
    add_router_to_api(resource_snake)


def add_router_to_api(resource_snake):
    """Add the new controller import and router include to api.py."""
    api_file_path = Path("app/controller/api.py")

    if api_file_path.exists():
        with open(api_file_path, "r") as f:
            content = f.read()

        # Check if the import already exists
        import_line = (
            f"from .{resource_snake}_controller import {resource_snake}_router"
        )

        if import_line not in content:
            # Add the import after the last existing import
            lines = content.split("\n")
            updated_lines = []
            import_added = False

            for line in lines:
                if (
                    line.startswith("from .")
                    and line.endswith("_router")
                    and not import_added
                ):
                    updated_lines.append(line)
                    updated_lines.append(
                        f"from .{resource_snake}_controller import {resource_snake}_router"
                    )
                    import_added = True
                else:
                    updated_lines.append(line)

            # Add include_router call before the end
            include_router_added = False
            final_lines = []
            for line in updated_lines:
                final_lines.append(line)
                if (
                    line.strip().startswith("api_router.include_router(")
                    and not include_router_added
                ):
                    # Add the new include_router call after the last include_router call
                    final_lines.append(
                        f"api_router.include_router({resource_snake}_router)"
                    )
                    include_router_added = True

            if not import_added:
                # If no import was found, add at the beginning with other imports
                new_lines = []
                for i, line in enumerate(final_lines):
                    if line.startswith("api_router = APIRouter"):
                        new_lines.insert(
                            i,
                            f"from .{resource_snake}_controller import {resource_snake}_router",
                        )
                        break
                final_lines = new_lines

            with open(api_file_path, "w") as f:
                f.write("\n".join(final_lines))

            print(f"  - Added {resource_snake}_router to app/controller/api.py")


def create_model_files(resource_snake, resource_pascal, model_dir):
    """Create all model files for the resource."""

    # Create __init__.py
    init_content = f'''from .domain import {resource_pascal}Entity
from .dto import {resource_pascal}, {resource_pascal}Create, {resource_pascal}Update
from .entity import {resource_pascal}Entity

__all__ = ["{resource_pascal}", "{resource_pascal}Create", "{resource_pascal}Update", "{resource_pascal}Entity", "{resource_pascal}Entity"]
'''
    with open(model_dir / "__init__.py", "w") as f:
        f.write(init_content)

    # Create domain.py
    domain_content = f'''"""
Entity Entity for {resource_pascal} - contains business logic and behavior
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.error.exceptions import ValidationException


@dataclass
class {resource_pascal}Entity:
    """Entity entity for {resource_pascal} with business logic."""

    id: str
    name: str  # Default field, change as needed
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    @classmethod
    def create(
        cls,
        name: str,  # Default field, change as needed
        resource_id: Optional[str] = None,
    ) -> "{resource_pascal}Entity":
        """Create a new {resource_pascal}Entity entity with validation."""
        # Validate inputs
        cls._validate_name(name)

        resource_id = resource_id or str(uuid4())
        now = datetime.now()

        return cls(
            id=resource_id,
            name=name,  # Default field, change as needed
            created_at=now,
            updated_at=now,
            is_active=True,
        )

    def update_info(
        self,
        name: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> None:
        """Update {resource_pascal} information with validation."""
        if name is not None:
            self._validate_name(name)
            self.name = name  # Default field, change as needed
        if is_active is not None:
            self.is_active = is_active

        self.updated_at = datetime.now()

    def deactivate(self) -> None:
        """Deactivate the {resource_pascal}."""
        self.is_active = False
        self.updated_at = datetime.now()

    def activate(self) -> None:
        """Activate the {resource_pascal}."""
        self.is_active = True
        self.updated_at = datetime.now()

    @staticmethod
    def _validate_name(name: str) -> None:
        """Validate name format."""
        if not name or len(name.strip()) == 0:
            raise ValidationException("Name cannot be empty", field="name")
        if len(name) > 100:
            raise ValidationException("Name is too long", field="name")

    # Conversion methods are now handled by the {resource_pascal}Mapper class
    # See app.models.{resource_snake}.mapper.{resource_pascal}Mapper
'''
    with open(model_dir / "domain.py", "w") as f:
        f.write(domain_content)

    # Create entity.py
    entity_content = f'''"""
{resource_pascal} entity as SQLAlchemy ORM model.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class {resource_pascal}Entity(Base):
    """{resource_pascal} entity for database storage."""

    __tablename__ = "{resource_snake}s"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # Default field, change as needed
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Add relationships to other entities as needed
'''
    with open(model_dir / "entity.py", "w") as f:
        f.write(entity_content)

    # Create dto.py
    dto_content = f'''from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class {resource_pascal}Base(BaseModel):
    """Base {resource_pascal} model with common fields."""

    name: str  # Default field, change as needed


class {resource_pascal}Create({resource_pascal}Base):
    """{resource_pascal} model for creating new {resource_snake}s"""

    pass  # Add specific fields for creation if needed


class {resource_pascal}Update(BaseModel):
    """{resource_pascal} model for updating existing {resource_snake}s"""

    name: Optional[str] = None  # Add specific fields for updates if needed
    is_active: Optional[bool] = None


class {resource_pascal}(BaseModel):
    """Public {resource_pascal} model without sensitive data"""

    id: str
    name: str  # Default field, change as needed
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    # Add other fields as needed but exclude sensitive data
'''
    with open(model_dir / "dto.py", "w") as f:
        f.write(dto_content)

    # Create mapper.py
    mapper_content = f'''"""
{resource_pascal} Mapper - handles conversion between {resource_pascal}Entity, {resource_pascal}Entity, and {resource_pascal} DTO
The Entity is the core of conversions
The Entity gets converted from DTO and Entity
And DTO and Entity gets converted from Entity
No Direct conversions from Entity to DTO or DTO to Entity
"""

from app.domain.entities import {resource_pascal}Entity
from app.models.{resource_snake}.dto import {resource_pascal} as {resource_pascal}DTO
from app.models.{resource_snake}.dto import {resource_pascal}Create, {resource_pascal}Update
from app.infrastructure.orm import {resource_pascal}Entity


class {resource_pascal}Mapper:
    """Mapper class to handle conversions between {resource_pascal} representations."""

    @staticmethod
    def from_dto(dto: {resource_pascal}Create) -> {resource_pascal}Entity:
        """Convert DTO {resource_pascal} to domain."""
        return {resource_pascal}Entity.create(
            name=dto.name,  # Default field, change as needed
        )

    @staticmethod
    def to_dto(domain_{resource_snake}: {resource_pascal}Entity) -> {resource_pascal}DTO:
        """Convert domain {resource_pascal} to DTO."""
        return {resource_pascal}DTO(
            id=domain_{resource_snake}.id,
            name=domain_{resource_snake}.name,  # Default field, change as needed
            created_at=domain_{resource_snake}.created_at,
            updated_at=domain_{resource_snake}.updated_at,
            is_active=domain_{resource_snake}.is_active,
        )

    @staticmethod
    def from_entity(entity_{resource_snake}: {resource_pascal}Entity) -> {resource_pascal}Entity:
        """Convert entity {resource_pascal} to domain."""
        return {resource_pascal}Entity(
            id=entity_{resource_snake}.id,
            name=entity_{resource_snake}.name,  # Default field, change as needed
            created_at=entity_{resource_snake}.created_at,
            updated_at=entity_{resource_snake}.updated_at,
            is_active=entity_{resource_snake}.is_active,
        )

    @staticmethod
    def to_entity(domain_{resource_snake}: {resource_pascal}Entity) -> {resource_pascal}Entity:
        """Convert domain {resource_pascal} to entity."""
        entity = {resource_pascal}Entity(
            id=domain_{resource_snake}.id,
            name=domain_{resource_snake}.name,  # Default field, change as needed
            created_at=domain_{resource_snake}.created_at,
            updated_at=domain_{resource_snake}.updated_at,
            is_active=domain_{resource_snake}.is_active,
        )
        return entity

    @staticmethod
    def update_from_dto({resource_snake}_update: {resource_pascal}Update, domain_{resource_snake}: {resource_pascal}Entity) -> {resource_pascal}Entity:
        """Apply {resource_pascal}Update DTO to an existing {resource_pascal}Entity and return updated domain entity."""
        # Update only the fields that are provided in the update DTO
        update_data = {{
            k: v for k, v in {resource_snake}_update.model_dump().items() if v is not None
        }}

        # Apply the updates to the domain {resource_pascal} using its update_info method
        domain_{resource_snake}.update_info(
            name=update_data.get("name"),
            is_active=update_data.get("is_active"),
        )

        return domain_{resource_snake}

    @staticmethod
    def update_entity(entity: {resource_pascal}Entity, domain: {resource_pascal}Entity):
        entity.name = domain.name  # Default field, change as needed
        entity.is_active = domain.is_active
        entity.updated_at = domain.updated_at
'''
    with open(model_dir / "mapper.py", "w") as f:
        f.write(mapper_content)


def create_repository_interface(resource_snake, resource_pascal, interface_dir):
    """Create repository interface file."""
    interface_content = f'''"""
Interface for {resource_snake} repository operations.
This follows the dependency inversion principle by having the service layer
depend on this abstraction rather than concrete implementations.
"""

from abc import ABC, abstractmethod
from typing import Optional

from fastapi_pagination import Page, Params

from app.domain.entities import {resource_pascal}Entity


class I{resource_pascal}Repository(ABC):
    """Interface for {resource_snake} repository operations."""

    @abstractmethod
    async def get_by_id(self, {resource_snake}_id: str) -> Optional[{resource_pascal}Entity]:
        """Get a {resource_snake} by ID from the repository."""
        pass

    @abstractmethod
    async def get_all(self, params: Params) -> Page[{resource_pascal}Entity]:
        """Get all {resource_snake}s from the repository."""
        pass

    @abstractmethod
    async def create(self, {resource_snake}_to_create: {resource_pascal}Entity) -> {resource_pascal}Entity:
        """Create a new {resource_snake} in the repository."""
        pass

    @abstractmethod
    async def update(self, source: {resource_pascal}Entity) -> Optional[{resource_pascal}Entity]:
        """Update a {resource_snake} in the repository."""
        pass

    @abstractmethod
    async def delete(self, {resource_snake}_id: str) -> Optional[{resource_pascal}Entity]:
        """Delete a {resource_snake} from the repository."""
        pass
'''
    with open(interface_dir / f"{resource_snake}_repository_interface.py", "w") as f:
        f.write(interface_content)


def create_repository_implementation(resource_snake, resource_pascal, repository_dir):
    """Create repository implementation file."""
    repository_content = f'''"""
Implementation of the {resource_snake} repository using SQLAlchemy.
This is the concrete repository implementation for PostgreSQL database.
"""

from typing import List, Optional

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.error.exceptions import ResourceNotFoundException
from app.interface.repositories.{resource_snake}_repository_interface import I{resource_pascal}Repository
from app.domain.entities import {resource_pascal}Entity
from app.infrastructure.orm import {resource_pascal}Entity
from app.models.{resource_snake}.mapper import {resource_pascal}Mapper


class {resource_pascal}Repository(I{resource_pascal}Repository):
    """Implementation of {resource_snake} repository operations using SQLAlchemy."""

    def __init__(self, db_session: AsyncSession):
        self.session = db_session

    async def create(self, {resource_snake}_to_create: {resource_pascal}Entity) -> {resource_pascal}Entity:
        """Create a new {resource_snake} in the repository."""
        # Convert domain entity to database entity for persistence
        {resource_snake}_entity = {resource_pascal}Mapper.to_entity({resource_snake}_to_create)

        self.session.add({resource_snake}_entity)
        await self.session.commit()

        # Refresh the entity to ensure it has the auto-generated fields (like ID)
        await self.session.refresh({resource_snake}_entity)

        # Convert back to domain entity for return
        return {resource_pascal}Mapper.from_entity({resource_snake}_entity)

    async def get_by_id(self, {resource_snake}_id: str) -> Optional[{resource_pascal}Entity]:
        """Get a {resource_snake} by ID from the repository."""
        result = await self.session.execute(
            select({resource_pascal}Entity).where({resource_pascal}Entity.id == {resource_snake}_id)
        )
        {resource_snake}_in_db = result.scalar_one_or_none()

        if {resource_snake}_in_db is None:
            return None

        return {resource_pascal}Mapper.from_entity({resource_snake}_in_db)

    async def get_all(self, params: Params) -> Page[{resource_pascal}Entity]:
        """Get all {resource_snake}s from the repository."""
        query = select({resource_pascal}Entity)
        {resource_snake}s_page: Page[{resource_pascal}Entity] = await paginate(self.session, query, params)

        {resource_snake}_domains: List[{resource_pascal}Entity] = []
        for {resource_snake} in {resource_snake}s_page.items:
            domain = {resource_pascal}Mapper.from_entity({resource_snake})
            {resource_snake}_domains.append(domain)

        {resource_snake}s_page.items = {resource_snake}_domains  # pyright: ignore[reportAttributeAccessIssue]

        return {resource_snake}s_page  # pyright: ignore[reportReturnType]

    async def update(self, source: {resource_pascal}Entity) -> Optional[{resource_pascal}Entity]:
        """Update a {resource_snake} in the repository."""
        {resource_snake}_entity = await self.session.get({resource_pascal}Entity, source.id)

        if not {resource_snake}_entity:
            return None

        {resource_pascal}Mapper.update_entity({resource_snake}_entity, source)

        await self.session.commit()
        await self.session.refresh({resource_snake}_entity)

        return {resource_pascal}Mapper.from_entity({resource_snake}_entity)

    async def delete(self, {resource_snake}_id: str) -> {resource_pascal}Entity:
        """Delete a {resource_snake} from the repository."""
        # Get the {resource_snake} to check if it exists
        result = await self.session.execute(
            select({resource_pascal}Entity).where({resource_pascal}Entity.id == {resource_snake}_id)
        )
        target = result.scalar_one_or_none()

        if not target:
            raise ResourceNotFoundException(resource_type="{resource_pascal}", identifier={resource_snake}_id)

        # Delete the {resource_snake}
        await self.session.delete(target)
        await self.session.commit()

        return {resource_pascal}Mapper.from_entity(target)
'''
    with open(repository_dir / f"{resource_snake}_repository.py", "w") as f:
        f.write(repository_content)


def create_service(resource_snake, resource_pascal, service_dir):
    """Create service file."""
    # Convert to PascalCase for class names (in case it's not passed correctly)
    resource_pascal = to_pascal_case(resource_snake)

    service_content = f'''from fastapi_pagination import Page, Params

from app.error.exceptions import ResourceNotFoundException
from app.interface.repositories.{resource_snake}_repository_interface import I{resource_pascal}Repository
from app.models.{resource_snake}.dto import {resource_pascal}, {resource_pascal}Create, {resource_pascal}Update
from app.models.{resource_snake}.mapper import {resource_pascal}Mapper


class {resource_pascal}Service:
    """
    Service layer for {resource_snake} operations.
    Contains business logic for {resource_snake} management.
    """

    def __init__(self, {resource_snake}_repository: I{resource_pascal}Repository):
        self.{resource_snake}_repo = {resource_snake}_repository

    async def get_all(self, params: Params) -> Page[{resource_pascal}]:
        """Get all {resource_snake}s with business logic."""
        {resource_snake}_domains_page = await self.{resource_snake}_repo.get_all(params)

        {resource_snake}_dtos: list[{resource_pascal}] = []
        for domain_{resource_snake} in {resource_snake}_domains_page.items:
            {resource_snake}_dtos.append({resource_pascal}Mapper.to_dto(domain_{resource_snake}))

        {resource_snake}_domains_page.items = {resource_snake}_dtos  # pyright: ignore[reportAttributeAccessIssue]

        return {resource_snake}_domains_page  # pyright: ignore[reportReturnType]

    async def get_by_id(self, {resource_snake}_id: str) -> {resource_pascal}:
        """Get a specific {resource_snake} by ID with business logic."""
        domain_{resource_snake} = await self.{resource_snake}_repo.get_by_id({resource_snake}_id)

        if not domain_{resource_snake}:
            raise ResourceNotFoundException(resource_type="{resource_pascal}", identifier={resource_snake}_id)

        return {resource_pascal}Mapper.to_dto(domain_{resource_snake})

    async def create(self, {resource_snake}_create: {resource_pascal}Create) -> {resource_pascal}:
        """Create a new {resource_snake} with business validation."""
        # Create domain entity from DTO to apply validation
        domain_{resource_snake} = {resource_pascal}Mapper.from_dto({resource_snake}_create)

        # Check if {resource_snake} with the same name already exists
        # existing_{resource_snake} = await self.{resource_snake}_repo.get_by_{resource_snake}_name({resource_snake}_create.name)
        # if existing_{resource_snake}:
        #     raise ConflictException(f"{{resource_pascal}} with name '{{{resource_snake}_create.name}}' already exists")

        # Create {resource_snake} via repository
        created_domain_{resource_snake} = await self.{resource_snake}_repo.create(domain_{resource_snake})

        return {resource_pascal}Mapper.to_dto(created_domain_{resource_snake})

    async def update(self, {resource_snake}_id: str, update_dto: {resource_pascal}Update) -> {resource_pascal}:
        """Update a {resource_snake} with business validation."""
        # Get the current {resource_snake} to check for conflicts
        target_domain = await self.{resource_snake}_repo.get_by_id({resource_snake}_id)

        if not target_domain:
            raise ResourceNotFoundException(resource_type="{resource_pascal}", identifier={resource_snake}_id)

        # Check if the new name conflicts with existing {resource_snake}s (excluding current {resource_snake})
        # if update_dto.name and update_dto.name != target_domain.name:
        #     existing_{resource_snake} = await self.{resource_snake}_repo.get_by_{resource_snake}_name(update_dto.name)
        #     if existing_{resource_snake} and existing_{resource_snake}.id != {resource_snake}_id:
        #         raise ConflictException(f"{{resource_pascal}} with name '{{update_dto.name}}' already exists")

        {resource_pascal}Mapper.update_from_dto(update_dto, target_domain)

        updated_domain = await self.{resource_snake}_repo.update(target_domain)

        if updated_domain is None:
            raise ResourceNotFoundException(resource_type="{resource_pascal}", identifier={resource_snake}_id)

        # Return DTO representation
        return {resource_pascal}Mapper.to_dto(updated_domain)

    async def delete(self, {resource_snake}_id: str) -> {resource_pascal}:
        """Delete a {resource_snake} with business logic."""
        # Verify {resource_snake} exists before deletion
        domain_{resource_snake} = await self.{resource_snake}_repo.get_by_id({resource_snake}_id)
        if not domain_{resource_snake}:
            raise ResourceNotFoundException(resource_type="{resource_pascal}", identifier={resource_snake}_id)

        # Delete {resource_snake} via repository
        deleted_domain_{resource_snake} = await self.{resource_snake}_repo.delete({resource_snake}_id)
        if not deleted_domain_{resource_snake}:
            raise ResourceNotFoundException(resource_type="{resource_pascal}", identifier={resource_snake}_id)

        return {resource_pascal}Mapper.to_dto(deleted_domain_{resource_snake})
'''
    with open(service_dir / f"{resource_snake}_service.py", "w") as f:
        f.write(service_content)


def create_controller_dependencies(resource_snake, resource_pascal, dependencies_dir):
    """Create controller dependencies file."""
    deps_content = f'''"""
{resource_snake}-related dependencies and dependency injection logic.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.interface.repositories.{resource_snake}_repository_interface import I{resource_pascal}Repository
from app.repository.{resource_snake}_repository import {resource_pascal}Repository
from app.service.{resource_snake}_service import {resource_pascal}Service


async def get_{resource_snake}_repository(db_session: AsyncSession = Depends(get_db_session)) -> I{resource_pascal}Repository:
    """Dependency to provide {resource_pascal}Repository instance with database session."""
    return {resource_pascal}Repository(db_session=db_session)


async def get_{resource_snake}_service(
    {resource_snake}_repository: I{resource_pascal}Repository = Depends(get_{resource_snake}_repository),
) -> {resource_pascal}Service:
    """Dependency to provide {resource_pascal}Service instance with repository."""
    return {resource_pascal}Service({resource_snake}_repository)
'''
    with open(dependencies_dir / f"{resource_snake}_dependencies.py", "w") as f:
        f.write(deps_content)


def create_controller(resource_snake, resource_pascal, controller_dir):
    """Create controller file."""

    controller_content = f'''from fastapi import APIRouter, Depends
from fastapi_pagination import Page, Params

from app.dependencies.{resource_snake}_dependencies import get_{resource_snake}_service
from app.models.responses import StandardResponse, success
from app.models.{resource_snake}.dto import {resource_pascal}, {resource_pascal}Create, {resource_pascal}Update
from app.service.{resource_snake}_service import {resource_pascal}Service

# Create router with prefix and tags
{resource_snake}_router = APIRouter(prefix="/{resource_snake}s", tags=["{resource_snake}s"])


@{resource_snake}_router.get("/", response_model=StandardResponse[Page[{resource_pascal}]])
async def get_{resource_snake}s(
    service: {resource_pascal}Service = Depends(get_{resource_snake}_service),
    params: Params = Depends(),
    # Add authentication dependencies if needed
):
    """Get a list of all {resource_snake}s"""
    {resource_snake}s = await service.get_all(params)

    return success(
        message="{resource_pascal}s retrieved successfully",
        payload={resource_snake}s,
    )


@{resource_snake}_router.post("/", response_model=StandardResponse[{resource_pascal}])
async def create_{resource_snake}(
    {resource_snake}_create: {resource_pascal}Create,
    service: {resource_pascal}Service = Depends(get_{resource_snake}_service),
    # Add authentication dependencies if needed
):
    """Create a new {resource_snake}"""
    {resource_snake} = await service.create({resource_snake}_create)

    return success(message="{resource_pascal} created successfully", payload={resource_snake})


@{resource_snake}_router.get("/{{{resource_snake}_id}}", response_model=StandardResponse[{resource_pascal}])
async def get_{resource_snake}(
    {resource_snake}_id: str,
    service: {resource_pascal}Service = Depends(get_{resource_snake}_service),
    # Add authentication dependencies if needed
):
    """Get a specific {resource_snake} by ID"""
    {resource_snake} = await service.get_by_id({resource_snake}_id)

    return success(message="{resource_pascal} retrieved successfully", payload={resource_snake})


@{resource_snake}_router.put("/{{{resource_snake}_id}}", response_model=StandardResponse[{resource_pascal}])
async def update_{resource_snake}(
    {resource_snake}_id: str,
    {resource_snake}_update: {resource_pascal}Update,
    service: {resource_pascal}Service = Depends(get_{resource_snake}_service),
    # Add authentication dependencies if needed
):
    """Update a specific {resource_snake} by ID"""
    {resource_snake} = await service.update({resource_snake}_id, {resource_snake}_update)

    return success(message="{resource_pascal} updated successfully", payload={resource_snake})


@{resource_snake}_router.delete("/{{{resource_snake}_id}}", response_model=StandardResponse[{resource_pascal}])
async def delete_{resource_snake}(
    {resource_snake}_id: str,
    service: {resource_pascal}Service = Depends(
        get_{resource_snake}_service,
    ),
    # Add authentication dependencies if needed
):
    """Delete a specific {resource_snake} by ID"""
    deleted_{resource_snake} = await service.delete({resource_snake}_id)

    return success(message="{resource_pascal} deleted successfully", payload=deleted_{resource_snake})
'''
    with open(controller_dir / f"{resource_snake}_controller.py", "w") as f:
        f.write(controller_content)


def main():
    if len(sys.argv) > 1:
        resource_name = sys.argv[1]
    else:
        resource_name = input("Enter resource name: ")

    create_resource(resource_name)


if __name__ == "__main__":
    main()
