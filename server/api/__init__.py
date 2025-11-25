from fastapi import APIRouter

from .auth import router as auth_router
from .data import router as data_router
from .explore import router as explore_router
from .files import router as files_router
from .project import router as project_router
from .user import router as user_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(project_router, prefix="/project")
router.include_router(files_router, prefix="/files")
router.include_router(data_router, prefix="/data")
router.include_router(auth_router, prefix="/auth")
router.include_router(explore_router, prefix="/explore")
router.include_router(user_router, prefix="/user")

__all__ = ["router"]