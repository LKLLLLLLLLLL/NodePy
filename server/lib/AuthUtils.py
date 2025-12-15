from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from server.config import (
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES as ACCESS_TOKEN_EXPIRE_MINUTES,
)
from server.config import (
    AUTH_ALGORITHM as ALGORITHM,
)
from server.config import (
    AUTH_REFRESH_TOKEN_EXPIRE_DAYS as REFRESH_TOKEN_EXPIRE_DAYS,
)
from server.config import (
    AUTH_SECRET_KEY as SECRET_KEY,
)
from server.models.database import UserRecord, get_async_session

pwd_context = CryptContext(
    schemes=["argon2"],
    argon2__time_cost=3,
    argon2__memory_cost=65536,
    argon2__parallelism=4,
    argon2__hash_len=32,
    argon2__salt_len=16,
)

class AuthUtils:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using Argon2"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()

        # Ensure sub is a string (JWT standard requirement)
        if "sub" in to_encode and not isinstance(to_encode["sub"], str):
            to_encode["sub"] = str(to_encode["sub"])
        
        if expires_delta:
            expire = datetime.now() + expires_delta
        else:
            expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a refresh token"""
        to_encode = data.copy()

        # Ensure sub is a string (JWT standard requirement)
        if "sub" in to_encode and not isinstance(to_encode["sub"], str):
            to_encode["sub"] = str(to_encode["sub"])
        
        expire = datetime.now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise ValueError("Could not validate credentials")
            return payload
        except JWTError:
            raise ValueError("Could not validate credentials")


security = HTTPBearer()
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_client: AsyncSession = Depends(get_async_session),
) -> UserRecord:
    """
    Auto check and extract the current authenticated user from the JWT token.
    This may raise a HTTPException with code 401
    """
    token = credentials.credentials
    try:
        payload = AuthUtils.verify_token(token)
    except ValueError:
        raise HTTPException(
            status_code=401, detail="Invalid token"
        )

    user_id_str = payload.get("sub")
    
    # convert user_id from string to integer
    try:
        user_id = int(user_id_str) # type: ignore
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid user ID in token"
        )

    user = await db_client.get(UserRecord, user_id)
    if user is None:
        raise HTTPException(
            status_code=401, detail="User not found"
        )

    return user