"""Login use case"""
from datetime import timedelta

from fastapi import HTTPException, status

from app.application.dto.auth_dto import LoginDTO, TokenDTO
from app.core.auth import fake_users_db
from app.core.config import settings
from app.core.security import create_access_token, verify_password


class LoginUseCase:
    """Use case for user login"""
    
    async def execute(self, dto: LoginDTO) -> TokenDTO:
        """Execute the login use case"""
        # TODO: Replace with actual user repository
        # For now, using mock user database
        user = fake_users_db.get(dto.username)
        if not user or not verify_password(dto.password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            claims={"sub": dto.username}, expires_delta=access_token_expires
        )
        
        return TokenDTO(access_token=access_token, token_type="bearer")

