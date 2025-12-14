import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from server.lib.ExampleProjManager import initialize_example_projects
from server.lib.FinancialDataManager import initialize_core_symbols

# from server.lib.ApiLoggerMiddleware import ApiLoggerMiddleware
from server.models.database import init_database

from .api import router

app = FastAPI(title="NodePy API", separate_input_output_schemas=False)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

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


# add debug middleware
# if DEBUG:
#     app.add_middleware(ApiLoggerMiddleware)

# init database
init_database()

# init financial data for core symbols
initialize_core_symbols()

# init example projects for learning user
initialize_example_projects()

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
