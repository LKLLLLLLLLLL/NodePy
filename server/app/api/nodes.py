from fastapi import APIRouter, HTTPException, WebSocket
from ..model.nodes import GraphRequestModel
from ...engine.task import execute_nodes_task
from celery.app.task import Task as CeleryTask
from typing import cast
from ...lib.SreamQueue import StreamQueue, Status

"""
The api for nodes runing, reporting and so on,
"""
router= APIRouter()

@router.post("/nodes/run")
async def nodes_run(graph: GraphRequestModel) -> dict[str, str]:
    """
    submit a node graph execution task and return the task id.
    You need to use this id to query the task status later.
    """
    user_id = "test_user"  # for debug
    
    try:
        celery_task = cast(CeleryTask, execute_nodes_task) # to suppress type checker error
        task = celery_task.delay( # the return message will be sent back via redis pub/sub
            graph_request_dict=graph.model_dump(),
            user_id=user_id
        )
        return {"task_id": task.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/nodes/status/{task_id}")
async def nodes_status(task_id: str, websocket: WebSocket):
    """
    WebSocket endpoint to get the return message of a node graph execution task.
    """
    await websocket.accept()

    async with StreamQueue(task_id) as queue:
        while True:
            status, message = await queue.read_message()
            
            if status == Status.TIMEOUT:
                await websocket.close(code=1006, reason="Task timed out.")

            assert message is not None
            await websocket.send_text(message)

            if status.is_finished():
                await websocket.close(code=1000, reason="Task finished.")
                break
