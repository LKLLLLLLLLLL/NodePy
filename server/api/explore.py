import base64

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.models.database import ProjectRecord, get_async_session
from server.models.explore_list import ExploreList, ExploreListItem

"""
API router for explore-related endpoints.
"""

router = APIRouter()

@router.get(
    "/explore/projects", 
    status_code=200,
)
async def get_explore_projects(
    db: AsyncSession = Depends(get_async_session),
) -> ExploreList:
    """
    Get the list of projects that are marked as 'show in explore'.
    """
    result = await db.execute(
        select(ProjectRecord).where(ProjectRecord.show_in_explore)
    )
    project_records = result.scalars().all()
    project_items = []
    for record in project_records:
        project_items.append(
            ExploreListItem(
                project_id=record.id,  # type: ignore
                project_name=record.name,  # type: ignore
                owner=record.owner_id,  # type: ignore
                created_at=int(record.created_at.timestamp() * 1000),  # type: ignore
                updated_at=int(record.updated_at.timestamp() * 1000),  # type: ignore
                thumb=base64.b64encode(record.thumb).decode("utf-8") if record.thumb else None,  # type: ignore
            )
        )
    return ExploreList(
        projects=project_items,
    )
