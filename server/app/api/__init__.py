from fastapi import APIRouter
from .nodes import router as nodes_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(nodes_router)

__all__ = ["router"]