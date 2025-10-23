from fastapi import APIRouter
from .project import router as project_router
from .files import router as files_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(project_router)
router.include_router(files_router)
router.include_router(files_router)

__all__ = ["router"]