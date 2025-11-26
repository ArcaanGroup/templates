"""Create role use case"""
import uuid
from datetime import datetime

from app.application.dto.role_dto import RoleCreateDTO, RoleDTO
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import RoleRepositoryInterface
from app.domain.entities.role import Role


class CreateRoleUseCase:
    """Use case for creating roles"""

    def __init__(
        self,
        repository: RoleRepositoryInterface,
        event_bus: EventBusInterface | None = None
    ):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, dto: RoleCreateDTO) -> RoleDTO:
        """Execute the use case to create a new role"""
        # Check if role with this title already exists
        existing_role = await self._repository.get_by_title(dto.title)
        if existing_role:
            raise ValueError(f"Role with title '{dto.title}' already exists")

        # Create the domain entity
        role = Role(
            id=uuid.uuid4(),
            title=dto.title,
            description=dto.description,
            permissions=dto.permissions,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Save the role
        saved_role = await self._repository.create(role)

        # TODO: Publish domain event when event system is implemented
        if self._event_bus:
            pass  # await self._event_bus.publish(...)

        # Return the DTO
        return RoleDTO(
            id=saved_role.id,
            title=saved_role.title,
            description=saved_role.description,
            permissions=saved_role.permissions,
            created_at=saved_role.created_at,
            updated_at=saved_role.updated_at
        )
