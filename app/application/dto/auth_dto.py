"""Authentication DTOs"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginDTO(BaseModel):
    """DTO for login request"""

    username: str
    password: str


class RegisterDTO(BaseModel):
    """DTO for user registration"""

    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)


class TokenDTO(BaseModel):
    """DTO for token response"""

    access_token: str
    token_type: str = "bearer"


class UserDTO(BaseModel):
    """DTO for user response"""

    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreateDTO(BaseModel):
    """DTO for creating a user"""

    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_active: bool = True


class UserUpdateDTO(BaseModel):
    """DTO for updating a user"""

    username: Optional[str] = Field(None, min_length=3, max_length=20)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class PasswordResetDTO(BaseModel):
    """DTO for password reset"""

    token: str
    new_password: str = Field(..., min_length=8)


class PasswordChangeDTO(BaseModel):
    """DTO for password change"""

    current_password: str
    new_password: str = Field(..., min_length=8)
