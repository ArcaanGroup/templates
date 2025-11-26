"""Delete role use case"""
import uuid

from app.application.interfaces.event_bus import EventBusInterface
from app.application.interfaces.repositories import RoleRepositoryInterface
from app.domain.exceptions import EntityNotFoundException


class DeleteRoleUseCase:
    """Use case for deleting a role"""

    def __init__(
        self,
        repository: RoleRepositoryInterface,
        event_bus: EventBusInterface | None = None
    ):
        self._repository = repository
        self._event_bus = event_bus

    async def execute(self, role_id: uuid.UUID) -> bool:
        """Execute the use case to delete a role"""
        # Check if role exists
        role = await self._repository.get_by_id(role_id)
        if not role:
            raise EntityNotFoundException("Role", str(role_id))

        # Delete the role
        deleted = await self._repository.delete(role_id)

        if not deleted:
            raise EntityNotFoundException("Role", str(role_id))

        # TODO: Publish domain event when event system is implemented
        if self._event_bus:
            pass  # await self._event_bus.publish(...)

        return deleted
