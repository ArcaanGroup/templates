"""Exception handling utilities"""
from fastapi import HTTPException, status

from app.domain.exceptions.base import DomainException
from app.domain.exceptions.item_exceptions import ItemNotFoundException


def map_domain_exception_to_http(exception: DomainException) -> HTTPException:
    """Map domain exception to HTTP exception"""
    if isinstance(exception, ItemNotFoundException):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=exception.message
        )
    
    # Default mapping
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=exception.message
    )

