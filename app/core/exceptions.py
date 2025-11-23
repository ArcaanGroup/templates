"""Exception handling utilities"""
from fastapi import HTTPException, status

from app.domain.exceptions.base import DomainException


def map_domain_exception_to_http(exception: DomainException) -> HTTPException:
    """Map domain exception to HTTP exception"""

    # Default mapping
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=exception.message
    )
