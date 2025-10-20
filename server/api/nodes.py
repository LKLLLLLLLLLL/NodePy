from fastapi import APIRouter, HTTPException, WebSocket
from server.models.graph import GraphRequestModel
from server.engine.task import execute_nodes_task
from celery.app.task import Task as CeleryTask
from typing import cast
from server.lib.SreamQueue import StreamQueue, Status
import asyncio
from server.celery import celery_app

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
