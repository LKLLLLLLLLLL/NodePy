from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from server.models.database import init_database
from pathlib import Path
from .api import router

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
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
