"""Base domain exception"""
from typing import Any


class DomainException(Exception):
    """Base exception for all domain errors"""
    
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

