"""Standard response schemas"""
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    success: bool
    message: str
    payload: T | None = None
    
    def __str__(self) -> str:
        return f"{self.success} : {self.message} -> {self.payload}"


def success(
    payload: T | None = None, message: str = "success"
) -> StandardResponse[T] | StandardResponse[None]:
    """Create a success response"""
    return StandardResponse(success=True, message=message, payload=payload)


def failure(
    payload: T | None = None, message: str = "failure"
) -> StandardResponse[T] | StandardResponse[None]:
    """Create a failure response"""
    return StandardResponse(success=False, message=message, payload=payload)

