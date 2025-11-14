from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from loguru import logger
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.lib.AuthUtils import AuthUtils, get_current_user
from server.models.database import UserRecord, get_async_session

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post(
    "/signup",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Username or email already registered"},
        500: {"description": "Internal server error"},
    }
)
async def signup(
    req: SignupRequest,
    response: Response,
    db_client: AsyncSession = Depends(get_async_session)
) -> TokenResponse:
    """sign up a new user, return a JWT token (no need to login again)"""
    try:
        # check if username or email already exists
        existing = await db_client.execute(
            select(UserRecord).where(
                (UserRecord.username == req.username) | (UserRecord.email == req.email)
            )
        )
        if existing.first() is not None:
            raise HTTPException(
                status_code=400,
                detail="Username or email already registered",
            )

        # create a new user
        hashed_pwd = AuthUtils.hash_password(req.password)
        new_user = UserRecord(
            username=req.username, email=req.email, hashed_password=hashed_pwd
        )
        db_client.add(new_user)
        await db_client.commit()
        await db_client.refresh(new_user)

        # generate tokens
        access_token = AuthUtils.create_access_token({"sub": new_user.id})
        refresh_token = AuthUtils.create_refresh_token({"sub": new_user.id})

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/api/auth"
        )

        return TokenResponse(access_token=access_token)

    except HTTPException:
        await db_client.rollback()
        raise
    except Exception as e:
        await db_client.rollback()
        logger.exception(f"Error signing up user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/login",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid username or password"},
        500: {"description": "Internal server error"},
    }
)
async def login(
    req: LoginRequest, 
    response: Response,
    db_client: AsyncSession = Depends(get_async_session)
) -> TokenResponse:
    """Login user and return JWT tokens"""
    try:
        # find user
        result = await db_client.execute(
            select(UserRecord).where(UserRecord.username == req.username)
        )
        user = result.first()

        if user is None or not AuthUtils.verify_password(
            req.password, user[0].hashed_password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        # generate tokens
        access_token = AuthUtils.create_access_token({"sub": user[0].id})
        refresh_token = AuthUtils.create_refresh_token({"sub": user[0].id})

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/api/auth"
        )

        return TokenResponse(access_token=access_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error logging in: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/refresh",
    responses = {
        200: {"description": "Access token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
        500: {"description": "Internal server error"},
    })
async def refresh_access_token(
    request: Request,
    db_client: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    """Use Refresh Token to get a new Access Token if access token expired"""
    # get Refresh Token from cookies
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    try:
        # verify Refresh Token
        payload = AuthUtils.verify_token(refresh_token)

        # ensure it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401, detail="Invalid token type"
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

        # verify user still exists
        user = await db_client.get(UserRecord, user_id)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )

        # create Access Token
        new_access_token = AuthUtils.create_access_token({"sub": user_id})

        return TokenResponse(access_token=new_access_token)

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=401, detail="Invalid refresh token"
        )
    except Exception as e:
        logger.exception(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/logout",
    responses={
        200: {"description": "Logged out successfully"}
    }
)
async def logout(response: Response) -> dict[str, str]:
    """Logout user by clearing the Refresh Token"""
    response.delete_cookie(key="refresh_token", path="/api/auth")
    return {"message": "Logged out successfully"}

@router.get(
    "/me",
    responses={
        200: {"description": "Current user information retrieved successfully"},
        401: {"description": "Unauthorized"},
    })
async def get_current_user_info(current_user: UserRecord = Depends(get_current_user)) -> dict[str, Any]:
    """Get current authenticated user's information, FOR DEBUGGING"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
    }
