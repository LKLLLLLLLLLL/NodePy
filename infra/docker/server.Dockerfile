# file structure of the container
# /nodepy/
#   ├── pyproject.toml
#   ├── uv.lock
#   ├── server/          # backend (-> project-root/server/)
#   │   ├── app/
#   │   │   └── main.py
#   │   └── ...
#   ├── static/          # frontend static files (-> project-root/client/dist/)
#   │   ├── index.html
#   │   ├── assets/
#   │   └── ...
#   └── scripts/         # utility scripts
#       └── ...


FROM python:3.13-slim AS development
WORKDIR /nodepy
# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot
# Configure uv
RUN pip install --no-cache-dir uv
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Omit development dependencies
ENV UV_NO_DEV=1
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-group worker --group server --no-group dev
# no need to copy src (in dev mode, this will be overridden by volume mount)
# Use the non-root user to run our application
USER nonroot
# Run server
CMD ["uv", "run", "fastapi", "dev", "server/main.py", "--host", "0.0.0.0", "--port", "8000"]


FROM python:3.13-slim AS production
WORKDIR /nodepy
# Setup a non-root user
RUN groupadd --system --gid 999 nonroot \
    && useradd --system --gid 999 --uid 999 --create-home nonroot
# Configure uv
RUN pip install --no-cache-dir uv
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Omit development dependencies
ENV UV_NO_DEV=1
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project --no-group worker --no-group dev --group server
# Copy src
COPY server /nodepy/server
# Copy frontend build artifacts produced on host into image
COPY client/dist /nodepy/static
# Copy scripts
COPY scripts /nodepy/scripts
# Use the non-root user to run our application
USER nonroot
# Run server
CMD ["uv", "run", "uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--access-log"]
