from fastapi import APIRouter, WebSocket, Depends
from ..services.websocket_service import WebSocketService
from ..context import get_websocket_service

router = APIRouter(prefix="/api")

@router.websocket("/ws/task/{task_id}")
async def task_status_websocket(
    websocket: WebSocket, 
    task_id: str,
    service: WebSocketService = Depends(get_websocket_service)
):
    """
    WebSocket endpoint for receiving real-time task status updates.
    """
    await service.connect(task_id, websocket)
