"""Create user use case"""
from app.application.dto.auth_dto import UserCreateDTO, UserDTO
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import UserRepositoryInterface, RoleRepositoryInterface
from app.domain.exceptions.auth_exceptions import UserAlreadyExistsException
from app.domain.entities.user import User
from app.domain.entities.role import Role
from app.domain.events.user_created import UserCreatedEvent
from app.domain.value_objects.email import Email
from app.domain.value_objects.password import Password
from app.domain.value_objects.username import Username


class CreateUserUseCase:
    """Use case for creating a user"""

    def __init__(
        self,
        repository: UserRepositoryInterface,
        role_repository: RoleRepositoryInterface,
        event_bus: EventBusInterface
    ):
        self.repository = repository
        self.role_repository = role_repository
        self.event_bus = event_bus

    async def execute(self, dto: UserCreateDTO) -> UserDTO:
        """Execute the create user use case"""
        # Check if user already exists by username
        existing_user_by_username = await self.repository.get_by_username(dto.username)
        if existing_user_by_username:
            raise UserAlreadyExistsException(f"User with username '{dto.username}' already exists")

        # Also check with email
        existing_user_by_email = await self.repository.get_by_email(dto.email)
        if existing_user_by_email:
            raise UserAlreadyExistsException(f"User with email '{dto.email}' already exists")

        # Create domain entity with roles
        roles = []
        if dto.role_ids:
            for role_id in dto.role_ids:
                role = await self.role_repository.get_by_id(role_id)
                if role:
                    roles.append(role)

        user = User(
            username=Username(dto.username),
            email=Email(dto.email),
            password=Password(dto.password),
            roles=roles,
            is_active=dto.is_active
        )

        # Persist entity
        created_user = await self.repository.create(user)

        # Publish domain event
        event = UserCreatedEvent(
            user_id=created_user.id,
            username=created_user.username.value,
            email=created_user.email.value,
            created_at=created_user.created_at
        )
        await self.event_bus.publish(event)

        # Convert to DTO - get role titles for the response
        role_titles = [role.title.value for role in created_user.roles]

        # Convert to DTO
        return UserDTO(
            id=created_user.id,
            username=created_user.username.value,
            email=created_user.email.value,
            is_active=created_user.is_active,
            roles=role_titles,
            created_at=created_user.created_at,
            updated_at=created_user.updated_at
        )
