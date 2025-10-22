from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from server.models.data import DataView
from server.models.graph import Graph
from server.engine.task import execute_nodes_task
from server.models.database import get_session, Project, Data as DBData
from celery.app.task import Task as CeleryTask
from typing import cast
from server.lib.SreamQueue import StreamQueue, Status
import asyncio
from server.celery import celery_app

"""
The api for nodes runing, reporting and so on,
"""
router = APIRouter()

@router.get(
    "/project/{project_id}", 
    status_code=200,
    responses = {
        200: {"description": "Graph retrieved successfully", "model": Graph},
        404: {"description": "Project or graph not found"},
        403: {"description": "User has no access to this project"},
        500: {"description": "Internal server error"},
    }
)
async def get_graph(project_id: int) -> Graph:
    """
    Get the node graph for a project.
    """
    user_id = 1 # for debug
    db_client = next(get_session())
    try:
        project = db_client.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.owner_id != user_id: # type: ignore
            raise HTTPException(status_code=403, detail="User has no access to this project")
        if project.graph is None:
            raise HTTPException(status_code=404, detail="Graph not found")
        return Graph.model_validate(project.graph)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    
    
class TaskResponse(BaseModel):
    """Response returned when a task is submitted."""
    task_id: str

class NothingTodoResponse(BaseModel):
    pass

@router.post(
    "/project/sync",
    status_code=202,
    responses={
        202: {"description": "Task accepted and running", "model": TaskResponse},
        403: {"description": "User has no access to this project"},
        404: {"description": "Project not found"},
        500: {"description": "Internal server error"},
    },
)
async def sync_graph(graph: Graph) -> TaskResponse | NothingTodoResponse:
    """
    Save a node graph to the database, if topology changed, enqueue a task to execute it.
    If decide to execute, enqueues a Celery task. Use
    the returned `task_id` to subscribe to the websocket status endpoint
    `/nodes/status/{task_id}`.
    """
    user_id = 1  # for debug
    project_id = graph.project_id
    db_client = next(get_session())
    
    need_exec: bool = True
    try:
        # 1. get project graph in db first
        project = db_client.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # 2. validate whether the user has access right
        if project.owner_id != user_id: # type: ignore
            raise HTTPException(status_code=403, detail="User has no access to this project")
        
        # 3. compare the compare the topo model to decide whether to run
        graph_topo = graph.to_topo()
        if project.graph is not None:
            existing_graph = Graph.model_validate(project.graph)
            existing_topo = existing_graph.to_topo()
            if existing_topo == graph_topo:
                need_exec = False

        # 4. save graph to db
        if need_exec:
            # cleanse the graph before saving
            project.graph = graph.cleanse().model_dump() # type: ignore
        else:
            project.graph = graph.model_dump() # type: ignore
    finally:
        db_client.commit()

    if not need_exec:
        return NothingTodoResponse()

    try:
        celery_task = cast(CeleryTask, execute_nodes_task)  # to suppress type checker error
        task = celery_task.delay(  # the return message will be sent back via streamqueue
            graph_request_dict=graph_topo.model_dump(),
            user_id=user_id,
        )
        return TaskResponse(task_id=task.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/project/status/{task_id}")
async def nodes_status(task_id: str, websocket: WebSocket) -> None:
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
                            await websocket.close(code=4001, reason="Client closed the connection.")
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
                                await websocket.close(code=4000, reason="Task timed out.")
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
        try:
            await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
        except Exception:
            pass

@router.get(
    "/project/data/{data_id}", 
    status_code=200,
    responses={
        200: {"description": "Data retrieved successfully", "model": DataView},
        404: {"description": "Data not found"},
        403: {"description": "User has no access to this data"},
        500: {"description": "Internal server error"},
    }
)
async def get_node_data(data_id: int) -> DataView:
    """
    Get the data generated by a node.
    """
    user_id = 1  # for debug
    try:
        # 1. get data row from db
        db_client = next(get_session())
        data_record = db_client.query(DBData).filter(DBData.id == data_id).first()
        if data_record is None:
            raise HTTPException(status_code=404, detail="Data not found")
        # 2. check user access right here
        db_project = db_client.query(Project).filter(Project.id == data_record.project_id).first()
        if db_project is None or db_project.owner_id != user_id: # type: ignore
            raise HTTPException(status_code=403, detail="User has no access to this data")
        return DataView.model_validate(data_record.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))