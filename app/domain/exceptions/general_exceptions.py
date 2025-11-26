"""General domain exceptions"""

from app.domain.exceptions.base import DomainException


class EntityNotFoundException(DomainException):
    """Raised when an entity is not found"""
    def __init__(self, entity_type: str, identifier: str | int):
        super().__init__(f"{entity_type} with identifier {identifier} not found")
        self.entity_type = entity_type
        self.identifier = identifier
