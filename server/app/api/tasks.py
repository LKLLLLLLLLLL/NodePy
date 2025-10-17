from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from ..services.task_service import TaskService
from ..context import get_task_service

router = APIRouter(prefix="/api")

@router.post("/run_nodes", status_code=202)
async def run_nodes(
    request: Dict[str, Any],
    task_service: TaskService = Depends(get_task_service)
) -> Dict[str, str]:
    """
    Submits a node execution task and returns the task ID.
    """
    project_id = "test_proj"
    user_id = "test_user"  # for debug
    
    try:
        task_id = task_service.submit_node_execution(
            node_graph=request,
            project_id=project_id,
            user_id=user_id
        )
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/task/{task_id}/status")
async def get_task_status(
    task_id: str,
    task_service: TaskService = Depends(get_task_service)
) -> Dict[str, Any]:
    """
    Retrieves the status of a specific task.
    """
    return task_service.get_task_status(task_id)
