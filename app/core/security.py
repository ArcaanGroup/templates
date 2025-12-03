"""Security utilities"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.application.dto.auth_dto import UserDTO
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=True)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(claims: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    claims_to_encode = claims.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    claims_to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(claims_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(claims: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token"""
    claims_to_encode = claims.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh tokens expire in 30 days by default
        expire = datetime.utcnow() + timedelta(days=30)
    claims_to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(claims_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_refresh_token(token: str) -> dict:
    """Decode a refresh token and return its payload"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_type = payload.get("type")
        if token_type != "refresh":
            raise JWTError("Invalid token type")
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from JWT token (legacy - for backward compatibility)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # TODO: In a real app, fetch user from DB here
    return {"username": username}


def verify_refresh_token(token: str) -> bool:
    """Verify if a refresh token is valid without decoding user info"""
    from app.domain.services.auth_service import TokenService

    try:
        user_id = TokenService.decode_refresh_token(token)
        return user_id is not None
    except:
        return False


async def get_current_user_from_token(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token - this is now a placeholder for dependency injection"""
    # This function is overridden in dependencies.py with proper DI implementation
    # For imports to work properly, we need this placeholder here
    from fastapi import HTTPException, status

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    raise credentials_exception
