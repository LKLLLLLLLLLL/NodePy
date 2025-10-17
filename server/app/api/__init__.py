from fastapi import APIRouter
from .tasks import router as tasks_router
from .websocket import router as websocket_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(tasks_router)
router.include_router(websocket_router)

__all__ = ["router"]