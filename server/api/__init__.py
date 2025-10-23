from fastapi import APIRouter
from .project import router as project_router
from .files import router as files_router
from .data import router as data_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(project_router, prefix="/project")
router.include_router(files_router, prefix="/files")
router.include_router(data_router, prefix="/data")

__all__ = ["router"]