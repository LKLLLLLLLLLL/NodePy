from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import os
from pathlib import Path

app = FastAPI(title="NodePy API")

# Add CORS middleware to allow local frontend development origins
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


# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/nodepy")
engine = create_engine(DATABASE_URL)


# Test DB connection and print a clear log
try:
    with engine.connect() as conn:
        print("Database connected successfully")
except Exception as e:
    print(f"Database connection failed: {e}")

@app.get("/api/health")
async def health():
    """Simple health check endpoint."""
    return {"status": "ok", "database": "connected"}

# Static files directory - fixed path in container
# In container: /nodepy/static (mapped from host client/dist via mount or COPY)
dist_dir = Path("/nodepy/static")


# Mount static files if they exist
if dist_dir.exists() and dist_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")
    print(f"Frontend static files mounted at {dist_dir}")
else:
    print(f"Dist directory not found at {dist_dir}; frontend files will not be served")


# @app.get("/")
# async def root():
#     """Return the frontend index page if available."""
#     index_file = dist_dir / "index.html"
#     if index_file.exists():
#         return FileResponse(str(index_file))
#     return {"message": "Frontend not built yet"}

