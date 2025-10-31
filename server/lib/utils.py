from sqlalchemy.ext.asyncio import AsyncSession
from server.models.project import Project, ProjUIState, ProjWorkflow
from server.models.database import ProjectRecord
import base64


async def get_project_by_id(
    db: AsyncSession, project_id: int, user_id: int
) -> Project | None:
    project_record = await db.get(ProjectRecord, project_id)
    if project_record is None:
        return None
    if project_record.owner_id != user_id:  # type: ignore
        raise PermissionError("User does not have access to this project.")
    workflow = ProjWorkflow(**project_record.workflow)  # type: ignore
    ui_state = ProjUIState(**project_record.ui_state)  # type: ignore
    return Project(
        project_name=project_record.name,  # type: ignore
        project_id=project_record.id,  # type: ignore
        user_id=project_record.owner_id,  # type: ignore
        updated_at=int(project_record.updated_at.timestamp() * 1000),  # type: ignore
        thumb=project_record.thumb.decode("utf-8") if project_record.thumb else None,  # type: ignore
        workflow=workflow,
        ui_state=ui_state,
    )


async def set_project_record(db: AsyncSession, project: Project, user_id: int) -> None:
    project_record = await db.get(ProjectRecord, project.project_id)
    if project_record is None:
        raise ValueError("Project not found.")
    if project_record.owner_id != user_id:  # type: ignore
        raise PermissionError("User does not have access to this project.")
    try:
        project_record.name = project.project_name  # type: ignore
        project_record.workflow = project.workflow.model_dump()  # type: ignore
        project_record.ui_state = project.ui_state.model_dump()  # type: ignore
        project_record.thumb = (  # type: ignore
            base64.b64decode(project.thumb) if project.thumb else None
        )
        await db.commit()
    except Exception:
        await db.rollback()
        raise
