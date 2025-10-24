from fastapi import APIRouter, HTTPException, WebSocket, Response
from pydantic import BaseModel
from server.models.project import Project, ProjWorkflow
from server.engine.task import execute_project_task
from server.models.database import get_session, ProjectRecord, UserRecord
from celery.app.task import Task as CeleryTask
from typing import cast
from server.lib.SreamQueue import StreamQueue, Status
from server.lib.ProjectLock import ProjectLock
import asyncio
from server.celery import celery_app
from server.models.exception import ProjectLockError
from loguru import logger

"""
The api for nodes runing, reporting and so on,
"""
router = APIRouter()

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
async def get_project(project_id: int) -> Project:
    """
    Get the full data structure of a project.
    """
    user_id = 1 # for debug
    db_client = next(get_session())
    try:
        project = db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != user_id: # type: ignore
            raise HTTPException(status_code=403, detail="User has no access to this project")
        if project.graph is None:
            raise HTTPException(status_code=404, detail="Graph not found")
        return Project.model_validate(project.graph)
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
async def create_project(project_name: str) -> None:
    """
    Create a new project for a user.
    """
    user_id = 1 # for debug
    db_client = next(get_session())
    # 1. check if user exists
    user = db_client.query(UserRecord).filter_by(id=user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    # 2. check if project name already exists
    existing_project = db_client.query(ProjectRecord).filter_by(name=project_name).first()
    if existing_project is not None:
        raise HTTPException(status_code=400, detail="Project name already exists")
    try:
        new_project = ProjectRecord(
            name=project_name,
            owner_id=user_id,
            graph=Project(
                project_name=project_name,
                project_id=0, # will be set after insert
                user_id=user_id,
                workflow=ProjWorkflow(
                    error_message=None,
                    nodes=[],
                    edges=[],
                ),
            ).model_dump(), # type: ignore
        )
        db_client.add(new_project)
        db_client.commit()
        db_client.refresh(new_project)
        return
    except Exception as e:
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
async def delete_project(project_id: int) -> None:
    """
    Delete a project.
    """
    user_id = 1 # for debug
    db_client = next(get_session())
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
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except Exception as e:
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
async def rename_project(project_id: int, new_name: str) -> None:
    """
    Rename a project.
    """
    user_id = 1 # for debug
    db_client = next(get_session())
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
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
    except Exception as e:
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
async def sync_project(project: Project, response: Response) -> TaskResponse | None:
    """
    Save a project to the database, if topology changed, enqueue a task to execute it.
    If decide to execute, enqueues a Celery task. Use
    the returned `task_id` to subscribe to the websocket status endpoint
    `/nodes/status/{task_id}`.
    """
    try:
        async with ProjectLock(project_id=project.project_id, max_block_time=5.0, identity=None) as lock:
            
            user_id = 1  # for debug
            project_id = project.project_id
            db_client = next(get_session())
            
            need_exec: bool = True
            try:
                # 1. get project graph in db first
                project_record = db_client.query(ProjectRecord).filter(ProjectRecord.id == project_id).first()
                if project_record is None:
                    raise HTTPException(status_code=404, detail="Project not found")
                
                # 2. validate whether the user has access right
                if project_record.owner_id != user_id: # type: ignore
                    raise HTTPException(status_code=403, detail="User has no access to this project")
                
                # 3. compare the compare the topo model to decide whether to run
                graph_topo = project.to_topo()
                if project_record.graph is not None:
                    existing_graph = Project.model_validate(project_record.graph)
                    existing_topo = existing_graph.to_topo()
                    if existing_topo == graph_topo:
                        need_exec = False

                # 4. save graph to db
                # get the project without running results
                clean_graph = project.cleanse() # type: ignore
                if not need_exec:
                    # merge old running results to the new graph
                    if project_record.graph is not None:
                        existing_graph = Project.model_validate(project_record.graph)
                        clean_graph.merge_run_results_from(existing_graph)
                        project_record.graph = clean_graph.model_dump() # type: ignore
                    else:
                        project_record.graph = clean_graph.model_dump() # type: ignore
                else:
                    # only save the cleansed graph, running results will be updated after execution
                    project_record.graph = clean_graph.model_dump() # type: ignore
            finally:
                db_client.commit()

            if not need_exec:
                response.status_code = 204  # No Content
                return None
            
            celery_task = cast(CeleryTask, execute_project_task)  # to suppress type checker error
            task = celery_task.delay(  # the return message will be sent back via streamqueue
                topo_graph_dict=graph_topo.model_dump(),
                user_id=user_id,
            )
            response.status_code = 202  # Accepted
            await lock.appoint_transfer_async(task.id)
            return TaskResponse(task_id=task.id)
    except ProjectLockError:
        raise HTTPException(status_code=423, detail="Project is locked, it may be being edited by another process")
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
    """
    await websocket.accept()

    try:
        async with StreamQueue(task_id) as queue:
            timeout_count = 0
            while True:
                # Create tasks for both queue and websocket
                read_task = asyncio.create_task(queue.read_message())
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
                
                # check if websocket is disconnected
                if websocket.client_state.name != "CONNECTED":
                    celery_app.control.revoke(task_id, terminate=True)
                    break
                
                # check if the websocket received a message from client
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
                
                # check if we received a message from the task
                if read_task in done:
                    try:
                        status, message = read_task.result()
                        
                        if status == Status.TIMEOUT:
                            timeout_count += 1
                            if timeout_count >= 3:
                                celery_app.control.revoke(task_id, terminate=True)
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
