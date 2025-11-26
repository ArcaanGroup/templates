"""Update user use case"""
from app.application.dto.auth_dto import UserDTO, UserUpdateDTO
from app.application.interfaces.cache import CacheInterface
from app.application.interfaces.repositories import UserRepositoryInterface, RoleRepositoryInterface
from app.domain.exceptions.user_exceptions import UserNotFoundException
from app.domain.entities.role import Role
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username


class UpdateUserUseCase:
    """Use case for updating a user"""

    def __init__(
        self,
        repository: UserRepositoryInterface,
        role_repository: RoleRepositoryInterface,
        cache: CacheInterface
    ):
        self.repository = repository
        self.role_repository = role_repository
        self.cache = cache

    async def execute(self, user_id: int, dto: UserUpdateDTO) -> UserDTO:
        """Execute the update user use case"""
        # Get the existing user
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        # Update fields if provided in DTO
        if dto.username is not None:
            user.update_username(Username(dto.username))

        if dto.email is not None:
            user.update_email(Email(dto.email))

        if dto.is_active is not None:
            if dto.is_active:
                user.activate()
            else:
                user.deactivate()

        # Update roles if provided
        if dto.role_ids is not None:
            roles = []
            for role_id in dto.role_ids:
                role = await self.role_repository.get_by_id(role_id)
                if role:
                    roles.append(role)
            user.update_roles(roles)

        # Save updated user
        updated_user = await self.repository.update(user)

        # Invalidate cache
        cache_key = f"user:{user_id}"
        await self.cache.delete(cache_key)

        # Convert to DTO - get role titles for the response
        role_titles = [role.title.value for role in updated_user.roles]

        # Convert to DTO
        return UserDTO(
            id=updated_user.id,
            username=updated_user.username.value,
            email=updated_user.email.value,
            is_active=updated_user.is_active,
            roles=role_titles,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
