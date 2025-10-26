from fastapi import APIRouter, HTTPException, WebSocket, Response, Depends
from pydantic import BaseModel
from server.models.project import Project, ProjWorkflow
from server.engine.task import execute_project_task
from server.models.database import get_session, ProjectRecord, UserRecord
from celery.app.task import Task as CeleryTask
from typing import cast
from server.lib.SreamQueue import StreamQueue, Status
from server.lib.ProjectLock import ProjectLock
from sqlalchemy.orm import Session
import asyncio
from server.celery import celery_app
from server.models.exception import ProjectLockError, ProjLockIdentityError
from loguru import logger
from server.models.project_list import ProjectList, ProjectListItem
from celery.result import AsyncResult

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
async def list_projects(db_client: Session = Depends(get_session)) -> ProjectList:
    """
    List all projects for the current user.
    """
    user_id = 1 # for debug
    try:
        project_records = db_client.query(ProjectRecord).filter(ProjectRecord.owner_id == user_id).all()
        projects: list[ProjectListItem] = []
        for project_record in project_records:
            projects.append(
                ProjectListItem(
                    project_id=project_record.id,  # type: ignore
                    project_name=project_record.name,  # type: ignore
                    owner=project_record.owner_id,  # type: ignore
                    created_at=int(project_record.created_at.timestamp() * 1000) if project_record.created_at else None,  # type: ignore
                    updated_at=int(project_record.updated_at.timestamp() * 1000) if project_record.updated_at else None,  # type: ignore
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
async def get_project(project_id: int, db_client: Session = Depends(get_session)) -> Project:
    """
    Get the full data structure of a project.
    """
    user_id = 1 # for debug
    try:
        project = db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != user_id: # type: ignore
            raise HTTPException(status_code=403, detail="User has no access to this project")
        if project.workflow is None:
            raise HTTPException(status_code=404, detail="Workflow not found")
        workflow = ProjWorkflow(**project.workflow) # type: ignore
        project = Project(
            project_name=project.name, # type: ignore
            project_id=project.id,     # type: ignore
            user_id=project.owner_id,  # type: ignore
            workflow=workflow,
        )
        return project
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
async def create_project(project_name: str, db_client: Session = Depends(get_session)) -> int:
    """
    Create a new project for a user.
    Return project id.
    """
    user_id = 1 # for debug
    try:
        # 1. check if user exists
        user = db_client.query(UserRecord).filter_by(id=user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        # 2. check if project name already exists
        existing_project = db_client.query(ProjectRecord).filter_by(name=project_name).first()
        if existing_project is not None:
            raise HTTPException(status_code=400, detail="Project name already exists")
        new_project = ProjectRecord(
            name=project_name,
            owner_id=user_id,
            workflow=ProjWorkflow.get_empty_workflow().model_dump()
        )
        db_client.add(new_project)
        db_client.commit()
        db_client.refresh(new_project)
        return new_project.id  # type: ignore
    except HTTPException:
        db_client.rollback()
        raise
    except Exception as e:
        db_client.rollback()
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
async def delete_project(project_id: int, db_client: Session = Depends(get_session)) -> None:
    """
    Delete a project.
    """
    user_id = 1 # for debug
    try:
        async with ProjectLock(project_id=project_id, max_block_time=5.0, identity=None):
            project = db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
            if project is None:
                raise HTTPException(status_code=404, detail="Project not found")
            if project.owner_id != user_id: # type: ignore
                raise HTTPException(status_code=403, detail="User has no access to this project")
            db_client.delete(project)
            db_client.commit()
            return
    except ProjectLockError:
        db_client.rollback()
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except Exception as e:
        db_client.rollback()
        logger.exception(f"Error deleting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post(
    "/rename",
    status_code=200,
    responses={
        200: {"description": "Project renamed successfully"},
        400: {"description": "Project name already exists"},
        404: {"description": "Project not found"},
        403: {"description": "User has no access to this project"},
        423: {"description": "Project is locked, it may be being edited by another process"},
        500: {"description": "Internal server error"},
    },
)
async def rename_project(project_id: int, new_name: str, db_client: Session = Depends(get_session)) -> None:
    """
    Rename a project.
    """
    user_id = 1 # for debug
    try:
        async with ProjectLock(project_id=project_id, max_block_time=5.0, identity=None):
            project = db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
            if project is None:
                raise HTTPException(status_code=404, detail="Project not found")
            if project.owner_id != user_id: # type: ignore
                raise HTTPException(status_code=403, detail="User has no access to this project")
            # check if new name already exists
            existing_project = db_client.query(ProjectRecord).filter_by(name=new_name).first()
            if existing_project is not None:
                raise HTTPException(status_code=400, detail="Project name already exists")
            project.name = new_name # type: ignore
            db_client.commit()
            return
    except ProjectLockError:
        db_client.rollback()
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except Exception as e:
        db_client.rollback()
        logger.exception(f"Error renaming project {project_id} to '{new_name}': {e}")
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
        403: {"description": "User has no access to this project"},
        404: {"description": "Project not found"},
        423: {"description": "Project is locked, it may be being edited by another process"},
        500: {"description": "Internal server error"},
    },
)
async def sync_project(project: Project, response: Response, db_client: Session = Depends(get_session)) -> TaskResponse | None:
    """
    Save a project to the database, if topology changed, enqueue a task to execute it.
    If decide to execute, enqueues a Celery task. Use
    the returned `task_id` to subscribe to the websocket status endpoint
    `/nodes/status/{task_id}`.
    """
    user_id = 1  # for debug
    project_id = project.project_id
    new_project = project
    try:
        async with ProjectLock(project_id=project.project_id, max_block_time=5.0, identity=None) as lock:            
            need_exec: bool = True
            try:
                # 1. get project workflow in db first
                project_record = db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
                if project_record is None:
                    raise HTTPException(status_code=404, detail="Project not found")
                
                # 2. validate whether the user has access right
                if project_record.owner_id != user_id: # type: ignore
                    raise HTTPException(status_code=403, detail="User has no access to this project")
                
                # 3. get old project object
                if project_record.workflow is None:
                    raise HTTPException(status_code=404, detail="Project.Workflow not found")
                old_project = Project(
                    project_name=project_record.name, # type: ignore
                    project_id=project_record.id,     # type: ignore
                    user_id=project_record.owner_id,  # type: ignore
                    workflow=ProjWorkflow(**project_record.workflow) # type: ignore
                )

                # 4. compare the compare the topo model to decide whether to run
                new_topo = new_project.to_topo()
                if project_record.workflow is not None:
                    old_topo = old_project.workflow.to_topo(project_id=project_id)
                    if old_topo == new_topo:
                        need_exec = False

                # 5. save workflow to db
                # get the project without running results
                if not need_exec:
                    # merge old running results to the new workflow
                    new_project.merge_run_results_from(old_project)
                    project_record.workflow = new_project.workflow.model_dump() # type: ignore
                else:
                    # only save the cleansed workflow, running results will be updated after execution
                    new_project.cleanse()
                    project_record.workflow = new_project.workflow.model_dump() # type: ignore
            finally:
                db_client.commit()

            if not need_exec:
                response.status_code = 204  # No Content
                return None
            
            celery_task = cast(CeleryTask, execute_project_task)  # to suppress type checker error
            task = celery_task.delay(  # the return message will be sent back via streamqueue
                topo_graph_dict=new_topo.model_dump(),
                user_id=user_id,
            )
            response.status_code = 202  # Accepted
            await lock.appoint_transfer_async(task.id)
            return TaskResponse(task_id=task.id)
    except ProjectLockError:
        db_client.rollback()
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except Exception as e:
        db_client.rollback()
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
                    await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
                    break
                
                # Cancel all pending tasks
                for task in pending:
                    task.cancel()
                
                # 3. check if websocket is disconnected
                if websocket.client_state.name != "CONNECTED":
                    celery_app.control.revoke(task_id, terminate=True)
                    break

                # 4. check if the websocket received a message from client
                if recv_task in done:
                    try:
                        message = recv_task.result()
                        # Client sent a message (usually means disconnect)
                        if message is not None:
                            celery_app.control.revoke(task_id, terminate=True)
                            await websocket.close(code=4401, reason="Client closed the connection.")
                            break
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
                        break
                
                # 5. check if received a message from the task
                if read_task in done:
                    try:
                        status, message = read_task.result()
                        
                        if status == Status.TIMEOUT:
                            timeout_count += 1
                            if timeout_count >= 12: # 1 minute timeout for one node
                                celery_app.control.revoke(task_id, terminate=True)
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
                        celery_app.control.revoke(task_id, terminate=True)
                        await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
                        break
    except Exception as e:
        logger.exception(f"Error processing websocket for task {task_id}: {e}")
        try:
            await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
        except Exception:
            pass
