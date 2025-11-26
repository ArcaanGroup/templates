"""Update role use case"""
from datetime import datetime
import uuid

from app.application.dto.role_dto import RoleDTO, RoleUpdateDTO
from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import RoleRepositoryInterface
from app.domain.exceptions import EntityNotFoundException


class UpdateRoleUseCase:
    """Use case for updating a role"""

    def __init__(
        self,
        repository: RoleRepositoryInterface,
        event_bus: EventBusInterface | None = None
    ):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, role_id: uuid.UUID, dto: RoleUpdateDTO) -> RoleDTO:
        """Execute the use case to update a role"""
        role = await self._repository.get_by_id(role_id)

        if not role:
            raise EntityNotFoundException("Role", str(role_id))

        # Update the role with provided values
        if dto.title is not None:
            role.update_title(dto.title)
        if dto.description is not None:
            role.update_description(dto.description)
        if dto.permissions is not None:
            role._permissions = dto.permissions
            role.mark_as_updated()

        # Save the updated role
        updated_role = await self._repository.update(role)

        # TODO: Publish domain event when event system is implemented
        if self._event_bus:
            pass  # await self._event_bus.publish(...)

        return RoleDTO(
            id=updated_role.id,
            title=updated_role.title,
            description=updated_role.description,
            permissions=updated_role.permissions,
            created_at=updated_role.created_at,
            updated_at=updated_role.updated_at
        )
