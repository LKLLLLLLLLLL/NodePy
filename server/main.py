from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from server.models.database import init_database
from pathlib import Path
from .api import router
import os
from loguru import logger
import sys

# config logging system
logger.remove()  # remove default handler
logger.add(
    sys.stdout,
    level="DEBUG",
    format="{time} | {level: <8} | {name}:{function}:{line} - {message}",
)  # 更详细的格式
logger.add(
    "/nodepy/logs/server.log",
    rotation="10 MB",
    level="DEBUG",
    format="{time} | {level: <8} | {name}:{function}:{line} - {message}",
)

app = FastAPI(title="NodePy API", separate_input_output_schemas=False)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# init database
init_database()

# Include API routes
app.include_router(router, prefix="/api")

# Static files directory
# In container: /nodepy/static (mapped from host client/dist via mount or COPY)
dist_dir = Path("/nodepy/static")
if dist_dir.exists():
    app.mount("/static", StaticFiles(directory=str(dist_dir), html=True), name="frontend")

# SPA fallback for all other routes
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    index_path = os.path.join(dist_dir, "index.html")
    return FileResponse(index_path)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})