from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.lib.AuthUtils import get_current_user
from server.models.database import (
    FileRecord,
    ProjectRecord,
    UserRecord,
    get_async_session,
)

router = APIRouter()


@router.get(
    "/me",
    responses={
        200: {"description": "Current user information retrieved successfully"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
)
async def get_current_user_info(
    db_client: AsyncSession = Depends(get_async_session),
    current_user: UserRecord = Depends(get_current_user),
) -> dict[str, Any]:
    """Get current authenticated user's information."""
    try:
        # get projects count
        projects_record = await db_client.execute(
            select(ProjectRecord).where(ProjectRecord.owner_id == current_user.id)
        )
        projects_count = len(projects_record.scalars().all())

        # get file space used and total
        user_record = await db_client.get(UserRecord, current_user.id)
        assert user_record is not None
        file_space_total = user_record.file_total_space
        files_result = await db_client.execute(
            select(FileRecord.file_size).where(
                FileRecord.user_id == current_user.id, FileRecord.is_deleted.is_(False)
            )
        )
        file_space_used = sum(row[0] for row in files_result.all())

        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "projects_count": projects_count,
            "file_space_used": file_space_used,
            "file_space_total": file_space_total,
        }
    except Exception as e:
        logger.exception(f"Error retrieving user info: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

