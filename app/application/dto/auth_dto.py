"""Authentication DTOs"""
from pydantic import BaseModel


class LoginDTO(BaseModel):
    """DTO for login request"""
    username: str
    password: str


class TokenDTO(BaseModel):
    """DTO for token response"""
    access_token: str
    token_type: str = "bearer"


class UserDTO(BaseModel):
    """DTO for user response"""
    username: str

