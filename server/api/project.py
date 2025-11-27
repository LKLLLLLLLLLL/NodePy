import asyncio
import base64
import binascii
from typing import cast

from celery.app.task import Task as CeleryTask
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Response, WebSocket
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.celery import celery_app
from server.interpreter.task import execute_project_task, revoke_project_task
from server.lib.AuthUtils import get_current_user
from server.lib.ProjectLock import ProjectLock
from server.lib.StreamQueue import Status, StreamQueue
from server.lib.utils import get_project_by_id, set_project_record
from server.models.database import ProjectRecord, UserRecord, get_async_session
from server.models.exception import ProjectLockError, ProjLockIdentityError
from server.models.project import Project, ProjectSetting, ProjUIState, ProjWorkflow
from server.models.project_list import ProjectList, ProjectListItem

"""
The api for nodes runing, reporting and so on,
"""
router = APIRouter() 

@router.get(
    "/list",
    status_code=200,
    responses={
        200: {"description": "List of projects retrieved successfully", "model": ProjectList},
        500: {"description": "Internal server error"},
    },
)
async def list_projects(
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> ProjectList:
    """
    List all projects for the current user.
    """
    user_id = int(user_record.id)  # type: ignore
    try:
        project_records = await db_client.execute(
            ProjectRecord.__table__.select().where(ProjectRecord.owner_id == user_id)
        )
        projects: list[ProjectListItem] = []
        for project_record in project_records:
            projects.append(
                ProjectListItem(
                    project_id=project_record.id,  # type: ignore
                    project_name=project_record.name,  # type: ignore
                    owner=project_record.owner_id,  # type: ignore
                    created_at=int(project_record.created_at.timestamp() * 1000) if project_record.created_at else None,  # type: ignore
                    updated_at=int(project_record.updated_at.timestamp() * 1000) if project_record.updated_at else None,  # type: ignore
                    thumb=base64.b64encode(project_record.thumb).decode('utf-8') if project_record.thumb else None  # type: ignore
                )
            )
        return ProjectList(
            userid=user_id,
            projects=projects,
        )
    except Exception as e:
        logger.exception(f"Error listing projects for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get(
    "/{project_id}", 
    status_code=200,
    responses = {
        200: {"description": "Graph retrieved successfully", "model": Project},
        404: {"description": "Project or graph not found"},
        403: {"description": "User has no access to this project"},
        500: {"description": "Internal server error"},
    }
)
async def get_project(
    project_id: int,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> Project:
    """
    Get the full data structure of a project.
    """
    user_id = int(user_record.id)  # type: ignore
    try:
        project = await get_project_by_id(db_client, project_id, user_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        return project
    except HTTPException:
        raise
    except PermissionError:
        raise HTTPException(status_code=403, detail="User has no access to this project")
    except Exception as e:
        logger.exception(f"Error getting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/create",
    status_code=201,
    responses={
        201: {"description": "Project created successfully"},
        400: {"description": "Project name already exists"},
        404: {"description": "User not found"},
        500: {"description": "Internal server error"},
    },
)
async def create_project(
    project_name: str,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> int:
    """
    Create a new project for a user.
    Return project id.
    """
    user_id = int(user_record.id)  # type: ignore
    try:
        # 1. check if user exists
        user = await db_client.get(UserRecord, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        # 2. check if project name already exists
        existing_project = await db_client.execute(
            select(ProjectRecord).where(
                (ProjectRecord.name == project_name) & 
                (ProjectRecord.owner_id == user_id))
        )
        if existing_project.first() is not None:
            raise HTTPException(status_code=400, detail="Project name already exists")
        # 3. create new project
        new_project = ProjectRecord(
            name=project_name,
            owner_id=user_id,
            workflow=ProjWorkflow.get_empty_workflow().model_dump(),
            ui_state = ProjUIState.get_empty_ui_state().model_dump(),
            thumb=None
        )
        db_client.add(new_project)
        await db_client.commit()
        await db_client.refresh(new_project)
        return new_project.id  # type: ignore
    except HTTPException:
        await db_client.rollback()
        raise
    except Exception as e:
        await db_client.rollback()
        logger.exception(f"Error creating project '{project_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.delete(
    "/{project_id}",
    status_code=204,
    responses={
        204: {"description": "Project deleted successfully"},
        404: {"description": "Project not found"},
        403: {"description": "User has no access to this project"},
        423: {"description": "Project is locked, it may be being edited by another process"},
        500: {"description": "Internal server error"},
    },
)
async def delete_project(
    project_id: int,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> None:
    """
    Delete a project.
    """
    user_id = int(user_record.id)  # type: ignore
    try:
        async with ProjectLock(project_id=project_id, max_block_time=5.0, identity=None, scope="all"):
            project = await db_client.get(ProjectRecord, project_id)
            if project is None:
                raise HTTPException(status_code=404, detail="Project not found")
            if project.owner_id != user_id: # type: ignore
                raise HTTPException(status_code=403, detail="User has no access to this project")
            await db_client.delete(project)
            await db_client.commit()
            return
    except ProjectLockError:
        await db_client.rollback()
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except HTTPException:
        raise
    except Exception as e:
        await db_client.rollback()
        logger.exception(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get(
    "/setting/{project_id}",
    status_code=200,
    responses={
        200: {"description": "Project setting retrieved successfully", "model": ProjectSetting},
        404: {"description": "Project not found"},
        403: {"description": "User has no access to this project"},
        500: {"description": "Internal server error"},
    }
)
async def get_project_setting(
    project_id: int,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> ProjectSetting:
    """
    Get the settings of a project.
    """
    user_id = int(user_record.id)  # type: ignore
    try:
        project_record = await db_client.get(ProjectRecord, project_id)
        if project_record is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if project_record.owner_id != user_id: # type: ignore
            raise HTTPException(status_code=403, detail="User has no access to this project")
        return ProjectSetting(
            show_to_explore=project_record.show_in_explore,  # type: ignore
            project_name=project_record.name,  # type: ignore
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting project setting for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/update_setting",
    status_code=200,
    responses={
        200: {"description": "Project setting updated successfully"},
        400: {"description": "Project setting update failed"},
        404: {"description": "Project not found"},
        403: {"description": "User has no access to this project"},
        423: {"description": "Project is locked, it may be being edited by another process"},
        500: {"description": "Internal server error"},
    },
)
async def update_project_setting(
    project_id: int,
    setting: ProjectSetting,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> None:
    """
    Update the settings of a project.
    """
    user_id = int(user_record.id)  # type: ignore
    try:
        async with ProjectLock(project_id=project_id, max_block_time=5.0, identity=None, scope="all"):
            project_record = await db_client.get(ProjectRecord, project_id)
            if project_record is None:
                raise HTTPException(status_code=404, detail="Project not found")
            if project_record.owner_id != user_id: # type: ignore
                raise HTTPException(status_code=403, detail="User has no access to this project")
            # check if new name already exists
            existing_project = await db_client.execute(
                select(ProjectRecord).where(
                    (ProjectRecord.name == setting.project_name) & 
                    (ProjectRecord.id != project_id) & 
                    (ProjectRecord.owner_id == user_id))
            )
            if existing_project.first() is not None:
                raise HTTPException(status_code=400, detail="Project name already exists")
            # update settings
            project_record.name = setting.project_name # type: ignore
            project_record.show_in_explore = setting.show_to_explore # type: ignore
            await db_client.commit()
            return
    except ProjectLockError:
        await db_client.rollback()
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except HTTPException:
        raise
    except Exception as e:
        await db_client.rollback()
        logger.exception(f"Error updating project setting for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/sync_ui"
)
async def sync_project_ui(
    project_id: int,
    ui_state: ProjUIState,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> None:
    """
    Only save the ui of a project. Make sure the ui_state corresponds to the workflow in last sync.
    """
    user_id = int(user_record.id)  # type: ignore
    try:
        async with ProjectLock(project_id=project_id, max_block_time=5.0, identity=None, scope="ui_state"):
            project = await get_project_by_id(db_client, project_id, user_id)
            if project is None:
                raise HTTPException(status_code=404, detail="Project not found")
            # check if ui state corresponds to the workflow by assignment
            project.ui_state = ui_state.model_dump()  # type: ignore
            await set_project_record(db_client, project, user_id)
            await db_client.commit()
            return
    except ProjectLockError:
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except PermissionError:
        raise HTTPException(status_code=403, detail="User has no access to this project")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error syncing UI state for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

class TaskResponse(BaseModel):
    """Response returned when a task is submitted."""
    task_id: str

@router.post(
    "/sync",
    status_code=202,
    responses={
        204: {"description": "No execution needed, project synced", "model": None},
        202: {"description": "Task accepted and running", "model": TaskResponse},
        400: {"description": "Invalid thumbnail data"},
        403: {"description": "User has no access to this project"},
        404: {"description": "Project not found"},
        423: {"description": "Project is locked, it may be being edited by another process"},
        500: {"description": "Internal server error"},
    },
)
async def sync_project(
    project: Project,
    response: Response,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_current_user),
) -> TaskResponse | None:
    """
    Save a project to the database, if topology changed, enqueue a task to execute it.
    If decide to execute, enqueues a Celery task. Use
    the returned `task_id` to subscribe to the websocket status endpoint
    `/nodes/status/{task_id}`.
    """
    user_id = int(user_record.id)  # type: ignore
    project_id = project.project_id
    new_project = project
    need_exec: bool = True
    try:
        async with ProjectLock(project_id=project.project_id, max_block_time=5.0, identity=None, scope="all") as lock:            
            # 1. get project object from db
            old_project = await get_project_by_id(db_client, project_id, user_id)
            if old_project is None:
                raise HTTPException(status_code=404, detail="Project not found")

            # 2. compare the topo model to decide whether to run
            new_topo = new_project.to_topo()
            old_topo = old_project.workflow.to_topo(project_id=project_id)
            if old_topo == new_topo:
                need_exec = False
            
            # 3. save to db
            if not need_exec:
                logger.warning(f"Project {project.project_id} topology not changed, no need to execute. Please use /sync_ui to update UI only.")
                await set_project_record(db_client, new_project, user_id)
            else:
                await set_project_record(db_client, new_project, user_id)

            if not need_exec:
                response.status_code = 204  # No Content
                await db_client.commit()
                return None

            celery_task = cast(CeleryTask, execute_project_task)  # to suppress type checker error
            task = celery_task.delay(  # the return message will be sent back via streamqueue
                project_id=project.project_id,
                user_id=user_id,
            )
            response.status_code = 202  # Accepted
            await lock.appoint_transfer_async(task.id)
            await db_client.commit()
            return TaskResponse(task_id=task.id)
    except binascii.Error as e:
        logger.error(f"Error decoding thumb for project {project.project_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid thumbnail data")
    except ProjectLockError:
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except PermissionError:
        raise HTTPException(status_code=403, detail="User has no access to this project")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error syncing project {project.project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.websocket("/status/{task_id}")
async def project_status(task_id: str, websocket: WebSocket) -> None:
    """
    WebSocket endpoint to stream execution status for a previously-submitted task.

    The websocket will send JSON messages pushed by the worker. Each message
    is a JSON-encoded string describing stage/status/error. The connection is
    closed with code 1000 when the task finishes successfully, or other close
    codes for errors/timeouts.
    
    - 1000: Normal closure when task finishes successfully.
    - 1011: Internal server error during task execution.
    - 4400: Task timed out due to inactivity.
    - 4401: Client closed the connection.
    - 4409: Project is locked and wait time out.
    """
    await websocket.accept()

    try:
        async with StreamQueue(task_id) as queue:
            timeout_count = 0
            while True:
                # 1. Check if task fail
                task_res = AsyncResult(task_id, app=celery_app)
                if task_res.failed():
                    # Because all exceptions are handled and reported via StreamQueue,
                    # this failed should happen very rarely.
                    if isinstance(task_res.result, Exception):
                        try:
                            raise task_res.result
                        except ProjectLockError as e:
                            logger.exception(f"Project lock error for task {task_id}: {e}")
                            await websocket.close(code=4409, reason=f"Project is locked, and waitting time out. This may be caused by running one project multiple times concurrently. Details: {str(e)}")
                            break # 4409 for conflict
                        except ProjLockIdentityError as e:
                            logger.exception(f"Project lock identity error for task {task_id}: {e}")
                            await websocket.close(code=4409, reason=f"Project lock identity error: {str(e)}")
                            break
                        except Exception as e:
                            logger.exception(f"Task {task_id} failed with exception: {e}")
                            await websocket.close(code=1011, reason=f"Task failed with exception: {str(e)}")
                            break
                    else:
                        await websocket.close(code=1011, reason="Task failed.")
                        break
                
                # 2. await messages from both queue and websocket
                # Create tasks for both queue and websocket
                read_task = asyncio.create_task(queue.read_message(timeout_ms=5*1000))
                recv_task = asyncio.create_task(websocket.receive_text())

                try:
                    done, pending = await asyncio.wait(
                        {read_task, recv_task},
                        return_when=asyncio.FIRST_COMPLETED
                    )
                except Exception as e:
                    read_task.cancel()
                    recv_task.cancel()
                    raise e
                
                # Cancel all pending tasks
                for task in pending:
                    task.cancel()
                
                # 3. check if websocket is disconnected
                if websocket.client_state.name != "CONNECTED":
                    await revoke_project_task(task_id)
                    break

                # 4. check if the websocket received a message from client
                if recv_task in done:
                    try:
                        message = recv_task.result()
                        # Client sent a message (usually means disconnect)
                        if message is not None:
                            await revoke_project_task(task_id)
                            await websocket.close(code=4401, reason="Client closed the connection.")
                            break
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        raise e
                
                # 5. check if received a message from the task
                if read_task in done:
                    try:
                        status, message = read_task.result()
                        
                        if status == Status.TIMEOUT:
                            timeout_count += 1
                            if timeout_count >= 12 * 10: # 10 minutes timeout for one node
                                await revoke_project_task(task_id)
                                # avoid dead loop for user provided workflow
                                await websocket.close(code=4400, reason="Task timed out.")
                                break
                            else:
                                continue
                        else:
                            # Reset timeout counter on successful message
                            timeout_count = 0

                        assert message is not None
                        await websocket.send_text(message)

                        if status.is_finished():
                            await websocket.close(code=1000, reason="Task finished.")
                            break
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        raise e
    except Exception as e:
        await revoke_project_task(task_id)
        logger.exception(f"Error processing websocket for task {task_id}: {e}")
        try:
            await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
        except Exception:
            pass
