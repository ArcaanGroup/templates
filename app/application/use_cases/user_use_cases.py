"""
True Clean Architecture Use Cases for User operations.
Use cases contain business logic and are independent of frameworks and external concerns.
"""

from dataclasses import dataclass
from typing import List, Optional

from fastapi_pagination import Params

from app.domain.entities import UserEntity
from app.domain.error.exceptions import ConflictException, ResourceNotFoundException
from app.interface.repository.role_repository_interface import IRoleRepository
from app.interface.repository.user_repository_interface import IUserRepository


@dataclass(frozen=True)
class GetAllUsersRequest:
    """Input port for getting all users."""

    page: int = 1
    size: int = 20


@dataclass(frozen=True)
class GetAllUsersResponse:
    """Output port for getting all users."""

    users: List[UserEntity]
    total: int
    page: int
    size: int


@dataclass(frozen=True)
class GetUserByIdRequest:
    """Input port for getting a user by ID."""

    user_id: str


@dataclass(frozen=True)
class GetUserByIdResponse:
    """Output port for getting a user by ID."""

    user: UserEntity


@dataclass(frozen=True)
class CreateUserRequest:
    """Input port for creating a user."""

    first_name: str
    last_name: str
    email: str
    username: str
    password: str


@dataclass(frozen=True)
class CreateUserResponse:
    """Output port for creating a user."""

    user: UserEntity


@dataclass(frozen=True)
class UpdateUserRequest:
    """Input port for updating a user."""

    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


@dataclass(frozen=True)
class UpdateUserResponse:
    """Output port for updating a user."""

    user: UserEntity


@dataclass(frozen=True)
class DeleteUserRequest:
    """Input port for deleting a user."""

    user_id: str


@dataclass(frozen=True)
class DeleteUserResponse:
    """Output port for deleting a user."""

    user: UserEntity


@dataclass(frozen=True)
class AssignRoleRequest:
    """Input port for assigning a role to a user."""

    user_id: str
    role_id: str


@dataclass(frozen=True)
class AssignRoleResponse:
    """Output port for assigning a role to a user."""

    user: UserEntity


@dataclass(frozen=True)
class RemoveRoleRequest:
    """Input port for removing a role from a user."""

    user_id: str
    role_id: str


@dataclass(frozen=True)
class RemoveRoleResponse:
    """Output port for removing a role from a user."""

    user: UserEntity


class GetAllUsersUseCase:
    """Use case for retrieving all users."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, request: GetAllUsersRequest) -> GetAllUsersResponse:
        """Execute the use case to get all users."""
        users = await self._user_repo.get_all(
            Params(page=request.page, size=request.size)
        )
        return GetAllUsersResponse(
            users=users,
            total=len(users),
            page=request.page,
            size=request.size,
        )


class GetUserByIdUseCase:
    """Use case for retrieving a user by ID."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, request: GetUserByIdRequest) -> GetUserByIdResponse:
        """Execute the use case to get a user by ID."""
        user = await self._user_repo.get_by_id(request.user_id)
        if not user:
            raise ResourceNotFoundException(
                resource_type="User", identifier=request.user_id
            )
        return GetUserByIdResponse(user=user)


class CreateUserUseCase:
    """Use case for creating a new user."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, request: CreateUserRequest) -> CreateUserResponse:
        """Execute the use case to create a new user."""
        # Check for existing user by email
        existing_email = await self._user_repo.get_by_email(request.email)
        if existing_email:
            raise ConflictException(f"User with email '{request.email}' already exists")

        # Check for existing user by username
        existing_username = await self._user_repo.get_by_username(request.username)
        if existing_username:
            raise ConflictException(
                f"User with username '{request.username}' already exists"
            )

        # Create user entity using domain factory method
        user = UserEntity.create(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            username=request.username,
            password=request.password,
        )

        created_user = await self._user_repo.create(user)
        return CreateUserResponse(user=created_user)


class UpdateUserUseCase:
    """Use case for updating a user."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, request: UpdateUserRequest) -> UpdateUserResponse:
        """Execute the use case to update a user."""
        user = await self._user_repo.get_by_id(request.user_id)
        if not user:
            raise ResourceNotFoundException(
                resource_type="User", identifier=request.user_id
            )

        # Check email uniqueness if changing
        if request.email and request.email != user.email:
            existing = await self._user_repo.get_by_email(request.email)
            if existing and existing.id != request.user_id:
                raise ConflictException(
                    f"User with email '{request.email}' already exists"
                )

        # Check username uniqueness if changing
        if request.username and request.username != user.username:
            existing = await self._user_repo.get_by_username(request.username)
            if existing and existing.id != request.user_id:
                raise ConflictException(
                    f"User with username '{request.username}' already exists"
                )

        # Update user using domain method
        user.update_info(
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            username=request.username,
            is_active=request.is_active,
        )

        updated_user = await self._user_repo.update(user)
        if not updated_user:
            raise ResourceNotFoundException(
                resource_type="User", identifier=request.user_id
            )

        return UpdateUserResponse(user=updated_user)


class DeleteUserUseCase:
    """Use case for deleting a user."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, request: DeleteUserRequest) -> DeleteUserResponse:
        """Execute the use case to delete a user."""
        user = await self._user_repo.get_by_id(request.user_id)
        if not user:
            raise ResourceNotFoundException(
                resource_type="User", identifier=request.user_id
            )

        deleted_user = await self._user_repo.delete(request.user_id)
        if not deleted_user:
            raise ResourceNotFoundException(
                resource_type="User", identifier=request.user_id
            )

        return DeleteUserResponse(user=deleted_user)


class AssignRoleToUserUseCase:
    """Use case for assigning a role to a user."""

    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: "IRoleRepository",
    ):
        self._user_repo = user_repository
        self._role_repo = role_repository

    async def execute(self, request: AssignRoleRequest) -> AssignRoleResponse:
        """Execute the use case to assign a role to a user."""
        # Verify user exists
        user = await self._user_repo.get_by_id(request.user_id)
        if not user:
            raise ResourceNotFoundException(
                resource_type="User", identifier=request.user_id
            )

        # Verify role exists
        from app.interface.repository.role_repository_interface import IRoleRepository

        role = await self._role_repo.get_by_id(request.role_id)
        if not role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        updated_user = await self._user_repo.assign_role(
            request.user_id, request.role_id
        )
        return AssignRoleResponse(user=updated_user)


class RemoveRoleFromUserUseCase:
    """Use case for removing a role from a user."""

    def __init__(
        self,
        user_repository: IUserRepository,
        role_repository: "IRoleRepository",
    ):
        self._user_repo = user_repository
        self._role_repo = role_repository

    async def execute(self, request: RemoveRoleRequest) -> RemoveRoleResponse:
        """Execute the use case to remove a role from a user."""
        # Verify user exists
        user = await self._user_repo.get_by_id(request.user_id)
        if not user:
            raise ResourceNotFoundException(
                resource_type="User", identifier=request.user_id
            )

        # Verify role exists
        from app.interface.repository.role_repository_interface import IRoleRepository

        role = await self._role_repo.get_by_id(request.role_id)
        if not role:
            raise ResourceNotFoundException(
                resource_type="Role", identifier=request.role_id
            )

        updated_user = await self._user_repo.remove_role(
            request.user_id, request.role_id
        )
        return RemoveRoleResponse(user=updated_user)
